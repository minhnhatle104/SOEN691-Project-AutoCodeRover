import ast
import contextlib
import glob
import os
import shutil
import subprocess
from collections.abc import Callable
from functools import wraps
from os import PathLike
from os.path import dirname as pdirname
from os.path import join as pjoin
from pathlib import Path
from subprocess import CalledProcessError
from app.log import log_and_print, log_exception


@contextlib.contextmanager
def cd(newdir):
    """
    Context manager for changing the current working directory
    :param newdir: path to the new directory
    :return: None
    """
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


def run_command(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """
    Run a command in the shell.
    Args:
        - cmd: command to run
    """
    try:
        cp = subprocess.run(cmd, check=True, **kwargs)
    except subprocess.CalledProcessError as e:
        log_and_print(f"Error running command: {cmd}, {e}")
        raise e
    return cp


def is_git_repo() -> bool:
    """
    Check if the current directory is a git repo.
    """
    git_dir = ".git"
    return os.path.isdir(git_dir)


def initialize_git_repo_and_commit(logger=None):
    """
    Initialize the current directory as a git repository and make an initial commit.
    """
    init_cmd = ["git", "init"]
    add_all_cmd = ["git", "add", "."]
    commit_cmd = ["git", "commit", "-m", "Temp commit made by ACR."]
    run_command(init_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    run_command(add_all_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    run_command(commit_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def get_current_commit_hash() -> str:
    command = ["git", "rev-parse", "HEAD"]
    cp = subprocess.run(command, text=True, capture_output=True)
    try:
        cp.check_returncode()
        return cp.stdout.strip()
    except CalledProcessError as e:
        raise RuntimeError(f"Failed to get SHA-1 of HEAD: {cp.stderr}") from e


def repo_commit_current_changes():
    """
    Commit the current active changes so that it's safer to do git reset later on.
    Use case: for storing the changes made in pre_install and test_patch in a commit.
    """
    add_all_cmd = ["git", "add", "."]
    commit_cmd = [
        "git",
        "commit",
        "--allow-empty",
        "-m",
        "Temporary commit for storing changes",
    ]
    run_command(add_all_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    run_command(commit_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def clone_repo(clone_link: str, dest_dir: str, cloned_name: str):
    """
    Clone a repo to dest_dir.

    Returns:
        - path to the newly cloned directory.
    """
    clone_cmd = ["git", "clone", clone_link, cloned_name]
    create_dir_if_not_exists(dest_dir)
    with cd(dest_dir):
        run_command(clone_cmd)
    cloned_dir = pjoin(dest_dir, cloned_name)
    return cloned_dir


def clone_repo_and_checkout(
    clone_link: str, commit_hash: str, dest_dir: str, cloned_name: str
):
    """
    Clone a repo to dest_dir, and checkout to commit `commit_hash`.

    Returns:
        - path to the newly cloned directory.
    """
    cloned_dir = clone_repo(clone_link, dest_dir, cloned_name)
    checkout_cmd = ["git", "checkout", commit_hash]
    with cd(cloned_dir):
        run_command(checkout_cmd)
    return cloned_dir


def repo_clean_changes() -> None:
    """
    Reset repo to HEAD. Basically clean active changes and untracked files on top of HEAD.

    A lightweight version of `repo_reset_and_clean_checkout`. This is also used in different scenarios.
    """
    reset_cmd = ["git", "reset", "--hard"]
    clean_cmd = ["git", "clean", "-fd"]
    run_command(reset_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    run_command(clean_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def repo_reset_and_clean_checkout(commit_hash: str) -> None:
    """
    Reset the repo to the original commit state.
    Cleans uncommitted and untracked files, and resets submodules.
    Ensures commit is fetched before checkout — compatible with Java projects.
    """

    # Step 0: Clean up leftover files from previous runs
    if os.path.exists(".coverage"):
        os.remove(".coverage")
    if os.path.exists("tests/.coveragerc"):
        os.remove("tests/.coveragerc")
    for f in glob.glob(".coverage.TSS.*", recursive=True):  # ✅ Corrected usage
        os.remove(f)

    # Step 1: Fetch commit if missing (handles shallow clones)
    try:
        run_command(["git", "fetch", "--no-tags", "origin", commit_hash])
    except Exception as e:
        print(f"[WARN] Unable to fetch commit {commit_hash}: {e}")

    # Step 2: Reset, clean, checkout
    reset_cmd = ["git", "reset", "--hard", commit_hash]
    clean_cmd = ["git", "clean", "-fd"]
    checkout_cmd = ["git", "checkout", commit_hash]
    run_command(reset_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    run_command(clean_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    run_command(checkout_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Step 3: Submodule cleanup and reinitialization
    submodule_unbind_cmd = ["git", "submodule", "deinit", "-f", "."]
    submodule_init_cmd = ["git", "submodule", "update", "--init"]
    run_command(submodule_unbind_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    run_command(submodule_init_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)



def run_script_in_conda(command: str, env_name: str = "", is_java: bool = False, **kwargs):
    if is_java or 'mvn' in command or 'gradle' in command:
        log_and_print(f"[Java] Running: {command}")
        return subprocess.run(command, shell=True, **kwargs)


def run_string_cmd_in_conda(command: str, env_name: str = "", is_java: bool = False, **kwargs):
    if is_java or 'mvn' in command or 'gradle' in command:
        log_and_print(f"[Java] Running: {command}")
        return subprocess.run(command, shell=True, **kwargs)



def create_dir_if_not_exists(dir_path: str):
    """
    Create a directory if it does not exist.
    Args:
        dir_path (str): Path to the directory.
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def create_fresh_dir(dir_path: str | PathLike):
    """
    Create a dir from fresh.
    If there is existing dir with the same name, remove it.
    Args:
        dir_path (str): Path to the directory.
    """
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.makedirs(dir_path)


def to_relative_path(file_path: str, project_root: str) -> str:
    """Convert an absolute path to a path relative to the project root.

    Args:
        - file_path (str): The absolute path.
        - project_root (str): Absolute path of the project root dir.

    Returns:
        The relative path.
    """
    if Path(file_path).is_absolute():
        return str(Path(file_path).relative_to(project_root))
    else:
        return file_path


def to_absolute_path(file_path: str, project_root: str) -> str:
    """Convert a relative path to an absolute path.

    Args:
        - file_path (str): The relative path.
        - project_root (str): Absolute path of a root dir.
    """
    return pjoin(project_root, file_path)


def find_file(directory, filename) -> str | None:
    """
    Find a file in a directory. filename can be short name, relative path to the
    directory, or an incomplete relative path to the directory.
    Returns:
        - the relative path to the file if found; None otherwise.
    """

    # Helper method one
    def find_file_exact_relative(directory, filename) -> str | None:
        if os.path.isfile(os.path.join(directory, filename)):
            return filename
        return None

    # Helper method two
    def find_file_shortname(directory, filename) -> str | None:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file == filename:
                    return os.path.relpath(os.path.join(root, file), directory)
        return None

    # if the filename is exactly the relative path.
    found = find_file_exact_relative(directory, filename)
    if found is not None:
        return found

    # if the filename is a short name without any directory
    found = find_file_shortname(directory, filename)
    if found is not None:
        return found

    # if the filename has some directory, but is not a relative path to
    # the directory
    parts = filename.split(os.path.sep)
    shortname = parts[-1]
    found = find_file_shortname(directory, shortname)
    if found is None:
        # really cannot find this file
        return None
    # can find this shortname, but we also need to check whether the intermediate
    # directories match
    if filename in found:
        return found
    else:
        return None


def parse_function_invocation(
    invocation_str: str,
) -> tuple[str, list[str]]:
    try:
        tree = ast.parse(invocation_str)
        expr = tree.body[0]
        assert isinstance(expr, ast.Expr)
        call = expr.value
        assert isinstance(call, ast.Call)
        func = call.func
        assert isinstance(func, ast.Name)
        function_name = func.id
        raw_arguments = [ast.unparse(arg) for arg in call.args]
        # clean up spaces or quotes, just in case
        arguments = [arg.strip().strip("'").strip('"') for arg in raw_arguments]

        try:
            new_arguments = [ast.literal_eval(x) for x in raw_arguments]
            if new_arguments != arguments:
                log_and_print(
                    f"Refactored invocation argument parsing gives different result on "
                    f"{invocation_str!r}: old result is {arguments!r}, new result "
                    f" is {new_arguments!r}",
                )
        except Exception as e:
            log_and_print(
                f"Refactored invocation argument parsing failed on {invocation_str!r}: {e!s}",
            )
    except Exception as e:
        raise ValueError(f"Invalid function invocation: {invocation_str}") from e

    return function_name, arguments


def catch_all_and_log(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_exception(e)
            err = str(e)
            # TODO: this string is there for legacy reasons
            summary = "The tool returned error message."
            return err, summary, False

    return wrapper


def coroutine(func):
    @wraps(func)
    def primer(*args, **kwargs):
        gen = func(*args, **kwargs)
        next(gen)
        return gen

    return primer
