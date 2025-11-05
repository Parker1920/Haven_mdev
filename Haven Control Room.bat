@echo off
setlocal EnableDelayedExpansion
REM Haven Control Room Launcher - Windows
REM Launches the main Control Room GUI with enhanced features:
REM   - Centralized theme configuration
REM   - Data backup/versioning system
REM   - Large dataset optimization
REM   - Moon visualization with orbital mechanics
REM   - Undo/redo functionality
REM   - Magic numbers extracted to constants
REM   - Comprehensive docstrings
REM 
REM USAGE: Haven Control Room.bat [--entry {control|system|map}]
REM   (Default is 'control' - opens the main GUI)
REM
cd /d "%~dp0"

REM Check Python availability
:start
REM 1) Prefer local venv (no extra setup once created)
if exist ".venv\Scripts\python.exe" (
  start "" ".venv\Scripts\python.exe" "src\control_room.py" %*
  exit /b 0
)

REM 2) Try Windows Python launcher (py)
where py >nul 2>&1
if %ERRORLEVEL%==0 (
  py -3 -c "import customtkinter" >nul 2>&1
  if %ERRORLEVEL% NEQ 0 (
    powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\First Run Setup.ps1" -AutoLaunch
    goto :start
  )
  start "" py -3 "src\control_room.py" %*
  exit /b 0
)

REM 3) Try python from PATH
where python >nul 2>&1
if %ERRORLEVEL%==0 (
  python -c "import customtkinter" >nul 2>&1
  if %ERRORLEVEL% NEQ 0 (
    powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\First Run Setup.ps1" -AutoLaunch
    goto :start
  )
  start "" python "src\control_room.py" %*
  exit /b 0
)

REM 4) No Python found -> run guided setup to install it, then relaunch
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\First Run Setup.ps1" -AutoLaunch
goto :start
