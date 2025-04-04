import glob
import re
from os.path import join as pjoin
from pathlib import Path
import javalang


def is_test_file(file_path: str) -> bool:
    """Check if a file is a test file.

    This is a simple heuristic to check if a file is a test file.
    """

    return (
        "test" in Path(file_path).parts
        or "tests" in Path(file_path).parts
        or file_path.endswith("Test.java")
    )


def find_java_files(dir_path: str) -> list[str]:
    def find_python_files(dir_path: str) -> list[str]:
    """Get all .java files recursively from a directory.

    Skips files that are obviously not from the source code, such third-party library code.

    Args:
        dir_path (str): Path to the directory.
    Returns:
        List[str]: List of .py file paths. These paths are ABSOLUTE path!
    """
    java_files = glob.glob(pjoin(dir_path, "**/*.java"), recursive=True)
    res = []
    for file in java_files:
        rel_path = file[len(dir_path) + 1 :]
        if is_test_file(rel_path):
            continue
        res.append(file)
    return res


def parse_class_def_args(source: str, node: javalang.tree.ClassDeclaration) -> list[str]:
    return [t.name for t in node.extends or []] + [t.name for t in node.implements or []]


def parse_java_file(file_full_path: str):
    try:
        file_content = Path(file_full_path).read_text()
        tree = javalang.parse.parse(file_content)
    except Exception:
        return None

    classes = []
    class_to_funcs = {}
    top_level_funcs = []
    class_relation_map = {}

    for _, node in tree.filter(javalang.tree.ClassDeclaration):
        class_name = node.name
        start_lineno = node.position.line if node.position else 1
        end_lineno = start_lineno + len(str(node).splitlines())
        classes.append((class_name, start_lineno, end_lineno))
        class_relation_map[(class_name, start_lineno, end_lineno)] = parse_class_def_args(file_content, node)

        methods = []
        for member in node.body:
            if isinstance(member, javalang.tree.MethodDeclaration):
                m_start = member.position.line if member.position else start_lineno
                m_end = m_start + len(str(member).splitlines())
                methods.append((member.name, m_start, m_end))
        class_to_funcs[class_name] = methods

    return classes, class_to_funcs, top_level_funcs, class_relation_map


def get_code_snippets(file_full_path: str, start: int, end: int, with_lineno=True) -> str:
    with open(file_full_path) as f:
        file_content = f.readlines()
    snippet = ""
    for i in range(start - 1, end):
        if with_lineno:
            snippet += f"{i+1} {file_content[i]}"
        else:
            snippet += file_content[i]
    return snippet


def get_code_region_containing_code(file_full_path: str, code_str: str, with_lineno=True) -> list[tuple[int, str]]:
    """In a file, get the region of code that contains a specific string.

    Args:
        - file_full_path: Path to the file. (absolute path)
        - code_str: The string that the function should contain.
    Returns:
        - A list of tuple, each of them is a pair of (line_no, code_snippet).
        line_no is the starting line of the matched code; code snippet is the
        source code of the searched region.
    """
    with open(file_full_path) as f:
        file_content = f.read()

    context_size = 3
    pattern = re.compile(re.escape(code_str))
    occurrences = []
    for match in pattern.finditer(file_content):
        matched_start_pos = match.start()
        matched_line_no = file_content.count("\n", 0, matched_start_pos)

        file_content_lines = file_content.splitlines()
        window_start_index = max(0, matched_line_no - context_size)
        window_end_index = min(len(file_content_lines), matched_line_no + context_size + 1)

        if with_lineno:
            context = ""
            for i in range(window_start_index, window_end_index):
                context += f"{i+1} {file_content_lines[i]}\n"
        else:
            context = "\n".join(file_content_lines[window_start_index:window_end_index])
        occurrences.append((matched_line_no + 1, context))

    return occurrences


def get_code_region_around_line(file_full_path: str, line_no: int, window_size: int = 10, with_lineno=True) -> str | None:
    with open(file_full_path) as f:
        file_content = f.readlines()

    if line_no < 1 or line_no > len(file_content):
        return None

    start = max(1, line_no - window_size)
    end = min(len(file_content), line_no + window_size)
    snippet = ""
    for i in range(start, end):
        if with_lineno:
            snippet += f"{i} {file_content[i - 1]}"
        else:
            snippet += file_content[i]
    return snippet


def get_func_snippet_with_code_in_file(file_full_path: str, code_str: str) -> list[str]:
    with open(file_full_path) as f:
        file_content = f.read()
    try:
        tree = javalang.parse.parse(file_content)
    except:
        return []

    all_snippets = []
    for _, class_node in tree.filter(javalang.tree.ClassDeclaration):
        for member in class_node.body:
            if isinstance(member, javalang.tree.MethodDeclaration):
                func_code = str(member)
                stripped_func = " ".join(func_code.split())
                stripped_code_str = " ".join(code_str.split())
                if stripped_code_str in stripped_func:
                    m_start = member.position.line if member.position else 1
                    m_end = m_start + len(func_code.splitlines())
                    all_snippets.append(get_code_snippets(file_full_path, m_start, m_end))

    return all_snippets


def get_class_signature(file_full_path: str, class_name: str) -> str:
    with open(file_full_path) as f:
        file_content = f.read()
    try:
        tree = javalang.parse.parse(file_content)
    except:
        return ""

    for _, node in tree.filter(javalang.tree.ClassDeclaration):
        if node.name == class_name:
            start = node.position.line if node.position else 1
            end = start + len(str(node).splitlines())
            return get_code_snippets(file_full_path, start, end, with_lineno=False)

    return ""
