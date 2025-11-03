#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v python3 >/dev/null 2>&1; then
  osascript -e 'display alert "Python 3 is required" message "Install Python 3.10+ from python.org and retry."'
  exit 1
fi

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

./.venv/bin/python -m pip install --upgrade pip >/dev/null 2>>logs/setup-errors.log
./.venv/bin/python -m pip install -r config/requirements.txt >/dev/null 2>>logs/setup-errors.log

TS=$(date +"%Y-%m-%d_%H%M")
LOG="logs/run-$TS.log"
echo "Launching Haven System Entry Wizard (logging to $LOG) ..."
./.venv/bin/python src/system_entry_wizard.py >>"$LOG" 2>&1
