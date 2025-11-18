"""
Small FastAPI server wrapping Haven Control Room operations
- CRUD systems via data provider
- Generate map (call Beta_VH_Map.main)
- Serve latest VH-Map.html
- Basic file uploads for photos
- Simple logs endpoint
- WebSocket support

This file is the initial scaffold for the conversion from a CustomTkinter desktop to a browser UI.
"""
from __future__ import annotations

import os
from pathlib import Path as _Path
try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import json
import sys
import asyncio
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from src.common.paths import project_root, data_dir, dist_dir, logs_dir
import sqlite3
import src.common.paths as cp
from pathlib import Path

# Allow this FastAPI app to use a separate data directory (Haven-UI) by setting
# the `HAVEN_UI_DIR` env var. If not set, default to repo `Haven-UI` folder.
# Load .env from Haven-UI if present (dev convenience)
if load_dotenv:
    # Try to load from explicit HAVEN_UI_DIR, else project default
    env_dir = os.environ.get('HAVEN_UI_DIR') or str(project_root() / 'Haven-UI')
    env_path = _Path(env_dir) / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=str(env_path))
        logging.info(f"Loaded .env from: {env_path}")

HAVEN_UI_DIR = os.environ.get('HAVEN_UI_DIR')
if HAVEN_UI_DIR:
    HAVEN_UI_ROOT = Path(HAVEN_UI_DIR)
else:
    HAVEN_UI_ROOT = project_root() / 'Haven-UI'

# Ensure the UI folders exist
HAVEN_UI_ROOT.mkdir(parents=True, exist_ok=True)
(HAVEN_UI_ROOT / 'data').mkdir(exist_ok=True)
(HAVEN_UI_ROOT / 'dist').mkdir(exist_ok=True)
(HAVEN_UI_ROOT / 'photos').mkdir(exist_ok=True)
(HAVEN_UI_ROOT / 'logs').mkdir(exist_ok=True)
try:
    # Override common.paths directories so modules like Beta_VH_Map write into Haven-UI
    cp.DATA_DIR = HAVEN_UI_ROOT / 'data'
    cp.LOGS_DIR = HAVEN_UI_ROOT / 'logs'
    cp.DIST_DIR = HAVEN_UI_ROOT / 'dist'
    cp.PHOTOS_DIR = HAVEN_UI_ROOT / 'photos'
    # Ensure directories exist via cp._ensure_dir
    cp._ensure_dir(cp.DATA_DIR)
    cp._ensure_dir(cp.LOGS_DIR)
    cp._ensure_dir(cp.DIST_DIR)
    cp._ensure_dir(cp.PHOTOS_DIR)
except Exception:
    pass
from src.common.data_provider import get_data_provider
from config.settings import USE_DATABASE
import uuid
import time

app = FastAPI(title="Haven Control Room - Web API")

# Allow CORS from Vite dev server for SPA development
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static UI from `src/web/static` if exists
static_dir = project_root() / 'src' / 'web' / 'static'
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Serve Haven-UI local static bundle when running in standalone mode
ui_dist_dir = HAVEN_UI_ROOT / 'dist'
if ui_dist_dir.exists():
    # Serve built React app from Haven-UI/dist under /haven-ui path to avoid masking API routes
    app.mount('/haven-ui', StaticFiles(directory=str(ui_dist_dir), html=True), name='ui')
    # Also expose assets under both /assets and /haven-ui/assets in case the built index uses absolute paths
    # Mount shared 'assets' if they exist (this is typically used by built SPA)
    assets_dir = ui_dist_dir / 'assets'
    if assets_dir.exists():
        app.mount('/assets', StaticFiles(directory=str(assets_dir)), name='assets')
        app.mount('/haven-ui/assets', StaticFiles(directory=str(assets_dir)), name='ui-assets')
    # Expose map-specific static files under /map/static so VH-Map.html can reference them
    map_static_dir = ui_dist_dir / 'static'
    if map_static_dir.exists():
        app.mount('/map/static', StaticFiles(directory=str(map_static_dir)), name='map-static')
        # Mount the whole dist directory at /map so system-specific pages (system_*.html) are served
        app.mount('/map', StaticFiles(directory=str(ui_dist_dir), html=True), name='map')
else:
    # Fallback: mount the static folder (prebuilt simple pages) under /haven-ui for consistent paths
    ui_static_dir = HAVEN_UI_ROOT / 'static'
    if ui_static_dir.exists():
        app.mount('/haven-ui', StaticFiles(directory=str(ui_static_dir), html=True), name='ui-static')
        # Mount static assets under the same base so CSS/icons load when `dist` is not built
        assets_dir = ui_static_dir / 'assets'
        if assets_dir.exists():
            app.mount('/haven-ui/assets', StaticFiles(directory=str(assets_dir)), name='ui-static-assets')

# Simple index route that redirects to the SPA if present
@app.get('/')
async def index():
    # If built SPA exists, serve its index.html
    if ui_dist_dir.exists():
        return FileResponse(str(ui_dist_dir / 'index.html'))
    # Otherwise, return fallback HTML
    return HTMLResponse("<html><body><h1>Haven Control Room API</h1><p>UI not found. Visit /haven-ui when built.</p></body></html>")

# Serve photos under /haven-ui-photos for convenience
photos_dir = HAVEN_UI_ROOT / 'photos'
if photos_dir.exists():
    app.mount('/haven-ui-photos', StaticFiles(directory=str(photos_dir)), name='haven-ui-photos')

logger = logging.getLogger(__name__)

# Initialize logger for web UI to use Haven-UI logs directory
def _setup_web_logging():
    logger = logging.getLogger()
    if any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
        return  # already configured
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    # File log
    try:
        web_logs = HAVEN_UI_ROOT / 'logs'
        web_logs.mkdir(exist_ok=True)
        fh = RotatingFileHandler(web_logs / 'control-room-web.log', maxBytes=2_000_000, backupCount=5)
        fh.setFormatter(fmt)
        fh.setLevel(logging.INFO)
        logger.addHandler(fh)
    except Exception as e:
        logger.warning(f"Failed to setup web logging: {e}")

_setup_web_logging()

# Setup data provider
provider = None
def get_ui_provider():
    global provider
    if provider:
        return provider
    # Pick storage under Haven-UI/data
    use_db = os.environ.get('HAVEN_UI_USE_DB') == '1' or USE_DATABASE
    json_path = str(HAVEN_UI_ROOT / 'data' / 'data.json')
    db_path = str(HAVEN_UI_ROOT / 'data' / 'haven_ui.db')
    provider = get_data_provider(use_database=use_db, json_path=json_path, db_path=db_path)
    return provider

# Simple in-memory admin session store
# Token -> expiry (epoch seconds)
_admin_sessions: dict[str, float] = {}
_SESSION_TTL = 8 * 60 * 60  # 8 hours


def _is_session_valid(token: str) -> bool:
    if not token:
        return False
    exp = _admin_sessions.get(token)
    if not exp:
        return False
    if time.time() > exp:
        # expired
        _admin_sessions.pop(token, None)
        return False
    return True


def _create_session() -> str:
    token = uuid.uuid4().hex
    _admin_sessions[token] = time.time() + _SESSION_TTL
    return token


def _destroy_session(token: str):
    if token in _admin_sessions:
        _admin_sessions.pop(token, None)


def _require_admin(request: Request):
    """Require admin token if configured via HAVEN_ADMIN_TOKEN environment variable."""
    # 1) Allow login cookie/session
    session_token = request.cookies.get('haven_session_token')
    if session_token and _is_session_valid(session_token):
        return True

    # 2) Allow X-HAVEN-ADMIN header with env token
    token = os.environ.get('HAVEN_ADMIN_TOKEN')
    if token:
        header = request.headers.get('X-HAVEN-ADMIN') or request.headers.get('X-Haven-Admin')
        if header and header == token:
            return True

    # 3) Fallback: if no admin token configured, allow by default but log
    if not token:
        logger.warning('No HAVEN_ADMIN_TOKEN configured; admin-only action allowed')
        return True

    raise HTTPException(status_code=403, detail='Admin token or session required')


def _verify_api_key(request: Request):
    """Verify HAVEN_API_KEY via header X-API-Key if configured; returns True if valid, False otherwise."""
    api_key = os.environ.get('HAVEN_API_KEY')
    if not api_key:
        # If no API key configured, allow by default (use admin token flow)
        return True
    header = request.headers.get('X-API-Key')
    if header and header == api_key:
        return True
    return False


@app.post('/api/admin/login')
async def admin_login(payload: dict, request: Request):
    """Login endpoint for web UI. Expects payload { password: '...' }"""
    try:
        pw = payload.get('password')
        if not pw:
            raise HTTPException(status_code=400, detail='password required')

        env_pw = os.environ.get('HAVEN_ADMIN_PASSWORD')
        if not env_pw:
            # If no password is configured, still check for HAVEN_ADMIN_TOKEN
            if os.environ.get('HAVEN_ADMIN_TOKEN'):
                # allow login if admin token matches provided
                if payload.get('admin_token') == os.environ.get('HAVEN_ADMIN_TOKEN'):
                    token = _create_session()
                    response = { 'status': 'ok' }
                    return { 'status': 'ok', 'token': token }
            raise HTTPException(status_code=500, detail='Admin password not configured on server')

        if pw == env_pw:
            token = _create_session()
            # Set a cookie in response by returning a Set-Cookie header
            from fastapi.responses import JSONResponse
            resp = JSONResponse({'status': 'ok'})
            # Cookie attributes: default to 'lax' to avoid cross-site issues. In development
            # set HAVEN_ALLOW_INSECURE_ADMIN_COOKIE=1 to use SameSite=None (and optionally Secure)
            allow_insecure = os.environ.get('HAVEN_ALLOW_INSECURE_ADMIN_COOKIE') == '1'
            cookie_secure = os.environ.get('HAVEN_ADMIN_COOKIE_SECURE', '') == '1'
            if allow_insecure:
                resp.set_cookie('haven_session_token', token, httponly=True, samesite='none', secure=cookie_secure)
            else:
                resp.set_cookie('haven_session_token', token, httponly=True, samesite='lax', secure=cookie_secure)
            return resp
        raise HTTPException(status_code=403, detail='Invalid password')
    except HTTPException:
        raise
    except Exception as e:
        logger.exception('Login failed')
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/admin/logout')
async def admin_logout(request: Request):
    try:
        session_token = request.cookies.get('haven_session_token')
        if session_token:
            _destroy_session(session_token)
        from fastapi.responses import JSONResponse
        resp = JSONResponse({'status': 'ok'})
        # Delete cookie with same attributes as set (secure/samesite)
        allow_insecure = os.environ.get('HAVEN_ALLOW_INSECURE_ADMIN_COOKIE') == '1'
        cookie_secure = os.environ.get('HAVEN_ADMIN_COOKIE_SECURE', '') == '1'
        if allow_insecure:
            resp.delete_cookie('haven_session_token', samesite='none', secure=cookie_secure)
        else:
            resp.delete_cookie('haven_session_token', samesite='lax', secure=cookie_secure)
        return resp
    except Exception as e:
        logger.exception('Logout failed')
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/admin/status')
async def admin_status(request: Request):
    try:
        session_token = request.cookies.get('haven_session_token')
        if session_token and _is_session_valid(session_token):
            return {'logged_in': True}
        # Or check env token
        if os.environ.get('HAVEN_ADMIN_TOKEN'):
            return { 'logged_in': True }
        return {'logged_in': False}
    except Exception as e:
        logger.exception('Admin status check failed')
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("startup")
async def log_startup_info():
    try:
        logger.info(f"APP STARTUP: HAVEN_UI_ROOT={HAVEN_UI_ROOT}")
        logger.info(f"APP STARTUP: USE_DATABASE={USE_DATABASE}")
        provider = get_ui_provider()
        logger.info(f"APP STARTUP: Provider class: {provider.__class__}")
        db_path = getattr(provider, 'db_path', None)
        logger.info(f"APP STARTUP: Provider DB path: {db_path}")
        # If database provider, inspect tables
        try:
            from sqlite3 import DatabaseError
            if hasattr(provider, 'db_class'):
                dbclass = provider.db_class
                dbpath = provider.db_path
                import sqlite3
                conn = sqlite3.connect(dbpath)
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
                tables = [r[0] for r in cur.fetchall()]
                logger.info(f"APP STARTUP: DB tables: {tables}")
                conn.close()
        except DatabaseError as e:
            logger.warning(f"APP STARTUP: Failed to inspect DB tables: {e}")

        # Log whether the API is running in a frozen EXE or Python (dev) mode
        try:
            import sys as _sys
            if getattr(_sys, 'frozen', False):
                logger.info('APP STARTUP: Running from frozen EXE (packaged).')
            else:
                logger.info('APP STARTUP: Running from Python environment.')
        except Exception:
            pass
    except Exception as e:
        logger.warning(f"APP STARTUP: Unexpected error in startup logging: {e}")


@app.on_event("startup")
async def ensure_settings_file():
    """Ensure that a settings.json exists and includes a default theme."""
    try:
        settings_path = project_root() / 'settings.json'
        if not settings_path.exists():
            default = {
                'theme': {
                    'bg': '#f8fafc',
                    'text': '#111827',
                    'card': '#ffffff',
                    'primary': '#06b6d4'
                }
            }
            settings_path.write_text(json.dumps(default, indent=2), encoding='utf-8')
            logger.info('Created default settings.json')
        else:
            # Ensure theme keys exist
            try:
                s = json.loads(settings_path.read_text(encoding='utf-8'))
                if 'theme' not in s:
                    s['theme'] = {'bg': '#f8fafc', 'text': '#111827', 'card': '#ffffff', 'primary': '#06b6d4'}
                    settings_path.write_text(json.dumps(s, indent=2), encoding='utf-8')
                    logger.info('Added default theme to settings.json')
            except Exception:
                logger.warning('Failed to inspect settings.json for theme; overwriting with default')
                default = {'theme': {'bg': '#f8fafc', 'text': '#111827', 'card': '#ffffff', 'primary': '#06b6d4'}}
                settings_path.write_text(json.dumps(default, indent=2), encoding='utf-8')
    except Exception as e:
        logger.warning(f'Could not ensure settings.json: {e}')

# ------------- Utility functions -------------

def get_vh_map_path():
    # Return the VH-Map path for the UI (use Haven-UI dist to avoid repo data)
    return HAVEN_UI_ROOT / 'dist' / 'VH-Map.html'

# ------------- API Endpoints -------------

@app.get("/api/status")
async def status():
    return {"status": "ok", "use_database": USE_DATABASE}


@app.get('/api/stats')
async def stats():
    provider = get_ui_provider()
    try:
        # Debug log provider info when available
        try:
            logger.info(f"Stats: provider class={provider.__class__}")
            db_path = getattr(provider, 'db_path', None)
            if db_path:
                logger.info(f"Stats: provider.db_path={db_path}")
        except Exception:
            logger.debug("Could not inspect provider for debug info")

        total = provider.get_total_count()
        regions = provider.get_regions()
        return {'total': total, 'regions': regions}
    except Exception as e:
        logger.exception('Failed to get stats')
        # Try a simple recovery: ensure DB schema exists if provider supports it, then retry
        try:
            provider = get_ui_provider()
            if hasattr(provider, 'db_class'):
                dbclass = provider.db_class
                dbpath = provider.db_path
                with dbclass(dbpath) as db:
                    db._ensure_database_exists()
            total = provider.get_total_count()
            regions = provider.get_regions()
            return {'total': total, 'regions': regions}
        except Exception:
            raise HTTPException(status_code=500, detail=str(e))


# Data sources endpoints (archived in web UI)
@app.get('/api/data_sources')
async def list_data_sources():
    return {'sources': {}, 'current': None, 'message': 'Data sources feature is archived in web UI. Use the configured DB.'}


@app.post('/api/data_sources/current')
async def set_current_data_source(payload: dict, request: Request):
    _require_admin(request)
    # This endpoint is intentionally disabled in web deployment
    raise HTTPException(status_code=501, detail='Changing data source is not supported in the web UI')


@app.get('/api/settings')
async def get_settings():
    try:
        settings_path = project_root() / 'settings.json'
        if not settings_path.exists():
            return {}
        settings = json.loads(settings_path.read_text(encoding='utf-8'))

        # If a theme file exists under the repo `themes/` directory, merge its colors
        try:
            theme_path = project_root() / 'themes' / 'haven_theme.json'
            if theme_path.exists():
                theme_json = json.loads(theme_path.read_text(encoding='utf-8'))
                colors = theme_json.get('colors', {})
                # Map theme colors into settings.theme expected keys if not already set
                theme = settings.get('theme', {})
                # Prefer explicit keys in settings, otherwise fill from theme file
                theme.setdefault('bg', colors.get('bg_dark') or colors.get('bg'))
                theme.setdefault('text', colors.get('text_primary') or colors.get('text'))
                theme.setdefault('card', colors.get('bg_card') or colors.get('card'))
                theme.setdefault('primary', colors.get('accent_cyan') or colors.get('accent'))
                settings['theme'] = theme
        except Exception:
            # Non-fatal: return settings even if theme file read fails
            pass

        return settings
    except Exception as e:
        logger.exception('Failed to get settings')
        raise HTTPException(status_code=500, detail=str(e))
@app.post('/api/settings')
async def save_settings(settings: dict, request: Request):
    _require_admin(request)
    try:
        settings_path = project_root() / 'settings.json'
        settings_path.write_text(json.dumps(settings, indent=2), encoding='utf-8')
        return {'status': 'ok'}
    except Exception as e:
        logger.exception('Failed to save settings')
        raise HTTPException(status_code=500, detail=str(e))

# Systems CRUD
@app.get("/api/systems")
async def list_systems(region: str | None = None, page: int = 1, per_page: int = 200):
    try:
        # provider supports pagination in common/data_provider
        provider = get_ui_provider()
        return provider.get_systems_paginated(page=page, per_page=per_page, region=region)
    except Exception as e:
        logger.exception("Failed to list systems")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/systems/{name}")
async def get_system(name: str):
    try:
        provider = get_ui_provider()
        sys = provider.get_system_by_name(name)
        if not sys:
            raise HTTPException(status_code=404, detail="Not found")
        return sys
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to get system")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/systems")
async def create_system(system: dict, request: Request):
    try:
        _require_admin(request)
        provider = get_ui_provider()
        new_id = provider.add_system(system)
        return {"id": new_id}
    except ValueError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.exception("Failed to create system")
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/save_system')
async def save_system(system: dict, request: Request):
    """Save system with validation and id generation similar to desktop wizard's save_system()."""
    try:
        # Validate coords (coerce numeric strings to numbers for tolerance)
        from src.common.validation import validate_system_data, validate_coordinates
        import uuid
        # Coerce coordinate-like fields into numbers so validators receive proper types
        try:
            x = float(system.get('x', 0))
        except Exception:
            x = system.get('x', 0)
        try:
            y = float(system.get('y', 0))
        except Exception:
            y = system.get('y', 0)
        try:
            z = float(system.get('z', 0))
        except Exception:
            z = system.get('z', 0)

        # Update the system dict so schema validation sees numeric types
        system['x'] = x
        system['y'] = y
        system['z'] = z

        is_valid, err = validate_coordinates(x, y, z)
        if not is_valid:
            raise ValueError(f"Invalid coordinates: {err}")

        _require_admin(request)
        provider = get_ui_provider()

        # If id missing, build one
        if 'id' not in system or not system['id']:
            unique_id = uuid.uuid4().hex[:8].upper()
            system['id'] = f"SYS_{system.get('region','').upper().replace(' ','_')}_{unique_id}"

        is_valid, error = validate_system_data(system)
        if not is_valid:
            raise ValueError(f"Validation failed: {error}")

        # If system exists by name or id, update; otherwise create
        try:
            existing = provider.get_system_by_name(system.get('name'))
        except Exception:
            existing = None
        if existing:
            provider.update_system(existing.get('id'), system)
            return {'id': existing.get('id'), 'status': 'updated'}
        else:
            new_id = provider.add_system(system)
            return {'id': new_id, 'status': 'created'}

    except ValueError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception('Failed to save system')
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/systems/{system_id}")
async def update_system(system_id: str, updates: dict, request: Request):
    try:
        _require_admin(request)
        provider = get_ui_provider()
        provider.update_system(system_id, updates)
        return {"status": "ok"}
    except Exception as e:
        logger.exception("Failed to update system")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/systems/{system_id}")
async def delete_system(system_id: str, request: Request):
    try:
        _require_admin(request)
        provider = get_ui_provider()
        provider.delete_system(system_id)
        return {"status": "deleted"}
    except Exception as e:
        logger.exception("Failed to delete system")
        raise HTTPException(status_code=500, detail=str(e))

# File upload for photos
@app.post("/api/photos")
async def upload_photo(file: UploadFile = File(...)):
    try:
        photos_dir = HAVEN_UI_ROOT / 'photos'
        photos_dir.mkdir(exist_ok=True)
        dest = photos_dir / Path(file.filename)
        with open(dest, 'wb') as f:
            f.write(await file.read())
        return {"path": str(dest.relative_to(HAVEN_UI_ROOT))}
    except Exception as e:
        logger.exception("Photo upload failed")
        raise HTTPException(status_code=500, detail=str(e))

# Generate map
@app.post("/api/generate_map")
async def generate_map(background_tasks: BackgroundTasks, noop: bool = False, limit: int | None = None):
    try:
        # Call Beta_VH_Map.main programmatically to generate output
        # Ensure 'src' is on sys.path for module imports when uvicorn runs (module is run with CWD root)
        _project_root = project_root()
        if str(_project_root) not in sys.path:
            sys.path.insert(0, str(_project_root))
        from src.Beta_VH_Map import main as generate_map_main

        argv = ["--no-open"]
        # Prefer database file for map generation (avoids JSON incompatibilities) when it exists
        db_file_ui = HAVEN_UI_ROOT / 'data' / 'haven_ui.db'
        # Use haven_ui.db if present; else look for HAVEN_UI_ROOT/data/data.json; else use canonical DATABASE_PATH
        if db_file_ui.exists():
            data_file_ui = str(db_file_ui)
        else:
            ui_data_json = HAVEN_UI_ROOT / 'data' / 'data.json'
            if ui_data_json.exists():
                data_file_ui = str(ui_data_json)
            else:
                # Fall back to master DB path if it exists
                try:
                    from src.common.paths import database_path
                    main_db = database_path()
                    if Path(main_db).exists():
                        data_file_ui = str(main_db)
                    else:
                        data_file_ui = str(HAVEN_UI_ROOT / 'data' / 'data.json')
                except Exception:
                    data_file_ui = str(HAVEN_UI_ROOT / 'data' / 'data.json')
        out_path = str(HAVEN_UI_ROOT / 'dist' / 'VH-Map.html')
        argv.extend(["--data-file", data_file_ui, "--out", out_path])
        logger.info(f"Queueing map generation with data_file={data_file_ui}, out={out_path}")
        if limit:
            argv.extend(["--limit", str(limit)])
        # Run in background
        def run():
            try:
                generate_map_main(argv)
                # Ensure a 'latest' redirect exists so /map/latest works under static mount
                try:
                    latest_file = HAVEN_UI_ROOT / 'dist' / 'latest'
                    latest_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(latest_file, 'w', encoding='utf-8') as f:
                        f.write('<!doctype html><html><head><meta http-equiv="refresh" content="0; url=VH-Map.html"/></head><body></body></html>')
                except Exception:
                    logger.exception("Failed to write 'latest' redirect file")
                # Write a simple status file that maps UI can poll to know if generation succeeded
                try:
                    status_file = HAVEN_UI_ROOT / 'dist' / 'map_status.json'
                    status = { 'status': 'ok', 'generated_at': time.time(), 'out': out_path }
                    with open(status_file, 'w', encoding='utf-8') as sf:
                        json.dump(status, sf)
                except Exception:
                    logger.exception("Failed to write map_status.json")
            except SystemExit:
                pass
            except Exception:
                logger.exception("Map generation failed")

        background_tasks.add_task(run)
        return {"status": "queued"}
    except Exception as e:
        logger.exception("Failed to queue map generation")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/map/latest")
async def latest_map():
    mpath = HAVEN_UI_ROOT / 'dist' / 'VH-Map.html'
    if not mpath.exists():
        raise HTTPException(status_code=404, detail="Map not found")
    return FileResponse(str(mpath), media_type='text/html')


@app.get('/api/map_status')
async def map_status():
    try:
        mpath = HAVEN_UI_ROOT / 'dist' / 'VH-Map.html'
        status_path = HAVEN_UI_ROOT / 'dist' / 'map_status.json'
        if not mpath.exists():
            return {'generated': False}
        result = { 'generated': True, 'path': str(mpath) }
        try:
            result['mtime'] = mpath.stat().st_mtime
        except Exception:
            pass
        if status_path.exists():
            try:
                content = json.loads(status_path.read_text(encoding='utf-8'))
                result['status_file'] = content
            except Exception:
                pass
        return result
    except Exception as e:
        logger.exception('Failed to get map_status')
        raise HTTPException(status_code=500, detail=str(e))

# Backups
@app.post("/api/backup")
async def backup():
    try:
        from common.vh_database_backup import backup_vh_database
        db_path = HAVEN_UI_ROOT / 'data' / 'haven_ui.db'
        if not db_path.exists():
            raise HTTPException(status_code=404, detail="VH-Database not found")
        backup_path = backup_vh_database(db_path)
        return {"backup_path": str(backup_path)}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Backup failed")
        raise HTTPException(status_code=500, detail=str(e))

# Logs (simple tail endpoint)
@app.get("/api/tests")
async def list_tests():
    try:
        tests_dir = project_root() / 'Program-tests'
        if not tests_dir.exists():
            return { 'tests': [] }
        tests = []
        for root, dirs, files in os.walk(tests_dir):
            for f in files:
                if f.endswith('.py') and f.startswith('test_'):
                    rel = Path(root) / f
                    tests.append(str(rel.relative_to(project_root())))
        return { 'tests': tests }
    except Exception as e:
        logger.exception('Failed to list tests')
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/api/logs')
async def fetch_logs(nlines: int = 200):
    try:
        logs_path = HAVEN_UI_ROOT / 'logs'
        # Pick any control-room log or the dedicated web log
        log_files = list(logs_path.glob('control-room-*.log')) + list(logs_path.glob('control-room-web.log'))
        if not log_files:
            return { 'lines': [] }
        log_files.sort(key=lambda p: p.stat().st_mtime)
        log_file = log_files[-1]
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return { 'file': log_file.name, 'lines': [l.rstrip('\n') for l in lines[-nlines:]] }
    except Exception as e:
        logger.exception('Failed to fetch logs')
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/tests/run')
async def run_test(payload: dict):
    try:
        test_path = payload.get('test_path')
        if not test_path:
            raise ValueError('test_path required')
        # Run pytest against a single file and capture output
        p = subprocess.run(['pytest', '-q', test_path], capture_output=True, text=True)
        return { 'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr }
    except Exception as e:
        logger.exception('Failed to run test')
        raise HTTPException(status_code=500, detail=str(e))
# Old helper logs() removed in favor of explicit endpoints: /api/logs and /api/rtai/history


@app.post('/api/rtai/clear')
async def clear_rtai_history():
    try:
        chat_log = HAVEN_UI_ROOT / 'logs' / 'ai_chat.log'
        if chat_log.exists():
            chat_log.write_text('')
        return {'status': 'cleared'}
    except Exception as e:
        logger.exception('Failed to clear RT AI history')
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/rtai/history')
async def rtai_history(n: int = 200):
    try:
        chat_log = HAVEN_UI_ROOT / 'logs' / 'ai_chat.log'
        if not chat_log.exists():
            return {'messages': []}
        with open(chat_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        msgs = [l.strip() for l in lines[-n:]]
        return {'messages': msgs}
    except Exception as e:
        logger.exception('Failed to read RT AI history')
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/systems/search')
async def search_systems(q: str, limit: int = 50):
    try:
        provider = get_ui_provider()
        results = provider.search_systems(q, limit=limit)
        return {'results': results}
    except Exception as e:
        logger.exception('Search failed')
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket('/ws/logs')
async def websocket_logs(ws: WebSocket):
    await ws.accept()
    try:
        log_path = HAVEN_UI_ROOT / 'logs'
        log_files = list(log_path.glob('control-room-*.log')) + list(log_path.glob('control-room-web.log'))
        if not log_files:
            await ws.send_text('')
            await ws.close()
            return
        log_files.sort(key=lambda p: p.stat().st_mtime)
        file = log_files[-1]
        with open(file, 'r', encoding='utf-8') as f:
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if line:
                    try:
                        await ws.send_text(line.rstrip('\n'))
                    except Exception:
                        break
                else:
                    await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        logger.debug('Websocket client disconnected from /ws/logs')
    except Exception:
        logger.exception('Failed to stream logs')
    finally:
        try:
            await ws.close()
        except Exception:
            pass


@app.websocket('/ws/rtai')
async def websocket_rtai(ws: WebSocket):
    await ws.accept()
    try:
        chat_log = HAVEN_UI_ROOT / 'logs' / 'ai_chat.log'
        if not chat_log.exists():
            await ws.send_text('')
            await ws.close()
            return
        with open(chat_log, 'r', encoding='utf-8') as f:
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if line:
                    try:
                        await ws.send_text(line.rstrip('\n'))
                    except Exception:
                        break
                else:
                    await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        logger.debug('Websocket client disconnected from /ws/rtai')
    except Exception:
        logger.exception('Failed to stream rtai')
    finally:
        try:
            await ws.close()
        except Exception:
            pass


# ==================== ROUND TABLE AI ENDPOINTS ====================

# Lazy initialization of Round Table AI
_rtai_instance = None

def get_rtai():
    """Get or initialize Round Table AI instance."""
    global _rtai_instance
    if _rtai_instance is None:
        try:
            from src.roundtable_ai.api_integration import get_round_table_ai
            _rtai_instance = get_round_table_ai(haven_ui_root=HAVEN_UI_ROOT)
            logger.info("Round Table AI initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Round Table AI: {e}")
            raise
    return _rtai_instance


@app.get('/api/rtai/status')
async def rtai_status():
    """Get Round Table AI system status."""
    try:
        rtai = get_rtai()
        stats = rtai.get_statistics()
        return {
            'status': 'operational',
            'statistics': stats,
            'agents': rtai.list_agents()
        }
    except Exception as e:
        logger.exception('Failed to get RTAI status')
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/rtai/analyze/discoveries')
async def rtai_analyze_discoveries(background_tasks: BackgroundTasks, limit: int = 10):
    """
    Trigger discovery analysis workflow.

    This runs in the background and logs to ai_chat.log.
    """
    try:
        rtai = get_rtai()

        # Run analysis in background
        async def run_analysis():
            try:
                result = await rtai.analyze_discoveries(limit=limit)
                logger.info(f"Discovery analysis complete: {result}")
            except Exception as e:
                logger.error(f"Discovery analysis failed: {e}")

        background_tasks.add_task(run_analysis)

        return {
            'status': 'started',
            'message': f'Analyzing up to {limit} discoveries in background',
            'note': 'Check /api/rtai/history or /ws/rtai for progress'
        }
    except Exception as e:
        logger.exception('Failed to start discovery analysis')
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/rtai/health-report')
async def rtai_health_report(days: int = 7):
    """Get community health report from The Sentinel."""
    try:
        rtai = get_rtai()
        report = await rtai.get_community_health_report(days=days)
        return report
    except Exception as e:
        logger.exception('Failed to get health report')
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/rtai/pattern-report')
async def rtai_pattern_report(days: int = 7):
    """Get pattern analysis report from The Archivist."""
    try:
        rtai = get_rtai()
        report = await rtai.generate_pattern_report(days=days)
        return report
    except Exception as e:
        logger.exception('Failed to get pattern report')
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/rtai/keeper/review')
async def rtai_review_keeper_response(data: dict):
    """
    Have The Lorekeeper review a Keeper bot response.

    Request body:
    {
        "keeper_response": "The response text",
        "discovery": {discovery object}
    }
    """
    try:
        rtai = get_rtai()

        keeper_response = data.get('keeper_response')
        discovery = data.get('discovery')

        if not keeper_response or not discovery:
            raise HTTPException(status_code=400, detail='Missing keeper_response or discovery')

        result = await rtai.review_keeper_response(keeper_response, discovery)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception('Failed to review Keeper response')
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/rtai/keeper/suggest')
async def rtai_suggest_keeper_response(discovery: dict):
    """
    Have The Lorekeeper suggest a Keeper bot response for a discovery.

    Request body: discovery object
    """
    try:
        rtai = get_rtai()
        result = await rtai.suggest_keeper_response(discovery)
        return result
    except Exception as e:
        logger.exception('Failed to suggest Keeper response')
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/dir')
async def list_dir(path: str = 'data'):
    try:
        base = HAVEN_UI_ROOT
        target = (base / path).resolve()
        if base not in target.parents and target != base:
            # Prevent directory traversal
            raise HTTPException(status_code=403, detail='Access denied')
        if not target.exists():
            raise HTTPException(status_code=404, detail='Path not found')
        items = []
        for p in sorted(target.iterdir()):
            items.append({ 'name': p.name, 'is_dir': p.is_dir(), 'size': p.stat().st_size if p.exists() else 0 })
        return { 'path': str(target.relative_to(base)), 'items': items }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception('Failed to list directory')
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/db_stats')
async def db_stats():
    try:
        provider = get_ui_provider()
        if not hasattr(provider, 'db_class'):
            raise HTTPException(status_code=400, detail='Database provider not active')
        from src.common.database import HavenDatabase
        dbpath = provider.db_path
        with HavenDatabase(dbpath) as db:
            stats = db.get_statistics()
        return {'stats': stats}
    except Exception as e:
        logger.exception('Failed to get DB stats')
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/db_upload')
async def upload_db(file: UploadFile = File(...), request: Request = None):
    # Admin only
    _require_admin(request)
    try:
        dest = HAVEN_UI_ROOT / 'data' / 'haven_ui.db'
        backup = dest.with_suffix('.db.bak')
        if dest.exists():
            dest.replace(backup)
        with open(dest, 'wb') as f:
            f.write(await file.read())
        # Reset provider
        global provider
        provider = None
        return {'status': 'ok', 'path': str(dest)}
    except Exception as e:
        logger.exception('DB upload failed')
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/discoveries')
async def list_discoveries(q: str | None = None, system_id: str | None = None, planet_id: int | None = None, moon_id: int | None = None, discovery_type: str | None = None, limit: int = 100):
    try:
        provider = get_ui_provider()
        if not hasattr(provider, 'db_class'):
            raise HTTPException(status_code=400, detail='Database provider not active')
        from src.common.database import HavenDatabase
        dbpath = provider.db_path
        with HavenDatabase(dbpath) as db:
            if q:
                res = db.search_discoveries(q, system_id=system_id, planet_id=planet_id, moon_id=moon_id, discovery_type=discovery_type, limit=limit)
            else:
                res = db.get_discoveries(system_id=system_id, planet_id=planet_id, moon_id=moon_id, discovery_type=discovery_type, limit=limit)
        return {'results': res}
    except Exception as e:
        logger.exception('Failed to list discoveries')
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/discoveries/{id}')
async def get_discovery(id: int):
    try:
        provider = get_ui_provider()
        if not hasattr(provider, 'db_class'):
            raise HTTPException(status_code=400, detail='Database provider not active')
        from src.common.database import HavenDatabase
        dbpath = provider.db_path
        with HavenDatabase(dbpath) as db:
            d = db.get_discovery_by_id(id)
            if not d:
                raise HTTPException(status_code=404, detail='Not found')
            return d
    except HTTPException:
        raise
    except Exception as e:
        logger.exception('Failed to fetch discovery')
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/discoveries', status_code=201)
async def create_discovery(discovery: dict, request: Request):
    """Create a new discovery; supports both bot API key (X-API-Key) and admin token (X-HAVEN-ADMIN)."""
    try:
        # Auth: accept either API key or admin token
        if not _verify_api_key(request):
            _require_admin(request)

        provider = get_ui_provider()
        if not hasattr(provider, 'db_class'):
            raise HTTPException(status_code=400, detail='Database provider not active')
        from src.common.database import HavenDatabase
        dbpath = provider.db_path
        with HavenDatabase(dbpath) as db:
            # Resolve system_id if system_name provided
            system_id = discovery.get('system_id')
            system_name = discovery.get('system_name')
            if system_name and not system_id:
                sys = db.get_system_by_name(system_name)
                if sys:
                    system_id = sys.get('id')

            # Resolve planet_id and moon_id if location_name provided
            planet_id = discovery.get('planet_id')
            moon_id = discovery.get('moon_id')
            location_type = discovery.get('location_type') or 'space'
            location_name = discovery.get('location_name')

            if location_type == 'planet' and location_name and system_id and not planet_id:
                cursor = db.conn.cursor()
                cursor.execute("SELECT id FROM planets WHERE system_id = ? AND name = ?", (system_id, location_name))
                res = cursor.fetchone()
                if res:
                    planet_id = res['id'] if isinstance(res, dict) or isinstance(res, sqlite3.Row) else res[0]

            if location_type == 'moon' and location_name and system_id and not moon_id:
                cursor = db.conn.cursor()
                cursor.execute("""
                    SELECT m.id, m.planet_id
                    FROM moons m
                    JOIN planets p ON m.planet_id = p.id
                    WHERE p.system_id = ? AND m.name = ?
                """, (system_id, location_name))
                res = cursor.fetchone()
                if res:
                    # row could be sqlite3.Row
                    moon_id = res['id'] if isinstance(res, dict) or isinstance(res, sqlite3.Row) else res[0]
                    planet_id = res['planet_id'] if isinstance(res, dict) or isinstance(res, sqlite3.Row) else res[1]

            payload = {
                'discovery_type': discovery.get('type') or discovery.get('discovery_type'),
                'discovery_name': discovery.get('discovery_name'),
                'system_id': system_id,
                'planet_id': planet_id,
                'moon_id': moon_id,
                'location_type': location_type,
                'location_name': location_name,
                'description': discovery.get('description'),
                'coordinates': discovery.get('coordinates'),
                'condition': discovery.get('condition'),
                'time_period': discovery.get('time_period'),
                'significance': discovery.get('significance'),
                'photo_url': discovery.get('photo_url') or discovery.get('evidence_url'),
                'evidence_urls': discovery.get('evidence_urls'),
                'discovered_by': discovery.get('discovered_by') or discovery.get('username'),
                'discord_user_id': discovery.get('discord_user_id') or discovery.get('user_id'),
                'discord_guild_id': discovery.get('discord_guild_id') or discovery.get('guild_id'),
                'pattern_matches': discovery.get('pattern_matches', 0),
                'mystery_tier': discovery.get('mystery_tier', 0),
                'analysis_status': discovery.get('analysis_status', 'pending'),
                'tags': discovery.get('tags'),
                'metadata': discovery.get('metadata')
            }

            # Merge any known extra fields if present (safe; DB add_discovery ignores unknown keys)
            # Historically, add_discovery only expects specific keys; we forward the reduced payload.
            disc_id = db.add_discovery(payload)
            return {'success': True, 'discovery_id': disc_id, 'system_id': system_id, 'planet_id': planet_id, 'moon_id': moon_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception('Failed to create discovery')
        raise HTTPException(status_code=500, detail=str(e))


@app.put('/api/discoveries/{id}')
async def update_discovery(id: int, updates: dict, request: Request):
    try:
        if not _verify_api_key(request):
            _require_admin(request)
        provider = get_ui_provider()
        if not hasattr(provider, 'db_class'):
            raise HTTPException(status_code=400, detail='Database provider not active')
        from src.common.database import HavenDatabase
        dbpath = provider.db_path
        with HavenDatabase(dbpath) as db:
            db.update_discovery(id, updates)
        return {'status': 'ok'}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception('Failed to update discovery')
        raise HTTPException(status_code=500, detail=str(e))


@app.delete('/api/discoveries/{id}')
async def delete_discovery(id: int, request: Request):
    try:
        if not _verify_api_key(request):
            _require_admin(request)
        provider = get_ui_provider()
        if not hasattr(provider, 'db_class'):
            raise HTTPException(status_code=400, detail='Database provider not active')
        from src.common.database import HavenDatabase
        dbpath = provider.db_path
        with HavenDatabase(dbpath) as db:
            db.delete_discovery(id)
        return {'status': 'deleted'}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception('Failed to delete discovery')
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/update_deps')
async def update_deps():
    try:
        # Run pip to update dependencies from the main requirements
        p = subprocess.run(['pip', 'install', '-r', 'requirements.txt'], capture_output=True, text=True)
        return {'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}
    except Exception as e:
        logger.exception('Failed to update dependencies')
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/export_app')
async def export_app():
    try:
        # Export packaging is platform-specific and may require pyinstaller
        # For now, just return a helpful message
        return {'status': 'not_implemented', 'message': 'Packaging via web is not implemented. Use build scripts or run packaging tools manually on target platform.'}
    except Exception as e:
        logger.exception('Failed to export app')
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/sync')
async def run_sync():
    """
    Sync endpoint removed: JSON↔DB synchronization is deprecated in the web-first project.
    This endpoint is retained as a safe stub for backward compatibility and will return
    a helpful message directing users to use the database-only workflows.
    """
    return { 'status': 'deprecated', 'message': 'JSON↔DB sync has been removed. The server now uses database-only workflows.' }

# Root UI
@app.get("/")
async def index():
    # Prefer static site from repository web/static, but if Haven-UI static exists, use that index
    ui_index = project_root() / 'Haven-UI' / 'static' / 'index.html'
    if ui_index.exists():
        return HTMLResponse(content=ui_index.read_text(encoding='utf-8'), status_code=200)
    index_path = static_dir / 'control_room.html' if static_dir.exists() else project_root() / 'README.md'
    if index_path.exists():
        if index_path.suffix.lower() == '.html':
            return HTMLResponse(content=index_path.read_text(encoding='utf-8'), status_code=200)
        else:
            return FileResponse(str(index_path))
    else:
        return {"message": "Control Room Web API. Static UI not found."}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
