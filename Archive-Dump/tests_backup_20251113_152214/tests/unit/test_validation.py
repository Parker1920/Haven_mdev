"""
Test JSON Schema Validation

Tests the validation module to ensure it properly validates system data
against the JSON schema and catches various error conditions.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from common.validation import (
    validate_system_data,
    validate_data_file,
    validate_coordinates,
    validate_system_name,
    validate_planet_data,
    generate_validation_report
)


def test_valid_system():
    """Test that a valid system passes validation."""
    print("\n[TEST] Valid System Data")
    print("=" * 70)

    system = {
        "id": "SYS_EUCLID_TEST",
        "name": "Test System",
        "region": "Euclid",
        "x": 50.5,
        "y": -30.2,
        "z": 10.7,
        "planets": []
    }

    is_valid, error = validate_system_data(system)

    if is_valid:
        print(f"  [OK] Valid system accepted")
        return True
    else:
        print(f"  [FAIL] Valid system rejected: {error}")
        return False


def test_missing_required_fields():
    """Test that systems missing required fields are rejected."""
    print("\n[TEST] Missing Required Fields")
    print("=" * 70)

    required_fields = ["id", "name", "region", "x", "y", "z"]
    passed = 0
    failed = 0

    for field in required_fields:
        system = {
            "id": "SYS_TEST",
            "name": "Test",
            "region": "Test Region",
            "x": 0,
            "y": 0,
            "z": 0,
            "planets": []
        }
        del system[field]

        is_valid, error = validate_system_data(system)

        if not is_valid and field in error:
            print(f"  [OK] Missing '{field}' detected: {error[:50]}...")
            passed += 1
        else:
            print(f"  [FAIL] Missing '{field}' not detected")
            failed += 1

    return failed == 0


def test_invalid_coordinates():
    """Test that out-of-range coordinates are rejected."""
    print("\n[TEST] Invalid Coordinates")
    print("=" * 70)

    invalid_coords = [
        (150, 0, 0, "X out of range"),
        (0, 150, 0, "Y out of range"),
        (0, 0, 30, "Z out of range"),
        (-150, 0, 0, "X negative out of range"),
    ]

    passed = 0
    failed = 0

    for x, y, z, description in invalid_coords:
        system = {
            "id": "SYS_TEST",
            "name": "Test",
            "region": "Test",
            "x": x,
            "y": y,
            "z": z,
            "planets": []
        }

        is_valid, error = validate_system_data(system)

        if not is_valid:
            print(f"  [OK] {description} rejected: {error[:50]}...")
            passed += 1
        else:
            print(f"  [FAIL] {description} not detected")
            failed += 1

    return failed == 0


def test_valid_complete_data_file():
    """Test that a complete valid data file passes validation."""
    print("\n[TEST] Valid Complete Data File")
    print("=" * 70)

    data = {
        "_meta": {
            "version": "3.0.0"
        },
        "System 1": {
            "id": "SYS_EUCLID_001",
            "name": "System 1",
            "region": "Euclid",
            "x": 10.0,
            "y": 20.0,
            "z": 5.0,
            "planets": [
                {
                    "name": "Planet A",
                    "sentinel": "Low",
                    "moons": [
                        {"name": "Moon 1"}
                    ]
                }
            ]
        },
        "System 2": {
            "id": "SYS_EUCLID_002",
            "name": "System 2",
            "region": "Euclid",
            "x": -10.0,
            "y": -20.0,
            "z": -5.0,
            "planets": []
        }
    }

    is_valid, errors = validate_data_file(data)

    if is_valid:
        print(f"  [OK] Valid data file accepted")
        return True
    else:
        print(f"  [FAIL] Valid data file rejected:")
        for error in errors:
            print(f"    - {error}")
        return False


def test_missing_meta():
    """Test that data file without _meta is rejected."""
    print("\n[TEST] Missing _meta")
    print("=" * 70)

    data = {
        "System 1": {
            "id": "SYS_001",
            "name": "System 1",
            "region": "Test",
            "x": 0,
            "y": 0,
            "z": 0,
            "planets": []
        }
    }

    is_valid, errors = validate_data_file(data)

    if not is_valid and any("_meta" in error for error in errors):
        print(f"  [OK] Missing _meta detected")
        return True
    else:
        print(f"  [FAIL] Missing _meta not detected")
        return False


def test_coordinate_validation():
    """Test coordinate validation function."""
    print("\n[TEST] Coordinate Validation Function")
    print("=" * 70)

    test_cases = [
        (0, 0, 0, True, "Valid coordinates"),
        (100, 100, 25, True, "Max valid coordinates"),
        (-100, -100, -25, True, "Min valid coordinates"),
        (101, 0, 0, False, "X too large"),
        (0, 101, 0, False, "Y too large"),
        (0, 0, 26, False, "Z too large"),
    ]

    passed = 0
    failed = 0

    for x, y, z, should_be_valid, description in test_cases:
        is_valid, error = validate_coordinates(x, y, z)

        if is_valid == should_be_valid:
            print(f"  [OK] {description}")
            passed += 1
        else:
            print(f"  [FAIL] {description}: expected={should_be_valid}, got={is_valid}")
            if error:
                print(f"       Error: {error}")
            failed += 1

    return failed == 0


def test_system_name_validation():
    """Test system name validation."""
    print("\n[TEST] System Name Validation")
    print("=" * 70)

    test_cases = [
        ("Valid System Name", True, "Normal name"),
        ("System-123", True, "Name with hyphen and numbers"),
        ("", False, "Empty name"),
        ("   ", False, "Whitespace only"),
        ("A" * 101, False, "Name too long"),
        ("System<script>", False, "Name with dangerous char"),
    ]

    passed = 0
    failed = 0

    for name, should_be_valid, description in test_cases:
        is_valid, error = validate_system_name(name)

        if is_valid == should_be_valid:
            print(f"  [OK] {description}")
            passed += 1
        else:
            print(f"  [FAIL] {description}: expected={should_be_valid}, got={is_valid}")
            if error:
                print(f"       Error: {error}")
            failed += 1

    return failed == 0


def test_planet_validation():
    """Test planet data validation."""
    print("\n[TEST] Planet Data Validation")
    print("=" * 70)

    test_cases = [
        ({"name": "Planet A"}, True, "Basic planet"),
        ({"name": "Planet B", "sentinel": "Low", "moons": []}, True, "Planet with sentinel and moons"),
        ({}, False, "Missing name"),
        ({"name": ""}, False, "Empty name"),
        ({"name": "Planet C", "sentinel": "Invalid"}, False, "Invalid sentinel level"),
        ({"name": "Planet D", "moons": [{}]}, False, "Moon missing name"),
    ]

    passed = 0
    failed = 0

    for planet, should_be_valid, description in test_cases:
        is_valid, error = validate_planet_data(planet)

        if is_valid == should_be_valid:
            print(f"  [OK] {description}")
            passed += 1
        else:
            print(f"  [FAIL] {description}: expected={should_be_valid}, got={is_valid}")
            if error:
                print(f"       Error: {error}")
            failed += 1

    return failed == 0


def test_validation_report():
    """Test validation report generation."""
    print("\n[TEST] Validation Report Generation")
    print("=" * 70)

    data = {
        "_meta": {"version": "3.0.0"},
        "System 1": {
            "id": "SYS_001",
            "name": "System 1",
            "region": "Euclid",
            "x": 0,
            "y": 0,
            "z": 0,
            "planets": [
                {
                    "name": "Planet A",
                    "moons": [{"name": "Moon 1"}, {"name": "Moon 2"}]
                }
            ]
        },
        "System 2": {
            "id": "SYS_002",
            "name": "System 2",
            "region": "Hilbert",
            "x": 10,
            "y": 10,
            "z": 5,
            "planets": []
        }
    }

    report = generate_validation_report(data)

    checks = [
        (report["valid"], "Report shows valid"),
        (report["stats"]["total_systems"] == 2, "Counted 2 systems"),
        (report["stats"]["total_planets"] == 1, "Counted 1 planet"),
        (report["stats"]["total_moons"] == 2, "Counted 2 moons"),
        (len(report["stats"]["regions"]) == 2, "Found 2 regions"),
    ]

    passed = 0
    failed = 0

    for check, description in checks:
        if check:
            print(f"  [OK] {description}")
            passed += 1
        else:
            print(f"  [FAIL] {description}")
            print(f"       Report: {report}")
            failed += 1

    return failed == 0


def run_all_tests():
    """Run all validation tests."""
    # Set UTF-8 encoding for Windows
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    print("\n" + "=" * 70)
    print("[VALIDATION] JSON Schema Validation Tests")
    print("=" * 70)

    tests = [
        ("Valid System Data", test_valid_system),
        ("Missing Required Fields", test_missing_required_fields),
        ("Invalid Coordinates", test_invalid_coordinates),
        ("Valid Complete Data File", test_valid_complete_data_file),
        ("Missing _meta", test_missing_meta),
        ("Coordinate Validation Function", test_coordinate_validation),
        ("System Name Validation", test_system_name_validation),
        ("Planet Data Validation", test_planet_validation),
        ("Validation Report Generation", test_validation_report),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n  [FAIL] Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "=" * 70)
    print("[SUMMARY] Test Results")
    print("=" * 70)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {name}")

    print("\n" + "=" * 70)
    print(f"  Total: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("  [SUCCESS] ALL VALIDATION TESTS PASSED!")
    else:
        print(f"  [WARN] {total_count - passed_count} test(s) failed")

    print("=" * 70 + "\n")

    return passed_count == total_count


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
