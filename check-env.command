#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "=== Design Review Agent: environment check ==="
echo "Project: $ROOT_DIR"
echo ""

if [ -x ".venv/bin/python" ]; then
  ".venv/bin/python" scripts/check_env.py || true
else
  if command -v python3 >/dev/null 2>&1; then
    python3 scripts/check_env.py || true
  else
    echo "Python3 not found."
  fi
fi

echo ""
echo "If NOT READY: run ./install.command"
read -r "?Press Enter to close..."
