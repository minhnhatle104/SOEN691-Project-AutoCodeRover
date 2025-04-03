#!/usr/bin/env python

import argparse
import os
import subprocess

from multiprocessing import Pool


def delete_folders_with_prefix(prefix, conda_path):
    """
    Find and rm folders with a particular prefix in the conda installation's env folder

    Args:
        prefix (str): Prefix of folders to remove
        conda_path (str): Path to conda installation
    """
    envs_folder = os.path.join(conda_path, "envs")
    command = f'find {envs_folder} -type d -name "{prefix}*" -exec rm -rf {{}} +'
    subprocess.run(command.split(" "))


def remove_environment(env_name, prefix):
    """
    Remove all conda environments with a particular prefix from a conda installation
    """
    if env_name.startswith(prefix):
        print(f"Removing {env_name}")
        conda_cmd = "conda remove -n " + env_name + " --all -y"
        cmd = conda_source + " && " + conda_cmd
        try:
            conda_create_output = subprocess.run(cmd.split(), check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            print(f"Error output: {e.stderr}")
            raise e
        print(f"Output: {conda_create_output.stdout}")


if __name__ == "__main__":
    """
    Logic for removing conda environments and their folders from a conda installation
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("prefix", type=str, help="Prefix for environments to delete")
    parser.add_argument(
        "--conda_path",
        type=str,
        help="Path to miniconda installation",
    )
    args = parser.parse_args()

    # Remove conda environments with a specific prefix
    conda_source = "source " + os.path.join(args.conda_path, "etc/profile.d/conda.sh")
    check_env = conda_source + " && " + "conda env list"
    try:
        conda_envs = subprocess.run(check_env.split(" "), check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Error output: {e.stderr.decode('utf-8')}")
        raise e

    # Remove env folder with the same prefix
    print(
        f"Removing miniconda folder for environments with {args.prefix} from {args.conda_path}"
    )
    delete_folders_with_prefix(args.prefix, args.conda_path)
    print(f"Done!")
