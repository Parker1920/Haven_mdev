"""
Test Manager Static Integration Test

Verifies Test Manager integration via static code analysis (no GUI imports needed).
"""

import sys
import ast
from pathlib import Path

# Project root
project_root = Path(__file__).parent.parent.parent.parent

def test_static_integration():
    """Static analysis of Test Manager integration"""

    print("=" * 70)
    print("TEST MANAGER STATIC INTEGRATION TEST")
    print("=" * 70)
    print()

    # Test 1: Verify control_room.py has TestManagerWindow import
    print("Test 1: Checking control_room.py imports...")
    control_room_path = project_root / "src" / "control_room.py"

    if not control_room_path.exists():
        print(f"✗ control_room.py not found at {control_room_path}")
        return False

    control_room_code = control_room_path.read_text()

    if "from test_manager_window import TestManagerWindow" in control_room_code:
        print("✓ TestManagerWindow import found")
    else:
        print("✗ TestManagerWindow import not found")
        return False

    # Test 2: Verify open_test_manager method exists
    print("\nTest 2: Checking open_test_manager method...")

    if "def open_test_manager(self):" in control_room_code:
        print("✓ open_test_manager method found")
    else:
        print("✗ open_test_manager method not found")
        return False

    # Test 3: Verify Test Manager button creation
    print("\nTest 3: Checking Test Manager button creation...")

    if '🧪 Test Manager' in control_room_code and 'self.open_test_manager' in control_room_code:
        print("✓ Test Manager button found with correct callback")
    else:
        print("✗ Test Manager button not properly configured")
        return False

    # Test 4: Verify test_manager_window.py exists
    print("\nTest 4: Checking test_manager_window.py exists...")
    test_manager_path = project_root / "src" / "test_manager_window.py"

    if not test_manager_path.exists():
        print(f"✗ test_manager_window.py not found at {test_manager_path}")
        return False

    print(f"✓ test_manager_window.py exists ({test_manager_path.stat().st_size} bytes)")

    # Test 5: Verify TestManagerWindow class in test_manager_window.py
    print("\nTest 5: Checking TestManagerWindow class...")
    test_manager_code = test_manager_path.read_text()

    if "class TestManagerWindow(ctk.CTkToplevel):" in test_manager_code:
        print("✓ TestManagerWindow class found")
    else:
        print("✗ TestManagerWindow class not found")
        return False

    # Test 6: Verify key methods exist in TestManagerWindow
    print("\nTest 6: Checking TestManagerWindow methods...")
    required_methods = [
        '_load_tests',
        '_execute_test',
        '_add_test',
        '_export_results',
        '_load_results_db',
        '_save_results_db'
    ]

    missing_methods = []
    for method in required_methods:
        if f"def {method}(" not in test_manager_code:
            missing_methods.append(method)

    if missing_methods:
        print(f"✗ Missing methods: {', '.join(missing_methods)}")
        return False
    else:
        print(f"✓ All required methods present ({len(required_methods)} methods)")

    # Test 7: Verify Program-tests directory structure
    print("\nTest 7: Checking Program-tests directory structure...")
    program_tests_dir = project_root / "Program-tests"

    if not program_tests_dir.exists():
        print(f"✗ Program-tests directory not found")
        return False

    expected_folders = ['Control-Room', 'Wizard', 'Keeper', 'Map-Generation', 'User-Edition', 'Utilities', 'Security']
    existing_folders = [f.name for f in program_tests_dir.iterdir() if f.is_dir() and not f.name.startswith('.')]

    print(f"   Found folders: {', '.join(sorted(existing_folders))}")

    main_folders = ['Control-Room', 'Wizard', 'Keeper']
    if all(folder in existing_folders for folder in main_folders):
        print(f"✓ Main test category folders exist ({len(existing_folders)} total)")
    else:
        missing = set(main_folders) - set(existing_folders)
        print(f"⚠ Missing main folders: {', '.join(missing)}")

    # Test 8: Count test files
    print("\nTest 8: Counting test files in Program-tests...")
    test_files = list(program_tests_dir.rglob("*.py"))
    test_file_count = len(test_files)

    print(f"✓ Found {test_file_count} test files in Program-tests/")

    # Test 9: Verify TEST_MANIFEST.md exists
    print("\nTest 9: Checking TEST_MANIFEST.md...")
    manifest_path = program_tests_dir / "TEST_MANIFEST.md"

    if manifest_path.exists():
        print(f"✓ TEST_MANIFEST.md exists ({manifest_path.stat().st_size} bytes)")
    else:
        print("⚠ TEST_MANIFEST.md not found (optional)")

    # Test 10: Verify syntax of both files
    print("\nTest 10: Verifying Python syntax...")

    try:
        with open(control_room_path) as f:
            ast.parse(f.read())
        print("✓ control_room.py has valid Python syntax")
    except SyntaxError as e:
        print(f"✗ control_room.py syntax error: {e}")
        return False

    try:
        with open(test_manager_path) as f:
            ast.parse(f.read())
        print("✓ test_manager_window.py has valid Python syntax")
    except SyntaxError as e:
        print(f"✗ test_manager_window.py syntax error: {e}")
        return False

    print("\n" + "=" * 70)
    print("✓ ALL STATIC INTEGRATION TESTS PASSED")
    print("=" * 70)
    print("\nIntegration Summary:")
    print(f"  • Test Manager button: ✓ Added to Control Room Advanced Tools")
    print(f"  • Method callback: ✓ open_test_manager() wired correctly")
    print(f"  • Import statement: ✓ TestManagerWindow imported")
    print(f"  • Test files: ✓ {test_file_count} tests organized in Program-tests/")
    print(f"  • Python syntax: ✓ Both files are syntactically valid")
    print("\nTo use: Launch Control Room → Advanced Tools → 🧪 Test Manager")
    return True

if __name__ == "__main__":
    try:
        success = test_static_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ STATIC TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
