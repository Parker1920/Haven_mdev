# Control Room → Web UI Conversion Plan

This document outlines the detailed plan, mapping, and required refactors to convert the current Control Room desktop app (CustomTkinter EXE) to a browser UI hosted on Raspberry Pi 5. It also includes a minimal implementation scaffold (`src/control_room_api.py` + static HTML) as a starting point.

---

## Goals
- Provide a web-based Control Room with the same functionality as the desktop app.
- Host the web server on Raspberry Pi 5 (edge) for local access and orchestration.
- Reuse existing business logic and data providers (JSONDataProvider/HavenDatabase) to keep behavior consistent.
- Use dual-GPU desktop solely for LLM training and heavy compute.

---

## Important Notes
- Many UI elements are tightly coupled to CustomTkinter window code and `messagebox` dialogs; we will not reuse GUI code directly on the server. Instead, call the business logic functions or data provider methods.
- The `System Entry Wizard` has logic for validation and file locking; we'll preserve these via `common` functions and the `data_provider` abstraction.
- Map generation script `Beta_VH_Map.py` is script-based but provides a `main()` function; it can be invoked directly to generate the `dist/VH-Map.html`.

---

## Feature Mapping (Desktop → Web)

1. Sidebar Actions
- Generate Map → POST `/api/generate_map` that runs `Beta_VH_Map.main` with `--no-open` and returns queued status.
- System Entry Wizard → Web page (form) and endpoints to create, update, delete systems using `get_data_provider()` methods.
- Open Latest Map → `/map/latest` endpoint serving the latest `dist/VH-Map.html`.
- Export/Packaging → Endpoint to run packaging scripts (e.g., export PWA) and return artifacts.
- Test Manager → Endpoints to list tests and run them; for UI, call existing scripts with `pytest` or run `Program-tests` as subprocess.
- Backups → POST `/api/backup` to invoke `backup_vh_database`.
- Logs → GET `/api/logs` (or SSE) to tail logs and display them in the web UI.

2. System Entry Wizard
- Use `provider.add_system` and `provider.update_system` in API to persist systems.
- Build a JS-driven form to add planets and nested moons (the front-end must send full payload to the API).
- Use `common.validation` functions server-side to validate inputs.

3. Settings & Theme
- Store and read theme settings from `settings.json` via endpoints and UI.

4. Photos and File Uploads
- Endpoint `/api/photos` to upload photos; store them in `photos/` and return relative path.

5. Test Manager & Scripts
- Web-based test runner that triggers test scripts and returns results; use `pytest` or script runner on the server.

6. Round Table AI & LLM Interaction
- Expose endpoints to trigger Round Table assistant actions and query status.
- Use the Pi 5 to orchestrate assistants, and your dual-GPU desktop for training/inference as appropriate.

---

## Required Code Changes
1. Decouple logic from GUI:
   - Move non-UI logic out to service modules where possible (data CRUD, validation, backups, map generation).
   - Replace GUI `messagebox` interactions with exceptions or API-friendly responses.

2. Create API server:
   - `src/control_room_api.py` (FastAPI as scaffold included in repo)
   - Add authentication and secure endpoints (e.g., token-based authentication).

3. Front-End UI:
   - Minimal HTML (in `src/web/static`) provided. Replace with React or full-featured SPA for better UX in the future.

4. Background Jobs & Task Queue:
   - Use `BackgroundTasks` (FastAPI) or add Celery for more robust job management.

5. WebSocket / SSE logging:
   - Implement efficient server push for real-time logs or chat monitor.

6. Testing & CI:
   - Add unit and integration tests around the server API and core logic.

---

## Deployment on Pi 5
- Install Python 3.10+ and the `requirements-web.txt` list (`fastapi`, `uvicorn`, `python-multipart`), and `llama.cpp`/local LLM stack if needed.
- Start the app with `uvicorn src.control_room_api:app --host 0.0.0.0 --port 8000` or create a systemd service for it.
- Optionally use `nginx` as a reverse proxy to serve static files and forward the API.
- Ensure `project_root` paths referenced by server are accessible (data files, logs, dist files).

---

## Security & Best Practices
- Add authentication (Basic / API token / OAuth2) and enable HTTPS via reverse proxy (TLS offload on `nginx` or `caddy`).
- Restrict access to local network or VPN.
- Use role-based access if multiple users exist.

---

## Future Enhancements
- Build a React or Vue SPA for a more interactive UI.
- Implement role-based access control and user sessions.
- Add real-time Round Table AI chat monitor as a full-screen dashboard with WebSocket streaming.
- Integrate PWA build step to publish a mobile-ready app aligned with the existing PWA outputs.

---

## Example Startup Commands (on Pi 5)

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-web.txt
uvicorn src.control_room_api:app --host 0.0.0.0 --port 8000 --reload
```

---

This plan provides the end-to-end mapping and a practical approach to converting the Control Room app from a desktop GUI to a web UI while reusing as much backend logic as possible. Use the scaffold in `src/control_room_api.py` and the static UI in `src/web/static/control_room.html` as a starting point, then iterate from there to add features and polish.
