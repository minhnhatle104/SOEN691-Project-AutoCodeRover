# SOEN691-Project-AutoCodeRover

Repositories:
1. [auto-code-rover](https://github.com/AutoCodeRoverSG/auto-code-rover)
2. [SWE-bench](https://github.com/yuntongzhang/SWE-bench) - Integrate swe-bench-java-verified
3. [multi-swe-bench-env](https://github.com/multi-swe-bench/multi-swe-bench-env)
4. [SWE-agent](https://github.com/SWE-agent/SWE-agent)

Pre-requisites
1. Debian 12 x86_64 VM [CPU: 2 Core/Threads; RAM: 4GB]
2. Conda (Anaconda or Miniconda)

# Installation (Python)
Clone the Repository
```bash
git clone https://github.com/minhnhatle104/SOEN691-Project-AutoCodeRover
```
Initialize Project Paths
```bash
cd SOEN691-Project-AutoCodeRover && source path_setup.sh
```
# New Workflow
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

python automate/mergejson.py # Prepare full_map.json
python automate/swe-batch.py # Run SWE-Agent for all tasks
```

## Step 3: Validating Patches (Multi-SWE-Bench)

