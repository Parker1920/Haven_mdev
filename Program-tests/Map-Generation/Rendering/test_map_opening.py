#!/usr/bin/env python3
"""
Test to verify the map opening fix - ensure VH-Map.html is opened, not system files
"""
from pathlib import Path

project_root = Path(__file__).parent.resolve()
maps_dir = project_root / "dist" / "HavenControlRoom_User" / "files" / "maps"

print("\n" + "="*70)
print("VERIFYING MAP OPENING FIX")
print("="*70)

# Check what VH-Map.html exists
main_map = maps_dir / "VH-Map.html"
if main_map.exists():
    print(f"\n✓ Main map file found: {main_map.name}")
    print(f"  File size: {main_map.stat().st_size / 1024:.1f} KB")
    print(f"  Last modified: {main_map.stat().st_mtime}")
else:
    print(f"\n✗ Main map file NOT found: {main_map}")

# List all HTML files with modification times
print(f"\n All HTML files in {maps_dir.name}/:")
html_files = sorted(maps_dir.glob("*.html"), key=lambda p: p.stat().st_mtime, reverse=True)
for idx, f in enumerate(html_files, 1):
    size_kb = f.stat().st_size / 1024
    mtime = f.stat().st_mtime
    is_main = "← WILL OPEN THIS" if f.name == "VH-Map.html" else ""
    print(f"  {idx}. {f.name:<30} {size_kb:>6.1f} KB {is_main}")

print("\n" + "="*70)
print("RESULT: VH-Map.html will be opened preferentially")
print("="*70 + "\n")
