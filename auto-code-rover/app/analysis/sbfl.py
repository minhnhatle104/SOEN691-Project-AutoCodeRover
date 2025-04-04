"""
Modified from pinpoint:
https://github.com/Generalized-SBFL/pytest-pinpoint/blob/master/pytest_pinpoint.py

Modified to support Java SBFL analysis using JaCoCo XML reports.

This file analyzes the coverage data for SBFL analysis.
"""

import os
import re
import math
import xml.etree.ElementTree as ET
from os.path import join as pjoin
from pathlib import Path
from typing import Tuple, List
from pprint import pformat
from functools import cache

from app import log
from app.task import SweTask, Task
from app.data_structures import MethodId


class NoCoverageData(RuntimeError):
    """Raised when JaCoCo coverage data is not available."""
    def __init__(self, testing_log_file: str):
        self.testing_log_file = testing_log_file


class FileExecStats:
    """Stores line-level test pass/fail statistics for a source file."""
    def __init__(self, filename: str):
        self.filename = filename
        self.line_stats: dict[int, tuple[int, int]] = dict()  # line -> (pass, fail)

    def incre_pass_count(self, line_no: int):
        if line_no in self.line_stats:
            passed, failed = self.line_stats[line_no]
            self.line_stats[line_no] = (passed + 1, failed)
        else:
            self.line_stats[line_no] = (1, 0)

    def incre_fail_count(self, line_no: int):
        if line_no in self.line_stats:
            passed, failed = self.line_stats[line_no]
            self.line_stats[line_no] = (passed, failed + 1)
        else:
            self.line_stats[line_no] = (0, 1)

    def __str__(self):
        return self.filename + "\n" + pformat(self.line_stats)


class ExecStats:
    """Aggregates execution statistics across files and computes suspiciousness scores."""
    def __init__(self):
        self.file_stats: dict[str, FileExecStats] = dict()

    def add_file(self, file_exec_stats: FileExecStats):
        self.file_stats[file_exec_stats.filename] = file_exec_stats

    @staticmethod
    def ochiai(failed, passed, total_fail, total_pass):
        denom = math.sqrt(total_fail * (failed + passed))
        return failed / denom if denom else 0

    def rank_lines(self, total_fail: int, total_pass: int) -> List[Tuple[str, int, float]]:
        """Compute suspiciousness scores using Ochiai and rank all lines."""
        lines_with_scores = []
        for file, stats in self.file_stats.items():
            for line_no, (passed, failed) in stats.line_stats.items():
                score = self.ochiai(failed, passed, total_fail, total_pass)
                lines_with_scores.append((file, line_no, score))
        lines_with_scores.sort(key=lambda x: (-x[2], x[0], x[1]))
        return lines_with_scores


def run(task: Task) -> tuple[list[str], list[tuple[str, int, float]], str]:
    """Entry point for SBFL analysis. Dispatches to Java or other handlers."""
    if isinstance(task, SweTask):
        return run_java_sbfl(task)
    raise NotImplementedError(f"SBFL does not support {type(task).__name__}")


def run_java_sbfl(task: SweTask) -> tuple[list[str], list[tuple[str, int, float]], str]:
    """Run SBFL analysis for Java using JaCoCo XML report."""
    jacoco_report_path = Path(task.project_path) / "target" / "site" / "jacoco" / "jacoco.xml"
    log_file = str(Path(task.project_path) / "jacoco_run.log")

    if not jacoco_report_path.exists():
        raise NoCoverageData(log_file)

    exec_stats = ExecStats()
    test_file_names = []

    tree = ET.parse(jacoco_report_path)
    root = tree.getroot()

    for pkg in root.findall("package"):
        pkg_name = pkg.attrib["name"]
        for src_file in pkg.findall("sourcefile"):
            file_name = src_file.attrib["name"]
            full_path = os.path.join(pkg_name.replace(".", "/"), file_name)
            test_file_names.append(full_path)
            file_stats = FileExecStats(full_path)

            for line in src_file.findall("line"):
                line_num = int(line.attrib["nr"])
                ci = int(line.attrib.get("ci", 0))
                mi = int(line.attrib.get("mi", 0))

                if ci > 0:
                    file_stats.incre_pass_count(line_num)
                elif mi > 0:
                    file_stats.incre_fail_count(line_num)

            exec_stats.add_file(file_stats)

    total_pass = 1  # dummy to avoid divide-by-zero
    total_fail = 1

    ranked_lines = exec_stats.rank_lines(total_fail, total_pass)
    return test_file_names, ranked_lines, log_file


def collate_results(
    ranked_lines: list[tuple[str, int, float]], test_file_names: list[str]
) -> list[tuple[str, int, int, float]]:
    """Merge adjacent suspicious lines and exclude test files."""
    positive_lines = [line for line in ranked_lines if line[2] > 0]
    survived_lines = []
    for file, line_no, score in positive_lines:
        if not any(file.endswith(t) for t in test_file_names):
            survived_lines.append((file, line_no, score))

    file_line_score = {}
    for file, line_no, score in survived_lines:
        file_line_score.setdefault(file, []).append((line_no, score))

    merged = []
    for file, entries in file_line_score.items():
        entries.sort()
        i = 0
        while i < len(entries):
            start = entries[i][0]
            score = entries[i][1]
            end = start
            while i + 1 < len(entries) and entries[i + 1][0] == end + 1:
                i += 1
                end = entries[i][0]
                score = max(score, entries[i][1])
            merged.append((file, start, end, score))
            i += 1

    merged.sort(key=lambda x: (-x[3], x[0], x[1]))
    return merged


def map_collated_results_to_methods(
    ranked_ranges: list[tuple[str, int, int, float]]
) -> list[tuple[str, str, str, float]]:
    """
    Map suspicious ranges to methods in Java files.
    NOTE: Placeholder implementation. Java method mapping requires javalang or similar parser.
    """
    results = []
    for file, start, end, score in ranked_ranges:
        results.append((file, "", "", score))  # no method mapping yet
    return results
