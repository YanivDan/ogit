import argparse
import sys
import subprocess
import logging
from typing import Optional

import pyperclip

from .ollama_client import OllamaClient, list_ollama_models, check_ollama_health
from .git_utils import (
    get_git_diff, validate_git_repo, get_current_branch, 
    is_branch_protected, execute_git_commands
)
from .editor_utils import prompt_user_to_edit, validate_commit_message
from .config import get_config, save_default_model, load_default_model
from .ui_utils import (
    ProgressSpinner, confirm_action, display_diff_summary,
    print_error, print_warning, print_info, print_success
)
from .constants import (
    OLLAMA_GENERATE_ENDPOINT, ERROR_GIT_NOT_INSTALLED, ERROR_OLLAMA_NOT_RUNNING,
    ERROR_NO_CHANGES, ERROR_NO_MODELS, GIT_ADD_ALL, GIT_COMMIT, GIT_PUSH
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_git_installed() -> bool:
    """
    Check if Git is installed and accessible.
    
    Returns:
        True if Git is installed
    """
    try:
        subprocess.run(
            ["git", "--version"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL, 
            check=True
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def prompt_for_model() -> Optional[str]:
    """
    Prompt user to select a model from available Ollama models.
    
    Returns:
        Selected model name or None if cancelled
    """
    models = list_ollama_models()
    if not models:
        print_error(ERROR_NO_MODELS)
        return None

    print_info("Available Ollama models:")
    for idx, m in enumerate(models, 1):
        print(f"{idx}. {m}")

    while True:
        try:
            choice = input("Select a model number to set as default (or 'q' to quit): ").strip()
            
            if choice.lower() == 'q':
                return None
            
            idx = int(choice) - 1
            if 0 <= idx < len(models):
                selected_model = models[idx]
                if save_default_model(selected_model):
                    print_success(f"Default model set to: {selected_model}")
                    return selected_model
                else:
                    print_error("Failed to save default model")
                    return None
            else:
                print_warning("Invalid selection. Please try again.")
        except (ValueError, KeyboardInterrupt):
            print_warning("Invalid input. Please enter a number or 'q' to quit.")
        except EOFError:
            print("\nOperation cancelled.")
            return None


def handle_git_workflow(commit_message: str, current_branch: str) -> bool:
    """
    Handle the git add, commit, and push workflow.
    
    Args:
        commit_message: Commit message to use
        current_branch: Current git branch
        
    Returns:
        True if successful
    """
    config = get_config()
    
    # Check if branch is protected
    if is_branch_protected(current_branch):
        if not confirm_action(f"Branch '{current_branch}' is protected. Continue anyway?", default=False):
            print_info("Operation cancelled.")
            return False
    
    commands = []
    
    # Add files if auto-add is enabled
    if config.auto_add:
        if confirm_action("Add all changes?", default=True):
            commands.append(GIT_ADD_ALL)
    
    # Commit
    if confirm_action("Commit with this message?", default=True):
        commands.append(GIT_COMMIT + [commit_message])
    else:
        print_info("Commit cancelled.")
        return False
    
    # Push if auto-push is enabled and not a protected branch
    if config.auto_push and not is_branch_protected(current_branch):
        if confirm_action("Push changes to remote?", default=False):
            commands.append(GIT_PUSH)
    elif not is_branch_protected(current_branch):
        if confirm_action("Push changes to remote?", default=False):
            commands.append(GIT_PUSH)
    
    # Execute commands
    if commands:
        success, error = execute_git_commands(commands)
        if success:
            print_success("Git operations completed successfully.")
            return True
        else:
            print_error(f"Git operation failed: {error}")
            return False
    
    return True


def main(
    model: Optional[str] = None,
    list_models: bool = False,
    set_default_model: bool = False,
    copy_to_clipboard: bool = False,
    verbose: bool = False
) -> int:
    """
    Main application logic.
    
    Args:
        model: Specific model to use
        list_models: Whether to list available models
        set_default_model: Whether to set default model
        copy_to_clipboard: Whether to copy message to clipboard
        verbose: Enable verbose logging
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    config = get_config()
    
    # Check prerequisites
    if not check_git_installed():
        print_error(ERROR_GIT_NOT_INSTALLED)
        print_info("Please install Git from https://git-scm.com/downloads")
        return 1

    if not check_ollama_health():
        print_error(ERROR_OLLAMA_NOT_RUNNING)
        print_info("Please start Ollama (see https://ollama.com/)")
        return 1

    # Handle list models command
    if list_models:
        models = list_ollama_models()
        print_info("Available Ollama models:")
        for m in models:
            print(f"- {m}")
        return 0

    # Handle set default model command
    if set_default_model:
        selected_model = prompt_for_model()
        return 0 if selected_model else 1

    # Validate git repository
    repo_valid, error_msg = validate_git_repo()
    if not repo_valid:
        print_error(error_msg)
        return 1

    # Get current branch
    current_branch = get_current_branch()
    if current_branch:
        logger.debug(f"Current branch: {current_branch}")
    
    # Determine model to use
    available_models = list_ollama_models()
    if not available_models:
        print_error(ERROR_NO_MODELS)
        return 1
    
    if model is None:
        model = load_default_model()
        if not model or model not in available_models:
            print_warning("No valid default model found.")
            model = prompt_for_model()
            if not model:
                return 1
    elif model not in available_models:
        print_error(f"Model '{model}' not found in available models.")
        return 1

    # Get git diff
    git_diff = get_git_diff()
    if not git_diff:
        print_info(ERROR_NO_CHANGES)
        return 0

    # Display diff summary
    if config.show_progress:
        display_diff_summary(git_diff)

    # Generate commit message
    spinner_msg = f"Generating commit message using {model}"
    
    if config.show_progress:
        with ProgressSpinner(spinner_msg) as spinner:
            ollama_client = OllamaClient(OLLAMA_GENERATE_ENDPOINT, timeout=config.api_timeout)
            commit_message = ollama_client.get_response({
                "model": model,
                "prompt": f"Generate a concise git commit message for the following diff:\n{git_diff}"
            })
            spinner.stop("✓ Commit message generated")
    else:
        ollama_client = OllamaClient(OLLAMA_GENERATE_ENDPOINT, timeout=config.api_timeout)
        commit_message = ollama_client.get_response({
            "model": model,
            "prompt": f"Generate a concise git commit message for the following diff:\n{git_diff}"
        })

    if not commit_message or commit_message == "No commit message generated.":
        print_error("Failed to generate commit message.")
        return 1

    print("\nGenerated Commit Message:")
    print(f"\n{commit_message}\n")

    # Validate commit message
    is_valid, validation_error = validate_commit_message(commit_message, config.max_commit_length)
    if not is_valid:
        print_warning(f"Commit message validation warning: {validation_error}")

    # Offer to edit the commit message
    if confirm_action("Edit the commit message?", default=False):
        try:
            commit_message = prompt_user_to_edit(commit_message)
            print("\nFinal Commit Message:")
            print(f"\n{commit_message}\n")
        except Exception as e:
            print_warning(f"Failed to open editor: {e}")

    # Copy to clipboard if requested
    if copy_to_clipboard:
        try:
            pyperclip.copy(commit_message)
            print_success("Commit message copied to clipboard!")
        except Exception as e:
            print_warning(f"Could not copy to clipboard: {e}")

    # Handle git workflow
    if current_branch:
        if handle_git_workflow(commit_message, current_branch):
            return 0
        else:
            return 1
    else:
        print_info("Next steps:")
        print("1. git add .")
        print(f"2. git commit -m \"{commit_message}\"")
        print("3. git push")
        return 0


def cli_entrypoint() -> None:
    """
    CLI entry point for the ogit command.
    """
    parser = argparse.ArgumentParser(
        description="Generate git commit messages using Ollama.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  ogit                          # Generate commit message with default model
  ogit --model gemma:2b         # Use specific model
  ogit --copy                   # Copy message to clipboard
  ogit --list-models            # List available models
  ogit --set-default-model      # Set default model
"""
    )
    
    parser.add_argument(
        "--model", 
        type=str, 
        help="Ollama model to use (overrides default)", 
        default=None
    )
    parser.add_argument(
        "--list-models", 
        action="store_true", 
        help="List available Ollama models"
    )
    parser.add_argument(
        "--set-default-model", 
        action="store_true", 
        help="Interactively set the default Ollama model"
    )
    parser.add_argument(
        "--copy", 
        action="store_true", 
        help="Copy the generated commit message to clipboard"
    )
    parser.add_argument(
        "--verbose", 
        "-v", 
        action="store_true", 
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    try:
        exit_code = main(
            model=args.model,
            list_models=args.list_models,
            set_default_model=args.set_default_model,
            copy_to_clipboard=args.copy,
            verbose=args.verbose
        )
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    cli_entrypoint()
