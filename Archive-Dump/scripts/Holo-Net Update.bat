@echo off
setlocal ENABLEDELAYEDEXPANSION
cd /d "%~dp0.."

REM Check for Git
where git >nul 2>nul
if errorlevel 1 (
  echo Git is not installed or not in PATH. Please install Git from https://git-scm.com/downloads
  pause
  exit /b 1
)

REM Ensure we are inside a Git repo
git rev-parse --is-inside-work-tree >nul 2>nul
if errorlevel 1 (
  echo This folder is not a Git repository. Skipping pull.
  goto :deps
)

REM Check if origin remote exists
git remote get-url origin >nul 2>nul
if errorlevel 1 (
  echo No 'origin' remote configured. Skipping git pull.
  goto :deps
)

REM Fetch and pull latest changes
echo Updating from remote...
git fetch --all
for /f "delims=" %%b in ('git rev-parse --abbrev-ref HEAD') do set BRANCH=%%b
echo On branch !BRANCH! - pulling latest (fast-forward only)...
git pull --ff-only origin !BRANCH!

:deps
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

echo Installing/Updating Python dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r config\requirements.txt

echo Update complete.
pause
exit /b 0

:fail
echo Failed to set up the environment. See logs\setup-errors.log
pause
exit /b 1
