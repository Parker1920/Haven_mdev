from __future__ import annotations
from pathlib import Path
import sys
import os

# Shared path helpers to keep structure stable even if files move

# Determine base directory depending on execution context
FROZEN = getattr(sys, 'frozen', False)

if FROZEN:
    # Running from a bundled EXE (PyInstaller)
    # PyInstaller sets sys._MEIPASS to the temp folder containing bundled data
    if hasattr(sys, '_MEIPASS'):
        BUNDLE_DIR = Path(sys._MEIPASS)
    else:
        BUNDLE_DIR = Path(sys.executable).parent
    
    BASE_DIR = Path(sys.executable).parent
else:
    # Running from source; project root is two levels up from this file
    BASE_DIR = Path(__file__).resolve().parents[2]
    BUNDLE_DIR = BASE_DIR

PROJECT_ROOT = BASE_DIR
SRC_DIR = PROJECT_ROOT / "src"

# Check if running in user edition mode (set by control_room_user.py)
IS_USER_EDITION = os.environ.get('HAVEN_USER_EDITION') == '1'

if IS_USER_EDITION and FROZEN:
    # User edition in frozen mode: 
    # - Bundled data is in BUNDLE_DIR/data (from PyInstaller)
    # - User files go to files/ subdirectory next to EXE
    FILES_DIR = PROJECT_ROOT / "files"
    DATA_DIR = BUNDLE_DIR / "data"  # Use bundled data from PyInstaller
    LOGS_DIR = FILES_DIR / "logs"
    PHOTOS_DIR = FILES_DIR / "photos"
    DIST_DIR = FILES_DIR / "maps"
elif IS_USER_EDITION:
    # User edition in development mode
    DATA_DIR = PROJECT_ROOT / "data"
    LOGS_DIR = PROJECT_ROOT / "logs"
    PHOTOS_DIR = PROJECT_ROOT / "photos"
    DIST_DIR = PROJECT_ROOT / "dist"
else:
    # Master edition: standard paths
    DATA_DIR = PROJECT_ROOT / "data"
    LOGS_DIR = PROJECT_ROOT / "logs"
    PHOTOS_DIR = PROJECT_ROOT / "photos"
    # When frozen, treat the EXE folder itself as the distribution/output folder.
    DIST_DIR = PROJECT_ROOT if FROZEN else (PROJECT_ROOT / "dist")

CONFIG_DIR = PROJECT_ROOT / "config"
DOCS_DIR = PROJECT_ROOT / "docs"


def _ensure_dir(p: Path) -> Path:
    try:
        p.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    return p


def project_root() -> Path:
    return PROJECT_ROOT


def src_dir() -> Path:
    return SRC_DIR


def data_dir() -> Path:
    return _ensure_dir(DATA_DIR)


def data_path(name: str) -> Path:
    return DATA_DIR / name


def logs_dir() -> Path:
    return _ensure_dir(LOGS_DIR)


def dist_dir() -> Path:
    return _ensure_dir(DIST_DIR)


def photos_dir() -> Path:
    return _ensure_dir(PHOTOS_DIR)


def config_dir() -> Path:
    return CONFIG_DIR


def docs_dir() -> Path:
    return DOCS_DIR
