from javalang import parse, tree
import os
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
    def __init__(self, testing_log_file: str):
        self.testing_log_file = testing_log_file


class FileExecStats:
    def __init__(self, filename: str):
        self.filename = filename
        self.line_stats: dict[int, tuple[int, int]] = dict()

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
    def __init__(self):
        self.file_stats: dict[str, FileExecStats] = dict()

    def add_file(self, file_exec_stats: FileExecStats):
        self.file_stats[file_exec_stats.filename] = file_exec_stats

    @classmethod
    def parse_jacoco(cls, jacoco_xml: str) -> "ExecStats":
        stats = ExecStats()
        tree = ET.parse(jacoco_xml)
        root = tree.getroot()

        for package in root.findall('.//package'):
            for sourcefile in package.findall('sourcefile'):
                filename = f"{package.attrib['name']}/{sourcefile.attrib['name']}"
                file_stats = FileExecStats(filename)

                for line in sourcefile.findall('.//line'):
                    line_no = int(line.attrib['nr'])
                    covered = int(line.attrib['ci']) > 0
                    if covered:
                        file_stats.incre_pass_count(line_no)
                    else:
                        file_stats.incre_fail_count(line_no)

                stats.add_file(file_stats)
        return stats

    @staticmethod
    def ochiai(failed, passed, total_fail, total_pass):
        denom = math.sqrt(total_fail * (failed + passed))
        return failed / denom if denom else 0

    def rank_lines(self, total_fail: int, total_pass: int) -> List[Tuple[str, int, float]]:
        lines_with_scores = []
        for file, stats in self.file_stats.items():
            for line_no, (passed, failed) in stats.line_stats.items():
                score = self.ochiai(failed, passed, total_fail, total_pass)
                lines_with_scores.append((file, line_no, score))
        lines_with_scores.sort(key=lambda x: (-x[2], x[0], x[1]))
        return lines_with_scores


def run(task: Task) -> tuple[list[str], list[tuple[str, int, float]], str]:
    if isinstance(task, SweTask):
        return run_java_sbfl(task)
    raise NotImplementedError(f"SBFL does not support {type(task).__name__}")


def run_java_sbfl(task: SweTask) -> tuple[list[str], list[tuple[str, int, float]], str]:
    jacoco_report_path = Path(task.project_path) / "target" / "site" / "jacoco" / "jacoco.xml"
    log_file = str(Path(task.project_path) / "jacoco_run.log")

    if not jacoco_report_path.exists():
        raise NoCoverageData(log_file)

    exec_stats = ExecStats.parse_jacoco(str(jacoco_report_path))
    total_fail = max(len(task.testcases_failing), 1)
    total_pass = max(len(task.testcases_passing), 1)

    ranked_lines = exec_stats.rank_lines(total_fail, total_pass)
    return [], ranked_lines, log_file


def collate_results(
    ranked_lines: list[tuple[str, int, float]], test_file_names: list[str]
) -> list[tuple[str, int, int, float]]:
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


def method_ranges_in_file_java(file: str) -> dict[MethodId, tuple[int, int]]:
    content = Path(file).read_text()
    try:
        ast = parse.parse(content)
    except Exception:
        return {}

    ranges = {}
    for path, node in ast.filter(tree.MethodDeclaration):
        class_node = next((n for n in path if isinstance(n, tree.ClassDeclaration)), None)
        if not class_node:
            continue
        start = node.position.line if node.position else 0
        end = node._position.line if node.position else start
        method_id = MethodId(class_node.name, node.name)
        ranges[method_id] = (start, end)
    return ranges


@cache
def method_ranges_in_file(file: str) -> dict[MethodId, tuple[int, int]]:
    if file.endswith(".java"):
        return method_ranges_in_file_java(file)
    return {}


def map_collated_results_to_methods(
    ranked_ranges: list[tuple[str, int, int, float]]
) -> list[tuple[str, str, str, float]]:
    results = []
    for file, start, end, score in ranked_ranges:
        method_map = method_ranges_in_file(file)
        for method_id, (m_start, m_end) in method_map.items():
            if m_start <= end and m_end >= start:
                results.append((file, method_id.class_name, method_id.method_name, score))
                break
    return results
