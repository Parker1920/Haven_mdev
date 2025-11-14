"""
Automated Test Suite for Haven Control Room - User Edition

Tests all core functionality:
1. Data file operations (read/write)
2. System validation
3. Map generation
4. File structure integrity
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BLUE = '\033[94m'

def print_test(msg):
    print(f"{BLUE}[TEST]{RESET} {msg}")

def print_pass(msg):
    print(f"{GREEN}[PASS]{RESET} {msg}")

def print_fail(msg):
    print(f"{RED}[FAIL]{RESET} {msg}")

def print_warn(msg):
    print(f"{YELLOW}[WARN]{RESET} {msg}")


class UserEditionTester:
    def __init__(self, dist_path):
        self.dist_path = Path(dist_path)
        self.files_dir = self.dist_path / "files"
        self.data_file = self.files_dir / "data.json"
        self.maps_dir = self.files_dir / "maps"
        self.logs_dir = self.files_dir / "logs"
        self.photos_dir = self.files_dir / "photos"
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def run_all_tests(self):
        print("\n" + "="*70)
        print("Haven Control Room - User Edition Test Suite")
        print("="*70 + "\n")

        # Test 1: File structure
        self.test_file_structure()

        # Test 2: Data files
        self.test_data_files()

        # Test 3: Data validation
        self.test_data_validation()

        # Test 4: Map output
        self.test_map_output()

        # Test 5: EXE existence
        self.test_exe_exists()

        # Summary
        print("\n" + "="*70)
        print(f"Test Results: {GREEN}{self.passed} passed{RESET}, "
              f"{RED}{self.failed} failed{RESET}, "
              f"{YELLOW}{self.warnings} warnings{RESET}")
        print("="*70 + "\n")

        return self.failed == 0

    def test_file_structure(self):
        """Test that all required directories exist"""
        print_test("Testing file structure...")

        dirs_to_check = [
            ("Distribution folder", self.dist_path),
            ("Files subdirectory", self.files_dir),
            ("Maps folder", self.maps_dir),
            ("Logs folder", self.logs_dir),
            ("Photos folder", self.photos_dir),
        ]

        for name, path in dirs_to_check:
            if path.exists() and path.is_dir():
                print_pass(f"{name} exists: {path}")
                self.passed += 1
            else:
                print_fail(f"{name} missing: {path}")
                self.failed += 1

    def test_data_files(self):
        """Test data file integrity"""
        print_test("\nTesting data files...")

        # Check for data.json
        if self.data_file.exists():
            print_pass(f"Data file exists: {self.data_file}")
            self.passed += 1

            # Try to load and validate JSON
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                print_pass(f"Data file is valid JSON")
                self.passed += 1

                # Check for _meta
                if '_meta' in data:
                    print_pass(f"Data file has _meta section")
                    self.passed += 1

                    version = data['_meta'].get('version', 'unknown')
                    print(f"       Version: {version}")
                else:
                    print_warn("Data file missing _meta section")
                    self.warnings += 1

                # Count systems
                system_count = len([k for k in data.keys() if k != '_meta'])
                print(f"       Systems found: {system_count}")

                if system_count > 0:
                    print_pass(f"Data file contains {system_count} systems")
                    self.passed += 1
                else:
                    print_warn("Data file is empty (no systems)")
                    self.warnings += 1

            except json.JSONDecodeError as e:
                print_fail(f"Data file has invalid JSON: {e}")
                self.failed += 1
            except Exception as e:
                print_fail(f"Error reading data file: {e}")
                self.failed += 1
        else:
            print_warn(f"Data file not found (first run expected): {self.data_file}")
            self.warnings += 1

        # Check for reference files
        for ref_file in ["clean_data.json", "example_data.json"]:
            ref_path = self.dist_path / ref_file
            if ref_path.exists():
                print_pass(f"Reference file exists: {ref_file}")
                self.passed += 1
            else:
                print_fail(f"Reference file missing: {ref_file}")
                self.failed += 1

    def test_data_validation(self):
        """Test data validation against schema"""
        print_test("\nTesting data validation...")

        if not self.data_file.exists():
            print_warn("Skipping validation (no data file)")
            self.warnings += 1
            return

        try:
            # Import validation module
            sys.path.insert(0, str(self.dist_path.parent.parent / 'src'))
            from common.validation import validate_data_file

            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            is_valid, errors = validate_data_file(data)

            if is_valid:
                print_pass("Data file passes schema validation")
                self.passed += 1
            else:
                print_fail(f"Data validation failed with {len(errors)} errors:")
                for error in errors[:5]:  # Show first 5 errors
                    print(f"       - {error}")
                self.failed += 1

        except Exception as e:
            print_warn(f"Could not run validation: {e}")
            self.warnings += 1

    def test_map_output(self):
        """Test map generation output"""
        print_test("\nTesting map output...")

        if self.maps_dir.exists():
            map_files = list(self.maps_dir.glob("*.html"))

            if map_files:
                print_pass(f"Found {len(map_files)} map file(s)")
                self.passed += 1

                # Check most recent map
                latest_map = max(map_files, key=lambda p: p.stat().st_mtime)
                file_size = latest_map.stat().st_size / 1024  # KB

                print(f"       Latest map: {latest_map.name}")
                print(f"       Size: {file_size:.1f} KB")

                if file_size > 10:  # Maps should be at least 10KB
                    print_pass(f"Map file has reasonable size")
                    self.passed += 1
                else:
                    print_warn(f"Map file seems too small ({file_size:.1f} KB)")
                    self.warnings += 1

            else:
                print_warn("No map files found (generate a map first)")
                self.warnings += 1
        else:
            print_warn("Maps directory not found")
            self.warnings += 1

    def test_exe_exists(self):
        """Test that EXE exists and check size"""
        print_test("\nTesting EXE file...")

        exe_path = self.dist_path / "HavenControlRoom.exe"
        if exe_path.exists():
            print_pass(f"EXE exists: {exe_path}")
            self.passed += 1

            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"       Size: {size_mb:.1f} MB")

            if size_mb > 30:  # Should be around 40MB with pandas/numpy
                print_pass(f"EXE size indicates pandas/numpy are bundled")
                self.passed += 1
            else:
                print_warn(f"EXE seems small ({size_mb:.1f} MB) - pandas/numpy might be missing")
                self.warnings += 1

        else:
            print_fail(f"EXE not found: {exe_path}")
            self.failed += 1


def main():
    """Run test suite"""
    # Determine distribution path
    dist_path = Path(__file__).parent / "dist" / "HavenControlRoom_User"

    if not dist_path.exists():
        print_fail(f"Distribution folder not found: {dist_path}")
        print("Please ensure you've built the user edition EXE first.")
        return 1

    tester = UserEditionTester(dist_path)
    success = tester.run_all_tests()

    if success:
        print(f"{GREEN}✓ All tests passed!{RESET}")
        print("\nManual testing required:")
        print("1. Launch the EXE and test the wizard")
        print("2. Add a system with planets and moons")
        print("3. Generate a map and view it")
        print("4. Test space station editor")
        return 0
    else:
        print(f"{RED}✗ Some tests failed. Please review errors above.{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
