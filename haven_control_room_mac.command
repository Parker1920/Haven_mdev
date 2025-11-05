#!/bin/bash
# Haven Control Room Launcher - macOS
# Launches the main Control Room GUI with enhanced features:
#   - Centralized theme configuration
#   - Data backup/versioning system
#   - Large dataset optimization
#   - Moon visualization with orbital mechanics
#   - Undo/redo functionality
#   - Magic numbers extracted to constants
#   - Comprehensive docstrings
#
# USAGE: haven_control_room_mac.command [--entry {control|system|map}]
#   (Default is 'control' - opens the main GUI)
#

cd "$(dirname "$0")"

# Create error logs directory if it doesn't exist
mkdir -p logs/error_logs

# Generate timestamp for log file
TIMESTAMP=$(date +"%Y-%m-%d_%H%M%S")
ERROR_LOG="logs/error_logs/control-room-launch-${TIMESTAMP}.log"

# Try Python 3 and capture output
echo "=== Control Room Launch Attempt: $(date) ===" > "$ERROR_LOG"
echo "Working directory: $(pwd)" >> "$ERROR_LOG"
echo "Arguments: $@" >> "$ERROR_LOG"
echo "" >> "$ERROR_LOG"

if [ -x ".venv/bin/python3" ]; then
  echo "Using: .venv/bin/python3" >> "$ERROR_LOG"
  .venv/bin/python3 src/control_room.py "$@" >> "$ERROR_LOG" 2>&1 &
  PYTHON_PID=$!
  echo "Python PID: $PYTHON_PID" >> "$ERROR_LOG"
elif command -v python3 >/dev/null 2>&1; then
  echo "Using: $(which python3)" >> "$ERROR_LOG"
  python3 src/control_room.py "$@" >> "$ERROR_LOG" 2>&1 &
  PYTHON_PID=$!
  echo "Python PID: $PYTHON_PID" >> "$ERROR_LOG"
else
  echo "Using: $(which python)" >> "$ERROR_LOG"
  python src/control_room.py "$@" >> "$ERROR_LOG" 2>&1 &
  PYTHON_PID=$!
  echo "Python PID: $PYTHON_PID" >> "$ERROR_LOG"
fi

echo "" >> "$ERROR_LOG"
echo "Launch script completed at: $(date)" >> "$ERROR_LOG"
exit 0
