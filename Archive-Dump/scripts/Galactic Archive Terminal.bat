@echo off
setlocal ENABLEDELAYEDEXPANSION
cd /d "%~dp0.."

REM Ensure Python exists
where python >nul 2>nul
if errorlevel 1 (
  echo Python is required but was not found in PATH.
  echo Install Python 3.10+ from https://www.python.org/downloads/ and retry.
  pause
  exit /b 1
)

REM Create venv if missing
if not exist .venv (
  echo Creating virtual environment...
  python -m venv .venv || goto :fail
)

echo Upgrading pip and installing requirements...
".venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>>"logs\setup-errors.log"
".venv\Scripts\python.exe" -m pip install -r config\requirements.txt >nul 2>>"logs\setup-errors.log"

REM Run the modern entry app (opens settings, can regenerate map)
set TS=%date:~10,4%-%date:~4,2%-%date:~7,2%_%time:~0,2%%time:~3,2%
set TS=%TS: =0%
set LOG=logs\run-!TS!.log

echo Launching Haven System Entry Wizard (logging to %LOG%)...
".venv\Scripts\python.exe" src\system_entry_wizard.py 1>>"%LOG%" 2>&1
exit /b 0

:fail
echo Failed to set up the environment. See logs\setup-errors.log
pause
exit /b 1
