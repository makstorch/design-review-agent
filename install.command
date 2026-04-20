#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "=== Design Review Agent: setup ==="
echo "Project: $ROOT_DIR"

if [ -x ".venv/bin/python" ] && ".venv/bin/python" scripts/check_env.py >/dev/null 2>&1; then
  echo "Environment is already ready."
  ".venv/bin/python" scripts/check_env.py || true
  echo ""
  read -r "?Press Enter to close..."
  exit 0
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "Installing uv (Python manager)..."
  curl -fsSL https://astral.sh/uv/install.sh | sh
fi

if [ -x "$HOME/.local/bin/uv" ]; then
  export PATH="$HOME/.local/bin:$PATH"
fi

echo "Installing Python 3.12 (if needed)..."
uv python install 3.12

echo "Creating virtual environment..."
uv venv .venv --python 3.12

echo "Installing dependencies..."
uv pip install --python .venv/bin/python -r scripts/requirements-all.txt

echo ""
echo "Running environment check..."
".venv/bin/python" scripts/check_env.py

echo ""
echo "Setup complete."
read -r "?Press Enter to close..."
