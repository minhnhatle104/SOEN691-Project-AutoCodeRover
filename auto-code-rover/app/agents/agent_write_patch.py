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

SYSTEM_PROMPT = """You are a Java software engineer fixing bugs using minimal and precise code edits.

You receive:
- A bug report between <issue> and </issue>
- Relevant buggy Java code snippets

Your task:
- Write a patch that ONLY modifies the necessary parts of the buggy code.
- DO NOT change test files or add test code.
- DO NOT include helper functions unless absolutely required.

⚠️ Patch rules:
- Use proper Java syntax, modifiers, and imports
- Match exact indentation, comments, and formatting of the original code
- Avoid changing unrelated logic

The correctness of your patch depends on your ability to match the <original> block perfectly from the source code. Validation will fail if there are formatting mismatches.

Think carefully and write only what's needed to fix the bug.
"""

USER_PROMPT_INIT = """You are fixing a Java bug based on relevant code context.

➡️ First, briefly explain your reasoning in 1–2 sentences.
➡️ Then provide the patch using the exact format described below.

Rules:
- ONLY change code that is required to resolve the issue.
- Use additional context if the bug spans multiple locations.
- DO NOT modify test files.
- DO NOT add helper functions unless absolutely needed.
- Use precise Java syntax, modifiers, and indentation.
- If you add imports, explain clearly why they are required.

⚠️ Critical Formatting Rules:
- The <original> block MUST be copied **verbatim** from the source file. This means:
  - EXACT same indentation and whitespace.
  - ALL modifiers (e.g., public static), comments, and annotations (e.g., @Override).
  - Match line breaks and structure precisely.

✅ Patch Format:

# modification 1

```
<file>path/to/File.java</file><original> [EXACT original code snippet from source] </original><patched> [Your modified version of the above snippet] </patched>
```

# modification 2
```
<file>...</file> <original>...</original> <patched>...</patched>
```
❌ DO NOT:
- Include line numbers.
- Re-indent the code.
- Omit modifiers or annotations.
- Make unrelated code changes.

✅ DO:
- Focus only on bug-related edits.
- Preserve existing style and structure.

Your output will be parsed and applied programmatically. Any mismatch in the <original> block will cause the patch to be rejected. Pay careful attention.
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
        prompt += "Only modify the locations that are necessary, but consider related locations if fixing one depends on or affects the other. If multiple code locations are needed to fully resolve the issue, include all necessary edits."
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

def generator(
    context_thread: MessageThread,
    output_dir: str,
) -> Generator[tuple[bool, str, str], str | None, None]:
    messages = deepcopy(context_thread.messages)
    new_thread: MessageThread = MessageThread(messages=messages)
    new_thread = agent_common.replace_system_prompt(new_thread, SYSTEM_PROMPT)

    new_thread.add_user(USER_PROMPT_INIT)
    print_acr(USER_PROMPT_INIT, "patch generation")

    index = 1
    feedback: str | None = None

    while True:
        if feedback:
            new_thread.add_user(feedback)
            print_patch_generation(feedback, f"feedback {index}")

        logger.info(f"Trying to write a patch. Try {index}.")
        res_text, *_ = common.SELECTED_MODEL.call(new_thread.to_msg())

        new_thread.add_model(res_text, tools=[])
        print_patch_generation(res_text, f"try {index}")

        raw_patch_file = pjoin(output_dir, f"agent_patch_raw_{index}")
        Path(raw_patch_file).write_text(res_text)

        debug_file = pjoin(output_dir, f"debug_agent_write_patch_{index}.json")
        new_thread.save_to_file(debug_file)

        with NamedTemporaryFile(prefix="extracted_patch-", suffix=".diff") as f:
            extract_status, extract_msg = extract_diff_one_instance(
                raw_patch_file, f.name
            )
            patch_content = Path(f.name).read_text()

        record_extract_status(output_dir, extract_status)

        if extract_status == ExtractStatus.APPLICABLE_PATCH:
            print_acr(f"```diff\n{patch_content}\n```", "extracted patch")
            feedback = yield True, "written an applicable patch", patch_content
            if feedback is None:
                return
            else:
                feedback = f"Your patch is invalid. {feedback}. Please try again:\n\n{USER_PROMPT_INIT}"
        else:
            feedback = yield False, "failed to write an applicable patch", ""
            if feedback is None:
                feedback = (
                    "Your edit could not be applied to the program. "
                    + extract_msg
                    + " Please try again.\n\n"
                    + USER_PROMPT_INIT
                )

        index += 1
