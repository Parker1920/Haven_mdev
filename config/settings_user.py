"""
Haven User Edition Configuration Settings

Simplified configuration for the standalone user distribution.
Users work with JSON files only - no database backend.
"""
import os
from pathlib import Path

# ========== USER EDITION CONFIGURATION ==========

# Determine if running as frozen EXE
IS_FROZEN = getattr(__import__('sys'), 'frozen', False)

# ========== DATA BACKEND CONFIGURATION ==========

# USER EDITION: JSON-only mode (no database)
USE_DATABASE = False
AUTO_DETECT_BACKEND = False

# ========== FILE PATHS ==========

if IS_FROZEN:
    # When running as EXE, use the EXE's directory
    import sys
    EXE_DIR = Path(sys.executable).parent
    PROJECT_ROOT = EXE_DIR

    # All user data goes in "files" subdirectory
    FILES_DIR = PROJECT_ROOT / "files"
    FILES_DIR.mkdir(exist_ok=True)

    DATA_DIR = FILES_DIR
    LOG_DIR = FILES_DIR / "logs"
    PHOTOS_DIR = FILES_DIR / "photos"

    # Reference files are bundled in the temp extraction directory (_MEIPASS)
    # PyInstaller extracts bundled files to sys._MEIPASS directory
    if hasattr(sys, '_MEIPASS'):
        # Template files bundled at root of extraction directory
        CLEAN_DATA_PATH = Path(sys._MEIPASS) / "clean_data.json"
        EXAMPLE_DATA_PATH = Path(sys._MEIPASS) / "example_data.json"
    else:
        # Fallback for old PyInstaller versions
        CLEAN_DATA_PATH = PROJECT_ROOT / "clean_data.json"
        EXAMPLE_DATA_PATH = PROJECT_ROOT / "example_data.json"
else:
    # Development mode - use standard paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    LOG_DIR = PROJECT_ROOT / "logs"
    PHOTOS_DIR = PROJECT_ROOT / "photos"
    CLEAN_DATA_PATH = DATA_DIR / "clean_data.json"
    EXAMPLE_DATA_PATH = DATA_DIR / "example_data.json"

# JSON data file (working data)
JSON_DATA_PATH = DATA_DIR / "data.json"

# Database not used in user edition
DATABASE_PATH = None

# Create required directories
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

# Backup directory
BACKUP_DIR = DATA_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

# ========== UI CONFIGURATION ==========

# USER EDITION: Hide database-related features
SHOW_BACKEND_STATUS = False
SHOW_SYSTEM_COUNT = True
ENABLE_BACKEND_TOGGLE = False
ENABLE_DATABASE_STATS = False

# ========== FEATURE FLAGS ==========

# USER EDITION: Simplified feature set
ENABLE_JSON_IMPORT = True  # Users can load JSON files
ENABLE_PROGRESSIVE_MAPS = False
ENABLE_API_SERVER = False

# ========== MAP GENERATION CONFIGURATION ==========

# MAP_OUTPUT_DIR: Directory for generated maps
if IS_FROZEN:
    MAP_OUTPUT_DIR = FILES_DIR / "maps"
else:
    MAP_OUTPUT_DIR = PROJECT_ROOT / "dist"

MAP_OUTPUT_DIR.mkdir(exist_ok=True)

# ========== LOGGING CONFIGURATION ==========

LOG_LEVEL = "INFO"

# ========== IMPORT/EXPORT CONFIGURATION ==========

# Not used in user edition
IMPORT_DIR = None
EXPORT_DIR = None
ALLOW_DUPLICATE_IMPORTS = False

# ========== PERFORMANCE CONFIGURATION ==========

# Pagination not needed for user edition (small datasets)
PAGINATION_DEFAULT = 100
PAGINATION_ENABLED = False
PAGINATION_THRESHOLD = 1000

SPATIAL_QUERY_RADIUS = 50.0
SPATIAL_QUERY_LIMIT = 5000
SEARCH_RESULT_LIMIT = 100

# ========== HELPER FUNCTIONS ==========

def get_current_backend() -> str:
    """Get current data backend type - always JSON for user edition"""
    return 'json'


def get_data_provider():
    """Get configured data provider - always JSON for user edition"""
    from src.common.data_provider import JSONDataProvider
    return JSONDataProvider(json_path=str(JSON_DATA_PATH))


def should_use_pagination(system_count: int) -> bool:
    """Pagination disabled in user edition"""
    return False


def should_use_progressive_maps(system_count: int) -> bool:
    """Progressive maps disabled in user edition"""
    return False


# ========== STARTUP FILE SELECTION ==========

def prompt_initial_data_file():
    """
    Prompt user to choose initial data file on startup.
    Returns the path to load, or None if cancelled.
    """
    import tkinter as tk
    from tkinter import messagebox, simpledialog

    # Create hidden root window
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    root.lift()
    root.focus_force()

    # Check if data.json already exists
    if JSON_DATA_PATH.exists() and JSON_DATA_PATH.stat().st_size > 100:
        # Data file exists - ask if they want to load it or start fresh
        result = messagebox.askyesnocancel(
            "Haven Control Room - Data File Found",
            "An existing data file was found.\n\n"
            "• YES - Continue with existing data\n"
            "• NO - Choose a different file\n"
            "• CANCEL - Exit application"
        )

        if result is None:  # Cancel
            root.destroy()
            return None
        elif result:  # Yes - use existing
            root.destroy()
            return JSON_DATA_PATH
        # else: No - continue to file selection dialog

    # Simple messagebox approach
    response = messagebox.askquestion(
        "Haven Control Room - First Run",
        "Welcome to Haven Control Room!\n\n"
        "Choose your starting data:\n\n"
        "• YES - Start with 3 example systems (recommended)\n"
        "• NO - Start with empty data\n\n"
        "You can load your own file later from the app.",
        icon='question'
    )

    root.destroy()

    if response == 'yes':
        return EXAMPLE_DATA_PATH
    else:
        return CLEAN_DATA_PATH


def initialize_data_file(source_path):
    """
    Initialize data.json from the chosen source file.

    Args:
        source_path: Path to the source JSON file (clean_data.json, example_data.json, or custom)

    Returns:
        True if successful, False otherwise
    """
    import shutil
    import json

    try:
        if source_path is None:
            return False

        source_path = Path(source_path)

        # If source is already data.json, no need to copy
        if source_path.resolve() == JSON_DATA_PATH.resolve():
            return True

        # Verify source file exists and is valid JSON
        if not source_path.exists():
            return False

        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)  # Validate JSON

        # Copy to data.json
        shutil.copy2(source_path, JSON_DATA_PATH)

        return True
    except Exception as e:
        print(f"Error initializing data file: {e}")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("HAVEN USER EDITION CONFIGURATION")
    print("=" * 70)
    print(f"Mode: {'FROZEN EXE' if IS_FROZEN else 'DEVELOPMENT'}")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Data Directory: {DATA_DIR}")
    print(f"JSON Data Path: {JSON_DATA_PATH}")
    print(f"Log Directory: {LOG_DIR}")
    print(f"Photos Directory: {PHOTOS_DIR}")
    print(f"Map Output: {MAP_OUTPUT_DIR}")
    print()
    print(f"Data Backend: JSON ONLY")
    print(f"Database Support: DISABLED")
    print(f"Features: Simplified for end users")
    print("=" * 70)
