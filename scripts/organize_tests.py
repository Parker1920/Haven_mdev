"""
Organize Test Scripts into Program-tests Folder
Creates structured test organization and moves all test files
"""

import shutil
import os
from pathlib import Path
from datetime import datetime

ROOT = Path("/Users/parkerstouffer/Desktop/Haven_mdev")

# Define test file organization
TEST_ORGANIZATION = {
    "Control-Room": {
        "Database": [
            "tests/test_phase1.py",
            "tests/test_yh_database_integration.py",
            "tests/check_db_planets.py",
            "tests/create_vh_database.py"
        ],
        "UI": [
            "tests/test_interactive_ui.py",
            "tests/test_bundle_integrity.py"
        ],
        "Integration": [
            "tests/test_phase2.py",
            "tests/test_integration.py",
            "tests/test_comprehensive_integration.py",
            "tests/test_data_source_unification.py",
            "tests/verify_complete_system.py"
        ],
        "Performance": [
            "tests/load_testing/verify_load_testing.py",
            "tests/load_testing/generate_load_test_db.py",
            "tests/stress_testing/generate_test_data.py",
            "tests/stress_testing/stress_test_performance.py",
            "tests/stress_testing/quick_stress_test.py",
            "tests/stress_testing/generate_100k_stress_test.py"
        ]
    },
    "Wizard": {
        "Data-Entry": [
            "tests/test_phase3.py",
            "tests/test_space_station_feature.py",
            "tests/generate_keeper_test_data.py"
        ],
        "Validation": [
            "tests/validation/test_wizard_validation.py",
            "tests/validation/test_system_entry_validation.py",
            "tests/unit/test_validation.py"
        ],
        "Save-Load": [
            "tests/test_wizard_save_fix.py",
            "tests/test_wizard_data_source.py",
            "tests/unit/test_file_lock.py"
        ]
    },
    "Keeper": {
        "Discovery-System": [
            "scripts/utils/check_discovery.py"
        ],
        "Pattern-Recognition": [],
        "Database": [],
        "Integration": [
            "tests/test_phase4.py",
            "tests/test_phase6.py"
        ]
    },
    "Map-Generation": {
        "Rendering": [
            "tests/test_map_generation.py",
            "tests/test_map_data_access.py",
            "tests/test_map_data_switching.py",
            "tests/test_map_opening.py"
        ],
        "Moon-Visualization": [
            "tests/verify_moon_orbits.py",
            "tests/verify_no_moon_duplicates.py"
        ]
    },
    "User-Edition": {
        "Packaging": [
            "tests/test_user_edition.py",
            "tests/test_user_edition_simple.py",
            "tests/test_user_edition_comprehensive.py"
        ]
    },
    "Utilities": {
        "Diagnostic-Scripts": [
            "scripts/diagnose_errors.py",
            "tests/debug_solar.py",
            "tests/verify_phase2.py"
        ],
        "Data-Verification": [
            "tests/check_json_planets.py",
            "tests/check_html_planets.py",
            "scripts/utils/test_parse.py"
        ]
    },
    "Security": {
        "Input-Sanitization": [
            "tests/security/test_input_sanitization.py",
            "tests/security/test_sanitization_functions.py"
        ]
    }
}

# Special files to keep in original location
KEEP_IN_PLACE = [
    "tests/conftest.py",  # Pytest configuration
    "tests/stress_testing/TESTING.json"  # Test data
]

def create_folder_structure():
    """Create Program-tests folder structure"""
    program_tests = ROOT / "Program-tests"
    program_tests.mkdir(exist_ok=True)

    print("📁 Creating folder structure...")
    for category, subcategories in TEST_ORGANIZATION.items():
        for subcategory in subcategories.keys():
            folder = program_tests / category / subcategory
            folder.mkdir(parents=True, exist_ok=True)
            print(f"   ✓ {category}/{subcategory}/")

    return program_tests

def move_test_files(program_tests):
    """Move test files to new structure"""
    print("\n📦 Moving test files...")

    moved_count = 0
    error_count = 0

    for category, subcategories in TEST_ORGANIZATION.items():
        for subcategory, files in subcategories.items():
            if not files:  # Skip empty categories
                continue

            print(f"\n{category}/{subcategory}:")

            for file_path in files:
                source = ROOT / file_path

                if not source.exists():
                    print(f"   ⊘ {source.name} (NOT FOUND)")
                    continue

                # Create target path
                target_dir = program_tests / category / subcategory
                target = target_dir / source.name

                try:
                    # Move file
                    shutil.move(str(source), str(target))
                    moved_count += 1
                    print(f"   ✓ {source.name}")
                except Exception as e:
                    error_count += 1
                    print(f"   ❌ {source.name}: {e}")

    return moved_count, error_count

def create_manifest(program_tests, moved_count):
    """Create manifest file documenting organization"""
    manifest = program_tests / "TEST_MANIFEST.md"

    content = f"""# Haven Program Tests - Organization Manifest

**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Test Files**: {moved_count}

## Folder Structure

### Control-Room
Tests for Haven Control Room application, database operations, and UI components.

- **Database/** - Database migration, integrity, and integration tests
- **UI/** - User interface component tests
- **Integration/** - Multi-component integration tests
- **Performance/** - Load testing, stress testing, and performance benchmarks

### Wizard
Tests for System Entry Wizard data entry and validation.

- **Data-Entry/** - System/planet/moon data entry tests
- **Validation/** - Input validation and schema compliance tests
- **Save-Load/** - File operations, locking, and persistence tests

### Keeper
Tests for The Keeper Discord bot integration.

- **Discovery-System/** - Discovery submission and tracking tests
- **Pattern-Recognition/** - Pattern detection algorithm tests
- **Database/** - Keeper database operations
- **Integration/** - Haven-Keeper integration tests

### Map-Generation
Tests for 3D map generation and visualization.

- **Rendering/** - Map generation pipeline and HTML output tests
- **Moon-Visualization/** - Moon orbit rendering and nesting tests

### User-Edition
Tests for packaged User Edition executable.

- **Packaging/** - Bundled application functionality tests

### Utilities
Diagnostic and verification utilities.

- **Diagnostic-Scripts/** - Error analysis and debugging tools
- **Data-Verification/** - Data integrity verification scripts

### Security
Security and input sanitization tests.

- **Input-Sanitization/** - XSS, SQL injection, path traversal tests

## Usage

### Running Individual Tests
```bash
python Program-tests/Control-Room/Database/test_phase1.py
```

### Running with Pytest
```bash
pytest Program-tests/Control-Room/Database/
```

### Using Test Manager UI
Launch from Haven Control Room → Advanced Tools → Test Manager

## Adding New Tests

1. Place test script in appropriate category/subcategory folder
2. Test will automatically appear in Test Manager UI
3. Follow naming convention: `test_*.py` for pytest compatibility

## Notes

- All tests use relative imports and are location-independent
- Tests automatically adjust paths using `Path(__file__).parent`
- Pytest configuration remains in `tests/conftest.py`
- Test data files remain in original locations (STRESS_TESTING.json, etc.)

---

*Generated by Haven Test Organization Script*
"""

    with open(manifest, 'w') as f:
        f.write(content)

    print(f"\n✅ Manifest created: {manifest.relative_to(ROOT)}")

def cleanup_empty_folders():
    """Remove empty test folders after migration"""
    print("\n🧹 Cleaning up empty folders...")

    folders_to_check = [
        ROOT / "tests/validation",
        ROOT / "tests/unit",
        ROOT / "tests/security",
        ROOT / "tests/load_testing",
        ROOT / "tests/stress_testing"
    ]

    for folder in folders_to_check:
        if folder.exists() and not any(folder.iterdir()):
            folder.rmdir()
            print(f"   ✓ Removed empty: {folder.relative_to(ROOT)}")

def main():
    """Main organization process"""
    print("="*70)
    print("HAVEN TEST SCRIPT ORGANIZATION")
    print("="*70)
    print()

    # Create backup
    print("💾 Creating backup...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = ROOT / "Archive-Dump" / f"tests_backup_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Backup entire tests folder
    if (ROOT / "tests").exists():
        shutil.copytree(ROOT / "tests", backup_dir / "tests")
        print(f"   ✓ Backed up tests/ → {backup_dir.relative_to(ROOT)}")

    # Create folder structure
    program_tests = create_folder_structure()

    # Move files
    moved_count, error_count = move_test_files(program_tests)

    # Create manifest
    create_manifest(program_tests, moved_count)

    # Cleanup
    cleanup_empty_folders()

    # Summary
    print("\n" + "="*70)
    print("ORGANIZATION COMPLETE")
    print("="*70)
    print(f"Files moved: {moved_count}")
    print(f"Errors: {error_count}")
    print(f"\n📂 Test folder: Program-tests/")
    print(f"💾 Backup: {backup_dir.relative_to(ROOT)}")
    print(f"📄 Manifest: Program-tests/TEST_MANIFEST.md")
    print("\nNext: Add Test Manager button to Control Room")

if __name__ == "__main__":
    main()
