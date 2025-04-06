"""
Utility functions for parsing and applying the patch.

Inspired by:
https://github.com/gpt-engineer-org/gpt-engineer/blob/main/gpt_engineer/core/chat_to_files.py
"""

import re
import difflib
from dataclasses import dataclass
from pprint import pformat
from typing import TextIO
from pathlib import Path

@dataclass
class Edit:
    filename: str
    before: str
    after: str

    def __str__(self):
        return f"{self.filename}\nBefore:\n{pformat(self.before)}\nAfter:\n{pformat(self.after)}\n"

    def __repr__(self):
        return str(self)

def parse_edits(chat_string: str) -> list[Edit]:
    def parse_in_fence(lines: list[str]):
        lines = [line for line in lines if line.strip() != "# Rest of the code..."]

        file_pattern = re.compile(r"<file>(.*?)</file>", re.DOTALL)
        original_pattern = re.compile(r"<original>(.*?)</original>", re.DOTALL)
        patched_pattern = re.compile(r"<patched>(.*?)</patched>", re.DOTALL)

        content = "\n".join(lines)
        files = file_pattern.findall(content)
        originals = original_pattern.findall(content)
        patched = patched_pattern.findall(content)

        return [
            Edit(file.strip(), orig.strip("\n"), patch.strip("\n"))
            for file, orig, patch in zip(files, originals, patched)
        ]

    edits, current, in_fence = [], [], False
    for line in chat_string.split("\n"):
        if line.startswith("```"):
            if in_fence:
                edits.extend(parse_in_fence(current))
                current = []
            in_fence = not in_fence
        elif in_fence:
            current.append(line)
    return edits

def apply_edit(edit: Edit, file_path: str) -> str | None:
    try:
        orig_lines = Path(file_path).read_text().splitlines(keepends=True)
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return None

    before_lines = edit.before.strip("\n").splitlines()
    after_lines = edit.after.strip("\n").splitlines()

    def normalize(s):
        return re.sub(r"\s+", "", s)

    norm_before = [normalize(line) for line in before_lines]

    for i in range(len(orig_lines) - len(before_lines) + 1):
        window = [normalize(line) for line in orig_lines[i : i + len(before_lines)]]
        if window == norm_before:
            leading_indent = len(orig_lines[i]) - len(orig_lines[i].lstrip())
            indented_after = [
                (" " * leading_indent + l).rstrip() + "\n" if l.strip() else "\n"
                for l in after_lines
            ]
            new_lines = orig_lines[:i] + indented_after + orig_lines[i + len(before_lines):]
            Path(file_path).write_text("".join(new_lines))
            print(f"✅ Patch applied to {file_path}")
            return file_path

    # Fuzzy fallback
    joined_orig = "".join(orig_lines)
    before_block = "\n".join(before_lines).strip()
    match = difflib.get_close_matches(before_block, [joined_orig], n=1, cutoff=0.8)
    if match:
        print(f"⚠️ Fuzzy match found for: {file_path} but not applied")
    else:
        print(f"❌ Could not apply patch to {file_path} - match not found")
        print("🔍 Tried to match:")
        print("\n".join(before_lines))
    return None

def lint_python_content(content: str) -> bool:
    # For Java, we assume it's valid syntax and skip linting
    return True

class Writable(TextIO):
    def __init__(self) -> None:
        self.content: list[str] = []
    def write(self, s: str) -> int:
        self.content.append(s)
        return len(s)
    def read(self, n: int = 0) -> str:
        return "\n".join(self.content)
