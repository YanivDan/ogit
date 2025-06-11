#!/bin/zsh
# This script sets up the ogit CLI tool in a virtual environment for seamless use.

set -e

# Create venv if it doesn't exist
if [ ! -d ".venv" ]; then
  echo "[ogit setup] Creating Python virtual environment in .venv..."
  python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate

echo "[ogit setup] Installing/updating pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

echo "[ogit setup] Installing ogit in editable mode..."
pip install -e .

echo "\n[ogit setup] Setup complete!"
echo "To use the ogit CLI tool, activate your environment:"
echo "  source .venv/bin/activate"
echo "Then run:"
echo "  ogit --help"
echo "  ogit --model <model>"
echo "\nYou can now use 'ogit' as a CLI tool in this shell."
