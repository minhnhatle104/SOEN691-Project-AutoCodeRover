# Java Projects Mapping - Constants for setup and installation
SPECS_DUBBO = {
    k: {
        "root_path": "SWE-bench/testbed/apache__dubbo",
        "jdk_version": "8",
        "env_type": "maven",
        "eval_cmd": "(mvn clean install -Dmaven.test.skip=true ; mvn clean test -Dsurefire.useFile=false -Dmaven.test.skip=false -D{test_spec}={test_func} -DfailIfNoTests=false -pl {module}) >>{module_escaped}:{test_func}.test.log"
    }
    for k in ["0.1"]
}

SPECS_GSON = {
    k: {
        "root_path": "",
        "jdk_version": "11",
        "env_type": "maven",
        "eval_cmd": "(mvn clean install -Dmaven.test.skip=true ; mvn clean test -Dsurefire.useFile=false -Dmaven.test.skip=false -D{test_spec}={test_func} -DfailIfNoTests=false -pl {module}) >>{module_escaped}:{test_func}.test.log"
    }
    for k in ["0.1"]
}

SPECS_JACKSON_CORE = {
    k: {
        "root_path": "",
        "jdk_version": "8",
        "env_type": "maven",
        "eval_cmd": "(mvn clean install -Dmaven.test.skip=true ; mvn clean test -Dsurefire.useFile=false -Dmaven.test.skip=false -D{test_spec}={test_func} -DfailIfNoTests=false -pl {module}) >>{module_escaped}:{test_func}.test.log"
    }
    for k in ["0.1"]
}

SPECS_JACKSON_DATABIND = {
    k: {
        "root_path": "",
        "jdk_version": "8",
        "env_type": "maven",
        "eval_cmd": "(mvn clean install -Dmaven.test.skip=true ; mvn clean test -Dsurefire.useFile=false -Dmaven.test.skip=false -D{test_spec}={test_func} -DfailIfNoTests=false -pl {module}) >>{module_escaped}:{test_func}.test.log"
    }
    for k in ["0.1"]
}

SPECS_JACKSON_DATAFORMAT_XML = {
    k: {
        "root_path": "",
        "jdk_version": "8",
        "env_type": "maven",
        "eval_cmd": "(mvn clean install -Dmaven.test.skip=true ; mvn clean test -Dsurefire.useFile=false -Dmaven.test.skip=false -D{test_spec}={test_func} -DfailIfNoTests=false -pl {module}) >>{module_escaped}:{test_func}.test.log"
    }
    for k in ["0.1"]
}

SPECS_JIB = {
    k: {
        "root_path": "",
        "jdk_version": "11",
        "env_type": "gradle",
        "eval_cmd": "./gradlew {module}:{test_spec} --tests {test_func} >{module}:{test_func}.test.log 2>&1"
    }
    for k in ["0.1"]
}

# Map each repository to its specs dictionary
MAP_REPO_VERSION_TO_SPECS = {
    "apache/dubbo": SPECS_DUBBO,
    "google/gson": SPECS_GSON,
    "fasterxml/jackson-core": SPECS_JACKSON_CORE,
    "fasterxml/jackson-databind": SPECS_JACKSON_DATABIND,
    "fasterxml/jackson-dataformat-xml": SPECS_JACKSON_DATAFORMAT_XML,
    "googlecontainertools/jib": SPECS_JIB,
}

# Constants - Repository Specific Installation Instructions
MAP_REPO_TO_INSTALL = {}

# Constants - Task Instance Installation Environment for Java Projects
MAP_VERSION_TO_INSTALL = {
    "apache/dubbo": {
        "0.1": {
            "jdk_version": "8",
            "env_type": "maven",
            "install": "mvn clean install",
            "test": "mvn test"
        }
    },
    "google/gson": {
        "0.1": {
            "jdk_version": "11",
            "env_type": "maven",
            "install": "mvn clean install",
             "test": "mvn test"
        }
    },
    
    "fasterxml/jackson-core": {
        "0.1": {
            "jdk_version": "8",
            "env_type": "maven",
            "install": "mvn clean install",
             "test": "mvn test"
        }
    },
    
    "fasterxml/jackson-databind": {
        "0.1": {
            "jdk_version": "8",
            "env_type": "maven",
            "install": "mvn clean install",
            "test": "mvn test"
        }
    },
    
    "fasterxml/jackson-dataformat-xml": {
        "0.1": {
            "jdk_version": "8",
            "env_type": "maven",
            "install": "mvn clean install",
            "test": "mvn test"
        }
    },
    "googlecontainertools/jib": {
        "0.1": {
            "jdk_version": "8",
            "env_type": "gradle",
            "install": "./gradlew clean build",
            "run": "./gradlew run",
            "test": "./gradlew test"
        }
    }
}

# Constants - Task Instance Test Frameworks for Java Projects
MAP_REPO_TO_TEST_FRAMEWORK = {
    "apache/dubbo": "mvn clean test",
    "google/gson": "mvn clean test",
    "fasterxml/jackson-core": "mvn clean test",
    "fasterxml/jackson-databind": "mvn clean test",
    "fasterxml/jackson-dataformat-xml": "mvn clean test",
    "googlecontainertools/jib": "./gradlew test"
}

# Constants - Task Instance Requirements File Paths for Java Projects (if applicable)
MAP_REPO_TO_REQS_PATHS = {
    "apache/dubbo": ["pom.xml"],
    "google/gson": ["pom.xml"],
    "fasterxml/jackson-core": ["pom.xml"],
    "fasterxml/jackson-databind": ["pom.xml"],
    "fasterxml/jackson-dataformat-xml": ["pom.xml"],
    "googlecontainertools/jib": ["build.gradle"]
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
