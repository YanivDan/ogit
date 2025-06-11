# ogit — AI-Powered Git Commit Message Generator

**ogit** is a lightweight CLI tool that uses [Ollama](https://ollama.com/) to generate meaningful, concise Git commit messages based on your code changes.

Make your commit history consistent and professional — effortlessly.

---

## Features

- AI-generated commit messages using Ollama models
- Model selection with default config
- Automatically `add`, `commit`, and `push` your changes
- Clipboard support for generated messages
- Inline message editing via your default `$EDITOR`

---

## Installation

### 1. Clone the repo

```zsh
git clone https://github.com/YanivDan/ogit.git
cd ogit
```

### 2. Install via `pipx` (recommended)

If you don’t have `pipx` yet:

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

### Basic usage

```zsh
ogit
```

If no default model is set, `ogit` will prompt you to select one from the available Ollama models and store it for future use.

### Options

| Flag                   | Description                                      |
|------------------------|--------------------------------------------------|
| `--model <name>`       | Use a specific model (overrides default)         |
| `--list-models`        | List available models from Ollama                |
| `--set-default-model`  | Change the default model                         |
| `--copy`               | Copy generated commit message to clipboard       |
| `--help`               | Show help message                                |

### Example

```zsh
ogit --model gemma:2b --copy
```

---

## Output Flow

1. Get `git diff`
2. Send diff to Ollama
3. Generate commit message
4. (Optionally) edit message in `$EDITOR`
5. (Optionally) auto `add`, `commit`, and `push`

---

## Uninstall

To remove `ogit` installed via `pipx`:

```zsh
pipx uninstall ogit
```

---

## Model Tip

The better your diff, the better your message. Use focused commits!

---

## Contributing

Bug reports and pull requests are welcome on GitHub. Please file an issue or open a PR with your suggestion.

---

## License

MIT License — see [`LICENSE`](./LICENSE) for details.
