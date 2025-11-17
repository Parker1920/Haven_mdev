<#
Start the Haven Control Room backend API.
Sets required env vars for modules/path and serves the web UI built assets (Haven-UI/dist) from /haven-ui.

Usage (PowerShell):
  .\scripts\start_backend.ps1

Notes:
  - Requires Python 3 and the project venv already set up if you're using one.
  - The command uses `python -m uvicorn src.control_room_api:app --reload --port 8000`.
#>
$ErrorActionPreference = 'Stop'

Write-Host "Setting PYTHONPATH to src and HAVEN_UI_DIR to Haven-UI..."
$env:PYTHONPATH = (Resolve-Path 'src').Path
$env:HAVEN_UI_DIR = (Resolve-Path 'Haven-UI').Path

Write-Host "Starting Haven Control Room API (uvicorn) on 0.0.0.0:8000 ..."
python -m uvicorn src.control_room_api:app --reload --host 0.0.0.0 --port 8000
