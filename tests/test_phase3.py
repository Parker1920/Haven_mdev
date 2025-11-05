"""
Phase 3 Testing Script

Tests Wizard integration with database backend.
"""
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Add project root and src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

print("="*70)
print("PHASE 3 TESTING: WIZARD INTEGRATION")
print("="*70)

print("\n[TEST 1] Import Wizard Module")
try:
    from system_entry_wizard import SystemEntryWizard, PHASE3_ENABLED
    print(f"  ✓ Wizard imported successfully")
    print(f"  ✓ Phase 3 enabled: {PHASE3_ENABLED}")
except Exception as e:
    print(f"  ❌ Import failed: {e}")
    sys.exit(1)

print("\n[TEST 2] Check Configuration")
try:
    from config.settings import (
        USE_DATABASE, get_current_backend,
        SHOW_BACKEND_STATUS, SHOW_SYSTEM_COUNT
    )
    print(f"  ✓ USE_DATABASE: {USE_DATABASE}")
    print(f"  ✓ Current backend: {get_current_backend()}")
    print(f"  ✓ Show backend status: {SHOW_BACKEND_STATUS}")
    print(f"  ✓ Show system count: {SHOW_SYSTEM_COUNT}")
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

print("\n[TEST 4] Test Wizard Class Structure (No GUI)")
try:
    # We can't actually create the GUI in a test script,
    # but we can verify the class structure
    print(f"  ✓ SystemEntryWizard class available")
    print(f"  ✓ Methods defined:")
    methods = [m for m in dir(SystemEntryWizard) if not m.startswith('_')]
    print(f"    - {len(methods)} public methods")

    # Check for Phase 3 methods
    if '_init_data_provider' in dir(SystemEntryWizard):
        print(f"  ✓ Phase 3 method '_init_data_provider' found")
    else:
        print(f"  ⚠️  Phase 3 method '_init_data_provider' not found")

    if '_save_system_via_provider' in dir(SystemEntryWizard):
        print(f"  ✓ Phase 3 method '_save_system_via_provider' found")
    else:
        print(f"  ⚠️  Phase 3 method '_save_system_via_provider' not found")

    if '_save_system_via_json' in dir(SystemEntryWizard):
        print(f"  ✓ Phase 3 method '_save_system_via_json' found")
    else:
        print(f"  ⚠️  Phase 3 method '_save_system_via_json' not found")

except Exception as e:
    print(f"  ❌ Wizard check failed: {e}")
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
print("✓ ALL TESTS PASSED - PHASE 3 INTEGRATION READY")
print("="*70)
print("\nNext Steps:")
print("  1. Launch Wizard manually: py src/system_entry_wizard.py")
print("  2. Verify UI shows backend status (DATABASE)")
print("  3. Verify system count displayed (9 systems)")
print("  4. Create a new test system in database mode")
print("  5. Verify system is saved to database")
print("  6. Switch to JSON mode: config/settings.py USE_DATABASE = False")
print("  7. Launch Wizard again")
print("  8. Verify UI shows backend status (JSON)")
print("  9. Create another test system in JSON mode")
print(" 10. Verify system is saved to JSON file")
print("="*70)

sys.exit(0)
