"""
Haven Configuration Settings

Central configuration file for the Haven Master system.
Controls data backend (JSON vs Database) and other system-wide settings.
"""
import os
from pathlib import Path

# ========== DATA BACKEND CONFIGURATION ==========

# USE_DATABASE: Controls which data backend to use
# - False: Use JSON files (data/data.json) - Default for testing phase
# - True: Use SQLite database (data/haven.db) - For production after testing
#
# IMPORTANT: After Phase 1 testing is complete and verified,
# this will be changed to True to make database the default.
USE_DATABASE = True  # Changed to True for Phase 2 testing

# AUTO_DETECT_BACKEND: If True, automatically choose backend based on dataset size
# - Systems < 1,000: Use JSON (faster for small datasets)
# - Systems >= 1,000: Use Database (required for large datasets)
AUTO_DETECT_BACKEND = False  # Set to True for intelligent backend selection

# BACKEND_THRESHOLD: System count threshold for auto-detection
BACKEND_THRESHOLD = 1000

# ========== FILE PATHS ==========

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directory
DATA_DIR = PROJECT_ROOT / "data"

# JSON data file (for JSON backend or EXE exports)
JSON_DATA_PATH = DATA_DIR / "data.json"

# SQLite database file (for database backend)
DATABASE_PATH = DATA_DIR / "haven.db"

# Backup directory
BACKUP_DIR = DATA_DIR / "backups"

# ========== DATABASE CONFIGURATION ==========

# PAGINATION_DEFAULT: Default number of systems per page in Control Room
PAGINATION_DEFAULT = 100

# PAGINATION_ENABLED: Enable pagination in Control Room
# Auto-enables when system count > PAGINATION_THRESHOLD
PAGINATION_ENABLED = True

# PAGINATION_THRESHOLD: Auto-enable pagination above this system count
PAGINATION_THRESHOLD = 100

# ========== MAP GENERATION CONFIGURATION ==========

# MAP_PROGRESSIVE_THRESHOLD: Use progressive loading for maps above this size
# - Systems < threshold: Generate static maps (embed all data)
# - Systems >= threshold: Generate progressive maps (load via API)
MAP_PROGRESSIVE_THRESHOLD = 1000

# MAP_OUTPUT_DIR: Directory for generated maps
MAP_OUTPUT_DIR = PROJECT_ROOT / "dist"

# ========== LOGGING CONFIGURATION ==========

# LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = "INFO"

# LOG_DIR: Directory for log files
LOG_DIR = PROJECT_ROOT / "logs"

# ========== IMPORT/EXPORT CONFIGURATION ==========

# IMPORT_DIR: Directory for importing JSON exports from public EXE version
IMPORT_DIR = DATA_DIR / "imports"

# EXPORT_DIR: Directory for exporting data
EXPORT_DIR = DATA_DIR / "exports"

# ALLOW_DUPLICATE_IMPORTS: Allow importing systems that already exist
# - False: Skip duplicate systems during import
# - True: Update existing systems with imported data
ALLOW_DUPLICATE_IMPORTS = False

# ========== PERFORMANCE CONFIGURATION ==========

# SPATIAL_QUERY_RADIUS: Default radius for spatial queries (in coordinate units)
SPATIAL_QUERY_RADIUS = 50.0

# SPATIAL_QUERY_LIMIT: Maximum systems to return from spatial queries
SPATIAL_QUERY_LIMIT = 5000

# SEARCH_RESULT_LIMIT: Maximum search results to display
SEARCH_RESULT_LIMIT = 100

# ========== UI CONFIGURATION ==========

# SHOW_BACKEND_STATUS: Show current data backend in Control Room status bar
SHOW_BACKEND_STATUS = True

# SHOW_SYSTEM_COUNT: Show system count in Control Room status bar
SHOW_SYSTEM_COUNT = True

# ENABLE_BACKEND_TOGGLE: Allow users to toggle between JSON/Database in UI
ENABLE_BACKEND_TOGGLE = True  # For testing; set to False in production

# ========== FEATURE FLAGS ==========

# ENABLE_DATABASE_STATS: Show database statistics in Control Room
ENABLE_DATABASE_STATS = True

# ENABLE_JSON_IMPORT: Enable JSON import tool in Control Room
ENABLE_JSON_IMPORT = True

# ENABLE_PROGRESSIVE_MAPS: Enable progressive map generation
ENABLE_PROGRESSIVE_MAPS = False  # Will enable in Phase 5 (API server)

# ENABLE_API_SERVER: Enable API server for progressive maps
ENABLE_API_SERVER = False  # Will enable in Phase 5

# ========== VALIDATION ==========

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
IMPORT_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
MAP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ========== HELPER FUNCTIONS ==========

def get_current_backend() -> str:
    """
    Get current data backend type

    Returns:
        'database' or 'json'
    """
    if AUTO_DETECT_BACKEND:
        # Auto-detect based on dataset size
        from src.common.data_provider import auto_detect_provider
        provider = auto_detect_provider(
            json_path=str(JSON_DATA_PATH),
            db_path=str(DATABASE_PATH),
            threshold=BACKEND_THRESHOLD
        )
        return 'database' if 'Database' in provider.__class__.__name__ else 'json'
    else:
        return 'database' if USE_DATABASE else 'json'


def get_data_provider():
    """
    Get configured data provider

    Returns:
        DataProvider instance (JSON or Database)
    """
    from src.common.data_provider import get_data_provider, auto_detect_provider

    if AUTO_DETECT_BACKEND:
        return auto_detect_provider(
            json_path=str(JSON_DATA_PATH),
            db_path=str(DATABASE_PATH),
            threshold=BACKEND_THRESHOLD
        )
    else:
        return get_data_provider(
            use_database=USE_DATABASE,
            json_path=str(JSON_DATA_PATH),
            db_path=str(DATABASE_PATH)
        )


def should_use_pagination(system_count: int) -> bool:
    """
    Determine if pagination should be used

    Args:
        system_count: Total number of systems

    Returns:
        True if pagination should be enabled
    """
    if not PAGINATION_ENABLED:
        return False
    return system_count >= PAGINATION_THRESHOLD


def should_use_progressive_maps(system_count: int) -> bool:
    """
    Determine if progressive maps should be used

    Args:
        system_count: Total number of systems

    Returns:
        True if progressive maps should be used
    """
    if not ENABLE_PROGRESSIVE_MAPS:
        return False
    return system_count >= MAP_PROGRESSIVE_THRESHOLD


# ========== CONFIGURATION SUMMARY ==========

def print_configuration():
    """Print current configuration (for debugging)"""
    print("=" * 70)
    print("HAVEN CONFIGURATION")
    print("=" * 70)
    print(f"Data Backend: {get_current_backend().upper()}")
    print(f"  USE_DATABASE: {USE_DATABASE}")
    print(f"  AUTO_DETECT_BACKEND: {AUTO_DETECT_BACKEND}")
    print(f"  JSON Path: {JSON_DATA_PATH}")
    print(f"  Database Path: {DATABASE_PATH}")
    print()
    print(f"Pagination: {'ENABLED' if PAGINATION_ENABLED else 'DISABLED'}")
    print(f"  Threshold: {PAGINATION_THRESHOLD} systems")
    print(f"  Default per page: {PAGINATION_DEFAULT}")
    print()
    print(f"Progressive Maps: {'ENABLED' if ENABLE_PROGRESSIVE_MAPS else 'DISABLED'}")
    print(f"  Threshold: {MAP_PROGRESSIVE_THRESHOLD} systems")
    print()
    print(f"Features:")
    print(f"  Backend Toggle: {'ENABLED' if ENABLE_BACKEND_TOGGLE else 'DISABLED'}")
    print(f"  Database Stats: {'ENABLED' if ENABLE_DATABASE_STATS else 'DISABLED'}")
    print(f"  JSON Import: {'ENABLED' if ENABLE_JSON_IMPORT else 'DISABLED'}")
    print(f"  API Server: {'ENABLED' if ENABLE_API_SERVER else 'DISABLED'}")
    print("=" * 70)


if __name__ == "__main__":
    print_configuration()
