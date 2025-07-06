"""Constants used throughout the ogit application."""

# API Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_GENERATE_ENDPOINT = f"{OLLAMA_BASE_URL}/api/generate"
OLLAMA_TAGS_ENDPOINT = f"{OLLAMA_BASE_URL}/api/tags"
OLLAMA_TIMEOUT = 30

# File paths
CONFIG_FILENAME = ".ogit_config"
TEMP_FILE_SUFFIX = ".tmp"

# Default values
DEFAULT_EDITOR = "nano"
DEFAULT_TIMEOUT = 2

# Commit message templates
CONVENTIONAL_COMMIT_TYPES = [
    "feat", "fix", "docs", "style", "refactor", 
    "test", "chore", "perf", "ci", "build"
]

# Git commands
GIT_DIFF_STAGED = ["git", "diff", "--cached"]
GIT_DIFF_UNSTAGED = ["git", "diff"]
GIT_ADD_ALL = ["git", "add", "."]
GIT_COMMIT = ["git", "commit", "-m"]
GIT_PUSH = ["git", "push"]
GIT_STATUS = ["git", "status", "--porcelain"]
GIT_BRANCH = ["git", "branch", "--show-current"]

# Error messages
ERROR_GIT_NOT_INSTALLED = "Git is not installed or not in your PATH."
ERROR_OLLAMA_NOT_RUNNING = "Ollama is not running or not installed."
ERROR_NO_CHANGES = "No changes detected."
ERROR_NO_MODELS = "No models found from Ollama."
ERROR_GIT_DIFF_FAILED = "Failed to retrieve git diff."
ERROR_PROTECTED_BRANCH = "Cannot auto-push to protected branch."

# Protected branches (common patterns)
PROTECTED_BRANCHES = {"main", "master", "develop", "staging", "production"}