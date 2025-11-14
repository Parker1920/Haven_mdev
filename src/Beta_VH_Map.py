"""Beta VH Map - Three.js-based interactive 3D star map visualization.

Fully data-driven architecture: reads all object types and properties from data.json
and renders them with professional 3D effects.

Creates two views:
- Galaxy View: Shows region centroids, click to explore
- System View: Shows individual systems within a region

Usage:
    python Beta_VH_Map.py            # generate plot.html and open it
    python Beta_VH_Map.py --out my.html
    python Beta_VH_Map.py --no-open
"""
from __future__ import annotations

import sys
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from common.paths import data_path, logs_dir, dist_dir, project_root

def _setup_logging() -> None:
    """Set up logging with console and file handlers."""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    # File handler
    try:
        log_dir = logs_dir()
        log_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime('%Y-%m-%d')
        fh = RotatingFileHandler(log_dir / f'map-{ts}.log', maxBytes=2_000_000, backupCount=5, encoding='utf-8')
        logging.getLogger().addHandler(fh)
    except Exception:
        # If logging to file fails, continue with console only
        pass

_setup_logging()

import argparse
import json
import math
import shutil
import subprocess
import webbrowser
from typing import List, Optional
from pathlib import Path

import pandas as pd
from typing import Tuple, Dict, Any

# Phase 4: Map Generator integration with database backend
# Ensure project root is in sys.path so config/ can be imported
_proj_root = project_root()
if str(_proj_root) not in sys.path:
    sys.path.insert(0, str(_proj_root))

try:
    # Import from settings_user if user edition is active, else use master settings
    from src.common.paths import IS_USER_EDITION
    
    if IS_USER_EDITION:
        from config.settings_user import (
            USE_DATABASE,
            get_data_provider,
            get_current_backend
        )
        logging.info("[Phase 4] User Edition: Using settings_user configuration")
    else:
        from config.settings import (
            USE_DATABASE,
            get_data_provider,
            get_current_backend
        )
        logging.info("Master Edition: Using settings configuration")

    logging.info("Map Generator database integration enabled")
except ImportError as e:
    # Fallback if database modules not available - map will use JSON directly
    USE_DATABASE = False
    logging.warning(f"Database integration disabled - using JSON fallback: {e}")


# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_FILE = data_path("data.json")


# ============================================================================
# DATA LOADING AND NORMALIZATION (Same as before)
# ============================================================================

def normalize_record(record: dict, region: Optional[str] = None) -> dict:
    """Normalize a system record by mapping legacy field names to standard names."""
    """
    Normalize a system record by mapping legacy field names to standard names.
    Args:
        record: The system or region record as a dict.
        region: Optional region name to override.
    Returns:
        Normalized record dict.
    """
    r = dict(record)
    # Map coordinate fields
    if "x_cords" in r and "x" not in r:
        r["x"] = r.pop("x_cords")
    if "y_cords" in r and "y" not in r:
        r["y"] = r.pop("y_cords")
    if "z_cords" in r and "z" not in r:
        r["z"] = r.pop("z_cords")
    # Map other legacy fields
    if "fauna #" in r and "fauna" not in r:
        r["fauna"] = r.pop("fauna #")
    if "flura #" in r and "flora" not in r:
        r["flora"] = r.pop("flura #")
    if "Sentinel level" in r and "sentinel" not in r:
        r["sentinel"] = r.pop("Sentinel level")
    if "Materials" in r and "materials" not in r:
        r["materials"] = r.pop("Materials")
    if "Base location" in r and "base_location" not in r:
        r["base_location"] = r.pop("Base location")
    # Set defaults
    r.setdefault("id", None)
    r.setdefault("name", r.get("name"))
    r.setdefault("planets", r.get("planets", []))
    # Set region (override if provided)
    if region is not None:
        r["region"] = region
    else:
        r.setdefault("region", r.get("region", "Unknown"))
    return r


def load_systems(path: Path = DATA_FILE) -> pd.DataFrame:
    """
    Load systems from the data file or database, supporting new and legacy formats.
    
    Phase 4: Now supports both JSON and database backends via data provider abstraction.
    Load Test: Also supports direct database file paths (haven_load_test.db)
    
    Args:
        path: Path to data.json file OR database file (.db extension)
    Returns:
        DataFrame of normalized system/region records.
    Raises:
        ValueError: If the JSON format is not supported.
    """
    # Check if path is a database file (.db extension)
    if str(path).endswith('.db'):
        logging.info(f"Loading systems from database file: {path}")
        try:
            from src.common.database import HavenDatabase
            with HavenDatabase(str(path)) as db:
                # Load with planets and moons for map visualization
                systems = db.get_all_systems(include_planets=True)
                records = []
                for system_data in systems:
                    records.append(normalize_record(system_data))
            
            df = pd.DataFrame(records)
            for c in ("id", "name", "x", "y", "z", "region", "fauna", "flora", "sentinel", "materials", "base_location", "planets"):
                if c not in df.columns:
                    df[c] = None
            df["x"] = pd.to_numeric(df["x"], errors="coerce")
            df["y"] = pd.to_numeric(df["y"], errors="coerce")
            df["z"] = pd.to_numeric(df["z"], errors="coerce")
            logging.info(f"Loaded {len(df)} systems from database file (with planets and moons)")
            return df
        except Exception as e:
            logging.error(f"Failed to load from database file: {e}")
            raise
    
    # Phase 4: Check if explicit test data path is provided (not the default DATA_FILE)
    # If a custom path is provided (like TESTING.json), always use that file directly
    # Compare absolute paths to handle both relative and absolute path arguments
    path_resolved = Path(path).resolve()
    data_file_resolved = Path(DATA_FILE).resolve()
    is_custom_path = path_resolved != data_file_resolved
    
    # Try to use data provider first (only if using default production data path)
    if USE_DATABASE and not is_custom_path:
        try:
            provider = get_data_provider()
            backend = get_current_backend()
            logging.info(f"[Phase 4] Loading systems from {backend.upper()} backend")
            
            # Load with planets and moons for map visualization
            systems = provider.get_all_systems(include_planets=True)
            records = []
            for system_data in systems:
                records.append(normalize_record(system_data))
            
            df = pd.DataFrame(records)
            for c in ("id", "name", "x", "y", "z", "region", "fauna", "flora", "sentinel", "materials", "base_location", "planets"):
                if c not in df.columns:
                    df[c] = None
            df["x"] = pd.to_numeric(df["x"], errors="coerce")
            df["y"] = pd.to_numeric(df["y"], errors="coerce")
            df["z"] = pd.to_numeric(df["z"], errors="coerce")
            logging.info(f"[Phase 4] Loaded {len(df)} systems from {backend} backend")
            return df
        except Exception as e:
            logging.warning(f"[Phase 4] Failed to load from data provider, falling back to JSON: {e}")
            # Fall through to JSON loading below
    
    # If custom path provided (test data), log it explicitly
    if is_custom_path:
        logging.info(f"Loading systems from custom data file: {path}")
    
    # Fallback: Load from JSON file directly
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        logging.error(f"Failed to read or parse {path}: {e}")
        raise
    records = []
    # Support formats in order of preference:
    # 1) New container map: { systems: { <systemName>: {name, region, x,y,z, planets: [...] } } }
    # 2) New container map without wrapper: { <systemName>: { ... } }
    # 3) Legacy list wrapper: { _meta, data: [ ... ] }
    # 4) Legacy region map: { <regionName>: [ { ...system... }, ... ] }
    if isinstance(raw, dict) and "systems" in raw and isinstance(raw["systems"], dict):
        for name, item in raw["systems"].items():
            if isinstance(item, dict):
                it = dict(item)
                it.setdefault("name", name)
                records.append(normalize_record(it))
    elif isinstance(raw, dict) and "data" in raw and isinstance(raw["data"], list):
        for item in raw["data"]:
            records.append(normalize_record(item))
    elif isinstance(raw, dict):
        # Heuristic: if values look like system objects (dicts with any of x/y/z/planets), treat as system map
        values = list(raw.values())
        if values and all(isinstance(v, dict) for v in values) and any(
            ("x" in v or "y" in v or "z" in v or "planets" in v) for v in values
        ):
            for name, item in raw.items():
                if name == "_meta" or (isinstance(name, str) and name.startswith("_")):
                    continue
                if isinstance(item, dict):
                    it = dict(item)
                    it.setdefault("name", name)
                    records.append(normalize_record(it))
        else:
            # Assume legacy region map
            for region, items in raw.items():
                for item in items:
                    records.append(normalize_record(item, region=region))
    elif isinstance(raw, list):
        for item in raw:
            records.append(normalize_record(item))
    else:
        logging.error("Unsupported JSON format for systems")
        raise ValueError("Unsupported JSON format for systems")
    df = pd.DataFrame(records)
    for c in ("id", "name", "x", "y", "z", "region", "fauna", "flora", "sentinel", "materials", "base_location", "planets"):
        if c not in df.columns:
            df[c] = None
    df["x"] = pd.to_numeric(df["x"], errors="coerce")
    df["y"] = pd.to_numeric(df["y"], errors="coerce")
    df["z"] = pd.to_numeric(df["z"], errors="coerce")
    logging.info(f"Loaded {len(df)} records from {path}")
    return df


def safe_filename(s: str) -> str:
    return "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in (s or "")).strip().replace(" ", "_")


def cartesian_to_orbital(x: float, y: float, z: float) -> Tuple[float, float, float]:
    """Convert cartesian coordinates to orbital positions.

    Args:
        x: X coordinate
        y: Y coordinate
        z: Z coordinate

    Returns:
        Tuple of (x, y, z) in orbital coordinates
    """
    radius = math.sqrt(x**2 + y**2 + z**2)
    if radius < 0.01:
        return 0.1, 0, 0
    theta = math.atan2(y, x)
    phi = math.acos(z / radius) if radius > 0 else 0
    return (
        radius * math.sin(phi) * math.cos(theta),
        radius * math.sin(phi) * math.sin(theta),
        radius * math.cos(phi)
    )


# ============================================================================
# TEMPLATE AND STATIC FILE MANAGEMENT
# ============================================================================

def load_template() -> str:
    """Load the HTML template from external file.

    Returns:
        HTML template string with placeholders for data injection.
    """
    # Handle both frozen (PyInstaller) and development modes
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle - use _MEIPASS
        base_path = Path(sys._MEIPASS)
        template_path = base_path / 'templates' / 'map_template.html'
    else:
        # Running from source
        template_path = Path(__file__).parent / 'templates' / 'map_template.html'

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    return template_path.read_text(encoding='utf-8')


def copy_static_files(output_dir: Path) -> None:
    """Copy CSS and JavaScript files to the output directory.

    Args:
        output_dir: Destination directory for the generated HTML files.
                   Static files will be copied to output_dir/static/

    Note:
        Uses dirs_exist_ok=True to overwrite existing files without removing
        the directory first. This prevents permission errors if files are
        locked (e.g., by a browser viewing the map).
    """
    src_static = Path(__file__).parent / 'static'
    dest_static = output_dir / 'static'

    if not src_static.exists():
        logging.warning(f"Static source directory not found: {src_static}")
        return

    # Copy files, overwriting if they exist (dirs_exist_ok available in Python 3.8+)
    try:
        shutil.copytree(src_static, dest_static, dirs_exist_ok=True)
        logging.info(f"Copied static files from {src_static} to {dest_static}")
    except Exception as e:
        logging.error(f"Error copying static files: {e}")
        # Try individual file copy as fallback
        try:
            dest_static.mkdir(parents=True, exist_ok=True)
            for src_file in src_static.rglob('*'):
                if src_file.is_file():
                    rel_path = src_file.relative_to(src_static)
                    dest_file = dest_static / rel_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_file, dest_file)
            logging.info(f"Copied static files individually (fallback method)")
        except Exception as e2:
            logging.error(f"Fallback copy also failed: {e2}")


def load_discoveries() -> List[Dict]:
    """
    Load discoveries from the database.
    
    Returns:
        List of discovery dictionaries, empty list if none found or database unavailable
    """
    try:
        if USE_DATABASE:
            try:
                provider = get_data_provider()
                # The provider should have access to get_discoveries through the database
                # For now, we'll access the database directly if available
                from src.common.database import HavenDatabase
                db_path = str(Path(__file__).parent.parent / 'data' / 'VH-Database.db')
                
                with HavenDatabase(db_path) as db:
                    # Get all discoveries (no filter)
                    discoveries = db.get_discoveries(limit=10000)
                    logging.info(f"Loaded {len(discoveries)} discoveries from database")
                    return discoveries
            except Exception as e:
                logging.warning(f"Failed to load discoveries from database: {e}")
                return []
        else:
            logging.debug("Database disabled, no discoveries will be shown")
            return []
    except Exception as e:
        logging.error(f"Error loading discoveries: {e}")
        return []


# Old embedded template removed - now using external files




# ============================================================================
# BUILD FUNCTIONS
# ============================================================================

def prepare_galaxy_systems_data(df: pd.DataFrame) -> List[dict]:
    """Prepare one point per system for Galaxy Overview."""
    items: List[dict] = []
    for _, row in df.iterrows():
        # Skip region metadata entries
        if row.get("type") == "region":
            continue
        try:
            x, y, z = cartesian_to_orbital(
                float(row.get("x", 0) or 0),
                float(row.get("y", 0) or 0),
                float(row.get("z", 0) or 0)
            )
        except Exception:
            x = y = z = 0.0
        item = {
            "type": "system",
            "name": row.get("name"),
            "region": row.get("region"),
            "x": x,
            "y": z,
            "z": y,
        }
        # Include a few fields for hover/detail (even though we navigate on click)
        for key in ("id", "attributes", "planets"):
            val = row.get(key)
            if val is not None:
                item[key] = val
        items.append(item)
    return items

def _angle_from_name(name: str, seed: float = 0.0) -> float:
    import hashlib, math as _m
    if not name:
        return (seed % 1.0) * 2 * _m.pi
    h = hashlib.sha256(name.encode("utf-8")).hexdigest()
    # Take first 8 hex digits to int, normalize 0..1
    v = int(h[:8], 16) / 0xFFFFFFFF
    return (v % 1.0) * 2 * _m.pi

def prepare_single_system_solar(row: dict) -> List[dict]:
    """Prepare planets and moons in a synthetic solar layout for a single system record."""
    data: List[dict] = []
    sys_name = row.get("name", "")
    region = row.get("region", "")
    # Planets may be objects or strings
    planets = row.get("planets") or []
    if planets and isinstance(planets, list) and len(planets) > 0 and isinstance(planets[0], str):
        planets = [{"name": p, "moons": []} for p in planets]
    # Layout params
    base_r = 3.0
    step_r = 2.0
    for i, p in enumerate(planets):
        pname = p.get("name", f"Planet {i+1}")
        r = base_r + i * step_r
        ang = _angle_from_name(f"{sys_name}:{pname}")
        x = r * math.cos(ang)
        z = r * math.sin(ang)
        y = 0.0
        item = {
            "type": "planet",
            "name": pname,
            "region": region,
            "x": x,
            "y": y,
            "z": z,
        }
        # Keep planet attributes for the info panel
        for key, val in p.items():
            if key not in ("x", "y", "z"):
                item[key] = val
        data.append(item)
        
        # Note: Moons are already nested in the planet's "moons" array above.
        # The MoonRenderer class in the HTML template handles rendering them
        # as orbiting objects. We do NOT create separate moon plot points.
        # This prevents duplicate moon visualization (orbiting + standalone).
    return data


def prepare_system_data(df: pd.DataFrame, region_filter: Optional[str] = None) -> List[dict]:
    """Prepare system data for System View - fully data-driven."""
    data = []
    
    # Filter by region if specified
    if region_filter:
        df = df[df["region"] == region_filter]
    
    for _, row in df.iterrows():
        # Skip region metadata entries
        if row.get("type") == "region":
            continue
            
        x, y, z = cartesian_to_orbital(
            float(row.get("x", 0) or 0),
            float(row.get("y", 0) or 0),
            float(row.get("z", 0) or 0)
        )
        
        # Build base item with all fields from JSON (data-driven)
        item = {
            "type": row.get("type", "system"),  # Use type from JSON or default to "system"
            "x": x,
            "y": z,  # Swap y and z for Three.js coordinate system
            "z": y,
        }
        
        # Copy all other fields from the row (data-driven approach)
        for key, value in row.items():
            if key not in ("x", "y", "z", "moons", "space_station", "space_stations"):
                # Handle different value types
                if isinstance(value, (list, dict)):
                    if value:  # Only add non-empty lists/dicts
                        item[key] = value
                elif pd.notna(value):
                    item[key] = value
        
        data.append(item)
        
        # Add moons if present
        moons = row.get("moons")
        if moons and isinstance(moons, list):
            for moon in moons:
                mx, my, mz = cartesian_to_orbital(
                    float(moon.get("x", 0) or 0),
                    float(moon.get("y", 0) or 0),
                    float(moon.get("z", 0) or 0)
                )
                moon_item = {
                    "type": "moon",
                    "x": mx,
                    "y": mz,
                    "z": my,
                }
                # Copy all moon fields
                for key, value in moon.items():
                    if key not in ("x", "y", "z"):
                        moon_item[key] = value
                data.append(moon_item)
        
        # Add space stations (handle both "space_station" singular and "space_stations" plural)
        station = row.get("space_station")
        stations = row.get("space_stations", [])
        
        # Convert singular to list
        if station and isinstance(station, dict):
            stations = [station]
        
        if stations and isinstance(stations, list):
            for station in stations:
                sx, sy, sz = cartesian_to_orbital(
                    float(station.get("x", 0) or 0),
                    float(station.get("y", 0) or 0),
                    float(station.get("z", 0) or 0)
                )
                station_item = {
                    "type": "station",
                    "x": sx,
                    "y": sz,
                    "z": sy,
                    "system": row.get("name")
                }
                # Copy all station fields
                for key, value in station.items():
                    if key not in ("x", "y", "z"):
                        station_item[key] = value
                data.append(station_item)
    
    return data



# ============================================================================
# RENDERING AND EXPORTING
# ============================================================================
def write_galaxy_and_system_views(df: pd.DataFrame, output: Path):
    """Generate Galaxy Overview (one point per system) and System View for each system.

    This function now uses external template files and copies static assets.
    Also includes discoveries from the database if available.
    """
    # Load the HTML template from external file
    template = load_template()

    # Copy static files (CSS, JS) to the output directory
    copy_static_files(output.parent)

    # Load discoveries from database
    discoveries_data = load_discoveries()
    logging.info(f"Including {len(discoveries_data)} discoveries in map generation")

    # Galaxy overview
    galaxy_data = prepare_galaxy_systems_data(df)
    html = template.replace("{{SYSTEMS_DATA}}", json.dumps(galaxy_data, indent=2))
    html = html.replace("{{VIEW_MODE}}", "galaxy")
    html = html.replace("{{REGION_NAME}}", "")
    html = html.replace("{{SYSTEM_META}}", json.dumps({}, indent=2))
    html = html.replace("{{DISCOVERIES_DATA}}", json.dumps(discoveries_data, indent=2))
    output.write_text(html, encoding="utf-8")
    logging.info(f"Wrote Galaxy Overview: {output}")

    # Per-system solar view pages
    for _, row in df.iterrows():
        if row.get("type") == "region":
            continue
        system_name = row.get("name") or "system"
        system_file = output.parent / f"system_{safe_filename(system_name)}.html"
        solar = prepare_single_system_solar(row)

        # System meta for sun panel
        meta = {
            "name": system_name,
            "region": row.get("region"),
            "attributes": row.get("attributes"),
            "x": row.get("x"),
            "y": row.get("y"),
            "z": row.get("z"),
        }

        # Filter discoveries for this system
        system_discoveries = [d for d in discoveries_data if d.get('system_id') == row.get('id')]

        html = template.replace("{{SYSTEMS_DATA}}", json.dumps(solar, indent=2))
        html = html.replace("{{VIEW_MODE}}", "system")
        html = html.replace("{{REGION_NAME}}", system_name)
        html = html.replace("{{SYSTEM_META}}", json.dumps(meta, indent=2))
        html = html.replace("{{DISCOVERIES_DATA}}", json.dumps(system_discoveries, indent=2))
        system_file.write_text(html, encoding="utf-8")
        logging.info(f"Wrote System View for {system_name}: {system_file.name}")



# ============================================================================
# BROWSER UTILITIES
# ============================================================================

def find_msedge() -> Optional[str]:
    candidates = [
        shutil.which("msedge"),
        r"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
        r"C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
    ]
    for c in candidates:
        if c and Path(c).exists():
            return str(c)
    return None


def open_in_edge(path: Path, debug: bool = False) -> bool:
    msedge = find_msedge()
    uri = path.resolve().as_uri()
    if msedge:
        try:
            subprocess.Popen([msedge, "--new-window", uri], shell=False)
            return True
        except Exception as e:
            if debug:
                print("msedge launch failed:", e)
    try:
        webbrowser.open_new(uri)
        return True
    except Exception:
        return False



# ============================================================================
# COMMAND LINE INTERFACE / MAIN ENTRY POINT
# ============================================================================

def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", "-o", default=str(dist_dir() / "VH-Map.html"))
    p.add_argument("--no-open", action="store_true", help="Don't open the output after writing")
    p.add_argument("--debug", action="store_true")
    p.add_argument("--only", nargs="*", help="Only include systems with these names (case-sensitive)")
    p.add_argument("--limit", type=int, help="Limit to first N systems after filtering")
    p.add_argument("--data-file", default=str(DATA_FILE), help="Path to data JSON file (default: data/data.json)")
    args = p.parse_args(argv)

    data_file_path = Path(args.data_file)
    if not data_file_path.exists():
        print("Data file not found:", data_file_path)
        return 1

    df = load_systems(data_file_path)
    # Optional filtering
    if args.only:
        try:
            df = df[df["name"].isin(args.only)]
        except Exception:
            pass
    if args.limit and args.limit > 0:
        df = df.head(args.limit)
    out = Path(args.out)
    # Ensure output directory exists
    out.parent.mkdir(parents=True, exist_ok=True)
    write_galaxy_and_system_views(df, out)

    if not args.no_open:
        opened = open_in_edge(out, debug=args.debug)
        if not opened:
            print("Could not open in Edge; try opening", out)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
