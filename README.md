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

## For development in the local

Please use .devcontainer/devcontainer.json and run in IntelliJ (it requires Docker)
In devcontainer.json, it will point to Dockerfile.localdev to run

## For running in docker

Using Dockerfile.minimal (the newest file to run)

---
---
---
# SOEN691-Project-AutoCodeRover

Repositories:
1. [auto-code-rover](https://github.com/AutoCodeRoverSG/auto-code-rover)
2. [SWE-bench](https://github.com/yuntongzhang/SWE-bench) - Integrate swe-bench-java-verified
3. [multi-swe-bench-env](https://github.com/multi-swe-bench/multi-swe-bench-env)
4. [SWE-agent](https://github.com/SWE-agent/SWE-agent)

Pre-requisites
1. Debian 12 x86_64 VM [CPU: 2 Core/Threads; RAM: 4GB]
2. Conda (Anaconda or Miniconda)

# Installation
Clone the Repository
```bash
git clone https://github.com/minhnhatle104/SOEN691-Project-AutoCodeRover
```
Initialize Project Paths
```bash
cd SOEN691-Project-AutoCodeRover && source path_setup.sh
```
# Workflow
## Step 1: Setting Up Testbed (SWE-bench)
### SWE-BENCH Setup
```bash
cd $SWE_BENCH_PATH

# swe-bench Environment Setup
conda env create -f environment.yml
conda activate swe-bench

# Linux Specific code
ln -sf /bin/bash /bin/sh            # Make bash default shell
sudo sed -i '/^deb / s/main/main contrib/' /etc/apt/sources.list # Debian: Add contrib repo
sudo apt update && sudo apt upgrade # Update System before
sudo apt install -y libffi-dev python3-pytest libfreetype6-dev libqhull-dev pkg-config texlive cm-super dvipng python3-tk ffmpeg imagemagick fontconfig ghostscript inkscape graphviz optipng fonts-comic-neue python3-pikepdf build-essential libssl-dev ttf-mscorefonts-installer 

# reboot system
sudo systemctl reboot
```
### Running SWE-BENCH
```bash
cd $SWE_BENCH_PATH
conda activate swe-bench
python harness/run_setup.py --log_dir logs --testbed testbed --result_dir setup_result --subset_file tasks.txt
```
> **setup_map** is saved to `setup_result/setup_map.json` <br>
> **tasks_map** is saved to `setup_result/tasks_map.json`

## Step 2: Getting Patches (AutoCodeRover)

## Step 2.5: Getting Patches (SWE-Agent)
### SWE-AGENT Setup
```bash
cd $SWE_AGENT_PATH

# swe-agent Environment Setup
conda env create -f environment.yml
conda activate swe-agent

# install
python -m pip install --upgrade pip && pip install --editable .

# test
sweagent --help

# setting api key
echo "# Remove the comment '#' in front of the line for all keys that you have set " > .env
echo "# OPENAI_API_KEY='OpenAI API Key Here if using OpenAI Model'" > .env # Edit this file to add openai key
```
### Running SWE-AGENT
```bash
cd $SWE_AGENT_PATH
conda activate swe-agent

# Prepare full_map.json
python automate/mergejson.py 

# Edit absolute paths `log_file' & `output_dir` inside `automate/swe-batch.py` before running it

# Run SWE-Agent for all tasks
python automate/swe-batch.py
```

## Step 3: Validating Patches (Multi-SWE-Bench)
