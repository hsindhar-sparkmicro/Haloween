#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
if [[ ! -x .venv/bin/python ]]; then python3 -m venv .venv; fi
if ! .venv/bin/python scripts/check_dependencies.py; then
    if [[ -n "${HALLOWEEN_WHEEL_DIR:-}" ]]; then
        .venv/bin/python -m pip install --no-index --find-links "$HALLOWEEN_WHEEL_DIR" -r requirements.txt
    else
        .venv/bin/python -m pip install --disable-pip-version-check -r requirements.txt
    fi
fi
exec .venv/bin/python -m halloween_hub "$@"
