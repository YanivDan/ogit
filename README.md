# ogit — AI-Powered Git Commit Message Generator

**ogit** is a terminal-native Git assistant powered by local AI.

It lets you write, explain, and undo commits using natural language - entirely offline using Ollama.

No cloud. No API keys. Just smarter Git from your terminal.

## Features

- 🤖 **AI-generated commit messages** using Ollama models
- 🎯 **Smart diff analysis** - handles both staged and unstaged changes
- 🔧 **Flexible configuration** - model selection, editor preferences, and more
- 📝 **Conventional commits** - follows industry-standard commit formats
- 🛡️ **Branch protection** - prevents accidental pushes to protected branches
- 📋 **Clipboard support** for generated messages
- ✏️ **Inline editing** via your default `$EDITOR`
- 🎨 **Progress indicators** with real-time feedback
- 🔍 **Commit validation** - ensures message quality and format
- 📊 **Diff summaries** - see what's changed at a glance

---

## Installation

### 1. Clone the repo

```zsh
git clone https://github.com/YanivDan/ogit.git
cd ogit
```

### 2. Install via `pipx` (recommended)

If you don't have `pipx` yet:

```zsh
brew install pipx
pipx ensurepath
```

Then install `ogit` globally (from the repo root):

```zsh
pipx install --editable .
```

---

## Prerequisites

- **Python 3.7+** installed  
  _Check with:_ `python3 --version`

- **[Ollama](https://ollama.com/)** installed and running locally  
  _Check with:_ `curl http://localhost:11434/api/tags`

---

## Usage

### Basic Usage

```bash
# Generate commit message with default model
ogit

# Use a specific model
ogit --model gemma:2b

# Copy message to clipboard
ogit --copy

# Enable verbose logging
ogit --verbose
```

### Command-Line Options

| Flag                   | Description                                      |
|------------------------|--------------------------------------------------|
| `--model <name>`       | Use a specific model (overrides default)         |
| `--list-models`        | List available models from Ollama                |
| `--set-default-model`  | Change the default model                         |
| `--copy`               | Copy generated commit message to clipboard       |
| `--verbose, -v`        | Enable verbose logging                           |
| `--help`               | Show help message                                |

### Examples

```bash
# Basic usage - will prompt for model selection if none set
ogit

# Use specific model and copy to clipboard
ogit --model gemma:2b --copy

# List all available models
ogit --list-models

# Set or change default model
ogit --set-default-model

# Debug mode with verbose output
ogit --verbose
```

### Configuration

**ogit** stores configuration in `~/.ogit_config` as JSON. You can customize:

- **default_model**: Your preferred Ollama model
- **editor**: Text editor for message editing (defaults to `$EDITOR`)
- **api_timeout**: API request timeout in seconds
- **auto_add**: Automatically add changes before commit
- **auto_push**: Automatically push after commit
- **show_progress**: Display progress indicators
- **conventional_commits**: Use conventional commit format
- **protected_branches**: List of branches to protect from auto-push
- **max_commit_length**: Maximum length for commit message first line

### Advanced Usage

#### Handling Different Types of Changes

```bash
# ogit automatically detects and handles:
# - Staged changes (git add)
# - Unstaged changes (modified files)
# - Mixed staged and unstaged changes
```

#### Branch Protection

```bash
# ogit protects important branches by default:
# - main, master, develop, staging, production
# 
# You'll be prompted before pushing to protected branches
```

#### Conventional Commits

**ogit** generates commit messages following [Conventional Commits](https://conventionalcommits.org/) format:

```bash
# Examples of generated messages:
feat(auth): add user authentication system
fix(api): resolve timeout issues in user endpoints
docs(readme): update installation instructions
refactor(utils): simplify error handling logic
```

---

## How It Works

1. **🔍 Analyze Changes**: Examines both staged and unstaged git changes
2. **📊 Show Summary**: Displays diff summary with files changed and line counts
3. **🤖 Generate Message**: Sends diff to Ollama with enhanced prompts
4. **✅ Validate**: Checks message format and length
5. **✏️ Edit (Optional)**: Open in your preferred editor with helpful guidelines
6. **🛡️ Safety Check**: Warns about protected branches
7. **🚀 Execute**: Runs git add, commit, and optionally push

### Workflow Examples

#### Simple Workflow
```bash
$ ogit
🔍 Analyzing changes...
✓ Done (took 0.2s)

Changes: +15 -3 lines
Files changed: src/main.py, tests/test_main.py

🤖 Generating commit message using gemma:2b...
✓ Commit message generated (took 2.1s)

Generated Commit Message:

feat(main): add user input validation and error handling

Edit the commit message? [y/N]: n
Add all changes? [Y/n]: y
Commit with this message? [Y/n]: y
Push changes to remote? [y/N]: y

✓ Git operations completed successfully.
```

#### Protected Branch Workflow
```bash
$ ogit
# ... (analysis and generation) ...

⚠️  Branch 'main' is protected. Continue anyway? [y/N]: y
Add all changes? [Y/n]: y
Commit with this message? [Y/n]: y
Push changes to remote? [y/N]: n

✓ Git operations completed successfully.
```

---

## Uninstall

To remove `ogit` installed via `pipx`:

```zsh
pipx uninstall ogit
```

---

## Tips for Better Commit Messages

### 🎯 Make Focused Commits
- **One change per commit**: Each commit should represent a single logical change
- **Stage selectively**: Use `git add <file>` instead of `git add .` for precise control
- **Split large changes**: Break big features into smaller, reviewable commits

### 📝 Writing Style
- **Use imperative mood**: "Add feature" not "Adds feature" or "Added feature"
- **Be concise**: Keep the first line under 50 characters when possible
- **Explain why, not what**: The diff shows what changed, explain why it changed

### 🔧 Configuration Tips
- **Set your editor**: `export EDITOR=vim` (or your preferred editor)
- **Choose fast models**: Smaller models like `gemma:2b` are quicker for simple commits
- **Use larger models**: For complex changes, try `llama3:8b` or `codegemma:7b`

### 📋 Example Quality Diffs

```bash
# Good: Focused change
$ git add src/auth.py
$ ogit
# Result: "feat(auth): add password validation"

# Better: Include tests
$ git add src/auth.py tests/test_auth.py
$ ogit
# Result: "feat(auth): add password validation with tests"
```

---

## Troubleshooting

### Common Issues

#### "Ollama is not running"
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Pull a model if none available
ollama pull gemma:2b
```

#### "Git is not installed"
```bash
# Install Git
# macOS: brew install git
# Ubuntu: sudo apt install git
# Windows: https://git-scm.com/downloads
```

#### "No changes detected"
```bash
# Check git status
git status

# Add changes if needed
git add .

# Or stage specific files
git add src/main.py
```

#### Editor Issues
```bash
# Set your preferred editor
export EDITOR=nano  # or vim, code, etc.

# Or configure in shell profile
echo 'export EDITOR=vim' >> ~/.bashrc
```

### Performance Tips

- **Use smaller models** for faster responses: `gemma:2b`, `phi3:mini`
- **Increase timeout** for complex diffs: edit `~/.ogit_config`
- **Enable progress indicators** to see what's happening

## Contributing

Bug reports and pull requests are welcome on GitHub!

### Development Setup

```bash
# Clone the repository
git clone https://github.com/YanivDan/ogit.git
cd ogit

# Install in development mode
pipx install --editable .

# Run with verbose logging
ogit --verbose
```

### Reporting Issues

When reporting issues, please include:
- Your operating system and version
- Python version (`python --version`)
- Ollama version (`ollama --version`)
- Output with `--verbose` flag
- Steps to reproduce the issue

---

## License

MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v0.1.0
- Initial release with basic commit message generation
- Model selection and configuration
- Editor integration
- Clipboard support

### Recent Improvements
- ✅ Enhanced error handling and logging
- ✅ Type hints throughout codebase
- ✅ Improved git workflow (staged/unstaged changes)
- ✅ Branch protection and commit validation
- ✅ Expanded configuration system
- ✅ Progress indicators and better UX
- ✅ Conventional commit format support
- ✅ Comprehensive documentation
