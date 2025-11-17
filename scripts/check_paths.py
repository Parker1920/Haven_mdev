"""
Check canonical paths used by the application for debugging and environment verification.

Usage:
    python scripts/check_paths.py
"""
from pathlib import Path
import sys
from pathlib import Path as _P
project_root_p = Path(__file__).resolve().parents[1]
if str(project_root_p) not in sys.path:
    sys.path.insert(0, str(project_root_p))
try:
    from src.common.paths import project_root, data_dir, dist_dir, photos_dir, logs_dir, database_path
except Exception as e:
    print('Could not import paths:', e)
    sys.exit(1)

print('PROJECT_ROOT:', project_root())
print('DATA_DIR:', data_dir())
print('DIST_DIR:', dist_dir())
print('PHOTOS_DIR:', photos_dir())
print('LOGS_DIR:', logs_dir())
print('DATABASE_PATH:', database_path())
