#!/bin/bash
# Direct launcher: starts Control Room GUI immediately (no menu)
cd "$(dirname "$0")"

# Try Python 3
if [ -x ".venv/bin/python3" ]; then
  .venv/bin/python3 src/control_room.py &
elif command -v python3 >/dev/null 2>&1; then
  python3 src/control_room.py &
else
  python src/control_room.py &
fi
exit 0
