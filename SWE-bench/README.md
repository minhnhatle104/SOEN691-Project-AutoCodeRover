# Fork of SWE-bench

Fork of [SWE-bench](https://github.com/princeton-nlp/SWE-bench) with modifications to use some of its scripts.

## Docker images

```
# only evaluation environment
yuntongzhang/swe-bench:latest
# additionally with projects setup for other tools
yuntongzhang/swe-bench:experiment
```

## Instructions

### To install
 Ensure the necessary libraries are installed, including git and subprocess

### To set up task instances for other tools

Run the following command to create a setup directory that is compatible with your local environment. This will also generate a setup.json file, which accounts for varying root_path across different systems.

**To set up all task instances, do:**

To generate setup_map and task_map, run the below command, cause based on directory the setup_map will genrate new directory that is compatoble for anyone's pc.

```
python harness/run_setup.py --log_dir logs --testbed testbed --result_dir setup_result
```

**You can also use multiple processes for setting up environment. However, note that conda is not thread-safe, and doing this may result in deadlock:**

```
python harness/run_setup.py --log_dir logs --testbed testbed --result_dir setup_result --num_processes 16
```


### To evaluate on some task instances

1. Prepare a prediction file in json. This `prediction.json` file should contain the model's output
   in the field 'model_patch', which will be used for evaluation.
   If just want to evaluate on one instance, you can put only that entry's answer in this file.
2. Prepare the big json file `swe-bench.json` that contains all the task instance definitions.
   This can be downloaded from the original Github repo.
3. Create directories `logs` and `eval-testbed` for storing logs and the temporarily cloned projects.

Run the evaluation script like this:

NOTE: do not overwrite existing `testbed` directory, as it contains setup for other tools to run.

```
mkdir eval_logs
mkdir eval_testbed
python harness/run_evaluation.py --predictions_path ../predictions_for_swebench.json --swe_bench_tasks ./data/swe-bench.json --log_dir eval_logs --testbed eval_testbed  --verbose
```
