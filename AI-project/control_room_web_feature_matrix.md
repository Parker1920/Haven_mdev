# Control Room Web Feature Matrix

This file maps Control Room desktop features to API endpoints and suggested UI components for the web UI.

## Sidebar / Main Actions
- Generate Map
  - Endpoint: POST /api/generate_map
  - UI: Button (with progress/queued status), shows link to/iframe of `dist/VH-Map.html` when finished
  - Backend: invokes `src.Beta_VH_Map.main` with `--no-open`

- System Entry Wizard
  - Endpoints: GET /api/systems, GET /api/systems/{name}, POST /api/systems, PUT /api/systems/{id}, DELETE /api/systems/{id}
  - UI: Multi-step form supporting nested planets & moons
  - Backend: Uses `common.data_provider.get_data_provider()` add/update/delete

- Open Latest Map
  - Endpoint: GET /map/latest
  - UI: Opens in new tab/iframe

- Test Manager
  - Endpoints: GET /api/tests (list), POST /api/tests/{id}/run (execute), GET /api/tests/{id}/results
  - UI: Test discovery, run, view logs & results
  - Backend: Calls `pytest` or existing script

- Data Provider / Backend Toggle
  - Endpoint: GET /api/status to show `use_database:true/false`
  - UI: Switch UI element, not necessarily toggleable without restart

- Backups
  - Endpoint: POST /api/backup
  - UI: Trigger & show last backup list
  - Backend: Calls `common.vh_database_backup.backup_vh_database`

## Settings & Theme
- Endpoints: GET /api/settings, POST /api/settings (save theme and other settings)
- UI: Theme selector & general app settings
- Backend: Uses `SETTINGS_FILE` with read/write

## File Uploads & Photos
- Endpoint: POST /api/photos
- UI: Photo picker in Wizard and System editor
- Backend: Moves file to `photos/` folder and returns relative path

## Logs & Monitoring
- Endpoint: GET /api/logs
- UI: Real-time logs panel; use SSE/WebSocket for streaming when ready

## Round Table AI Chat Monitor
- Endpoint: /api/rtai/chat (logs & messages) -- (future: websockets)
- UI: Chat interface with assistant participants, filters, replay capabilities

## Security & Authentication
- Recommended: Bearer token / API keys / HTTP Basic on Pi; lock down to LAN for early access

## Deployment Notes
- Run app with `uvicorn` on Pi 5: `uvicorn src.control_room_api:app --host 0.0.0.0 --port 8000`
- Use `nginx` as reverse proxy and TLS (optional)
- Use systemd to manage process for always-on behavior

## Front-end Recommendations
- Start with a simple, accessible HTML page (in `src/web/static`) and port to a single-page React/Vue app later
- Use websockets for live logs & chat; fallback to polling for initial version
- Keep form validation consistent with `common.validation` on the server side

---

This matrix should be used as authoritative mapping when implementing or extending the web UI.
