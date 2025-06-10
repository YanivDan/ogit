# ogit - A Git Commit Message Generator using Ollama

## Overview
ogit is a Python tool that communicates with the Ollama service to generate meaningful git commit messages based on the current git diffs. This project aims to streamline the commit process by providing users with well-structured commit messages, enhancing the clarity and quality of version control history.

## Features
- Generates commit messages from git diffs using AI (Ollama).
- Simple command-line interface.

## Project Structure
```
ogit/
├── src/
│   ├── main.py          # Entry point of the application
│   ├── ollama_client.py # Handles communication with the Ollama service
│   ├── git_utils.py     # Utility function for retrieving git diff
│   └── __init__.py      # Marks the directory as a Python package
├── requirements.txt      # Lists project dependencies
└── README.md             # Project documentation
```

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