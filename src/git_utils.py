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
        logging.error(f"Error retrieving git diff: {e}")
        return None