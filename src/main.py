import argparse
import sys
import subprocess
import requests
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

def main(model=None, list_models=False):
    # Check if Ollama is running
    if not check_ollama_running():
        print("[ERROR] Ollama is not running or not installed. Please start Ollama (see https://ollama.com/) and try again.")
        sys.exit(1)

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
    parser.add_argument("--model", type=str, help="Ollama model to use", default=None)
    parser.add_argument("--list-models", action="store_true", help="List available Ollama models")
    args = parser.parse_args()
    main(model=args.model, list_models=args.list_models)

# Only run the CLI if this file is executed directly (not on import)
if __name__ == "__main__":
    cli_entrypoint()