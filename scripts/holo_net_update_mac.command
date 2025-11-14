#!/bin/bash
cd "$(dirname "$0")/.."

set -e

# Check for git
if ! command -v git >/dev/null 2>&1; then
  echo "Git is not installed. Please install from https://git-scm.com/downloads"
  exit 1
fi

# If in git repo and origin exists, pull
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if git remote get-url origin >/dev/null 2>&1; then
    echo "Updating from remote..."
    git fetch --all
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    echo "On branch $BRANCH - pulling latest (fast-forward only)..."
    git pull --ff-only origin "$BRANCH"
  else
    echo "No 'origin' remote configured. Skipping git pull."
  fi
else
  echo "Not a git repository. Skipping pull."
fi

# Ensure venv
if [ ! -d .venv ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

# Install deps
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r config/requirements.txt

echo "Update complete."
