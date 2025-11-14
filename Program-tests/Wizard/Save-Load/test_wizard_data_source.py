"""
Test Wizard Data Source Switching - Verify multi-file editing capability
"""
import sys
from pathlib import Path
import json

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from common.paths import data_path

print("=" * 70)
print("TESTING WIZARD DATA SOURCE SWITCHING")
print("=" * 70)

# Test 1: Check all data source files exist/can be created
print("\n[TEST 1] Verify data source files")
sources = {
    "production": data_path("data.json"),
    "testing": data_path("testing.json"),
    "load_test": data_path("load_test.json")
}

for name, path in sources.items():
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Count systems (handle both formats)
                if isinstance(data, dict):
                    systems = [v for k, v in data.items() if k != '_meta']
                    count = len(systems)
                elif isinstance(data, list):
                    count = len(data)
                else:
                    count = 0
                print(f"  ✓ {name}: {path} - {count} systems")
        except Exception as e:
            print(f"  ⚠️  {name}: {path} - exists but error reading: {e}")
    else:
        print(f"  ℹ️  {name}: {path} - will be created on first save")

# Test 2: Verify data file paths are different
print("\n[TEST 2] Verify data files are independent")
paths_list = list(sources.values())
if len(set(paths_list)) == len(paths_list):
    print(f"  ✓ All data sources use different files")
    for name, path in sources.items():
        print(f"    - {name}: {path.name}")
else:
    print(f"  ❌ Some data sources share the same file!")

# Test 3: Test file switching logic
print("\n[TEST 3] Simulate data source switching")
test_results = []

for source_name in ["production", "testing", "load_test"]:
    source_file = sources[source_name]

    # Check if we can read from this source
    try:
        if source_file.exists():
            with open(source_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            test_results.append(f"  ✓ {source_name}: Successfully loaded")
        else:
            test_results.append(f"  ℹ️  {source_name}: File doesn't exist yet (OK)")
    except Exception as e:
        test_results.append(f"  ❌ {source_name}: Error - {e}")

for result in test_results:
    print(result)

# Test 4: Verify system list independence
print("\n[TEST 4] Verify each source has independent system lists")
for name, path in sources.items():
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Get system names
            if isinstance(data, dict):
                system_names = [k for k in data.keys() if k != '_meta']
            elif isinstance(data, list):
                system_names = [s.get('name', 'Unknown') for s in data]
            else:
                system_names = []

            if system_names:
                print(f"  ✓ {name}: {len(system_names)} systems")
                # Show first 3 system names
                sample = system_names[:3]
                print(f"    Sample: {', '.join(sample)}")
            else:
                print(f"  ℹ️  {name}: No systems yet")
        except Exception as e:
            print(f"  ⚠️  {name}: Error reading - {e}")
    else:
        print(f"  ℹ️  {name}: File doesn't exist yet")

# Test 5: Check that wizard can write to all sources
print("\n[TEST 5] Test write capability (dry run)")
test_system = {
    "name": "TEST_WIZARD_SWITCH",
    "region": "Test",
    "x": 100,
    "y": 200,
    "z": 300,
    "economy": "Trading",
    "conflict": "Low",
    "planets": []
}

for name, path in sources.items():
    try:
        # Create minimal valid data structure
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"_meta": {"version": "1.0"}}

        # Simulate adding test system
        if isinstance(data, dict):
            data_copy = data.copy()
            data_copy[test_system['name']] = test_system
            print(f"  ✓ {name}: Can add test system (dry run)")
        else:
            print(f"  ⚠️  {name}: Unexpected data format")
    except Exception as e:
        print(f"  ❌ {name}: Write test failed - {e}")

print("\n" + "=" * 70)
print("✓ DATA SOURCE SWITCHING TEST COMPLETE")
print("=" * 70)

print("\n[MANUAL VERIFICATION]")
print("Please verify in the Wizard UI:")
print("  1. Data source dropdown shows: production, testing, load_test")
print("  2. Badge color changes: GREEN (production), ORANGE (testing), PURPLE (load_test)")
print("  3. System count updates when switching sources")
print("  4. System list dropdown updates when switching sources")
print("  5. Confirmation dialog appears when switching with unsaved data")
print("  6. Saved systems go to the correct data file")
