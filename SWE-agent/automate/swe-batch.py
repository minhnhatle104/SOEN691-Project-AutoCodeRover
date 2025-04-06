import subprocess
import json
import os
import glob
import shutil
import datetime

def write_log(message, log_file='/home/user/SOEN691-Project-AutoCodeRover/SWE-agent/automate/swe-batch.log'):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a') as file:
        file.write(f'{timestamp} - {message}\n')

def run_sweagent(instance_id, env_repo_path, agent_model_name, output_dir):
    """
    Runs the sweagent command, extracts the generated patch, saves it to a JSON file,
    and deletes the patch folder.

    :param instance_id: String of instance_id.
    :param env_repo_path: Path to the environment repository.
    :param agent_model_name: OpenAI Model name to use.
    :param output_dir: Directory where output is stored.
    """
    
    # Run the sweagent command
    problem_statement_path = env_repo_path + "/problem_statement.md"
    write_log(f'Running SWE-Agent for {instance_id}')

    command = [
        "sweagent", "run",
        "--agent.model.name", agent_model_name,
        "--env.repo.path", env_repo_path,
        "--problem_statement.path", problem_statement_path,
        "--output_dir", output_dir
    ]
    subprocess.run(command, check=True)
    write_log(f'Finished SWE-Agent for {instance_id}')

    # Find the generated patch folder (assuming a randomly named directory is created inside `output_dir`)
    patch_folders = [d for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))]

    if patch_folders:
        patch_folder = os.path.join(output_dir, patch_folders[0])  # Get the first patch folder
        patch_files = glob.glob(os.path.join(patch_folder, "*.patch"))

        if patch_files:
            patch_file = patch_files[0]  # Get the first .patch file
            with open(patch_file, "r") as f:
                patch_content = f.read()

            json_file = os.path.join(output_dir, f"swe-agent.json")

            # Load existing data if the file exists and is not empty
            if os.path.exists(json_file) and os.path.getsize(json_file) > 0:
                with open(json_file, "r") as f:
                    try:
                        data = json.load(f)  # Load existing JSON list
                        if not isinstance(data, list):
                            data = []  # Ensure it's a list
                    except json.JSONDecodeError:
                        data = []  # If file is empty or corrupt, start fresh
            else:
                data = []

            # Append new patch data
            data.append({
                "instance_id": instance_id,
                "model_name_or_path": agent_model_name,
                "model_patch": patch_content
            })

            # Write updated JSON back to file
            with open(json_file, "w") as f:
                json.dump(data, f, indent=4)

            print(f"Patch saved to {json_file}")
            write_log(f'Patch saved for {instance_id}')

        # Delete the patch folder after extraction
        shutil.rmtree(patch_folder)
        print(f"Deleted patch folder: {patch_folder}")
    else:
        print("No patch folder found.")

def swe_batch(json_path):
    # Load JSON data
    write_log(f'Started SWE-Batch')
    with open(json_path, "r") as f:
        data = json.load(f)
    
    # Iterate through all top-level keys
    for top_key, repo_info in data.items():
        repo_path = repo_info.get("repo_path")
        base_commit = repo_info.get("base_commit")
        instance_id = repo_info.get("instance_id")
        problem_statement = repo_info.get("problem_statement")

        write_log(f'Begin {instance_id}')

        if not repo_path or not base_commit or not problem_statement:
            print(f"Skipping {top_key}: Missing required fields.")
            continue
        
        # Navigate to the repo path
        if os.path.exists(repo_path):
            os.chdir(repo_path)
                        
            try:
                # Checkout the base commit
                subprocess.run(["git", "checkout", base_commit], check=True)
                write_log(f'Git checkout')
                # Save problem_statement as a Markdown file
                problem_file = os.path.join(repo_path, "problem_statement.md")
                with open(problem_file, "w") as f:
                    f.write(problem_statement)
                write_log(f'saved problem_statement.md')

                # Run 'ls -la' to list files
                run_sweagent(
                    instance_id=instance_id,
                    env_repo_path=repo_path,
                    agent_model_name="gpt-4o-mini-2024-07-18",
                    output_dir="/home/user/SOEN691-Project-AutoCodeRover/SWE-agent/automate"
                )
            except subprocess.CalledProcessError as e:
                print(f"Error occurred: {e}")
                write_log(f'Git checkout Error')
                write_log(f'Skipped {instance_id}')
                continue           
            
        else:
            print(f"Error: Repository path '{repo_path}' for {top_key} does not exist.")
        write_log(f'End {instance_id}')
    write_log(f'Completed SWE-Batch')

# Example usage:
if __name__ == "__main__":
    swe_batch("../SWE-bench/setup_result/full_map.json")