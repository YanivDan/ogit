import argparse
import sys
import subprocess
import requests
import os
from ollama_client import OllamaClient, list_ollama_models
from git_utils import get_git_diff

def check_ollama_running():
    """
    Check if Ollama is running locally.
    """
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            return True
    except Exception:
        pass
    return False

def get_config_path():
    """Return the path to the user's ogit config file."""
    return os.path.expanduser("~/.ogit_config")

def save_default_model(model):
    """Save the default model to the config file."""
    with open(get_config_path(), "w") as f:
        f.write(model.strip() + "\n")

def load_default_model():
    """Load the default model from the config file, or return None if not set."""
    try:
        with open(get_config_path(), "r") as f:
            return f.read().strip()
    except Exception:
        return None

def main(model=None, list_models=False, set_default_model=False):
    # Check if Ollama is running
    if not check_ollama_running():
        print("[ERROR] Ollama is not running or not installed. Please start Ollama (see https://ollama.com/) and try again.")
        sys.exit(1)

    if set_default_model:
        models = list_ollama_models()
        if not models:
            print("No models found from Ollama.")
            return
        print("Available Ollama models:")
        for idx, m in enumerate(models, 1):
            print(f"{idx}. {m}")
        choice = input("Select a model number to set as default: ").strip()
        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(models):
                raise ValueError
            save_default_model(models[idx])
            print(f"Default model set to: {models[idx]}")
        except Exception:
            print("Invalid selection. No changes made.")
        return

    # Retrieve the current git diff
    git_diff = get_git_diff()

    if not git_diff:
        print("No changes detected.")
        return

    # Initialize the Ollama client
    ollama_client = OllamaClient("http://localhost:11434/api/generate")

    if list_models:
        models = list_ollama_models()
        print("Available Ollama models:")
        for m in models:
            print(f"- {m}")
        return

    if not model:
        model = load_default_model()

    # Send the git diff to Ollama and get the commit message
    commit_message = ollama_client.get_response({
        "diff": git_diff,
        "model": model
    })

    # Print the generated commit message
    print("Generated Commit Message:")
    print(commit_message)

    # Ask user to confirm and run git commands
    confirm = input("\nWould you like to automatically add, commit, and push these changes? [y/N]: ").strip().lower()
    if confirm == 'y':
        import subprocess
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            subprocess.run(["git", "push"], check=True)
            print("\nChanges have been added, committed, and pushed.")
        except subprocess.CalledProcessError as e:
            print(f"\nError running git command: {e}")
    else:
        print("\nNext steps:")
        print("1. git add .")
        print("2. git commit -m \"<use the generated message above>\"")
        print("3. git push")

def cli_entrypoint():
    parser = argparse.ArgumentParser(description="Generate git commit messages using Ollama.")
    parser.add_argument("--model", type=str, help="Ollama model to use (overrides default)", default=None)
    parser.add_argument("--list-models", action="store_true", help="List available Ollama models")
    parser.add_argument("--set-default-model", action="store_true", help="Interactively set the default Ollama model")
    args = parser.parse_args()
    main(model=args.model, list_models=args.list_models, set_default_model=args.set_default_model)

# Only run the CLI if this file is executed directly (not on import)
if __name__ == "__main__":
    cli_entrypoint()