import subprocess
import logging
from typing import Optional, Tuple

from .constants import (
    GIT_DIFF_STAGED, GIT_DIFF_UNSTAGED, GIT_STATUS, GIT_BRANCH,
    ERROR_GIT_DIFF_FAILED, PROTECTED_BRANCHES, ERROR_PROTECTED_BRANCH
)

logger = logging.getLogger(__name__)


def get_git_diff(include_staged: bool = True, include_unstaged: bool = True) -> str:
    """
    Retrieve the current git diff as a string.
    
    Args:
        include_staged: Whether to include staged changes
        include_unstaged: Whether to include unstaged changes
    
    Returns:
        Git diff as a string, empty if no changes or error occurred
    """
    diffs = []
    
    if include_staged:
        staged_diff = _get_diff_output(GIT_DIFF_STAGED, "staged")
        if staged_diff:
            diffs.append(f"# Staged changes:\n{staged_diff}")
    
    if include_unstaged:
        unstaged_diff = _get_diff_output(GIT_DIFF_UNSTAGED, "unstaged")
        if unstaged_diff:
            diffs.append(f"# Unstaged changes:\n{unstaged_diff}")
    
    if not diffs:
        logger.info("No git changes detected")
        return ""
    
    return "\n\n".join(diffs)


def _get_diff_output(cmd: list[str], diff_type: str) -> str:
    """
    Execute git diff command and return output.
    
    Args:
        cmd: Git command to execute
        diff_type: Type of diff for logging purposes
    
    Returns:
        Diff output as string, empty if error occurred
    """
    try:
        diff = subprocess.check_output(cmd, universal_newlines=True, stderr=subprocess.PIPE)
        if diff.strip():
            logger.debug(f"Retrieved {diff_type} git diff: {len(diff)} characters")
        return diff
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to retrieve {diff_type} git diff: {e}")
        logger.debug(f"Git stderr: {e.stderr}")
        return ""
    except Exception as e:
        logger.error(f"Unexpected error retrieving {diff_type} git diff: {e}")
        return ""


def get_git_status() -> Optional[str]:
    """
    Get the current git status in porcelain format.
    
    Returns:
        Git status output or None if error occurred
    """
    try:
        status = subprocess.check_output(GIT_STATUS, universal_newlines=True, stderr=subprocess.PIPE)
        logger.debug(f"Git status retrieved: {len(status.splitlines())} files")
        return status.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get git status: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting git status: {e}")
        return None


def get_current_branch() -> Optional[str]:
    """
    Get the current git branch name.
    
    Returns:
        Branch name or None if error occurred
    """
    try:
        branch = subprocess.check_output(GIT_BRANCH, universal_newlines=True, stderr=subprocess.PIPE)
        branch_name = branch.strip()
        logger.debug(f"Current branch: {branch_name}")
        return branch_name
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get current branch: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting current branch: {e}")
        return None


def is_branch_protected(branch: str) -> bool:
    """
    Check if a branch is protected (should not auto-push).
    
    Args:
        branch: Branch name to check
    
    Returns:
        True if branch is protected
    """
    return branch.lower() in PROTECTED_BRANCHES


def validate_git_repo() -> Tuple[bool, str]:
    """
    Validate that we're in a git repository with changes.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        subprocess.check_output(["git", "rev-parse", "--git-dir"], stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        return False, "Not in a git repository"
    except Exception as e:
        return False, f"Error checking git repository: {e}"
    
    status = get_git_status()
    if status is None:
        return False, "Cannot read git status"
    
    if not status:
        return False, "No changes detected in repository"
    
    return True, ""


def execute_git_commands(commands: list[list[str]], stop_on_error: bool = True) -> Tuple[bool, str]:
    """
    Execute a series of git commands.
    
    Args:
        commands: List of git commands to execute
        stop_on_error: Whether to stop on first error
    
    Returns:
        Tuple of (success, error_message)
    """
    for cmd in commands:
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.debug(f"Executed: {' '.join(cmd)}")
            if result.stdout:
                logger.debug(f"Output: {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed: {' '.join(cmd)}. Error: {e.stderr}"
            logger.error(error_msg)
            if stop_on_error:
                return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error executing {' '.join(cmd)}: {e}"
            logger.error(error_msg)
            if stop_on_error:
                return False, error_msg
    
    return True, ""
