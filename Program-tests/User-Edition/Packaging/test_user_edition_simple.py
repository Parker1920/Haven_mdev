#!/usr/bin/env python3
"""
Simplified User Edition Test - Focus on core functionality
"""
import json
import sys
from pathlib import Path
import subprocess

def test_user_edition():
    project_root = Path(__file__).parent.resolve()
    user_edition_dir = project_root / "dist" / "HavenControlRoom_User"
    data_file = user_edition_dir / "files" / "data.json"
    maps_dir = user_edition_dir / "files" / "maps"
    
    print("\n" + "="*70)
    print("USER EDITION TEST - CORE FUNCTIONALITY")
    print("="*70)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Directory structure
    print("\nTest 1: Directory Structure")
    required = [
        user_edition_dir / "HavenControlRoom.exe",
        data_file,
        maps_dir,
    ]
    for path in required:
        if path.exists():
            print(f"  OK: {path.name if path.is_file() else path.name + '/'}")
            tests_passed += 1
        else:
            print(f"  FAIL: Missing {path}")
            tests_failed += 1
    
    # Test 2: Data integrity
    print("\nTest 2: Data File Integrity")
    try:
        with open(data_file, 'r') as f:
            data = json.load(f)
        systems = {k: v for k, v in data.items() if k != "_meta"}
        print(f"  OK: Data contains {len(systems)} systems")
        tests_passed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        tests_failed += 1
    
    # Test 3: Map generation
    print("\nTest 3: Map Generator Standalone")
    try:
        map_output = maps_dir / "VH-Map-TEST.html"
        if map_output.exists():
            map_output.unlink()
        
        map_script = project_root / "src" / "Beta_VH_Map.py"
        result = subprocess.run([
            sys.executable,
            str(map_script),
            "--data-file", str(data_file),
            "--out", str(map_output),
            "--no-open"
        ], capture_output=True, timeout=30)
        
        if result.returncode == 0 and map_output.exists():
            with open(map_output, 'r', encoding='utf-8', errors='ignore') as f:
                html = f.read()
            if '"type": "system"' in html and 'window.SYSTEMS_DATA = []' not in html:
                print(f"  OK: Map generated with system data")
                tests_passed += 1
            else:
                print(f"  FAIL: Map has no system data")
                tests_failed += 1
        else:
            print(f"  FAIL: Map generation failed - {result.stderr[:100]}")
            tests_failed += 1
    except Exception as e:
        print(f"  FAIL: {e}")
        tests_failed += 1
    
    # Summary
    print("\n" + "="*70)
    print(f"RESULTS: {tests_passed} passed, {tests_failed} failed")
    print("="*70)
    
    return tests_failed == 0

if __name__ == "__main__":
    success = test_user_edition()
    sys.exit(0 if success else 1)
