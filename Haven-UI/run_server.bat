@echo off
REM Run the Haven Web UI (Windows batch wrapper) - robust path handling
pushd %~dp0\..
SET REPO_ROOT=%CD%
popd
SET PYTHONPATH=%REPO_ROOT%\src
SET HAVEN_UI_DIR=%~dp0
echo Starting Haven Control Room API with REPO_ROOT=%REPO_ROOT% PYTHONPATH=%PYTHONPATH% HAVEN_UI_DIR=%HAVEN_UI_DIR%

REM Prefer venv python if exists
SET VENV_PY=%REPO_ROOT%\.venv\Scripts\python.exe
IF EXIST %VENV_PY% (
	echo Using venv python: %VENV_PY%
	echo Starting in background, output to Haven-UI\logs\run_server.out.log
	mkdir Haven-UI\logs 2>nul
	start /B "%VENV_PY%" %VENV_PY% -m uvicorn src.control_room_api:app --host 127.0.0.1 --port 8000 > Haven-UI\logs\run_server.out.log 2> Haven-UI\logs\run_server.err.log
) ELSE (
	echo Using system python
	mkdir Haven-UI\logs 2>nul
	start /B "python" python -m uvicorn src.control_room_api:app --host 127.0.0.1 --port 8000 > Haven-UI\logs\run_server.out.log 2> Haven-UI\logs\run_server.err.log
)
