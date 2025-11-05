@echo off
setlocal
REM Direct launcher: starts Control Room GUI immediately (no menu)
cd /d "%~dp0"

:start
REM 1) Prefer local venv (no extra setup once created)
if exist ".venv\Scripts\python.exe" (
  start "" ".venv\Scripts\python.exe" "src\control_room.py"
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
  start "" py -3 "src\control_room.py"
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
  start "" python "src\control_room.py"
  exit /b 0
)

REM 4) No Python found -> run guided setup to install it, then relaunch
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\First Run Setup.ps1" -AutoLaunch
goto :start
