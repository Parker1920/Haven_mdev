#!/usr/bin/env python3
"""Check map generation and static mount state for the web UI.

Prints info about the HAVEN_UI_ROOT dist, static, and assets directories, and reports whether VH-Map.html exists, and whether the static assets exist.
"""
import os
from pathlib import Path

try:
    from src.common.paths import project_root
    HAVEN_UI_DIR = os.environ.get('HAVEN_UI_DIR') or str(project_root() / 'Haven-UI')
except Exception:
    HAVEN_UI_DIR = os.environ.get('HAVEN_UI_DIR') or 'Haven-UI'

HAVEN_UI_ROOT = Path(HAVEN_UI_DIR)
print(f"HAVEN_UI_ROOT: {HAVEN_UI_ROOT}")

ui_dist = HAVEN_UI_ROOT / 'dist'
print(f"ui_dist exists: {ui_dist.exists()}")
print(f"ui_dist path: {ui_dist}")

ui_static = ui_dist / 'static'
ui_assets = ui_dist / 'assets'
print(f"ui_static exists: {ui_static.exists()} -> {ui_static}")
print(f"ui_assets exists: {ui_assets.exists()} -> {ui_assets}")

vh_map = ui_dist / 'VH-Map.html'
print(f"VH-Map.html exists: {vh_map.exists()} -> {vh_map}")

if vh_map.exists():
    print(f"VH-Map file size KB: {vh_map.stat().st_size / 1024:.2f}")
    print(f"VH-Map mtime: {vh_map.stat().st_mtime}")
else:
    print("VH-Map not found; try generating via /api/generate_map")

# Show sample files in static
if ui_static.exists():
    js_files = list(ui_static.rglob('*.js'))
    css_files = list(ui_static.rglob('*.css'))
    print(f"Static JS count: {len(js_files)}")
    print(f"Static CSS count: {len(css_files)}")
    if js_files:
        print(f"First 3 JS files: {[str(x.relative_to(ui_static)) for x in js_files[:3]]}")
else:
    print("Static directory absent; map fetches for '/map/static' will 404")

print("Done.")
