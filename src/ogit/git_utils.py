import subprocess
import logging


def get_git_diff():
    """
    Retrieve the current git diff as a string.
    """
    cmd = ['git', 'diff']
    try:
        diff = subprocess.check_output(cmd, universal_newlines=True)
        return diff
    except subprocess.CalledProcessError as e:
        print("[ERROR] Failed to retrieve git diff.")
        print("[!] Make sure you're in a git repo with staged changes.")
        return ""