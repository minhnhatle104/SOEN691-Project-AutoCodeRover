import re

from enum import Enum


class TestStatus(Enum):
    FAILED = "FAILED"
    PASSED = "PASSED"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"


def parse_log_pytest(log: str) -> dict:
    """
    Parser for test logs generated with PyTest framework

    Args:
        log (str): log content
    Returns:
        dict: test case to test status mapping
    """
    test_status_map = {}
    for line in log.split("\n"):
        if any([line.startswith(x.value) for x in TestStatus]):
            # Additional parsing for FAILED status
            if line.startswith(TestStatus.FAILED.value):
                line = line.replace(" - ", " ")
            test_case = line.split()
            if len(test_case) <= 1:
                continue
            test_status_map[test_case[1]] = test_case[0]
    return test_status_map


def parse_log_django(log: str) -> dict:
    """
    Parser for test logs generated with Django tester framework

    Args:
        log (str): log content
    Returns:
        dict: test case to test status mapping
    """
    test_status_map = {}
    lines = log.split("\n")
    for line in lines:
        line = line.strip()
        if line.endswith(" ... ok"):
            test = line.split(" ... ok")[0]
            test_status_map[test] = TestStatus.PASSED.value
        if " ... skipped" in line:
            test = line.split(" ... skipped")[0]
            test_status_map[test] = TestStatus.SKIPPED.value
        if line.endswith(" ... FAIL"):
            test = line.split(" ... FAIL")[0]
            test_status_map[test] = TestStatus.FAILED.value
        if line.startswith("FAIL:"):
            test = line.split()[1].strip()
            test_status_map[test] = TestStatus.FAILED.value
        if line.endswith(" ... ERROR"):
            test = line.split(" ... ERROR")[0]
            test_status_map[test] = TestStatus.ERROR.value
        if line.startswith("ERROR:"):
            test = line.split()[1].strip()
            test_status_map[test] = TestStatus.ERROR.value
    return test_status_map


def parse_log_pytest_v2(log):
    """
    Parser for test logs generated with PyTest framework (Later Version)

    Args:
        log (str): log content
    Returns:
        dict: test case to test status mapping
    """
    test_status_map = {}
    escapes = "".join([chr(char) for char in range(1, 32)])
    for line in log.split("\n"):
        line = re.sub(r"\[(\d+)m", "", line)
        translator = str.maketrans("", "", escapes)
        line = line.translate(translator)
        if any([line.startswith(x.value) for x in TestStatus]):
            if line.startswith(TestStatus.FAILED.value):
                line = line.replace(" - ", " ")
            test_case = line.split()
            test_status_map[test_case[1]] = test_case[0]
    return test_status_map


def parse_log_seaborn(log):
    """
    Parser for test logs generated with seaborn testing framework

    Args:
        log (str): log content
    Returns:
        dict: test case to test status mapping
    """
    test_status_map = {}
    for line in log.split("\n"):
        if line.startswith(TestStatus.FAILED.value):
            test_case = line.split()[1]
            test_status_map[test_case] = TestStatus.FAILED.value
        elif f" {TestStatus.PASSED.value} " in line:
            parts = line.split()
            if parts[1] == TestStatus.PASSED.value:
                test_case = parts[0]
                test_status_map[test_case] = TestStatus.PASSED.value
    return test_status_map


def parse_log_sympy(log):
    """
    Parser for test logs generated with Sympy framework

    Args:
        log (str): log content
    Returns:
        dict: test case to test status mapping
    """
    test_status_map = {}
    pattern = r"(_*) (.*)\.py:(.*) (_*)"
    matches = re.findall(pattern, log)
    for match in matches:
        test_case = f"{match[1]}.py:{match[2]}"
        test_status_map[test_case] = TestStatus.FAILED.value
    for line in log.split("\n"):
        line = line.strip()
        if line.startswith("test_"):
            if line.endswith(" E"):
                test = line.split()[0]
                test_status_map[test] = TestStatus.ERROR.value
            if line.endswith(" F"):
                test = line.split()[0]
                test_status_map[test] = TestStatus.FAILED.value
            if line.endswith(" ok"):
                test = line.split()[0]
                test_status_map[test] = TestStatus.PASSED.value
    return test_status_map


# ================== Java Parsers ==================
def parse_log_java_maven(log: str) -> dict:
    """Parse Maven surefire test reports"""
    test_status_map = {}
    # Match failed tests pattern
    for match in re.finditer(r"Tests run: .*?Failed:.*?\[(.*?)\]", log):
        test_class = match.group(1)
        test_status_map[test_class] = TestStatus.FAILED.value
    
    # Match individual test failures
    for line in log.split("\n"):
        if "FAILED" in line and "Test " in line:
            test_name = line.split("Test ")[1].split()[0]
            test_status_map[test_name] = TestStatus.FAILED.value
    return test_status_map

def parse_log_java_gradle(log: str) -> dict:
    """Parse Gradle test reports"""
    test_status_map = {}
    test_pattern = re.compile(r"> ([\w.]+) (FAILED|PASSED)")
    for line in log.split("\n"):
        match = test_pattern.search(line)
        if match:
            test_name, status = match.groups()
            test_status_map[test_name] = status
    return test_status_map

# ================== Parser Mapping ==================
MAP_REPO_TO_PARSER = {
    # Existing Python projects
    "astropy/astropy": parse_log_pytest,
    "django/django": parse_log_django,
    "pytest-dev/pytest": parse_log_pytest,
    
    # Java projects
    "apache__dubbo": parse_log_java_maven,
    "fasterxml__jackson-databind": parse_log_java_maven,
    "fasterxml__jackson-core": parse_log_java_maven,
    "google__gson": parse_log_java_maven,
    "fasterxml__jackson-dataformat-xml": parse_log_java_maven,
    "googlecontainertools__jib": parse_log_java_gradle,
    
    # Other Python projects
    "mwaskom/seaborn": lambda log: parse_log_pytest(log),
    "sympy/sympy": lambda log: parse_log_pytest(log),
    "pallets/flask": parse_log_pytest,
    "psf/requests": parse_log_pytest,
}

# ================== Helper Assignments ==================
parse_log_astroid = parse_log_pytest
parse_log_flask = parse_log_pytest
parse_log_marshmallow = parse_log_pytest
parse_log_matplotlib = parse_log_pytest
parse_log_pydicom = parse_log_pytest
parse_log_pvlib = parse_log_pytest
parse_log_pylint = parse_log_pytest
parse_log_pyvista = parse_log_pytest
parse_log_requests = parse_log_pytest
parse_log_sqlfluff = parse_log_pytest
parse_log_xarray = parse_log_pytest
