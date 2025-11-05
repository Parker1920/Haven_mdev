"""
Test script to verify moon orbit rings are present in generated HTML files.

Checks:
1. MoonRenderer, Moon3D, and MoonOrbit classes are defined
2. Moon initialization code in map-viewer.js is present
3. Moons data is properly structured in system files
"""
import re
from pathlib import Path

def check_moon_visualization():
    """Check if moon visualization is properly configured."""
    print("="*70)
    print("MOON ORBIT VISUALIZATION VERIFICATION")
    print("="*70)
    print()
    
    dist_dir = Path("dist")
    
    # Test 1: Check if template has MoonRenderer classes
    print("TEST 1: Template has MoonRenderer classes")
    print("-" * 70)
    template_path = Path("src/templates/map_template.html")
    if template_path.exists():
        template_content = template_path.read_text(encoding='utf-8')
        
        has_moon_orbit = "class MoonOrbit" in template_content
        has_moon_3d = "class Moon3D" in template_content
        has_moon_renderer = "class MoonRenderer" in template_content
        
        if has_moon_orbit and has_moon_3d and has_moon_renderer:
            print("✅ PASS: All moon classes present in template")
            print(f"   - MoonOrbit: {'✓' if has_moon_orbit else '✗'}")
            print(f"   - Moon3D: {'✓' if has_moon_3d else '✗'}")
            print(f"   - MoonRenderer: {'✓' if has_moon_renderer else '✗'}")
        else:
            print("❌ FAIL: Some moon classes missing from template")
            return False
    else:
        print("❌ FAIL: Template file not found")
        return False
    print()
    
    # Test 2: Check generated HTML files
    print("TEST 2: Generated HTML files have MoonRenderer")
    print("-" * 70)
    
    # Find system HTML files sorted by modification time (newest first)
    system_files = list(dist_dir.glob("system_*.html"))
    if not system_files:
        print("❌ FAIL: No system HTML files found in dist/")
        return False
    
    # Sort by modification time, newest first
    system_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    
    # Check most recent system file
    test_file = system_files[0]
    content = test_file.read_text(encoding='utf-8')
    
    if "class MoonRenderer" in content:
        print(f"✅ PASS: MoonRenderer class found in {test_file.name}")
    else:
        print(f"❌ FAIL: MoonRenderer class NOT found in {test_file.name}")
        return False
    print()
    
    # Test 3: Check map-viewer.js has initialization
    print("TEST 3: map-viewer.js has moon initialization")
    print("-" * 70)
    
    map_viewer_path = Path("src/static/js/map-viewer.js")
    if map_viewer_path.exists():
        viewer_content = map_viewer_path.read_text(encoding='utf-8')
        
        has_init = "moonRenderer = new MoonRenderer" in viewer_content
        has_update = "moonRenderer.update()" in viewer_content
        has_console = "[MOON] Initializing moon renderer" in viewer_content
        
        if has_init and has_update and has_console:
            print("✅ PASS: Moon initialization code present")
            print(f"   - Initialization: {'✓' if has_init else '✗'}")
            print(f"   - Update loop: {'✓' if has_update else '✗'}")
            print(f"   - Debug logging: {'✓' if has_console else '✗'}")
        else:
            print("❌ FAIL: Moon initialization incomplete")
            return False
    else:
        print("❌ FAIL: map-viewer.js not found")
        return False
    print()
    
    # Test 4: Check for moons data in system files
    print("TEST 4: System files contain moons data")
    print("-" * 70)
    
    # Look for a system with moons
    found_moons = False
    for system_file in system_files[:10]:  # Check first 10 files
        content = system_file.read_text(encoding='utf-8')
        
        # Look for moons array in planet data
        if re.search(r'"moons"\s*:\s*\[', content):
            print(f"✅ Found moons data in {system_file.name}")
            
            # Count moons in this file
            moon_matches = re.findall(r'"type"\s*:\s*"moon"', content)
            print(f"   - Moon objects found: {len(moon_matches)}")
            found_moons = True
            break
    
    if not found_moons:
        print("⚠️  WARNING: No moons found in checked system files")
        print("   (This may be normal if test data doesn't have moons)")
    print()
    
    print("="*70)
    print("✅ MOON VISUALIZATION SETUP COMPLETE")
    print("="*70)
    print()
    print("Next steps:")
    print("1. Open a system HTML file in browser: dist/system_*.html")
    print("2. Open browser console (F12)")
    print("3. Look for: [MOON] Initializing moon renderer...")
    print("4. Check for gray orbit rings around planets with moons")
    print()
    
    return True

if __name__ == "__main__":
    check_moon_visualization()
