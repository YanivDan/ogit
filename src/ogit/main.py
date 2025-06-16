import argparse
import sys
import subprocess
import requests
import os
import pyperclip

from ogit.ollama_client import OllamaClient, list_ollama_models
from ogit.git_utils import get_git_diff
from ogit.editor_utils import prompt_user_to_edit

def check_ollama_running():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except Exception:
        return False

def get_config_path():
    return os.path.expanduser("~/.ogit_config")

def save_default_model(model):
    with open(get_config_path(), "w") as f:
        f.write(model.strip() + "\n")

def load_default_model():
    try:
        with open(get_config_path(), "r") as f:
            return f.read().strip()
    except Exception:
        return None

def prompt_for_model():
    models = list_ollama_models()
    if not models:
        print("[ERROR] No models found from Ollama.")
        sys.exit(1)

    print("Available Ollama models:")
    for idx, m in enumerate(models, 1):
        print(f"{idx}. {m}")

    while True:
        choice = input("Select a model number to set as default: ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(models):
                selected_model = models[idx]
                save_default_model(selected_model)
                print(f"Default model set to: {selected_model}")
                return selected_model
            else:
                raise ValueError
        except Exception:
            print("Invalid selection. Please try again.")

def check_git_installed():
    try:
        subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def main(model=None, list_models=False, set_default_model=False, copy_to_clipboard=False):
    if not check_git_installed():
        print("[ERROR] Git is not installed or not in your PATH.")
        print("Please install Git from https://git-scm.com/downloads and try again.")
        sys.exit(1)

    if not check_ollama_running():
        print("[ERROR] Ollama is not running or not installed. Please start Ollama (see https://ollama.com/) and try again.")
        sys.exit(1)

    if list_models:
        models = list_ollama_models()
        print("Available Ollama models:")
        for m in models:
            print(f"- {m}")
        return

    models = list_ollama_models()

    if set_default_model:
        model = prompt_for_model()
    elif model is not None:
        # use model provided via CLI option
        if model not in models:
            print(f"[WARN] Specified model '{model}' not found in available models.")
        # nothing else to do, CLI-specified model overrides defaults
    else:
        default_model = load_default_model()
        if not default_model or default_model not in models:
            model = prompt_for_model()
        else:
            model = default_model

    git_diff = get_git_diff()
    if not git_diff:
        print("No changes detected.")
        return

    ollama_client = OllamaClient("http://localhost:11434/api/generate")
    commit_message = ollama_client.get_response({
        "model": model,
        "prompt": f"Generate a concise git commit message for the following diff:\n{git_diff}"
    })

    print("\nGenerated Commit Message:")
    print(commit_message or "[No commit message returned by the model]")

    edit = input("Would you like to edit the commit message before proceeding? [y/N]: ").strip().lower()
    if edit == "y":
        try:
            commit_message = prompt_user_to_edit(commit_message)
        except Exception as e:
            print(f"[WARN] Failed to open editor. Continuing with original message. Error: {e}")

    if copy_to_clipboard:
        try:
            pyperclip.copy(commit_message)
            print("Commit message copied to clipboard!")
        except Exception as e:
            print(f"[WARN] Could not copy to clipboard: {e}")

    confirm = input("\nWould you like to automatically add, commit, and push these changes? [y/N]: ").strip().lower()
    if confirm == 'y':
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
        print(f"2. git commit -m \"{commit_message}\"")
        print("3. git push")

def cli_entrypoint():
    parser = argparse.ArgumentParser(description="Generate git commit messages using Ollama.")
    parser.add_argument("--model", type=str, help="Ollama model to use (overrides default)", default=None)
    parser.add_argument("--list-models", action="store_true", help="List available Ollama models")
    parser.add_argument("--set-default-model", action="store_true", help="Interactively set the default Ollama model")
    parser.add_argument("--copy", action="store_true", help="Copy the generated commit message to clipboard")
    args = parser.parse_args()
    main(
        model=args.model,
        list_models=args.list_models,
        set_default_model=args.set_default_model,
        copy_to_clipboard=args.copy
    )

if __name__ == "__main__":
    cli_entrypoint()
