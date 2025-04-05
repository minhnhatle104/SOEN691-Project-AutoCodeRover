# 🛠️ SOEN691-Project-AutoCodeRover

## 🚀 Commands to Run AutoCodeRover for Patch Generation

### ✅ Step 1: Navigate to the project directory SWE-Bench
     1. Navigate to swe-bench
     ```bash
       cd SWE-bench
    ```
    2. Create `tasks.txt` file that contains all task id of the project
    3. Generate setup.json and task.json files:

    ```bash
      python harness/run_setup.py \
        --log_dir logs \
        --testbed testbed \
        --result_dir setup_result \
        --subset_file tasks.txt
    ```

### ✅ Step 2: Navigate to the project directory of autocoderover

1. Setup environment & export OPENAI Key

2. Run the below command for one task 1.

    ```bash
    cd auto-code-rover

    PYTHONPATH=. python app/main.py swe-bench \
    --model gpt-4o-mini-2024-07-18 \
    --model-temperature 0.2 \
    --output-dir output \
    --setup-map ../SWE-bench/setup_result/setup_map.json \
    --tasks-map ../SWE-bench/setup_result/tasks_map.json \
    --task apache__dubbo-10638 \
    --num-processes 1
    ```

3. Command to run all tasks together
 
 ```bash 
    PYTHONPATH=. python app/main.py swe-bench \
    --model gpt-4o-mini-2024-07-18 \
    --model-temperature 0.2 \
    --output-dir output \
    --setup-map ../SWE-bench/setup_result/setup_map.json \
    --tasks-map ../SWE-bench/setup_result/tasks_map.json \
    --task-list-file ../SWE-bench/tasks.txt \
    --num-processes 1
```

### ✅ Step 3: Use swebench.harness.run_evaluation to evaluate your predictions on Multi-SWE-bench:

```bash
  python -m swebench.harness.run_evaluation \
    --dataset_name Daoguang/Multi-SWE-bench \
    --predictions_path <path_to_predictions> \
    --max_workers <num_workers> \
    --run_id <run_id>
```

