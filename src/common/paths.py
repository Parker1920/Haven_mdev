from __future__ import annotations
from pathlib import Path
import sys

# Shared path helpers to keep structure stable even if files move

# Determine base directory depending on execution context
FROZEN = getattr(sys, 'frozen', False)
if FROZEN:
    # Running from a bundled EXE (PyInstaller)
    BASE_DIR = Path(sys.executable).parent
else:
    # Running from source; project root is two levels up from this file
    BASE_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BASE_DIR
SRC_DIR = PROJECT_ROOT / "src"
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
# When frozen, treat the EXE folder itself as the distribution/output folder.
DIST_DIR = PROJECT_ROOT if FROZEN else (PROJECT_ROOT / "dist")
PHOTOS_DIR = PROJECT_ROOT / "photos"
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
