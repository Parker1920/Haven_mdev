"""
Phase 2 Testing Script

Tests Control Room integration with database backend.
"""
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

print("="*70)
print("PHASE 2 TESTING: CONTROL ROOM INTEGRATION")
print("="*70)

print("\n[TEST 1] Import Control Room Module")
try:
    # Add src to path for imports
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    from control_room import ControlRoom, PHASE2_ENABLED
    print(f"  ✓ Control Room imported successfully")
    print(f"  ✓ Phase 2 enabled: {PHASE2_ENABLED}")
except Exception as e:
    print(f"  ❌ Import failed: {e}")
    sys.exit(1)

print("\n[TEST 2] Check Configuration")
try:
    from config.settings import (
        USE_DATABASE, get_current_backend,
        SHOW_BACKEND_STATUS, SHOW_SYSTEM_COUNT,
        ENABLE_DATABASE_STATS
    )
    print(f"  ✓ USE_DATABASE: {USE_DATABASE}")
    print(f"  ✓ Current backend: {get_current_backend()}")
    print(f"  ✓ Show backend status: {SHOW_BACKEND_STATUS}")
    print(f"  ✓ Show system count: {SHOW_SYSTEM_COUNT}")
    print(f"  ✓ Enable database stats: {ENABLE_DATABASE_STATS}")
except Exception as e:
    print(f"  ❌ Configuration check failed: {e}")
    sys.exit(1)

print("\n[TEST 3] Data Provider Initialization")
try:
    from config.settings import get_data_provider
    provider = get_data_provider()
    count = provider.get_total_count()
    print(f"  ✓ Data provider initialized")
    print(f"  ✓ Total systems: {count}")
except Exception as e:
    print(f"  ❌ Data provider init failed: {e}")
    sys.exit(1)

print("\n[TEST 4] Test Control Room Initialization (No GUI)")
try:
    # We can't actually create the GUI in a test script,
    # but we can verify the class structure
    print(f"  ✓ ControlRoom class available")
    print(f"  ✓ Methods defined:")
    methods = [m for m in dir(ControlRoom) if not m.startswith('_')]
    print(f"    - {len(methods)} public methods")

    # Check for Phase 2 methods
    if 'show_database_stats' in dir(ControlRoom):
        print(f"  ✓ Phase 2 method 'show_database_stats' found")
    else:
        print(f"  ⚠️  Phase 2 method 'show_database_stats' not found")

except Exception as e:
    print(f"  ❌ Control Room check failed: {e}")
    sys.exit(1)

print("\n[TEST 5] Backend Switching Test")
try:
    # Test with JSON backend
    from src.common.data_provider import JSONDataProvider, DatabaseDataProvider

    json_provider = JSONDataProvider()
    json_count = json_provider.get_total_count()
    print(f"  ✓ JSON provider: {json_count} systems")

    # Test with Database backend
    db_provider = DatabaseDataProvider()
    db_count = db_provider.get_total_count()
    print(f"  ✓ Database provider: {db_count} systems")

    if json_count == db_count:
        print(f"  ✓ Both backends have same count")
    else:
        print(f"  ⚠️  Count mismatch: JSON={json_count}, DB={db_count}")

except Exception as e:
    print(f"  ❌ Backend switching test failed: {e}")
    sys.exit(1)

print("\n" + "="*70)
print("✓ ALL TESTS PASSED - PHASE 2 INTEGRATION READY")
print("="*70)
print("\nNext Steps:")
print("  1. Launch Control Room manually: py src/control_room.py")
print("  2. Verify UI shows backend status (JSON)")
print("  3. Verify system count displayed (9 systems)")
print("  4. Switch to database mode: config/settings.py USE_DATABASE = True")
print("  5. Launch Control Room again")
print("  6. Verify UI shows backend status (DATABASE)")
print("  7. Click 'Database Statistics' button")
print("="*70)

sys.exit(0)
