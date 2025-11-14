"""
Test Sanitization Functions

Verifies that the sanitization functions in common.sanitize properly
protect against various attack vectors.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from common.sanitize import (
    sanitize_html,
    sanitize_system_name,
    is_safe_path,
    sanitize_filename,
    sanitize_coordinate,
    sanitize_unicode,
    sanitize_user_input,
    validate_json_keys
)


def test_xss_prevention():
    """Test XSS attack prevention."""
    print("\n[TEST] XSS Prevention")
    print("=" * 70)

    attacks = [
        '<script>alert("XSS")</script>',
        '<img src=x onerror=alert("XSS")>',
        'javascript:alert("XSS")',
    ]

    passed = True
    for attack in attacks:
        result = sanitize_html(attack)
        if '<script' in result or 'javascript:' in result or 'onerror' in result:
            print(f"  [FAIL] XSS not sanitized: {attack[:40]}")
            passed = False
        else:
            print(f"  [OK] Sanitized: {attack[:40]} -> {result[:40]}")

    return passed


def test_path_traversal_prevention():
    """Test path traversal prevention."""
    print("\n[TEST] Path Traversal Prevention")
    print("=" * 70)

    safe_paths = [
        'data/systems.json',
        'dist/VH-Map.html',
    ]

    dangerous_paths = [
        '../../etc/passwd',
        '../../../../../etc/shadow',
        'C:\\Windows\\System32',
        '/etc/passwd',
        '%2e%2e%2fetc%2fpasswd',
    ]

    passed = True

    for path in safe_paths:
        if not is_safe_path(path):
            print(f"  [FAIL] Safe path rejected: {path}")
            passed = False
        else:
            print(f"  [OK] Safe path accepted: {path}")

    for path in dangerous_paths:
        if is_safe_path(path):
            print(f"  [FAIL] Dangerous path accepted: {path}")
            passed = False
        else:
            print(f"  [OK] Dangerous path rejected: {path}")

    return passed


def test_filename_sanitization():
    """Test filename sanitization."""
    print("\n[TEST] Filename Sanitization")
    print("=" * 70)

    tests = [
        ('../../../etc/passwd', 'etc_passwd'),
        ('system<script>.json', 'system_script_.json'),
        ('CON', 'file_CON'),
        ('normal_file.json', 'normal_file.json'),
    ]

    passed = True
    for input_name, expected in tests:
        result = sanitize_filename(input_name)
        # Check that no dangerous chars remain
        if any(c in result for c in ['..', '/', '\\', '<', '>']):
            print(f"  [FAIL] Dangerous chars in: {input_name} -> {result}")
            passed = False
        else:
            print(f"  [OK] Sanitized: {input_name} -> {result}")

    return passed


def test_coordinate_validation():
    """Test coordinate validation."""
    print("\n[TEST] Coordinate Validation")
    print("=" * 70)

    tests = [
        (50.5, -100, 100, 50.5),  # Valid
        (150, -100, 100, 100),  # Clamped to max
        (-150, -100, 100, -100),  # Clamped to min
        ('Infinity', -100, 100, 0.0),  # Rejected
        ('NaN', -100, 100, 0.0),  # Rejected
    ]

    passed = True
    for value, min_val, max_val, expected in tests:
        result = sanitize_coordinate(value, min_val, max_val, 0.0)
        if result == expected:
            print(f"  [OK] {value} -> {result}")
        else:
            print(f"  [FAIL] {value} -> {result} (expected {expected})")
            passed = False

    return passed


def test_unicode_sanitization():
    """Test Unicode attack prevention."""
    print("\n[TEST] Unicode Sanitization")
    print("=" * 70)

    attacks = [
        'test\u202egnitseuqer',  # RTL override
        'test\u200b\u200c\u200dmalicious',  # Zero-width chars
    ]

    passed = True
    for attack in attacks:
        result = sanitize_unicode(attack)
        if '\u202e' in result or '\u200b' in result:
            print(f"  [FAIL] Unicode not sanitized: {repr(attack)}")
            passed = False
        else:
            print(f"  [OK] Sanitized: {repr(attack)} -> {repr(result)}")

    return passed


def test_json_validation():
    """Test JSON prototype pollution prevention."""
    print("\n[TEST] JSON Validation (Prototype Pollution)")
    print("=" * 70)

    passed = True

    # Safe JSON
    safe_json = {"name": "test", "value": 123}
    try:
        validate_json_keys(safe_json)
        print(f"  [OK] Safe JSON accepted")
    except ValueError:
        print(f"  [FAIL] Safe JSON rejected")
        passed = False

    # Dangerous JSON
    dangerous_jsons = [
        {"__proto__": {"polluted": True}},
        {"constructor": {"prototype": {"polluted": True}}},
    ]

    for dangerous in dangerous_jsons:
        try:
            validate_json_keys(dangerous)
            print(f"  [FAIL] Dangerous JSON accepted: {list(dangerous.keys())}")
            passed = False
        except ValueError:
            print(f"  [OK] Dangerous JSON rejected: {list(dangerous.keys())}")

    return passed


def run_all_tests():
    """Run all sanitization function tests."""
    # Set UTF-8 for Windows
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    print("\n" + "=" * 70)
    print("[SECURITY] Sanitization Function Tests")
    print("=" * 70)

    tests = [
        ("XSS Prevention", test_xss_prevention),
        ("Path Traversal Prevention", test_path_traversal_prevention),
        ("Filename Sanitization", test_filename_sanitization),
        ("Coordinate Validation", test_coordinate_validation),
        ("Unicode Sanitization", test_unicode_sanitization),
        ("JSON Validation", test_json_validation),
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
        print("  [SUCCESS] ALL SANITIZATION FUNCTIONS WORKING!")
    else:
        print(f"  [WARN] {total_count - passed_count} test(s) failed")

    print("=" * 70 + "\n")

    return passed_count == total_count


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
