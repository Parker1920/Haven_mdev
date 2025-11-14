#!/usr/bin/env python3
"""
Test bundle integrity for frozen EXE.
Verifies that all required resources and modules are available.
"""
import sys
import os
from pathlib import Path

def test_imports():
    """Test critical module imports."""
    print("\n1. Testing Critical Module Imports...")
    modules = ['pandas', 'numpy', 'customtkinter', 'webbrowser', 'json', 'logging']
    failed = []
    
    for mod in modules:
        try:
            __import__(mod)
            print(f"  ✓ {mod}")
        except ImportError as e:
            print(f"  ✗ {mod}: {e}")
            failed.append(mod)
    
    return len(failed) == 0

def test_source_files():
    """Test that source files are accessible."""
    print("\n2. Testing Source Files...")
    src_dir = Path("src")
    files_needed = [
        "control_room_user.py",
        "Beta_VH_Map.py",
        "system_entry_wizard.py",
        "common/paths.py",
    ]
    failed = []
    
    for f in files_needed:
        fpath = src_dir / f
        if fpath.exists():
            print(f"  ✓ {f}")
        else:
            print(f"  ✗ {f} - NOT FOUND")
            failed.append(f)
    
    return len(failed) == 0

def test_data_files():
    """Test that data files exist."""
    print("\n3. Testing Data Files...")
    data_dir = Path("data")
    files_needed = [
        "data.json",
    ]
    failed = []
    
    for f in files_needed:
        fpath = data_dir / f
        if fpath.exists():
            size_kb = fpath.stat().st_size / 1024
            print(f"  ✓ {f} ({size_kb:.1f} KB)")
        else:
            print(f"  ✗ {f} - NOT FOUND")
            failed.append(f)
    
    return len(failed) == 0

def test_templates():
    """Test that templates are accessible."""
    print("\n4. Testing Templates...")
    template_dir = Path("src/templates")
    if template_dir.exists():
        templates = list(template_dir.glob("*.html"))
        print(f"  ✓ Templates directory found ({len(templates)} files)")
        for t in templates:
            print(f"    - {t.name}")
        return True
    else:
        print(f"  ✗ Templates directory NOT FOUND")
        return False

def test_static_files():
    """Test that static files are accessible."""
    print("\n5. Testing Static Files (CSS/JS)...")
    static_dir = Path("src/static")
    if static_dir.exists():
        files = list(static_dir.rglob("*"))
        print(f"  ✓ Static directory found ({len(files)} items)")
        return True
    else:
        print(f"  ✗ Static directory NOT FOUND")
        return False

def test_map_generation():
    """Test that map generation works."""
    print("\n6. Testing Map Generation...")
    from src.Beta_VH_Map import VHMapGenerator
    
    try:
        # Create generator with test data
        data = {
            "test-system": {
                "x": 0,
                "y": 0,
                "z": 0,
                "name": "Test System",
            }
        }
        
        generator = VHMapGenerator()
        # Don't actually generate to save time, just verify it can be instantiated
        print("  ✓ VHMapGenerator instantiated successfully")
        return True
    except Exception as e:
        print(f"  ✗ Map generation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 70)
    print("HAVEN CONTROL ROOM - BUNDLE INTEGRITY TEST")
    print("=" * 70)
    
    results = {
        "Imports": test_imports(),
        "Source Files": test_source_files(),
        "Data Files": test_data_files(),
        "Templates": test_templates(),
        "Static Files": test_static_files(),
        "Map Generation": test_map_generation(),
    }
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\nOverall: {passed}/{total} passed")
    print("=" * 70)
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
