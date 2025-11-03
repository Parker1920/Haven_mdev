@echo off
setlocal ENABLEDELAYEDEXPANSION
cd /d "%~dp0.."

where python >nul 2>nul
if errorlevel 1 (
  echo Python is required but was not found in PATH.
  pause
  exit /b 1
)

if not exist .venv (
  python -m venv .venv || goto :fail
)

".venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>>"logs\setup-errors.log"
".venv\Scripts\python.exe" -m pip install -r config\requirements.txt >nul 2>>"logs\setup-errors.log"

set TS=%date:~10,4%-%date:~4,2%-%date:~7,2%_%time:~0,2%%time:~3,2%
set TS=%TS: =0%
set LOG=logs\map-!TS!.log

echo Generating 3D map (logging to %LOG%)...
".venv\Scripts\python.exe" src\Beta_VH_Map.py 1>>"%LOG%" 2>&1
exit /b 0

:fail
echo Failed to set up the environment. See logs\setup-errors.log
pause
exit /b 1
