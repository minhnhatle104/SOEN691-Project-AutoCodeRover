"""
Directly taken from Multi-SWE-bench. Main content are from multi-swe-bench-env/swebench/harness/log_parsers.py
"""

import re
from enum import Enum


class TestStatus(Enum):
    FAILED = "FAILED"
    PASSED = "PASSED"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"

def parse_log_maven(log: str, test_id: str) -> dict:
    test_status_map = {}
    if "[ERROR] Failures:" in log or "[ERROR] Errors:" in log:
        test_status_map[test_id] = TestStatus.FAILED.value
    elif "[ERROR]" in log:
        test_status_map[test_id] = TestStatus.ERROR.value
    elif "[INFO] BUILD SUCCESS" in log:
        test_status_map[test_id] = TestStatus.PASSED.value
    elif "Tests run: 0" in log or "T E S T" not in log:
        test_status_map[test_id] = TestStatus.SKIPPED.value
    else:
        test_status_map[test_id] = TestStatus.FAILED.value
    return test_status_map

def parse_log_gradle(log: str, test_id: str) -> dict:
    test_status_map = {}
    if "FAILURE" in log:
        test_status_map[test_id] = TestStatus.FAILED.value
    elif "BUILD FAILED" in log:
        test_status_map[test_id] = TestStatus.ERROR.value
    elif "BUILD SUCCESSFUL" in log:
        test_status_map[test_id] = TestStatus.PASSED.value
    else:
        test_status_map[test_id] = TestStatus.FAILED.value
    return test_status_map

MAP_REPO_TO_PARSER = {
    "apache/dubbo": parse_log_maven,
    "fasterxml/jackson-core": parse_log_maven,
    "fasterxml/jackson-databind": parse_log_maven,
    "fasterxml/jackson-dataformat-xml": parse_log_maven,
    "google/gson": parse_log_maven,

    "googlecontainertools/jib": parse_log_gradle,

    # You can expand this for completeness if needed
}

def normalize_repo_name_from_task_id(task_id: str) -> str:
    repo = task_id.split("-")[0]
    return repo.replace("__", "/")

TESTS_ERROR = ">>>>> Tests Errored"
TESTS_TIMEOUT = ">>>>> Tests Timed Out"

def get_logs_eval(task_id: str, log_file_path: str):
    repo_name = normalize_repo_name_from_task_id(task_id)
    log_parser = MAP_REPO_TO_PARSER.get(repo_name)
    if not log_parser:
        raise ValueError(f"No log parser registered for {repo_name}")
    with open(log_file_path) as f:
        content = f.read()
        if TESTS_ERROR in content or TESTS_TIMEOUT in content:
            return {}, False
        return log_parser(content, task_id), True

def test_passed(case, sm):
    return case in sm and sm[case] == TestStatus.PASSED.value

def test_failed(case, sm):
    return case not in sm or sm[case] in [TestStatus.FAILED.value, TestStatus.ERROR.value]

FAIL_TO_PASS = "FAIL_TO_PASS"
FAIL_TO_FAIL = "FAIL_TO_FAIL"
PASS_TO_PASS = "PASS_TO_PASS"
PASS_TO_FAIL = "PASS_TO_FAIL"

def get_eval_report(eval_sm: dict, gold_results: dict, calculate_to_fail: bool = False) -> dict:
    f2p_success, f2p_failure = [], []
    for test_case in gold_results[FAIL_TO_PASS]:
        if test_passed(test_case, eval_sm):
            f2p_success.append(test_case)
        elif test_failed(test_case, eval_sm):
            f2p_failure.append(test_case)

    p2p_success, p2p_failure = [], []
    for test_case in gold_results[PASS_TO_PASS]:
        if test_passed(test_case, eval_sm):
            p2p_success.append(test_case)
        elif test_failed(test_case, eval_sm):
            p2p_failure.append(test_case)

    results = {
        FAIL_TO_PASS: {"success": f2p_success, "failure": f2p_failure},
        PASS_TO_PASS: {"success": p2p_success, "failure": p2p_failure},
    }

    if calculate_to_fail:
        f2f_success, f2f_failure, p2f_success, p2f_failure = [], [], [], []
        for test_case in gold_results[FAIL_TO_FAIL]:
            if test_passed(test_case, eval_sm):
                f2f_success.append(test_case)
            elif test_failed(test_case, eval_sm):
                f2f_failure.append(test_case)

        for test_case in gold_results[PASS_TO_FAIL]:
            if test_passed(test_case, eval_sm):
                p2f_success.append(test_case)
            elif test_failed(test_case, eval_sm):
                p2f_failure.append(test_case)

        results.update({
            FAIL_TO_FAIL: {"success": f2f_success, "failure": f2f_failure},
            PASS_TO_FAIL: {"success": p2f_success, "failure": p2f_failure},
        })

    return results

class ResolvedStatus(Enum):
    NO = "RESOLVED_NO"
    PARTIAL = "RESOLVED_PARTIAL"
    FULL = "RESOLVED_FULL"

def compute_fail_to_pass(report: dict) -> float:
    total = len(report[FAIL_TO_PASS]["success"]) + len(report[FAIL_TO_PASS]["failure"])
    return 1 if total == 0 else len(report[FAIL_TO_PASS]["success"]) / total

def compute_pass_to_pass(report: dict) -> float:
    total = len(report[PASS_TO_PASS]["success"]) + len(report[PASS_TO_PASS]["failure"])
    return 1 if total == 0 else len(report[PASS_TO_PASS]["success"]) / total

def get_resolution_status(report: dict) -> ResolvedStatus:
    f2p = compute_fail_to_pass(report)
    p2p = compute_pass_to_pass(report)
    if f2p == 1 and p2p == 1:
        return ResolvedStatus.FULL
    elif 0 < f2p < 1 and p2p == 1:
        return ResolvedStatus.PARTIAL
    else:
        return ResolvedStatus.NO
