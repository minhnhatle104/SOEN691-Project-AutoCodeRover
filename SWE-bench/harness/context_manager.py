import logging, os, platform, subprocess
from constants import (
    APPLY_PATCH_FAIL,
    APPLY_PATCH_PASS,
    INSTALL_FAIL,
    INSTALL_PASS,
    INSTALL_TIMEOUT,
    KEY_INSTANCE_ID,
    KEY_MODEL,
    MAP_REPO_TO_INSTALL,
    MAP_REPO_TO_TEST_FRAMEWORK,
    MAP_VERSION_TO_INSTALL,
    RESET_FAILED,
    TESTS_FAILED,
    TESTS_PASSED,
    TESTS_TIMEOUT,
    TESTS_ERROR,
)
from tempfile import TemporaryDirectory
from traceback import format_exc
from utils import (
    clone_repo,
    get_environment_yml,
    get_requirements,
    get_test_directives,
)
from traceback import format_exc

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger_testbed = logging.getLogger("testbed_context_manager")

class ExecWrapper:
    def __init__(self, subprocess_args: dict = None):
        self.subprocess_args = subprocess_args or {}

    def __call__(self, cmd, raise_error=True, **kwargs):
        try:
            combined_args = {**self.subprocess_args, **kwargs}
            output = subprocess.run(cmd, **combined_args)
            return output
        except subprocess.CalledProcessError as e:
            if raise_error:
                logger_testbed.error(f"Error: {e}")
                logger_testbed.error(f"Error stdout: {e.stdout}")
                logger_testbed.error(f"Error stderr: {e.stderr}")
                logger_testbed.error(f"Error traceback: {format_exc()}")
                raise e

class TestbedContextManager:
    def __init__(
        self,
        task_instances: list,
        log_dir: str,
        temp_dir: str = None,
        testbed: str = None,
        timeout: int = None,
        verbose: bool = False,
    ):
        logger_testbed.propagate = verbose
        self.log_dir = os.path.abspath(log_dir)
        self.timeout = timeout
        self.verbose = verbose
        self.exec = ExecWrapper(
            subprocess_args={
                "check": True,
                "shell": False,
                "capture_output": True,
                "text": True,
            }
        )

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)
        if temp_dir is not None and not os.path.exists(temp_dir):
            logger_testbed.info(f"[Testbed] Creating temp directory {temp_dir}")
            os.makedirs(temp_dir, exist_ok=True)
        temp_dir = os.path.abspath(temp_dir) if temp_dir is not None else None

        # Set up conda path, create in temp directory if None
        if path_conda is not None:
            self.temp_dir_conda = None
            self.path_conda = os.path.abspath(path_conda)
        else:
            self.temp_dir_conda = TemporaryDirectory(dir=temp_dir)
            self.path_conda = self.temp_dir_conda.name
        logger_testbed.info(f"[Testbed] Using conda path {self.path_conda}")

        # Set up testbed path, create in temp directory if None
        if testbed is not None:
            self.temp_dir_work = None
            self.testbed = os.path.abspath(testbed)
        else:
            self.temp_dir_work = TemporaryDirectory(dir=temp_dir)
            self.testbed = self.temp_dir_work.name
        logger_testbed.info(
            f"[Testbed] Using working directory {self.testbed} for testbed"
        )

        # Sort task instances by created_at
        self.task_instances = sorted(
            task_instances, key=lambda x: x["created_at"], reverse=True
        )

        # Group repos by repo, then version
        self.task_instances_grouped = {}
        for instance in self.task_instances:
            test_type = MAP_REPO_TO_TEST_FRAMEWORK[instance["repo"]]
            test_directives = get_test_directives(instance)
            instance["test_cmd"] = f"{test_type} {' '.join(test_directives)}"

            # Group task instances by repo, version
            repo = instance["repo"]
            version = instance["version"] if "version" in instance else None
            if repo not in self.task_instances_grouped:
                self.task_instances_grouped[repo] = {}
            if version not in self.task_instances_grouped[repo]:
                self.task_instances_grouped[repo][version] = []
            self.task_instances_grouped[repo][version].append(instance)

        # Log grouped task instances to be run
        self.setup_refs = {}
        for repo, map_version_to_instances in self.task_instances_grouped.items():
            logger_testbed.info(
                f"[Testbed] Repo {repo}: {len(map_version_to_instances)} versions"
            )

            # Determine instances to use for environment installation
            self.setup_refs[repo] = {}
            for version, instances in map_version_to_instances.items():
                logger_testbed.info(
                    f"[Testbed] \tVersion {version}: {len(instances)} instances"
                )
                self.setup_refs[repo][version] = instances[0]

        # Remove None versions, versions not in MAP_VERSION_TO_INSTALL
        self._custom_restraints()

    def __enter__(self):
        for repo, version_to_setup_ref in self.setup_refs.items():
            for version, instance in version_to_setup_ref.items():
                env_name = f"{repo.replace('/', '__')}__{version}"
                repo_path = os.path.join(self.testbed, env_name)

                if not os.path.exists(repo_path):
                    clone_repo(repo, repo_path)

                os.makedirs(os.path.join(repo_path, "setup_temp"), exist_ok=True)
                install_cmd = MAP_VERSION_TO_INSTALL[repo][version].get("install", "")
                if install_cmd:
                    logger_testbed.info(f"[{env_name}] Running install command: {install_cmd}")
                    self.exec(f"cd {repo_path} && {install_cmd}")

        return self

    def get_distributed_tasks(self) -> list:
        """
        Create task group (instances + keywords) for each repo/version

        Returns:
            list: List of task groups, each group containing task instances
                from the same repo with the same version
        """
        distributed_tasks = []
        for repo, map_version_to_instances in self.task_instances_grouped.items():
            for version, instances in map_version_to_instances.items():
                env_name = f"{repo.replace('/', '__')}__{version}"
                distributed_tasks.append({
                    "task_instances": instances,
                    "log_dir": self.log_dir,
                    "testbed": os.path.join(self.testbed, env_name),
                    "timeout": self.timeout,
                    "venv": env_name,
                    "version": version,
                    "verbose": self.verbose,
                })
        return distributed_tasks

    def _custom_restraints(self):
        """
        Custom restraints per repo
        """
        for repo, group in self.task_instances_grouped.items():
            if None in group:
                logger_testbed.info(f"[Testbed] Removed None version from repo {repo}")
                del group[None]
            versions = list(group.keys())
            for version in versions:
                if version not in MAP_VERSION_TO_INSTALL[repo]:
                    logger_testbed.info(
                        f"[Testbed] Removed {version} version from repo {repo} (Install instructions not given)"
                    )
                    del group[version]

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.temp_dir_work is not None:
            self.temp_dir_work.cleanup()


logger_taskenv = logging.getLogger("taskenv_context_manager")

class TaskEnvContextManager:
    def __init__(
        self, instance: dict, testbed: str, venv: str, log_dir: str,
        verbose: bool = False, timeout: int = None, is_eval: bool = False, log_suffix: str = None
    ):
        """
        Sets up execution context for a single task instance

        Args:
            instance (dict): Task instance
            testbed (str): Path to testbed directory
            venv (str): Name of conda environment (should exist in conda_path)
            log_dir (str): Path to log directory
            verbose (bool): Whether to show logs
            timeout (int): Timeout for actions
            is_eval (bool): Whether this is for evaluating a model on SWE Bench
                (Mainly for logging purposes)
        """
        logger_taskenv.propagate = verbose
        self.instance = instance
        self.testbed = testbed
        self.testbed_name = testbed.split("/")[-1]
        self.venv = venv
        self.timeout = timeout
        self.is_eval = is_eval

        log_file_name = (
            f"{instance[KEY_INSTANCE_ID]}.{instance[KEY_MODEL]}.eval.log"
            if is_eval else f"{instance[KEY_INSTANCE_ID]}.log"
        )
        if log_suffix:
            log_file_name = (
                f"{instance[KEY_INSTANCE_ID]}.{instance[KEY_MODEL]}.{log_suffix}.eval.log"
                if is_eval else f"{instance[KEY_INSTANCE_ID]}.{log_suffix}.log"
            )
        self.log_file = os.path.join(log_dir, log_file_name)
        self.cwd = os.getcwd()
        self.exec = ExecWrapper(subprocess_args={"check": True, "shell": True, "capture_output": True, "text": True})

    def __enter__(self):
        os.chdir(self.testbed)
        with open(self.log_file, "w") as f:
            f.write(
                f"Task Metadata:\n\t- Instance ID: {self.instance[KEY_INSTANCE_ID]}\n"
                f"\t- Testbed: {self.testbed}\n\t- Environment: {self.venv}\n"
            )
            if self.is_eval:
                f.write(f"\t- Evaluation Model: {self.instance[KEY_MODEL]}\n")
        return self

    def reset_task_env(self, instance: dict):
        """
        Reset task environment + testbed and checkout base commit of given task instance

        Args:
            instance (dict): Task instance
        Returns:
            bool: True if reset successful, False otherwise
        """
        try:
            # Remove all paths in .gitignore
            if os.path.exists(".gitignore"):
                self.exec(
                    "git ls-files --ignored --exclude-standard -o -z | xargs -0 -r rm -rf".split(),
                    raise_error=False,
                )

            # Reset git repo + checkout base commit
            self.exec("git restore .".split(" "))
            self.exec("git reset HEAD .".split(" "))
            self.exec("git clean -fdx".split(" "))
            self.exec(
                f"git -c advice.detachedHead=false checkout {instance['base_commit']}".split(
                    " "
                )
            )
            logger_taskenv.info(
                f"[{self.testbed_name}] [{instance[KEY_INSTANCE_ID]}] Reset task environment to {instance['base_commit']}"
            )
            return True
        except Exception as e:
            err_msg = f"{RESET_FAILED}; Failed to reset task environment to {instance['base_commit']}: {e}"
            logger_taskenv.error(f"[{self.testbed_name}] {err_msg}")
            with open(self.log_file, "a") as f:
                f.write(err_msg)
            return False

    def run_install_task(self, instance: dict) -> bool:
        """
        Run installation for task instance

        Args:
            instance (dict): Task instance
        Returns:
            bool: True if installation successful, False otherwise
        """
        # Get installation instructions by repo/version
        specifications = MAP_VERSION_TO_INSTALL[instance["repo"]][instance["version"]]

        # (0) For matplotlib, qhull tarball download fails,
        # so we need to pre-install the system version and specify to use it here
        if "matplotlib" in instance["repo"]:
            with open("mplsetup.cfg", "w") as f:
                f.write("[libs]\nsystem_qhull = true")

        # Run pre-install set up if provided
        if "pre_install" in specifications:
            for pre_install in specifications["pre_install"]:
                cmd_pre_install = f"{self.cmd_activate} && {pre_install}"
                logger_taskenv.info(
                    f"[{self.testbed_name}] [{instance[KEY_INSTANCE_ID]}] Running pre-install setup command: {cmd_pre_install}"
                )
                out_pre_install = self.exec(
                    cmd_pre_install, timeout=self.timeout, shell=True
                )
                with open(self.log_file, "a") as f:
                    f.write(f"Pre-installation Command: {cmd_pre_install}\n")
                    f.write(f"Std. Output: {out_pre_install.stdout}\n")
                    f.write(f"Std. Error: {out_pre_install.stderr}\n")
                if out_pre_install.returncode != 0:
                    logger_taskenv.error(
                        f"[{self.testbed_name}] [{instance[KEY_INSTANCE_ID]}] Pre-install setup failed"
                    )
                    with open(self.log_file, "a") as f:
                        f.write(f"\n{INSTALL_FAIL}\n")
                    return False

        # Skip installation if no instructions provided
        if "install" not in specifications:
            return True

        cmd_install = f"{self.cmd_activate} && {specifications['install']}"
        logger_taskenv.info(
            f"[{self.testbed_name}] [{instance[KEY_INSTANCE_ID]}] Installing with command: {cmd_install}"
        )
        try:
            # Run installation command
            out_install = self.exec(cmd_install, timeout=self.timeout, shell=True)

            # Write installation logs to log file
            with open(self.log_file, "a") as f:
                f.write(f"Installation Command: {cmd_install}\n")
                f.write(f"Std. Output: {out_install.stdout}\n")
                f.write(f"Std. Error: {out_install.stderr}\n")

            if out_install.returncode != 0:
                # Installation failed
                logger_taskenv.error(
                    f"[{self.testbed_name}] [{instance[KEY_INSTANCE_ID]}] Installation failed"
                )
                with open(self.log_file, "a") as f:
                    f.write(f"\n{INSTALL_FAIL}\n")
                return False

            # Installation successful
            logger_taskenv.info(
                f"[{self.testbed_name}] [{instance[KEY_INSTANCE_ID]}] Installation successful"
            )
            with open(self.log_file, "a") as f:
                f.write(f"\n{INSTALL_PASS}\n")
            return True
        except subprocess.TimeoutExpired:
            # Installation timed out
            logger_taskenv.error(
                f"[{self.testbed_name}] [{self.instance[KEY_INSTANCE_ID]}] Installation timed out"
            )
            with open(self.log_file, "a") as f:
                f.write(f"\n{INSTALL_TIMEOUT}\n")
            return False
        except Exception as e:
            # Installation failed
            logger_taskenv.error(
                f"[{self.testbed_name}] [{instance[KEY_INSTANCE_ID]}] Installation failed"
            )
            with open(self.log_file, "a") as f:
                f.write(f"\n{INSTALL_FAIL}: {e}\n")
            return False

    def apply_patch(
        self, patch: str, patch_type: str = "", revert: bool = False
    ) -> bool:
        """
        Apply patch to task environment

        Args:
            patch (str): Plaintext of patch to apply
            patch_type (str): Type of patch (e.g. "eval", "test")
        Returns:
            bool: True if patch applied successfully, False otherwise
        """
        # If patch is `None`, indicate in log and skip
        if patch is None:
            logger_taskenv.error(
                f"[{self.testbed_name}] [{self.instance[KEY_INSTANCE_ID]}] Patch is `None` ({patch_type})"
            )
            with open(self.log_file, "a") as f:
                f.write(f"{APPLY_PATCH_FAIL}; Prediction patch is `None`")
            return False

        # Write patch to temporary patch file in parent directory
        patch_path = os.path.join(
            os.path.dirname(self.testbed.rstrip("/")),
            f"temp_{self.instance[KEY_INSTANCE_ID]}_{patch_type}.patch",
        )
        with open(patch_path, "w") as f:
            f.write(patch)

        # Apply patch to testbed directory
        apply_cmd = (
            f"git apply -v -R {patch_path}" if revert else f"git apply -v {patch_path}"
        )
        out_patch = self.exec(apply_cmd.split(" "), raise_error=False, check=False)
        os.remove(patch_path)

        log_cmd = "Revert" if revert else "Apply"
        if out_patch.returncode != 0:
            # Patch apply failed
            logger_taskenv.error(
                f"[{self.testbed_name}] [{self.instance[KEY_INSTANCE_ID]}] {log_cmd} patch failed ({patch_type})"
            )
            with open(self.log_file, "a") as f:
                f.write(f"{APPLY_PATCH_FAIL}; ({patch_type})\nOutput:\n")
                f.write(out_patch.stdout)
                f.write(out_patch.stderr)
            return False

        # Patch apply succeeded
        logger_taskenv.info(
            f"[{self.testbed_name}] [{self.instance[KEY_INSTANCE_ID]}] {log_cmd} patch successful ({patch_type})"
        )
        with open(self.log_file, "a") as f:
            f.write(f"{APPLY_PATCH_PASS} ({patch_type})\n")
        return True

    def run_tests_task(self, instance: dict):
        """
        Run tests for task instance

        Args:
            instance (dict): Task instance
        Returns:
            bool: True if test script ran successfully, False otherwise
        """
        try:
            # Run test command for task instance
            test_cmd = f"{self.cmd_activate} && {instance['test_cmd']}"
            with open(self.log_file, "a") as f:
                f.write(f"Test Script: {test_cmd};\n")
            out_test = self.exec(
                test_cmd, shell=True, timeout=self.timeout, check=False
            )

            # Write test results to log file
            with open(self.log_file, "a") as f:
                f.write(f"Output:\n")
                f.write(out_test.stdout)
                f.write(out_test.stderr)
                if out_test.returncode != 0:
                    f.write(f"\n{TESTS_FAILED}\n")
                else:
                    f.write(f"\n{TESTS_PASSED}\n")

            logger_taskenv.info(
                f"[{self.testbed_name}] [{instance[KEY_INSTANCE_ID]}] Test script run successful"
            )
            return True
        except subprocess.TimeoutExpired:
            # Test command run timed out
            logger_taskenv.error(
                f"[{self.testbed_name}] [{instance[KEY_INSTANCE_ID]}] Test script run time out {self.timeout}"
            )
            with open(self.log_file, "a") as f:
                f.write(f"{TESTS_TIMEOUT} after {self.timeout} seconds\n")
            return False
        except Exception as e:
            # Test command run failed
            logger_taskenv.error(
                f"[{self.testbed_name}] [{instance[KEY_INSTANCE_ID]}] Test script run failed"
            )
            with open(self.log_file, "a") as f:
                f.write(f"{TESTS_ERROR}: {e}\n")
            return False

    def __exit__(self, exc_type, exc_value, exc_traceback):
        os.chdir(self.cwd)
