"""
Standalone server to run the Haven Control Room web UI using the existing repo back-end.
This works when run from the repository root.

Usage:
    python server.py

It imports the FastAPI `app` from `src.control_room_api` and runs uvicorn.
"""
import os
import sys
from pathlib import Path

# Ensure project root and src in path so imports like 'common' and 'src' work
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
src_dir = REPO_ROOT / 'src'
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Ensure control_room_api picks up the right HAVEN_UI_DIR BEFORE importing it
os.environ['HAVEN_UI_DIR'] = str(REPO_ROOT / 'Haven-UI')
from fastapi.staticfiles import StaticFiles
from src.control_room_api import app
# Mount the photos folder for static serving
photos_dir = REPO_ROOT / 'Haven-UI' / 'photos'
if photos_dir.exists():
    app.mount('/haven-ui-photos', StaticFiles(directory=str(photos_dir)), name='haven-ui-photos')

# Mount the local static folder in Haven-UI under /haven-ui-static for convenience
ui_static_dir = REPO_ROOT / 'Haven-UI' / 'static'
if ui_static_dir.exists():
    # Expose static fallback under /haven-ui (preferred) and /haven-ui-static (legacy)
    app.mount('/haven-ui', StaticFiles(directory=str(ui_static_dir), html=True), name='ui-static')
    app.mount('/haven-ui-static', StaticFiles(directory=str(ui_static_dir)), name='haven-ui-static')
    assets_dir = ui_static_dir / 'assets'
    if assets_dir.exists():
        app.mount('/haven-ui/assets', StaticFiles(directory=str(assets_dir)), name='ui-static-assets')

if __name__ == '__main__':
    import uvicorn
    print("Starting Haven Control Room Web Server on 0.0.0.0:8000")
    uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info')
