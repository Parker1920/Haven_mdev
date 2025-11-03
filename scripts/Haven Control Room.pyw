# Launcher: No-console start of Haven Control Room on Windows (scripts version)
# This .pyw file runs without opening a console window.

import sys
import os
import subprocess
from pathlib import Path

# scripts/ -> project root
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src'

# Prefer the project virtual environment's pythonw.exe if available
CANDIDATES = []
venv_pythonw = ROOT / '.venv' / 'Scripts' / 'pythonw.exe'
if venv_pythonw.exists():
    CANDIDATES.append(str(venv_pythonw))

# Python Launcher for Windows (pyw.exe) if available
CANDIDATES.append('pyw')

# System-wide pythonw.exe
CANDIDATES.append('pythonw')
CANDIDATES.append('pythonw.exe')

# Build the command to run control_room.py from the src folder so imports work
cmd_args = ['control_room.py']

# Try the interpreters in order
last_err = None
for interp in CANDIDATES:
    try:
        # Launch detached (no console). pythonw does not create a console by design.
        subprocess.Popen([interp, *cmd_args], cwd=str(SRC))
        break
    except Exception as e:
        last_err = e
else:
    # If we get here, we failed all interpreters; show a Windows message box
    try:
        import ctypes
        msg = (
            "Could not launch Haven Control Room.\n\n"
            "Please ensure Python is installed and dependencies are set up.\n\n"
            f"Details: {last_err}"
        )
        ctypes.windll.user32.MessageBoxW(0, msg, "Haven Control Room", 0x30)
    except Exception:
        pass
