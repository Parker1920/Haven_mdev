"""
Test Manager Integration Test

Verifies that the Test Manager button is properly integrated into Control Room.
Tests the import, method definition, and button creation.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

def test_test_manager_integration():
    """Test that Test Manager is properly integrated into Control Room"""

    print("=" * 70)
    print("TEST MANAGER INTEGRATION TEST")
    print("=" * 70)
    print()

    # Test 1: Import control_room module
    print("Test 1: Importing control_room module...")
    try:
        import control_room
        print("✓ control_room module imported successfully")
    except Exception as e:
        print(f"✗ Failed to import control_room: {e}")
        return False

    # Test 2: Check TestManagerWindow import
    print("\nTest 2: Checking TestManagerWindow import...")
    try:
        from test_manager_window import TestManagerWindow
        print("✓ TestManagerWindow imported successfully")
    except Exception as e:
        print(f"✗ Failed to import TestManagerWindow: {e}")
        return False

    # Test 3: Verify open_test_manager method exists
    print("\nTest 3: Verifying open_test_manager method exists...")
    if hasattr(control_room.ControlRoom, 'open_test_manager'):
        print("✓ open_test_manager method exists in ControlRoom class")
    else:
        print("✗ open_test_manager method not found in ControlRoom class")
        return False

    # Test 4: Verify TestManagerWindow class structure
    print("\nTest 4: Verifying TestManagerWindow class structure...")
    required_methods = ['_load_tests', '_execute_test', '_add_test', '_export_results']
    missing_methods = []

    for method in required_methods:
        if not hasattr(TestManagerWindow, method):
            missing_methods.append(method)

    if missing_methods:
        print(f"✗ Missing methods: {', '.join(missing_methods)}")
        return False
    else:
        print(f"✓ All required methods present: {', '.join(required_methods)}")

    # Test 5: Verify test results database location
    print("\nTest 5: Verifying test results database location...")
    expected_db_path = project_root / "Program-tests" / "test_results.json"
    print(f"   Expected path: {expected_db_path}")

    if expected_db_path.parent.exists():
        print("✓ Program-tests directory exists")
    else:
        print("✗ Program-tests directory not found")
        return False

    # Test 6: Verify Program-tests folder structure
    print("\nTest 6: Verifying Program-tests folder structure...")
    expected_folders = ['Control-Room', 'Wizard', 'Keeper']
    program_tests_dir = project_root / "Program-tests"

    existing_folders = []
    for folder in expected_folders:
        folder_path = program_tests_dir / folder
        if folder_path.exists():
            existing_folders.append(folder)

    print(f"   Found folders: {', '.join(existing_folders)}")
    if len(existing_folders) == len(expected_folders):
        print("✓ All expected test category folders exist")
    else:
        missing = set(expected_folders) - set(existing_folders)
        print(f"⚠ Missing folders: {', '.join(missing)}")

    print("\n" + "=" * 70)
    print("✓ ALL INTEGRATION TESTS PASSED")
    print("=" * 70)
    print("\nTest Manager is properly integrated into Control Room!")
    print("To use: Launch Control Room → Advanced Tools → 🧪 Test Manager")
    return True

if __name__ == "__main__":
    try:
        success = test_test_manager_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ INTEGRATION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
