#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import sys
from pathlib import Path


REQUIRED_MODULES = ("PIL", "markdown", "fpdf", "numpy")
MIN_PYTHON = (3, 10)


def check_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def run_checks(project_root: Path) -> dict:
    venv_python = project_root / ".venv" / "bin" / "python"
    py_ok = tuple(sys.version_info[:2]) >= MIN_PYTHON
    module_map = {name: check_module(name) for name in REQUIRED_MODULES}
    modules_ok = all(module_map.values())
    venv_ok = venv_python.exists()
    all_ok = py_ok and modules_ok and venv_ok
    return {
        "ok": all_ok,
        "python_ok": py_ok,
        "python_version": platform.python_version(),
        "venv_ok": venv_ok,
        "venv_python": str(venv_python),
        "modules": module_map,
    }


def print_human(result: dict) -> None:
    status = "OK" if result["ok"] else "NOT READY"
    print(f"[design-review] environment: {status}")
    print(f"- python version: {result['python_version']}")
    print(f"- python >= {MIN_PYTHON[0]}.{MIN_PYTHON[1]}: {'yes' if result['python_ok'] else 'no'}")
    print(f"- .venv python exists: {'yes' if result['venv_ok'] else 'no'} ({result['venv_python']})")
    print("- modules:")
    for name, ok in result["modules"].items():
        print(f"  - {name}: {'ok' if ok else 'missing'}")
    if not result["ok"]:
        print("\nRun ./install.command and then re-check.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Design Review Agent local Python environment")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    result = run_checks(project_root)
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print_human(result)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
