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
Output
```sh
2025-03-23 14:40:33,960 - INFO - env_name for all setup entries: ['setup_apache__dubbo__0.1', 'setup_fasterxml__jackson-core__0.1', 'setup_fasterxml__jackson-databind__0.1', 'setup_fasterxml__jackson-dataformat-xml__0.1', 'setup_google__gson__0.1', 'setup_googlecontainertools__jib__0.1']
2025-03-23 14:40:33,961 - INFO - Starting parallel setup.
2025-03-23 14:40:33,961 - INFO -        Number of setup tasks: 6
2025-03-23 14:40:33,961 - INFO -        Number of processes: 1
2025-03-23 14:40:33,961 - INFO -  *** PRINT MINH LE:  apache__dubbo /home/user/SOEN691-Project-AutoCodeRover/SWE-bench/testbed/apache__dubbo/setup_apache__dubbo__0.1 =======
2025-03-23 14:40:33,961 - INFO - [setup_apache__dubbo__0.1] ======= Start setting up for apache__dubbo 0.1 =======
2025-03-23 14:40:33,961 - INFO -  *** REPOSITORY MINH LE:  https://git@github.com/minhnhatle104/apache__dubbo.git apache__dubbo =======
2025-03-23 14:40:45,138 - INFO - [setup_apache__dubbo__0.1] Cloned apache__dubbo to /home/user/SOEN691-Project-AutoCodeRover/SWE-bench/testbed/apache__dubbo/setup_apache__dubbo__0.1
2025-03-23 14:40:45,139 - INFO -  *** PRINT MINH LE:  fasterxml__jackson-core /home/user/SOEN691-Project-AutoCodeRover/SWE-bench/testbed/fasterxml__jackson-core/setup_fasterxml__jackson-core__0.1 =======
2025-03-23 14:40:45,139 - INFO - [setup_fasterxml__jackson-core__0.1] ======= Start setting up for fasterxml__jackson-core 0.1 =======
2025-03-23 14:40:45,139 - INFO -  *** REPOSITORY MINH LE:  https://git@github.com/minhnhatle104/fasterxml__jackson-core.git fasterxml__jackson-core =======
2025-03-23 14:40:49,655 - INFO - [setup_fasterxml__jackson-core__0.1] Cloned fasterxml__jackson-core to /home/user/SOEN691-Project-AutoCodeRover/SWE-bench/testbed/fasterxml__jackson-core/setup_fasterxml__jackson-core__0.1
2025-03-23 14:40:49,655 - INFO -  *** PRINT MINH LE:  fasterxml__jackson-databind /home/user/SOEN691-Project-AutoCodeRover/SWE-bench/testbed/fasterxml__jackson-databind/setup_fasterxml__jackson-databind__0.1 =======
2025-03-23 14:40:49,655 - INFO - [setup_fasterxml__jackson-databind__0.1] ======= Start setting up for fasterxml__jackson-databind 0.1 =======
2025-03-23 14:40:49,655 - INFO -  *** REPOSITORY MINH LE:  https://git@github.com/minhnhatle104/fasterxml__jackson-databind.git fasterxml__jackson-databind =======
2025-03-23 14:41:02,521 - INFO - [setup_fasterxml__jackson-databind__0.1] Cloned fasterxml__jackson-databind to /home/user/SOEN691-Project-AutoCodeRover/SWE-bench/testbed/fasterxml__jackson-databind/setup_fasterxml__jackson-databind__0.1
2025-03-23 14:41:02,522 - INFO -  *** PRINT MINH LE:  fasterxml__jackson-dataformat-xml /home/user/SOEN691-Project-AutoCodeRover/SWE-bench/testbed/fasterxml__jackson-dataformat-xml/setup_fasterxml__jackson-dataformat-xml__0.1 =======
2025-03-23 14:41:02,522 - INFO - [setup_fasterxml__jackson-dataformat-xml__0.1] ======= Start setting up for fasterxml__jackson-dataformat-xml 0.1 =======
2025-03-23 14:41:02,522 - INFO -  *** REPOSITORY MINH LE:  https://git@github.com/minhnhatle104/fasterxml__jackson-dataformat-xml.git fasterxml__jackson-dataformat-xml =======
2025-03-23 14:41:04,076 - INFO - [setup_fasterxml__jackson-dataformat-xml__0.1] Cloned fasterxml__jackson-dataformat-xml to /home/user/SOEN691-Project-AutoCodeRover/SWE-bench/testbed/fasterxml__jackson-dataformat-xml/setup_fasterxml__jackson-dataformat-xml__0.1
2025-03-23 14:41:04,076 - INFO -  *** PRINT MINH LE:  google__gson /home/user/SOEN691-Project-AutoCodeRover/SWE-bench/testbed/google__gson/setup_google__gson__0.1 =======
2025-03-23 14:41:04,076 - INFO - [setup_google__gson__0.1] ======= Start setting up for google__gson 0.1 =======
2025-03-23 14:41:04,076 - INFO -  *** REPOSITORY MINH LE:  https://git@github.com/minhnhatle104/google__gson.git google__gson =======
2025-03-23 14:41:06,034 - INFO - [setup_google__gson__0.1] Cloned google__gson to /home/user/SOEN691-Project-AutoCodeRover/SWE-bench/testbed/google__gson/setup_google__gson__0.1
2025-03-23 14:41:06,034 - INFO -  *** PRINT MINH LE:  googlecontainertools__jib /home/user/SOEN691-Project-AutoCodeRover/SWE-bench/testbed/googlecontainertools__jib/setup_googlecontainertools__jib__0.1 =======
2025-03-23 14:41:06,034 - INFO - [setup_googlecontainertools__jib__0.1] ======= Start setting up for googlecontainertools__jib 0.1 =======
2025-03-23 14:41:06,035 - INFO -  *** REPOSITORY MINH LE:  https://git@github.com/minhnhatle104/googlecontainertools__jib.git googlecontainertools__jib =======
2025-03-23 14:41:08,954 - INFO - [setup_googlecontainertools__jib__0.1] Cloned googlecontainertools__jib to /home/user/SOEN691-Project-AutoCodeRover/SWE-bench/testbed/googlecontainertools__jib/setup_googlecontainertools__jib__0.1
Done with setup.
setup_map is saved to setup_result/setup_map.json
tasks_map is saved to setup_result/tasks_map.json
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
```
#### Basic Example Project uning gpt-4o-mini
```bash
sweagent run \
  --agent.model.name=gpt-4o-mini-2024-07-18 \
  --env.repo.github_url=https://github.com/SWE-agent/test-repo \
  --problem_statement.github_url=https://github.com/SWE-agent/test-repo/issues/1

PATCH_FILE_PATH = "$SWE_AGENT_PATH/trajectories/user/anthropic_filemap__gpt-4o-mini-*___SWE-agent__test-repo-i1/SWE-agent__test-repo-i1/SWE-agent__test-repo-i1.patch"

# Inspect it:
cat "${PATCH_FILE_PATH}"
# Apply it to a local repository:
# cd <your local repo root>
# git apply "${PATCH_FILE_PATH}"
```
#### Local Repo Mode
```bash
sweagent run \
    --agent.model.name=gpt-4o-mini-2024-07-18 \
    --env.repo.path /path/to/repo \
    --problem_statement.path=path/to/problem_statement.md
```
- IDEA: During SWE-Bench Dataset preparation, we also extract the issue into a problem_statement.md in the same project directory

```bash
sweagent run \
    --agent.model.name=gpt-4o-mini-2024-07-18 \
    --env.repo.path "/home/user/SOEN691-Project-AutoCodeRover/SWE-bench/testbed/apache__dubbo/setup_apache__dubbo__0.1" \
    --problem_statement.path="/home/user/SOEN691-Project-AutoCodeRover/SWE-bench/testbed/apache__dubbo/setup_apache__dubbo__0.1/problem_statement.md" \
    --output_dir "automate"
```
Output
```
🤠 INFO     Trajectory saved to /home/user/SOEN691-Project-AutoCodeRover/SWE-agent/trajectories/user/anthropic_filemap__gpt-4o-mini-2024-07-18__t-0.00__p-1.00__c-3.00___6b97db/6b97db/6b97db.traj                 
╭──────────────────────────── 🎉 Submission successful 🎉 ────────────────────────────╮
│ SWE-agent has produced a patch that it believes will solve the issue you submitted! │
│ Use the code snippet below to inspect or apply it!                                  │
╰─────────────────────────────────────────────────────────────────────────────────────╯
                                                                                                                                                                                                                   
 # The patch has been saved to your local filesystem at:                                                                                                                                                           
 PATCH_FILE_PATH='/home/user/SOEN691-Project-AutoCodeRover/SWE-agent/trajectories/user/anthropic_filemap__gpt-4o-mini-2024-07-18__t-0.00__p-1.00__c-3.00___6b97db/6b97db/6b97db.patch'                             
 # Inspect it:                                                                                                                                                                                                     
 cat "${PATCH_FILE_PATH}"                                                                                                                                                                                          
 # Apply it to a local repository:                                                                                                                                                                                 
 cd <your local repo root>                                                                                                                                                                                         
 git apply "${PATCH_FILE_PATH}"                                                                                                                                                                                    
                                                                                                                                                                                                                   
🏃 INFO     Done                                                                                                                                                                                                   
��� INFO   Beginning environment shutdown...                                                                                                                                                                       
🦖 DEBUG    Ensuring deployment is stopped because object is deleted
```

### Final Automated Approach

```bash
python automate/mergejson.py # Prepare full_map.json
python automate/swe-batch.py # Run SWE-Agent for all tasks
```
## Step 3: Validating Patches (Multi-SWE-Bench)

