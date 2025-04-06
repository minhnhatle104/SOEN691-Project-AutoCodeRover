# constants.py

# Define the setup configurations for each repository version
# constants.py

# Define the setup configurations for each repository version
SPECS_APACHE_DUBBO = {
    "0.1": {
        "root_path": "SWE-bench/testbed/apache__dubbo",
        "jdk_version": "17",
        "env_type": "maven",
        "eval_cmd": "(mvn clean install -DskipTests -Dmaven.javadoc.skip=true ; mvn clean test -Dsurefire.useFile=false -Dmaven.test.skip=false -D{test_spec}={test_func} -DfailIfNoTests=false -pl {module}) >>{module_escaped}:{test_func}.test.log"
    }
}

SPECS_FASTERXML_JACKSON_DATABIND = {
    "0.1": {
        "root_path": "SWE-bench/testbed/fasterxml__jackson-databind",
        "jdk_version": "8",
        "env_type": "maven",
        "eval_cmd": "(mvn clean install -DskipTests -Dmaven.javadoc.skip=true ; mvn clean test -Dsurefire.useFile=false -Dmaven.test.skip=false -D{test_spec}={test_func} -DfailIfNoTests=false -pl {module}) >>{module_escaped}:{test_func}.test.log"
    }
}

SPECS_FASTERXML_JACKSON_CORE = {
    "0.1": {
        "root_path": "SWE-bench/testbed/fasterxml__jackson-core",
        "jdk_version": "8",
        "env_type": "maven",
        "eval_cmd": "(mvn clean install -DskipTests -Dmaven.javadoc.skip=true ; mvn clean test -Dsurefire.useFile=false -Dmaven.test.skip=false -D{test_spec}={test_func} -DfailIfNoTests=false -pl {module}) >>{module_escaped}:{test_func}.test.log"
    }
}

SPECS_GOOGLE_GSON = {
    "0.1": {
        "root_path": "SWE-bench/testbed/google__gson",
        "jdk_version": "11",
        "env_type": "maven",
        "eval_cmd": "(mvn clean install -DskipTests -Dmaven.javadoc.skip=true ; mvn clean test -Dsurefire.useFile=false -Dmaven.test.skip=false -D{test_spec}={test_func} -DfailIfNoTests=false -pl {module}) >>{module_escaped}:{test_func}.test.log"
    }
}

SPECS_FASTERXML_JACKSON_DATAFORMAT_XML = {
    "0.1": {
        "root_path": "SWE-bench/testbed/fasterxml__jackson-dataformat-xml",
        "jdk_version": "8",
        "env_type": "maven",
        "eval_cmd": "(mvn clean install -DskipTests -Dmaven.javadoc.skip=true ; mvn clean test -Dsurefire.useFile=false -Dmaven.test.skip=false -D{test_spec}={test_func} -DfailIfNoTests=false -pl {module}) >>{module_escaped}:{test_func}.test.log"
    }
}

SPECS_GOOGLECONTAINERS_JIB = {
    "0.1": {
        "root_path": "SWE-bench/testbed/googlecontainertools__jib",
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
    "apache__dubbo": "mvn clean install -DskipTests -Dmaven.javadoc.skip=true",
    "fasterxml__jackson-databind": "mvn clean install -DskipTests -Dmaven.javadoc.skip=true",
    "fasterxml__jackson-core": "mvn clean install -DskipTests -Dmaven.javadoc.skip=true",
    "google__gson": "mvn clean install -DskipTests -Dmaven.javadoc.skip=true",
    "fasterxml__jackson-dataformat-xml": "mvn clean install -DskipTests -Dmaven.javadoc.skip=true",
    "googlecontainertools__jib": "./gradlew build",
}

# Define test framework mapping for repositories
MAP_REPO_TO_TEST_FRAMEWORK = {
    "apache__dubbo": "mvn clean test",
    "fasterxml__jackson-databind": "mvn clean test",
    "fasterxml__jackson-core": "mvn clean test",
    "google__gson": "mvn clean test",
    "fasterxml__jackson-dataformat-xml": "mvn clean test",
    "googlecontainertools__jib": "./gradlew test",
}

# Mapping versions to installation instructions
MAP_VERSION_TO_INSTALL = {
    "apache__dubbo": {
        "0.1": {
            "jdk_version": "17",
            "env_type": "maven",
            "install": "mvn clean install -DskipTests -Dmaven.javadoc.skip=true",
        }
    },
    "fasterxml__jackson-databind": {
        "0.1": {
            "jdk_version": "8",
            "env_type": "maven",
            "install": "mvn clean install -DskipTests -Dmaven.javadoc.skip=true",
        }
    },
    "fasterxml__jackson-core": {
        "0.1": {
            "jdk_version": "8",
            "env_type": "maven",
            "install": "mvn clean install -DskipTests -Dmaven.javadoc.skip=true",
        }
    },
    "google__gson": {
        "0.1": {
            "jdk_version": "11",
            "env_type": "maven",
            "install": "mvn clean install -DskipTests -Dmaven.javadoc.skip=true",
        }
    },
    "fasterxml__jackson-dataformat-xml": {
        "0.1": {
            "jdk_version": "8",
            "env_type": "maven",
            "install": "mvn clean install -DskipTests -Dmaven.javadoc.skip=true",
        }
    },
    "googlecontainertools__jib": {
        "0.1": {
            "jdk_version": "11",
            "env_type": "gradle",
            "install": "./gradlew build",
        }
    },
}

MAP_REPO_TO_REQS_PATHS = {
    "apache__dubbo": ["pom.xml"],
    "google__gson": ["pom.xml"],
    "fasterxml__jackson-core": ["pom.xml"],
    "fasterxml__jackson-databind": ["pom.xml"],
    "fasterxml__jackson-dataformat-xml": ["pom.xml"],
    "googlecontainertools__jib": ["build.gradle"],
}

MAP_REPO_TO_ENV_YML_PATHS = {}

KEY_INSTANCE_ID = "instance_id"
KEY_MODEL = "model_name_or_path"
KEY_PREDICTION = "model_patch"

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

NON_TEST_EXTS = [".json", ".png", "csv", ".txt", ".md", ".jpg", ".jpeg", ".pkl", ".yml", ".yaml", ".toml"]
SWE_BENCH_URL_RAW = "https://raw.githubusercontent.com/"
