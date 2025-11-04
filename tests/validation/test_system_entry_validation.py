"""
Test System Entry validation and data output
"""
import json
import sys
import io
from pathlib import Path

# Fix Windows console encoding for emoji output
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from common.paths import data_path, project_root

def test_schema_compliance():
    """Test that data.json matches the schema structure"""
    print("Testing schema compliance...")

    data_file = data_path("data.json")
    schema_file = project_root() / "data" / "data.schema.json"

    if not data_file.exists():
        print("❌ data.json not found")
        return False

    if not schema_file.exists():
        print("❌ data.schema.json not found")
        return False

    # Load data
    with open(data_file, 'r', encoding='utf-8') as f:
        data_obj = json.load(f)

    # Load schema
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema = json.load(f)

    # Basic structure checks
    if not isinstance(data_obj, dict):
        print("❌ Data file should be a dict")
        return False

    if '_meta' not in data_obj:
        print("❌ Missing _meta key")
        return False

    # Support both new top-level map format and legacy formats
    systems = []

    # Format 1: Top-level map (preferred) - { "_meta": {...}, "SYSTEM_NAME": {...} }
    system_keys = [k for k in data_obj.keys() if k != '_meta']
    if system_keys:
        # Check if values are system objects with coordinates
        first_sys = data_obj[system_keys[0]]
        if isinstance(first_sys, dict) and ('x' in first_sys or 'y' in first_sys or 'z' in first_sys):
            systems = [data_obj[k] for k in system_keys]
            print(f"✅ Structure: Top-level map format (preferred)")
            print(f"✅ Found {len(systems)} systems")

    # Format 2: Legacy wrapper - { "_meta": {...}, "data": [...] }
    if not systems and 'data' in data_obj:
        if isinstance(data_obj['data'], list):
            systems = [item for item in data_obj['data'] if item.get('type') != 'region']
            regions = [item for item in data_obj['data'] if item.get('type') == 'region']
            print(f"✅ Structure: Legacy data array format")
            print(f"✅ Found {len(systems)} systems, {len(regions)} regions")

    # Format 3: Systems wrapper - { "_meta": {...}, "systems": {...} }
    if not systems and 'systems' in data_obj:
        if isinstance(data_obj['systems'], dict):
            systems = list(data_obj['systems'].values())
            print(f"✅ Structure: Systems wrapper format")
            print(f"✅ Found {len(systems)} systems")

    if not systems:
        print("❌ No systems found in any supported format")
        return False

    # Validate required fields for systems
    required_fields = ['id', 'name', 'region', 'x', 'y', 'z']
    for i, system in enumerate(systems):
        missing = [f for f in required_fields if f not in system]
        if missing:
            print(f"❌ System {i} ({system.get('name', 'unknown')}) missing: {missing}")
            return False

        # Check coordinate types
        for coord in ['x', 'y', 'z']:
            if not isinstance(system[coord], (int, float)):
                print(f"❌ System {system['name']}: {coord} must be numeric, got {type(system[coord])}")
                return False

    print(f"✅ All systems have required fields and valid types")

    return True

def test_draft_autosave():
    """Test that draft file structure is valid"""
    print("\nTesting draft autosave structure...")
    
    draft_file = project_root() / "data" / ".draft_system.json"
    
    if not draft_file.exists():
        print("ℹ️  No draft file found (expected if no active draft)")
        return True
    
    try:
        with open(draft_file, 'r', encoding='utf-8') as f:
            draft = json.load(f)
        
        expected_keys = ['name', 'region', 'x', 'y', 'z', 'properties', 'materials', 'custom', 'planets', 'photo']
        missing = [k for k in expected_keys if k not in draft]
        if missing:
            print(f"⚠️  Draft missing keys: {missing}")
        else:
            print(f"✅ Draft structure valid")
        
        return True
    except Exception as e:
        print(f"❌ Draft file invalid: {e}")
        return False

def test_theme_file():
    """Test that theme file exists and is valid"""
    print("\nTesting theme configuration...")
    
    theme_file = project_root() / "themes" / "haven_theme.json"
    
    if not theme_file.exists():
        print("❌ Theme file not found")
        return False
    
    try:
        with open(theme_file, 'r', encoding='utf-8') as f:
            theme = json.load(f)
        
        if 'colors' not in theme:
            print("❌ Theme missing colors key")
            return False
        
        colors = theme['colors']
        expected_colors = ['bg_dark', 'bg_card', 'accent_cyan', 'text_primary']
        missing = [c for c in expected_colors if c not in colors]
        if missing:
            print(f"⚠️  Theme missing colors: {missing}")
        else:
            print(f"✅ Theme has {len(colors)} color tokens")
        
        return True
    except Exception as e:
        print(f"❌ Theme file invalid: {e}")
        return False

def test_validation_logic():
    """Test validation helper functions"""
    print("\nTesting validation logic...")
    
    # Test numeric validation
    test_cases = [
        ("123", True),
        ("-45.6", True),
        ("0", True),
        ("abc", False),
        ("12.34.56", False),
        ("", False),
    ]
    
    def is_valid_number(val):
        if not val:
            return False
        try:
            float(val)
            return True
        except ValueError:
            return False
    
    for val, expected in test_cases:
        result = is_valid_number(val)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{val}' -> {result} (expected {expected})")
        if result != expected:
            return False
    
    print("✅ Validation logic correct")
    return True

def main():
    print("=" * 60)
    print("System Entry QA Tests")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Schema Compliance", test_schema_compliance()))
    results.append(("Draft Autosave", test_draft_autosave()))
    results.append(("Theme Config", test_theme_file()))
    results.append(("Validation Logic", test_validation_logic()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
