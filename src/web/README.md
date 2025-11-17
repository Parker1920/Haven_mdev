# Haven Control Room - Web UI (Static)

This simple static UI is a starting point for the Control Room web dashboard. It uses the FastAPI backend (`src/control_room_api.py`) to interact with the Haven data.

Usage (development):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-web.txt
uvicorn src.control_room_api:app --host 0.0.0.0 --port 8000 --reload
```

Then visit: http://<pi5-ip>:8000/

Features:
- List systems (paginated)
- Create new system (name, region, coords)
- Generate map (calls `Beta_VH_Map` to create `dist/VH-Map.html`)
- View latest map
- Upload photo (via `/api/photos`)
- View basic logs

Notes:
- This is a minimal starting UI. Swap it for a React app or extend functionality as required.
- Ensure the server is run from the repository root so `project_root()` paths resolve correctly.
