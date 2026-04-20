#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "=== Design Review Agent: repair environment ==="
echo "Project: $ROOT_DIR"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found. Installing..."
  curl -fsSL https://astral.sh/uv/install.sh | sh
fi

if [ -x "$HOME/.local/bin/uv" ]; then
  export PATH="$HOME/.local/bin:$PATH"
fi

echo "Ensuring Python 3.12 is available..."
uv python install 3.12

if [ ! -x ".venv/bin/python" ]; then
  echo "Virtual environment not found. Creating new .venv..."
  uv venv .venv --python 3.12
fi

echo "Reinstalling requirements into existing .venv..."
uv pip install --python .venv/bin/python --upgrade -r scripts/requirements-all.txt

echo ""
echo "Running environment check..."
".venv/bin/python" scripts/check_env.py

echo ""
echo "Repair complete."
read -r "?Press Enter to close..."
