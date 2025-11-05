"""
Verify moon duplication fix - ensure moons only appear as nested objects,
not as standalone plot points.
"""
import json
from pathlib import Path

def verify_no_duplicate_moons():
    """Verify moons are nested in planets, not standalone objects."""
    print("="*70)
    print("MOON DUPLICATION FIX VERIFICATION")
    print("="*70)
    print()
    
    dist_dir = Path("dist")
    system_files = sorted(list(dist_dir.glob("system_*.html")), 
                         key=lambda p: p.stat().st_mtime, reverse=True)
    
    if not system_files:
        print("❌ No system files found")
        return False
    
    # Check for STRESS-MU-001 specifically (known to have moons)
    stress_mu_file = dist_dir / "system_STRESS-MU-001.html"
    if stress_mu_file.exists():
        test_file = stress_mu_file
    else:
        test_file = system_files[0]
    
    print(f"Checking: {test_file.name}")
    print("-" * 70)
    
    content = test_file.read_text(encoding='utf-8', errors='replace')
    
    # Extract SYSTEMS_DATA
    start_marker = "window.SYSTEMS_DATA = "
    end_marker = "window.VIEW_MODE"
    
    if start_marker not in content:
        print("❌ Cannot find SYSTEMS_DATA")
        return False
    
    start_idx = content.index(start_marker) + len(start_marker)
    end_idx = content.index(end_marker, start_idx)
    data_str = content[start_idx:end_idx].strip()
    
    # Remove trailing semicolon and whitespace
    data_str = data_str.rstrip(';').strip()
    
    try:
        systems_data = json.loads(data_str)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON: {e}")
        return False
    
    # Count objects
    planets = [obj for obj in systems_data if obj.get('type') == 'planet']
    standalone_moons = [obj for obj in systems_data if obj.get('type') == 'moon']
    
    # Count nested moons
    nested_moon_count = 0
    planets_with_moons = 0
    for planet in planets:
        moons = planet.get('moons', [])
        if moons:
            nested_moon_count += len(moons)
            planets_with_moons += 1
    
    print(f"Planets: {len(planets)}")
    print(f"Planets with moons: {planets_with_moons}")
    print(f"Nested moons (in planet.moons arrays): {nested_moon_count}")
    print(f"Standalone moon objects: {len(standalone_moons)}")
    print()
    
    if len(standalone_moons) > 0:
        print("❌ FAIL: Found standalone moon objects (duplicates)")
        print("   These should not exist - moons should only be nested in planets")
        return False
    else:
        print("✅ PASS: No standalone moon objects found")
    
    if nested_moon_count > 0:
        print(f"✅ PASS: Found {nested_moon_count} properly nested moons")
    else:
        print("⚠️  WARNING: No nested moons found (may be normal if no planets have moons)")
    
    print()
    print("="*70)
    print("✅ MOON DUPLICATION FIX VERIFIED")
    print("="*70)
    print()
    print("Expected behavior:")
    print("- Moons appear ONLY as orbiting objects around planets")
    print("- NO standalone moon plot points in space")
    print("- Moons are defined in planet.moons arrays")
    print()
    
    return True

if __name__ == "__main__":
    verify_no_duplicate_moons()
