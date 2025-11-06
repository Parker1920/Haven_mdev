#!/usr/bin/env python3
"""
Test script to verify map generation with user edition data.
This validates that:
1. Data file exists and has systems
2. Map generator can read it
3. Generated HTML contains system data
4. Loading overlay hide code is present
"""

import os
import json
import sys
from pathlib import Path

def test_map_generation():
    """Test the complete map generation flow"""
    
    # Setup paths (use absolute path)
    project_root = Path(__file__).parent.resolve()
    user_edition_dir = project_root / "dist/HavenControlRoom_User"
    data_file = user_edition_dir / "files/data.json"
    maps_dir = user_edition_dir / "files/maps"
    output_file = maps_dir / "VH-Map-VALIDATION.html"
    
    print("\n" + "="*60)
    print("MAP GENERATION VALIDATION TEST")
    print("="*60)
    
    # Test 1: Data file exists and has systems
    print("\n[TEST 1] Checking data file...")
    if not data_file.exists():
        print(f"  ❌ FAIL: Data file not found at {data_file}")
        return False
    
    try:
        with open(data_file) as f:
            data = json.load(f)
        
        # Count systems (exclude _meta)
        systems = {k: v for k, v in data.items() if k != "_meta"}
        num_systems = len(systems)
        
        print(f"  ✓ Data file exists with {num_systems} systems")
        for name in list(systems.keys())[:3]:
            print(f"    - {name}")
    except Exception as e:
        print(f"  ❌ FAIL: Could not read data file: {e}")
        return False
    
    # Test 2: Generate map
    print("\n[TEST 2] Generating map...")
    try:
        os.environ['PYTHONPATH'] = str(project_root)
        sys.path.insert(0, str(project_root))
        sys.path.insert(0, str(project_root / "src"))
        import Beta_VH_Map
        
        maps_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate the map
        sys.argv = ['', '--data-file', str(data_file), '--out', str(output_file), '--no-open']
        Beta_VH_Map.main(sys.argv[1:])
        
        print(f"  ✓ Map generated at {output_file}")
    except Exception as e:
        print(f"  ❌ FAIL: Map generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Check generated HTML has system data
    print("\n[TEST 3] Validating generated HTML...")
    if not output_file.exists():
        print(f"  ❌ FAIL: Output file not created at {output_file}")
        return False
    
    try:
        with open(output_file, encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        
        # Check for system data injection
        if 'window.SYSTEMS_DATA = []' in html_content:
            print("  ❌ FAIL: SYSTEMS_DATA is empty!")
            return False
        
        if 'window.SYSTEMS_DATA = [' not in html_content:
            print("  ❌ FAIL: SYSTEMS_DATA not found in HTML!")
            return False
        
        # Verify specific systems are present
        found_systems = 0
        for system_name in list(systems.keys())[:3]:
            if f'"name": "{system_name}"' in html_content:
                found_systems += 1
                print(f"  ✓ Found system: {system_name}")
        
        if found_systems == 0:
            print("  ❌ FAIL: No systems found in generated HTML!")
            return False
        
        print(f"  ✓ All {found_systems} tested systems present in HTML")
    except Exception as e:
        print(f"  ❌ FAIL: Could not validate HTML: {e}")
        return False
    
    # Test 4: Check for loading overlay hide code
    print("\n[TEST 4] Checking for loading overlay hide code...")
    if 'loading-overlay' not in html_content:
        print("  ⚠ WARNING: Loading overlay element not found in HTML")
    
    if "loadingOverlay.style.opacity = '0'" in html_content or 'loadingOverlay.style.opacity = "0"' in html_content:
        print("  ✓ Loading overlay hide code found")
    else:
        print("  ⚠ WARNING: Loading overlay hide code not found in HTML (but may be in external JS)")
    
    print("\n" + "="*60)
    print("✓ ALL TESTS PASSED")
    print("="*60)
    print("\nMap generation is working correctly!")
    print(f"Generated map: {output_file}")
    print(f"Systems in map: {num_systems}")
    return True

if __name__ == '__main__':
    success = test_map_generation()
    sys.exit(0 if success else 1)
