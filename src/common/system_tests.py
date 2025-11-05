"""
System Test Runner - Interactive test suite for Haven Control Room

Provides unified interface to run various tests on the system including:
- Validation tests (wizard, schema, coordinates)
- Security tests (input sanitization, XSS, injection)
- Unit tests (file operations, constants)
- Stress tests (large datasets, memory optimization)

All tests are current and integrated with the latest codebase.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any
import json


class SystemTest:
    """Represents a single test that can be run."""
    
    def __init__(self, name: str, description: str, command: List[str], category: str):
        """Initialize a test.
        
        Args:
            name: Display name of the test
            description: Short description of what it tests
            command: Command to run the test
            category: Category (validation, security, unit, stress)
        """
        self.name = name
        self.description = description
        self.command = command
        self.category = category
        self.passed = False
        self.output = ""
        self.error = ""

    def run(self) -> Tuple[bool, str, str]:
        """Run the test and capture output.

        Returns:
            Tuple of (success: bool, stdout: str, stderr: str)
        """
        try:
            result = subprocess.run(
                self.command,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8',
                errors='replace'
            )
            self.output = result.stdout
            self.error = result.stderr
            self.passed = result.returncode == 0
            return self.passed, self.output, self.error
        except subprocess.TimeoutExpired:
            self.passed = False
            self.error = "Test timed out (60 seconds)"
            return False, "", self.error
        except Exception as e:
            self.passed = False
            self.error = str(e)
            return False, "", self.error


class TestSuite:
    """Manages collection of available tests."""
    
    def __init__(self, project_root: Path):
        """Initialize test suite.
        
        Args:
            project_root: Root directory of the Haven project
        """
        self.project_root = project_root
        self.tests = self._discover_tests()

    def _discover_tests(self) -> Dict[str, List[SystemTest]]:
        """Discover available tests organized by category.
        
        Returns:
            Dict with categories as keys and lists of tests as values
        """
        tests = {
            "validation": [],
            "security": [],
            "unit": [],
            "stress": []
        }

        # =====================================================================
        # VALIDATION TESTS - Data structure and schema validation
        # =====================================================================
        
        tests["validation"].append(SystemTest(
            name="Wizard Data Structure",
            description="Validates wizard saves proper data structure",
            command=[sys.executable, "-m", "pytest", "-xvs",
                    "tests/validation/test_wizard_validation.py::test_wizard_data_structure"],
            category="validation"
        ))

        tests["validation"].append(SystemTest(
            name="Map Compatibility",
            description="Tests system data compatibility with map generation",
            command=[sys.executable, "-m", "pytest", "-xvs",
                    "tests/validation/test_wizard_validation.py::test_map_compatibility"],
            category="validation"
        ))

        tests["validation"].append(SystemTest(
            name="Unique Name Validation",
            description="Ensures system names are unique and valid",
            command=[sys.executable, "-m", "pytest", "-xvs",
                    "tests/validation/test_wizard_validation.py::test_unique_name_validation"],
            category="validation"
        ))

        tests["validation"].append(SystemTest(
            name="Required Fields",
            description="Validates all required fields are present",
            command=[sys.executable, "-m", "pytest", "-xvs",
                    "tests/validation/test_wizard_validation.py::test_required_fields"],
            category="validation"
        ))

        tests["validation"].append(SystemTest(
            name="Schema Validation",
            description="Tests data against JSON schema",
            command=[sys.executable, "-m", "pytest", "-xvs",
                    "tests/validation/test_wizard_validation.py::test_schema_validation"],
            category="validation"
        ))

        tests["validation"].append(SystemTest(
            name="Schema Compliance",
            description="Validates system entry schema compliance",
            command=[sys.executable, "-m", "pytest", "-xvs",
                    "tests/validation/test_system_entry_validation.py::test_schema_compliance"],
            category="validation"
        ))

        tests["validation"].append(SystemTest(
            name="Draft Autosave",
            description="Tests draft auto-save functionality",
            command=[sys.executable, "-m", "pytest", "-xvs",
                    "tests/validation/test_system_entry_validation.py::test_draft_autosave"],
            category="validation"
        ))

        tests["validation"].append(SystemTest(
            name="Theme File",
            description="Validates theme configuration file",
            command=[sys.executable, "-m", "pytest", "-xvs",
                    "tests/validation/test_system_entry_validation.py::test_theme_file"],
            category="validation"
        ))

        tests["validation"].append(SystemTest(
            name="Validation Logic",
            description="Tests core validation logic",
            command=[sys.executable, "-m", "pytest", "-xvs",
                    "tests/validation/test_system_entry_validation.py::test_validation_logic"],
            category="validation"
        ))

        # =====================================================================
        # UNIT TESTS - Core functionality validation
        # =====================================================================

        tests["unit"].append(SystemTest(
            name="Valid System",
            description="Tests valid system data passes validation",
            command=[sys.executable, "-m", "pytest", "-xvs",
                    "tests/unit/test_validation.py::test_valid_system"],
            category="unit"
        ))

        tests["unit"].append(SystemTest(
            name="Missing Required Fields",
            description="Tests detection of missing required fields",
            command=[sys.executable, "-m", "pytest", "-xvs",
                    "tests/unit/test_validation.py::test_missing_required_fields"],
            category="unit"
        ))

        tests["unit"].append(SystemTest(
            name="Invalid Coordinates",
            description="Tests coordinate validation",
            command=[sys.executable, "-m", "pytest", "-xvs",
                    "tests/unit/test_validation.py::test_invalid_coordinates"],
            category="unit"
        ))

        tests["unit"].append(SystemTest(
            name="Valid Complete Data File",
            description="Tests complete data file validation",
            command=[sys.executable, "-m", "pytest", "-xvs",
                    "tests/unit/test_validation.py::test_valid_complete_data_file"],
            category="unit"
        ))

        tests["unit"].append(SystemTest(
            name="Coordinate Validation",
            description="Tests coordinate range and format validation",
            command=[sys.executable, "-m", "pytest", "-xvs",
                    "tests/unit/test_validation.py::TestCoordinateValidation"],
            category="unit"
        ))

        tests["unit"].append(SystemTest(
            name="System Name Validation",
            description="Tests system name validation rules",
            command=[sys.executable, "-m", "pytest", "-xvs",
                    "tests/unit/test_validation.py::TestSystemNameValidation"],
            category="unit"
        ))

        tests["unit"].append(SystemTest(
            name="Planet Validation",
            description="Tests planet data validation",
            command=[sys.executable, "-m", "pytest", "-xvs",
                    "tests/unit/test_validation.py::test_planet_validation"],
            category="unit"
        ))

        tests["unit"].append(SystemTest(
            name="File Lock Operations",
            description="Tests file locking mechanism",
            command=[sys.executable, "-m", "pytest", "-xvs",
                    "tests/unit/test_file_lock.py"],
            category="unit"
        ))

        # =====================================================================
        # SECURITY TESTS - Input validation and attack prevention
        # =====================================================================

        tests["security"].append(SystemTest(
            name="Input Sanitization",
            description="Tests XSS, injection, and path traversal prevention",
            command=[sys.executable, "-m", "pytest", "-xvs",
                    "tests/security/test_input_sanitization.py"],
            category="security"
        ))

        tests["security"].append(SystemTest(
            name="Sanitization Functions",
            description="Tests individual sanitization functions",
            command=[sys.executable, "-m", "pytest", "-xvs",
                    "tests/security/test_sanitization_functions.py"],
            category="security"
        ))

        # =====================================================================
        # STRESS TESTS - Large dataset and performance testing
        # =====================================================================

        tests["stress"].append(SystemTest(
            name="Quick Stress Test (100K)",
            description="Tests 100K systems with memory optimization (9 seconds)",
            command=[sys.executable, "tests/stress_testing/quick_stress_test.py",
                    "--data-file", "tests/stress_testing/STRESS-100K.json"],
            category="stress"
        ))

        tests["stress"].append(SystemTest(
            name="Generate 100K Test Dataset",
            description="Generates 100K systems for stress testing (5-10 seconds)",
            command=[sys.executable, "tests/stress_testing/generate_100k_stress_test.py"],
            category="stress"
        ))

        tests["stress"].append(SystemTest(
            name="Generate 50K Test Dataset",
            description="Generates 50K systems for faster testing",
            command=[sys.executable, "tests/stress_testing/generate_100k_stress_test.py", "--small"],
            category="stress"
        ))

        tests["stress"].append(SystemTest(
            name="Map Generation (100K)",
            description="Tests map generation with 100K dataset",
            command=[sys.executable, "src/Beta_VH_Map.py",
                    "--data-file", "tests/stress_testing/STRESS-100K.json", "--no-open"],
            category="stress"
        ))

        return tests

    def get_tests_by_category(self, category: str = None) -> Dict[str, List[SystemTest]]:
        """Get tests filtered by category.
        
        Args:
            category: Category name or None for all
            
        Returns:
            Filtered dictionary of tests
        """
        if category is None:
            return self.tests
        return {category: self.tests.get(category, [])}

    def run_test(self, test: SystemTest) -> Tuple[bool, str, str]:
        """Run a single test.
        
        Args:
            test: Test to run
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        return test.run()

    def run_category(self, category: str) -> Dict[str, Any]:
        """Run all tests in a category.
        
        Args:
            category: Category name
            
        Returns:
            Dictionary with results for each test
        """
        results = {
            "category": category,
            "tests": [],
            "passed": 0,
            "failed": 0,
            "total": 0
        }
        
        tests = self.tests.get(category, [])
        for test in tests:
            results["total"] += 1
            success, stdout, stderr = self.run_test(test)
            results["tests"].append({
                "name": test.name,
                "passed": success,
                "output": stdout[:500],  # Truncate output
                "error": stderr[:500]
            })
            if success:
                results["passed"] += 1
            else:
                results["failed"] += 1
        
        return results

    def run_all(self) -> Dict[str, Any]:
        """Run all tests.
        
        Returns:
            Dictionary with results for all tests
        """
        results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "categories": {}
        }
        
        for category in self.tests.keys():
            cat_results = self.run_category(category)
            results["categories"][category] = cat_results
            results["total"] += cat_results["total"]
            results["passed"] += cat_results["passed"]
            results["failed"] += cat_results["failed"]
        
        return results


# ============================================================================
# Module-level functions for easy access
# ============================================================================

def get_test_suite(project_root: Path = None) -> TestSuite:
    """Get test suite instance.
    
    Args:
        project_root: Root directory (auto-detected if None)
        
    Returns:
        TestSuite instance
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent
    return TestSuite(project_root)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Haven Control Room System Tests")
    parser.add_argument("--category", help="Test category (validation, unit, security, stress)")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--list", action="store_true", help="List all available tests")
    
    args = parser.parse_args()
    
    suite = get_test_suite()
    
    if args.list:
        for category, tests in suite.tests.items():
            print(f"\n{category.upper()} TESTS ({len(tests)}):")
            for test in tests:
                print(f"  - {test.name}: {test.description}")
    
    elif args.all:
        print("Running all tests...\n")
        results = suite.run_all()
        print(f"Results: {results['passed']}/{results['total']} passed")
    
    elif args.category:
        print(f"Running {args.category} tests...\n")
        results = suite.run_category(args.category)
        print(f"Results: {results['passed']}/{results['total']} passed")
    
    else:
        print("Use --help for options")
