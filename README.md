# ogit - A Git Commit Message Generator using Ollama

## Prerequisites

- **Python 3.7+** must be installed. You can check your version with:
  ```sh
  python3 --version
  ```
- **Ollama** must be installed and running locally. See [Ollama documentation](https://ollama.com/) for installation instructions.

---

## Overview
**ogit** is a Python CLI tool that uses Ollama AI to instantly generate clear, high-quality git commit messages from your code changes. Make your commit history concise and professional—effortlessly.

## Features
- Generates commit messages from git diffs using AI (Ollama).

## Installation & Quick Start
1. **Clone the repo:**
   ```zsh
   git clone https://github.com/YanivDan/ogit.git
   cd ogit
   ```
2. **Run the setup script (recommended):**
   ```zsh
   zsh setup_ogit.sh
   ```
   This will create a virtual environment, install dependencies, and set up the CLI tool for you.

   Or, install manually:
   ```zsh
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```
3. **Activate the environment (if not already active):**
   ```zsh
   source .venv/bin/activate
   ```

## CLI Usage
- Generate a commit message using the current git diff:
  ```zsh
  ogit --model <model>
  ```
- List available Ollama models:
  ```zsh
  ogit --list-models
  ```
- Show help:
  ```zsh
  ogit --help
  ```

- Run inside a git repository with changes.
- The tool will generate a commit message and can auto-commit/push for you.

## Uninstall
To remove the venv and all installed files:
```zsh
rm -rf .venv
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.