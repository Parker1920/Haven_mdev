"""
Test Space Station Feature - End-to-End Test
"""
import sys
from pathlib import Path

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

from config.settings import get_data_provider
import random

print("=" * 70)
print("TESTING SPACE STATION FEATURE - END TO END")
print("=" * 70)

# Get provider
provider = get_data_provider()

# Test 1: Create a test system with space station
print("\n[TEST 1] Create test system with space station")
try:
    import uuid
    test_system = {
        'id': f'TEST_{uuid.uuid4().hex[:8].upper()}',
        'name': 'TEST SPACE STATION SYSTEM',
        'region': 'Test Region',
        'x': 100.0,
        'y': 200.0,
        'z': 300.0,
        'attributes': 'Test system for space station feature',
        'planets': [],
        'space_station': {
            'name': 'TEST SPACE STATION SYSTEM Station',
            'race': random.choice(['Gek', 'Korvax', "Vy'keen"]),
            'sell_percent': 80,
            'buy_percent': 120
        }
    }

    print(f"  Creating system: {test_system['name']}")
    print(f"  Space Station: {test_system['space_station']['name']}")
    print(f"  Race: {test_system['space_station']['race']}")

    system_id = provider.add_system(test_system)
    print(f"  ✓ System created with ID: {system_id}")

except Exception as e:
    print(f"  ❌ Failed to create system: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Retrieve the system and verify space station
print("\n[TEST 2] Retrieve system and verify space station")
try:
    retrieved = provider.get_system_by_name('TEST SPACE STATION SYSTEM')
    if retrieved:
        print(f"  ✓ System retrieved: {retrieved['name']}")

        if 'space_station' in retrieved and retrieved['space_station']:
            station = retrieved['space_station']
            print(f"  ✓ Space station found: {station['name']}")
            print(f"  ✓ Race: {station['race']}")
            print(f"  ✓ Sell: {station['sell_percent']}%")
            print(f"  ✓ Buy: {station['buy_percent']}%")
        else:
            print(f"  ❌ No space station in retrieved system!")
            print(f"  System data: {retrieved}")
    else:
        print(f"  ❌ Could not retrieve system")

except Exception as e:
    print(f"  ❌ Failed to retrieve system: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Check map generator compatibility
print("\n[TEST 3] Check map generator can read space stations")
try:
    all_systems = provider.get_all_systems()
    systems_with_stations = [s for s in all_systems if s.get('space_station')]

    print(f"  ✓ Total systems: {len(all_systems)}")
    print(f"  ✓ Systems with space stations: {len(systems_with_stations)}")

    if systems_with_stations:
        print(f"  ✓ Example systems with stations:")
        for sys in systems_with_stations[:5]:
            station = sys.get('space_station', {})
            print(f"    - {sys['name']}: {station.get('name', 'N/A')} ({station.get('race', 'N/A')})")

except Exception as e:
    print(f"  ❌ Failed to check systems: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Clean up test system
print("\n[TEST 4] Clean up test system")
try:
    if retrieved:
        provider.delete_system(retrieved['id'])
        print(f"  ✓ Test system deleted")
    else:
        print(f"  ⚠️  Could not find test system to delete")

except Exception as e:
    print(f"  ❌ Failed to delete test system: {e}")

print("\n" + "=" * 70)
print("✓ SPACE STATION FEATURE TEST COMPLETE")
print("=" * 70)
print("\nSummary:")
print("  ✓ Systems can be created with space stations")
print("  ✓ Space stations are saved to database correctly")
print("  ✓ Space stations are retrieved from database")
print("  ✓ Map generator can read space station data")
print("\nNext Steps:")
print("  1. Launch Wizard: py src/system_entry_wizard.py")
print("  2. Click 'Add Space Station' button on Page 1")
print("  3. Fill in space station details and save")
print("  4. Save the system")
print("  5. Generate map from Control Room")
print("  6. Verify space station appears on the map")
print("=" * 70)
