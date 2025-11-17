# Local development and quick start

This file documents how to start the backend API and SPA locally for development or quick testing without requiring advanced setup.

Prerequisites:
- Python 3.10+ and a virtual environment with dependencies installed (`pip install -r requirements.txt`)
- Node.js and npm if you want the Vite dev server (optional)

Start backend API (recommended):

PowerShell:
```powershell
# From repository root
$env:PYTHONPATH = 'src'
$env:HAVEN_UI_DIR = (Resolve-Path 'Haven-UI').Path
python -m uvicorn src.control_room_api:app --reload --host 0.0.0.0 --port 8000
```

Notes:
- The API serves the SPA assets directly if `Haven-UI/dist` or `Haven-UI/static` is present.
- Visit `http://127.0.0.1:8000/` or `http://127.0.0.1:8000/haven-ui/` to access the app once the API is running.

Start SPA dev server (optional, needs Node/npm):
```powershell
cd Haven-UI
npm install
npm run dev
```

If you don't have Node/npm installed:
- You can still view the SPA if `Haven-UI/dist` is already built (the API will serve it).
- If `Haven-UI/dist` is missing and you can't run the dev server, request a build from another machine or install Node locally.

Quick helper scripts (PowerShell):
- `scripts/start_backend.ps1` — begins the backend API with env vars set.
- `scripts/start_ui_dev.ps1` — runs `npm run dev` (requires npm).
- `scripts/start_server_combo.ps1` — starts backend and UI dev in parallel (if npm available).

Troubleshooting:
- If the `Invoke-RestMethod -Uri http://127.0.0.1:8000/api/status` fails: ensure the backend is started using `start_backend.ps1` and check `Haven-UI/logs/control-room-web.log` for errors.
- If nothing shows in the browser: ensure a firewall isn't blocking port 8000 or HTTP on 0.0.0.0, then check the logs.
