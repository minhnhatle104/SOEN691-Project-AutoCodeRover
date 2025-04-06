# File: agent_write_patch.py
# File: agent_write_patch.py
import os
from collections import defaultdict
from collections.abc import Generator
from copy import deepcopy
from os.path import join as pjoin
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TypeAlias

from loguru import logger

from app.agents import agent_common
from app.agents.agent_common import InvalidLLMResponse
from app.data_structures import BugLocation, MessageThread
from app.log import print_acr, print_patch_generation
from app.model import common
from app.post_process import (
    ExtractStatus,
    convert_response_to_diff,
    extract_diff_one_instance,
    record_extract_status,
)
from app.search.search_manage import SearchManager
from app.task import Task

SYSTEM_PROMPT = """You are a software developer maintaining a large Java project.
You are working on an issue submitted to your project.
The issue contains a description marked between <issue> and </issue>.
Another developer has already collected code context related to the issue for you.
Your task is to write a patch that resolves this issue.
Do not make changes to test files or write tests; you are only interested in crafting a patch.
REMEMBER:
- You should only make minimal changes to the code to resolve the issue.
- Your patch should preserve the program functionality as much as possible.
- In your patch, DO NOT include the line numbers at the beginning of each line!
- You are working with Java code. Pay close attention to:
  - matching exact whitespace/indentation from the source file,
  - preserving class/method structure,
  - avoiding imports unless absolutely needed,
  - generic types and exception safety.
"""

USER_PROMPT_INIT = """Write a patch for the issue, based on the relevant Java code context.
First explain your reasoning in 1-2 sentences.
Then provide the patch in the specified format below.

Rules:
 - Modify only the necessary locations.
 - Pay attention to additional context if fixing there makes more sense.
 - You must exactly match the original snippet in formatting, indentation, and casing.
 - Avoid editing test files.
 - Do not include helper functions unless clearly necessary.
 - If you import anything, explain why.

Format:

# modification 1
```
<file>...</file>
<original>...</original>
<patched>...</patched>
```

# modification 2
```
<file>...</file>
<original>...</original>
<patched>...</patched>
```

NOTE:
- DO NOT include line numbers.
- The content in <original> MUST match the exact block of Java code in the source file.
- Use correct syntax and formatting to ensure the patch applies successfully.
"""

PatchHandle: TypeAlias = str


class PatchAgent:
    EMPTY_PATCH_HANDLE = "EMPTY"

    def __init__(self, task: Task, search_manager: SearchManager, issue_stmt: str, context_thread: MessageThread, bug_locs: list[BugLocation], task_dir: str) -> None:
        self.task = task
        self.search_manager = search_manager
        self.issue_stmt = issue_stmt
        self.context_thread = context_thread
        self.bug_locs: list[BugLocation] = bug_locs
        self.task_dir = task_dir

        self._request_idx: int = -1
        self._responses: dict[PatchHandle, str] = {}
        self._diffs: dict[PatchHandle, str] = {}
        self._feedbacks: dict[PatchHandle, list[str]] = defaultdict(list)
        self._history: list[PatchHandle] = []

    def write_applicable_patch_without_feedback(self, retries: int = 3) -> tuple[PatchHandle, str]:
        return self._write_applicable_patch(max_feedbacks=0, retries=retries)

    def write_applicable_patch_with_feedback(self, max_feedbacks: int = 1, retries: int = 3) -> tuple[PatchHandle, str]:
        return self._write_applicable_patch(max_feedbacks=max_feedbacks, retries=retries)

    def add_feedback(self, handle: PatchHandle, feedback: str) -> None:
        if handle not in self._diffs:
            raise ValueError("patch {} does not exist", handle)
        self._feedbacks[handle].append(feedback)

    def _write_applicable_patch(self, max_feedbacks: int, retries: int) -> tuple[PatchHandle, str]:
        max_feedbacks = max_feedbacks if max_feedbacks >= 0 else len(self._history)
        num_feedbacks = min(max_feedbacks, len(self._history))
        history_handles = self._history[-num_feedbacks:]

        for _ in range(retries):
            applicable, response, diff_content, thread = self._write_patch(history_handles)
            self._request_idx += 1
            print_patch_generation(response)
            Path(self.task_dir, f"patch_raw_{self._request_idx}.md").write_text(response)
            thread.save_to_file(Path(self.task_dir, f"conv_patch_{self._request_idx}.json"))

            msg = "Patch is applicable" if applicable else "Patch is not applicable"
            print_acr(msg)
            if applicable:
                print_acr(f"```diff\n{diff_content}\n```", "Extracted patch")
                handle = self._register_applicable_patch(response, diff_content)
                return handle, diff_content

        raise InvalidLLMResponse(f"Failed to write an applicable patch in {retries} attempts")

    def _write_patch(self, history_handles: list[PatchHandle] | None = None) -> tuple[bool, str, str, MessageThread]:
        history_handles = history_handles or []
        thread = self._construct_init_thread()

        for handle in history_handles:
            feedbacks = self._feedbacks.get(handle, [])
            if not feedbacks:
                logger.warning("patch {} does not have a feedback; skipping", handle)
                continue
            thread.add_model(self._responses[handle], [])
            for feedback in feedbacks:
                thread.add_user(feedback)

        thread.add_user(USER_PROMPT_INIT)

        if not history_handles:
            print_acr(USER_PROMPT_INIT)

        patch_resp, *_ = common.SELECTED_MODEL.call(thread.to_msg())
        thread.add_model(patch_resp)

        extract_status, _, diff_content = convert_response_to_diff(patch_resp, self.task_dir)
        record_extract_status(self.task_dir, extract_status)

        return (
            extract_status == ExtractStatus.APPLICABLE_PATCH,
            patch_resp,
            diff_content,
            thread,
        )

    def _construct_init_thread(self) -> MessageThread:
        if self.bug_locs:
            thread = MessageThread()
            thread.add_system(SYSTEM_PROMPT)
            thread.add_user(f"Here is the issue:\n{self.issue_stmt}")
            thread.add_user(self._construct_code_context_prompt())
        else:
            messages = deepcopy(self.context_thread.messages)
            thread = MessageThread(messages)
            thread = agent_common.replace_system_prompt(thread, SYSTEM_PROMPT)
        return thread

    def _construct_code_context_prompt(self) -> str:
        prompt = "Here are the possible buggy locations collected by someone else. "
        prompt += "Each location contains the actual code snippet and the intended behavior of the code for resolving the issue.\n"
        prompt += BugLocation.multiple_locs_to_str_for_model(self.bug_locs)
        prompt += "Note that you DO NOT NEED to modify every location; you should think what changes are necessary for resolving the issue, and only propose those modifications."
        return prompt

    def _register_applicable_patch(self, response: str, diff_content: str) -> PatchHandle:
        handle = str(self._request_idx)
        assert handle not in self._responses
        assert handle not in self._feedbacks
        assert handle not in self._diffs
        assert handle not in self._history
        self._responses[handle] = response
        self._diffs[handle] = diff_content
        self._history.append(handle)
        return handle
