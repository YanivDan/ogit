# ogit - A Git Commit Message Generator using Ollama

## Overview
**ogit** is a Python CLI tool that uses Ollama AI to instantly generate clear, high-quality git commit messages from your code changes. Make your commit history concise and professional—effortlessly.

## Features
- Generates commit messages from git diffs using AI (Ollama).
- Simple command-line interface.

## Installation
1. Clone the repository:
   ```sh
   git clone <repository-url>
   cd ogit
   ```
2. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```
   Or, to create a virtual environment and install:
   ```sh
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## CLI Usage

### Generate a Commit Message with AI
- Generate a commit message using the current git diff:
  ```sh
  ogit commit-msg [--model <model>]
  ```
- List available Ollama models:
  ```sh
  ogit commit-msg --list-models
  ```

For more details on each command and its options, run:
```sh
ogit commit-msg --help
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.