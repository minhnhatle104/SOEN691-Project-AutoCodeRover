# constants.py

# Define the setup configurations for each repository version
SPECS_APACHE_DUBBO = {
    "0.1": {
        "root_path": "SWE-bench/testbed/apache__dubbo",  # Corrected repo name
        "jdk_version": "17",
        "env_type": "maven",
        "eval_cmd": "(mvn clean install -Dmaven.test.skip=true ; mvn clean test -Dsurefire.useFile=false -Dmaven.test.skip=false -D{test_spec}={test_func} -DfailIfNoTests=false -pl {module}) >>{module_escaped}:{test_func}.test.log"
    }
}

SPECS_FASTERXML_JACKSON_DATABIND = {
    "0.1": {
        "root_path": "SWE-bench/testbed/fasterxml__jackson-databind",  # Corrected repo name
        "jdk_version": "8",
        "env_type": "maven",
        "eval_cmd": "(mvn clean install -Dmaven.test.skip=true ; mvn clean test -Dsurefire.useFile=false -Dmaven.test.skip=false -D{test_spec}={test_func} -DfailIfNoTests=false -pl {module}) >>{module_escaped}:{test_func}.test.log"
    }
}

SPECS_FASTERXML_JACKSON_CORE = {
    "0.1": {
        "root_path": "SWE-bench/testbed/fasterxml__jackson-core",  # Corrected repo name
        "jdk_version": "8",
        "env_type": "maven",
        "eval_cmd": "(mvn clean install -Dmaven.test.skip=true ; mvn clean test -Dsurefire.useFile=false -Dmaven.test.skip=false -D{test_spec}={test_func} -DfailIfNoTests=false -pl {module}) >>{module_escaped}:{test_func}.test.log"
    }
}

SPECS_GOOGLE_GSON = {
    "0.1": {
        "root_path": "SWE-bench/testbed/google__gson",  # Corrected repo name
        "jdk_version": "11",
        "env_type": "maven",
        "eval_cmd": "(mvn clean install -Dmaven.test.skip=true ; mvn clean test -Dsurefire.useFile=false -Dmaven.test.skip=false -D{test_spec}={test_func} -DfailIfNoTests=false -pl {module}) >>{module_escaped}:{test_func}.test.log"
    }
}

SPECS_FASTERXML_JACKSON_DATAFORMAT_XML = {
    "0.1": {
        "root_path": "SWE-bench/testbed/fasterxml__jackson-dataformat-xml",  # Corrected repo name
        "jdk_version": "8",
        "env_type": "maven",
        "eval_cmd": "(mvn clean install -Dmaven.test.skip=true ; mvn clean test -Dsurefire.useFile=false -Dmaven.test.skip=false -D{test_spec}={test_func} -DfailIfNoTests=false -pl {module}) >>{module_escaped}:{test_func}.test.log"
    }
}

SPECS_GOOGLECONTAINERS_JIB = {
    "0.1": {
        "root_path": "SWE-bench/testbed/googlecontainertools__jib",  # Corrected repo name
        "jdk_version": "11",
        "env_type": "gradle",
        "eval_cmd": "./gradlew {module}:{test_spec} --tests {test_func} >{module}:{test_func}.test.log 2>&1"
    }
}

# Map each repository to its specs dictionary for easy access during setup
MAP_REPO_VERSION_TO_SPECS = {
    "apache__dubbo": SPECS_APACHE_DUBBO,
    "fasterxml__jackson-databind": SPECS_FASTERXML_JACKSON_DATABIND,
    "fasterxml__jackson-core": SPECS_FASTERXML_JACKSON_CORE,
    "google__gson": SPECS_GOOGLE_GSON,
    "fasterxml__jackson-dataformat-xml": SPECS_FASTERXML_JACKSON_DATAFORMAT_XML,
    "googlecontainertools__jib": SPECS_GOOGLECONTAINERS_JIB,
}

# Define custom installation commands for repositories
MAP_REPO_TO_INSTALL = {
    "apache__dubbo": "mvn clean install -Dmaven.test.skip=true",  # Add appropriate install command for dubbo
    "fasterxml__jackson-databind": "mvn clean install -Dmaven.test.skip=true",  # Add appropriate install command for jackson-databind
    "fasterxml__jackson-core": "mvn clean install -Dmaven.test.skip=true",  # Add appropriate install command for jackson-core
    "google__gson": "mvn clean install -Dmaven.test.skip=true",  # Add appropriate install command for gson
    "fasterxml__jackson-dataformat-xml": "mvn clean install -Dmaven.test.skip=true",  # Add appropriate install command for jackson-dataformat-xml
    "googlecontainertools__jib": "./gradlew build",  # Add appropriate install command for jib
}

# Define test framework mapping for repositories
MAP_REPO_TO_TEST_FRAMEWORK = {
    "apache__dubbo": "mvn test",  # Add appropriate test framework for dubbo
    "fasterxml__jackson-databind": "mvn test",  # Add appropriate test framework for jackson-databind
    "fasterxml__jackson-core": "mvn test",  # Add appropriate test framework for jackson-core
    "google__gson": "mvn test",  # Add appropriate test framework for gson
    "fasterxml__jackson-dataformat-xml": "mvn test",  # Add appropriate test framework for jackson-dataformat-xml
    "googlecontainertools__jib": "./gradlew test",  # Add appropriate test framework for jib
}

# Mapping versions to installation instructions
MAP_VERSION_TO_INSTALL = {
    "apache__dubbo": {
        "0.1": {
            "jdk_version": "17",
            "env_type": "maven",
            "install": "mvn clean install -Dmaven.test.skip=true",  # Add install command for dubbo
        }
    },
    "fasterxml__jackson-databind": {
        "0.1": {
            "jdk_version": "8",
            "env_type": "maven",
            "install": "mvn clean install -Dmaven.test.skip=true",  # Add install command for jackson-databind
        }
    },
    "fasterxml__jackson-core": {
        "0.1": {
            "jdk_version": "8",
            "env_type": "maven",
            "install": "mvn clean install -Dmaven.test.skip=true",  # Add install command for jackson-core
        }
    },
    "google__gson": {
        "0.1": {
            "jdk_version": "11",
            "env_type": "maven",
            "install": "mvn clean install -Dmaven.test.skip=true",  # Add install command for gson
        }
    },
    "fasterxml__jackson-dataformat-xml": {
        "0.1": {
            "jdk_version": "8",
            "env_type": "maven",
            "install": "mvn clean install -Dmaven.test.skip=true",  # Add install command for jackson-dataformat-xml
        }
    },
    "googlecontainertools__jib": {
        "0.1": {
            "jdk_version": "11",
            "env_type": "gradle",
            "install": "./gradlew build",  # Add install command for jib
        }
    },
}


# Constants - Task Instance Test Frameworks for Java Projects
MAP_REPO_TO_TEST_FRAMEWORK = {
    "apache__dubbo": "mvn clean test",
    "google__gson": "mvn clean test",
    "fasterxml__jackson-core": "mvn clean test",
    "fasterxml__jackson-databind": "mvn clean test",
    "fasterxml__jackson-dataformat-xml": "mvn clean test",
    "googlecontainertools__jib": "./gradlew test"
}

# Constants - Task Instance Requirements File Paths for Java Projects (if applicable)
# Constants - Task Instance Requirements File Paths for Java Projects (if applicable)
MAP_REPO_TO_REQS_PATHS = {
    "apache__dubbo": ["pom.xml"],  # Corrected repo name
    "google__gson": ["pom.xml"],  # Corrected repo name
    "fasterxml__jackson-core": ["pom.xml"],  # Corrected repo name
    "fasterxml__jackson-databind": ["pom.xml"],  # Corrected repo name
    "fasterxml__jackson-dataformat-xml": ["pom.xml"],  # Corrected repo name
    "googlecontainertools__jib": ["build.gradle"],  # Corrected repo name
}

# Constants - Task Instance environment.yml File Paths (if applicable)
MAP_REPO_TO_ENV_YML_PATHS = {}

# Constants - Evaluation Keys
KEY_INSTANCE_ID = "instance_id"
KEY_MODEL = "model_name_or_path"
KEY_PREDICTION = "model_patch"

# Constants - Logging
APPLY_PATCH_FAIL = ">>>>> Patch Apply Failed"
APPLY_PATCH_PASS = ">>>>> Applied Patch"
INSTALL_FAIL = ">>>>> Init Failed"
INSTALL_PASS = ">>>>> Init Succeeded"
INSTALL_TIMEOUT = ">>>>> Init Timed Out"
RESET_FAILED = ">>>>> Reset Failed"
TESTS_ERROR = ">>>>> Tests Errored"
TESTS_FAILED = ">>>>> Some Tests Failed"
TESTS_PASSED = ">>>>> All Tests Passed"
TESTS_TIMEOUT = ">>>>> Tests Timed Out"

# Constants - Miscellaneous
NON_TEST_EXTS = [".json", ".png", "csv", ".txt", ".md", ".jpg", ".jpeg", ".pkl", ".yml", ".yaml", ".toml"]
SWE_BENCH_URL_RAW = "https://raw.githubusercontent.com/"
