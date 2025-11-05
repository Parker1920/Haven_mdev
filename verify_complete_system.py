#!/usr/bin/env python3
"""
Complete System Verification Script

This script runs all test suites and provides a comprehensive
verification report for the Haven Control Room project.

Usage:
    python verify_complete_system.py
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

# ANSI colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'


def print_header(text):
    """Print a formatted header."""
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{text.center(70)}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")


def print_success(text):
    """Print success message."""
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text):
    """Print error message."""
    print(f"{RED}❌ {text}{RESET}")


def print_warning(text):
    """Print warning message."""
    print(f"{YELLOW}⚠️  {text}{RESET}")


def print_info(text):
    """Print info message."""
    print(f"{BLUE}ℹ️  {text}{RESET}")


def run_test_suite(test_file):
    """
    Run a test suite and return results.
    
    Args:
        test_file: Path to test file
        
    Returns:
        tuple: (success: bool, output: str)
    """
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',  # Replace invalid characters instead of failing
            timeout=30
        )
        success = result.returncode == 0 and "FAILED" not in result.stdout
        return success, result.stdout
    except subprocess.TimeoutExpired:
        return False, "Test suite timed out after 30 seconds"
    except Exception as e:
        return False, f"Error running test: {e}"


def main():
    """Main verification script."""
    print_header("HAVEN CONTROL ROOM - COMPLETE SYSTEM VERIFICATION")
    print_info(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Python: {sys.version.split()[0]}")
    print()
    
    # Define test suites
    test_suites = [
        {
            'name': 'Phase 2: Control Room Integration',
            'file': 'test_phase2.py',
            'description': 'Data provider, backend switching, UI integration'
        },
        {
            'name': 'Phase 3: Wizard Integration',
            'file': 'test_phase3.py',
            'description': 'System Entry Wizard database integration'
        },
        {
            'name': 'Phase 4: Map Generator Integration',
            'file': 'test_phase4.py',
            'description': 'Map generator database backend'
        },
        {
            'name': 'Phase 6: Production Deployment',
            'file': 'test_phase6.py',
            'description': 'Comprehensive production readiness'
        }
    ]
    
    # Track results
    results = []
    total_tests = 0
    passed_tests = 0
    
    # Run each test suite
    for suite in test_suites:
        print_header(suite['name'])
        print_info(f"Description: {suite['description']}")
        print_info(f"Running: {suite['file']}")
        print()
        
        success, output = run_test_suite(suite['file'])
        
        # Parse results
        if success:
            # Try to extract test count from output
            if "RESULTS:" in output:
                for line in output.split('\n'):
                    if "RESULTS:" in line:
                        # Extract "X/Y tests passed"
                        parts = line.split("RESULTS:")[1].strip()
                        if "/" in parts:
                            test_counts = parts.split()[0]
                            passed, total = map(int, test_counts.split('/'))
                            total_tests += total
                            passed_tests += passed
                            print_success(f"{suite['name']}: {test_counts} tests passed")
                            results.append((suite['name'], True, test_counts))
                            break
            else:
                # For Phase 2/3 which have different output format
                if "ALL TESTS PASSED" in output:
                    # Count test lines
                    test_count = output.count("[TEST")
                    total_tests += test_count
                    passed_tests += test_count
                    print_success(f"{suite['name']}: {test_count}/{test_count} tests passed")
                    results.append((suite['name'], True, f"{test_count}/{test_count}"))
        else:
            print_error(f"{suite['name']}: FAILED")
            results.append((suite['name'], False, "FAILED"))
            # Print error details
            if output:
                print("\nError details:")
                print(output[:500])  # Print first 500 chars of error
        
        print()
    
    # Print summary
    print_header("VERIFICATION SUMMARY")
    
    print(f"\n{BOLD}Test Suite Results:{RESET}")
    for name, success, count in results:
        if success:
            print_success(f"{name}: {count}")
        else:
            print_error(f"{name}: {count}")
    
    print(f"\n{BOLD}Overall Statistics:{RESET}")
    print(f"  Total Tests Run: {total_tests}")
    print(f"  Tests Passed: {passed_tests}")
    print(f"  Tests Failed: {total_tests - passed_tests}")
    print(f"  Success Rate: {(passed_tests/total_tests*100) if total_tests > 0 else 0:.1f}%")
    
    # Final status
    print()
    if passed_tests == total_tests and total_tests > 0:
        print_success("🎉 ALL TESTS PASSED - SYSTEM IS PRODUCTION READY!")
        print_info(f"Documentation: See PHASE_6_COMPLETE.md and COMPLETE_INTEGRATION_SUMMARY.md")
        return 0
    else:
        print_error("⚠️  SOME TESTS FAILED - REVIEW ERRORS ABOVE")
        return 1


if __name__ == "__main__":
    sys.exit(main())
