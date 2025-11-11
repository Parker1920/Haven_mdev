"""
JSON Import Tool for Haven Master

Imports JSON files from public EXE version into master database.
This is how the master aggregates data collected by public users.

Features:
- Import single JSON file
- Import multiple JSON files from directory
- Handle duplicate systems (skip or update)
- Validate data before import
- Generate import report

Usage:
    # Import single file
    python src/migration/import_json.py path/to/export.json

    # Import all files from directory
    python src/migration/import_json.py data/imports/ --batch

    # Update existing systems
    python src/migration/import_json.py path/to/export.json --update
"""
import json
import sys
from pathlib import Path
from datetime import datetime
import argparse
from typing import List, Dict, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.common.database import HavenDatabase
from src.common.data_provider import get_data_provider
from config.settings import USE_DATABASE, JSON_DATA_PATH, DATABASE_PATH


class ImportStats:
    """Track import statistics"""
    def __init__(self):
        self.files_processed = 0
        self.systems_found = 0
        self.systems_imported = 0
        self.systems_updated = 0
        self.systems_skipped = 0
        self.systems_failed = 0
        self.errors = []

    def __str__(self):
        return f"""
Import Statistics:
  Files Processed: {self.files_processed}
  Systems Found: {self.systems_found}
  Systems Imported: {self.systems_imported}
  Systems Updated: {self.systems_updated}
  Systems Skipped: {self.systems_skipped}
  Systems Failed: {self.systems_failed}
  Errors: {len(self.errors)}
"""


class JSONImporter:
    """Handles importing JSON exports from public EXE version"""

    def __init__(self, use_database: bool = USE_DATABASE):
        """
        Initialize importer

        Args:
            use_database: If True, import to database; if False, import to JSON
        """
        self.use_database = use_database
        self.stats = ImportStats()
        self.provider = get_data_provider(
            use_database=use_database,
            json_path=str(JSON_DATA_PATH),
            db_path=str(DATABASE_PATH)
        )

    def _normalize_system_data(self, system_data: dict) -> dict:
        """
        Normalize system data to ensure consistent structure.
        Handles mixed planet formats (strings vs objects).

        Args:
            system_data: Raw system data from JSON

        Returns:
            Normalized system data with properly structured planets
        """
        normalized = dict(system_data)

        # Normalize planets
        planets = normalized.get('planets', [])
        if planets:
            normalized_planets = []
            for planet in planets:
                if isinstance(planet, str):
                    # Convert string planet name to object format
                    normalized_planets.append({
                        'name': planet,
                        'type': 'Unknown',
                        'fauna': 'Unknown',
                        'flora': 'Unknown',
                        'sentinel': 'Unknown',
                        'materials': 'Unknown',
                        'moons': []
                    })
                elif isinstance(planet, dict):
                    # Already an object, ensure it has required fields
                    normalized_planet = {
                        'name': planet.get('name', 'Unknown'),
                        'type': planet.get('type', 'Unknown'),
                        'fauna': planet.get('fauna', 'Unknown'),
                        'flora': planet.get('flora', 'Unknown'),
                        'sentinel': planet.get('sentinel', 'Unknown'),
                        'materials': planet.get('materials', 'Unknown'),
                        'moons': planet.get('moons', [])
                    }
                    # Preserve any additional fields
                    for key, value in planet.items():
                        if key not in normalized_planet:
                            normalized_planet[key] = value
                    normalized_planets.append(normalized_planet)
            normalized['planets'] = normalized_planets

        return normalized

    def import_file(self, file_path: Path, allow_updates: bool = False,
                   skip_validation: bool = False) -> bool:
        """
        Import single JSON file

        Args:
            file_path: Path to JSON file
            allow_updates: If True, update existing systems; if False, skip
            skip_validation: Skip validation (not recommended)

        Returns:
            True if successful, False otherwise
        """
        print(f"\n{'='*70}")
        print(f"IMPORTING: {file_path.name}")
        print(f"{'='*70}")

        # Load JSON
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✓ JSON loaded successfully")
        except Exception as e:
            print(f"❌ ERROR: Failed to load JSON: {e}")
            self.stats.errors.append(f"{file_path.name}: Failed to load - {e}")
            return False

        # Validate
        if not skip_validation:
            if not self._validate_data(data, file_path.name):
                return False

        # Import systems
        for key, value in data.items():
            if key == "_meta" or not isinstance(value, dict):
                continue

            self.stats.systems_found += 1
            self._import_system(key, value, allow_updates)

        self.stats.files_processed += 1
        print(f"\n✓ Import complete for {file_path.name}")
        print(f"  Imported: {self.stats.systems_imported}")
        print(f"  Updated: {self.stats.systems_updated}")
        print(f"  Skipped: {self.stats.systems_skipped}")
        print(f"  Failed: {self.stats.systems_failed}")

        return True

    def import_directory(self, dir_path: Path, allow_updates: bool = False,
                        skip_validation: bool = False) -> bool:
        """
        Import all JSON files from directory

        Args:
            dir_path: Path to directory containing JSON files
            allow_updates: If True, update existing systems
            skip_validation: Skip validation

        Returns:
            True if successful, False otherwise
        """
        print(f"\n{'='*70}")
        print(f"BATCH IMPORT FROM: {dir_path}")
        print(f"{'='*70}")

        # Find all JSON files
        json_files = list(dir_path.glob("*.json"))

        if not json_files:
            print(f"❌ ERROR: No JSON files found in {dir_path}")
            return False

        print(f"Found {len(json_files)} JSON files")

        # Import each file
        for json_file in json_files:
            self.import_file(json_file, allow_updates, skip_validation)

        # Summary
        print(f"\n{'='*70}")
        print(f"BATCH IMPORT COMPLETE")
        print(f"{'='*70}")
        print(self.stats)

        return self.stats.systems_failed == 0

    def _validate_data(self, data: dict, filename: str) -> bool:
        """
        Validate JSON data structure

        Args:
            data: JSON data dictionary
            filename: Filename for error messages

        Returns:
            True if valid, False otherwise
        """
        # Check if data is dict
        if not isinstance(data, dict):
            print(f"❌ ERROR: Invalid JSON structure (expected dict)")
            self.stats.errors.append(f"{filename}: Invalid structure")
            return False

        # Count systems
        system_count = sum(1 for k, v in data.items()
                          if k != "_meta" and isinstance(v, dict))

        if system_count == 0:
            print(f"⚠️  WARNING: No systems found in {filename}")
            return True  # Not an error, just empty

        print(f"✓ Found {system_count} systems to import")

        # Validate required fields in first system
        for key, value in data.items():
            if key == "_meta" or not isinstance(value, dict):
                continue

            system = value
            required_fields = ['name', 'x', 'y', 'z', 'region']
            missing_fields = [f for f in required_fields if f not in system]

            if missing_fields:
                print(f"⚠️  WARNING: System '{key}' missing fields: {missing_fields}")
                print(f"   This system may fail to import")

            # Only check first system
            break

        return True

    def _import_system(self, key: str, system_data: dict, allow_updates: bool):
        """
        Import single system

        Args:
            key: System key from JSON
            system_data: System data dictionary
            allow_updates: If True, update existing; if False, skip
        """
        system_name = system_data.get('name', key)

        try:
            # Normalize system data (handles mixed planet formats)
            normalized_data = self._normalize_system_data(system_data)

            # Check if system exists
            exists = self.provider.system_exists(system_name)

            if exists:
                if allow_updates:
                    # Update existing system
                    system_id = system_data.get('id', key)
                    self.provider.update_system(system_id, normalized_data)
                    self.stats.systems_updated += 1
                    print(f"  ↻ Updated: {system_name}")
                else:
                    # Skip duplicate
                    self.stats.systems_skipped += 1
                    print(f"  ⊘ Skipped: {system_name} (already exists)")
            else:
                # Import new system
                system_copy = dict(normalized_data)
                
                # Handle ID: check if it conflicts with existing IDs
                if 'id' in system_copy:
                    # Check if this ID already exists in the database
                    try:
                        # Try to add with the existing ID
                        self.provider.add_system(system_copy)
                    except Exception as id_error:
                        # If it's a UNIQUE constraint error on ID, generate a new one
                        if "UNIQUE constraint failed" in str(id_error) or "UNIQUE" in str(id_error):
                            print(f"    ⚠ Warning: System ID conflict, generating new ID")
                            del system_copy['id']
                            self.provider.add_system(system_copy)
                        else:
                            raise  # Re-raise if it's a different error
                else:
                    # No ID provided, let provider generate one
                    self.provider.add_system(system_copy)
                
                self.stats.systems_imported += 1
                print(f"  + Imported: {system_name}")

        except Exception as e:
            self.stats.systems_failed += 1
            error_msg = f"Failed to import '{system_name}': {e}"
            self.stats.errors.append(error_msg)
            print(f"  ❌ ERROR: {error_msg}")

    def generate_report(self, output_path: Path):
        """
        Generate import report

        Args:
            output_path: Path to save report
        """
        report = f"""HAVEN JSON IMPORT REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{self.stats}

Backend: {'Database' if self.use_database else 'JSON'}
Target: {DATABASE_PATH if self.use_database else JSON_DATA_PATH}

"""

        if self.stats.errors:
            report += "ERRORS:\n"
            for error in self.stats.errors:
                report += f"  - {error}\n"
            report += "\n"

        if self.stats.systems_skipped > 0:
            report += f"NOTE: {self.stats.systems_skipped} duplicate systems were skipped.\n"
            report += "      Use --update flag to update existing systems.\n"

        # Save report
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n✓ Import report saved: {output_path}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Import JSON files from public EXE version into master database"
    )
    parser.add_argument('path', help='Path to JSON file or directory')
    parser.add_argument('--batch', action='store_true',
                       help='Import all JSON files from directory')
    parser.add_argument('--update', action='store_true',
                       help='Update existing systems instead of skipping')
    parser.add_argument('--skip-validation', action='store_true',
                       help='Skip validation (not recommended)')
    parser.add_argument('--use-json', action='store_true',
                       help='Import to JSON instead of database')
    parser.add_argument('--report', help='Path to save import report')

    args = parser.parse_args()

    # Determine backend
    use_database = USE_DATABASE and not args.use_json

    print("="*70)
    print("HAVEN JSON IMPORTER")
    print("="*70)
    print(f"Backend: {'Database' if use_database else 'JSON'}")
    print(f"Target: {DATABASE_PATH if use_database else JSON_DATA_PATH}")
    print(f"Update Existing: {'Yes' if args.update else 'No'}")
    print("="*70)

    # Create importer
    importer = JSONImporter(use_database=use_database)

    # Get path
    path = Path(args.path)

    if not path.exists():
        print(f"❌ ERROR: Path not found: {path}")
        sys.exit(1)

    # Import
    if args.batch or path.is_dir():
        if not path.is_dir():
            print(f"❌ ERROR: --batch specified but path is not a directory")
            sys.exit(1)
        success = importer.import_directory(
            path,
            allow_updates=args.update,
            skip_validation=args.skip_validation
        )
    else:
        if not path.is_file():
            print(f"❌ ERROR: Path is not a file: {path}")
            sys.exit(1)
        success = importer.import_file(
            path,
            allow_updates=args.update,
            skip_validation=args.skip_validation
        )

    # Generate report if requested
    if args.report:
        importer.generate_report(Path(args.report))
    else:
        # Default report location
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = Path(f"logs/import_report_{timestamp}.txt")
        importer.generate_report(report_path)

    # Print final stats
    print(f"\n{'='*70}")
    print("IMPORT COMPLETE")
    print("="*70)
    print(importer.stats)

    if importer.stats.errors:
        print(f"⚠️  {len(importer.stats.errors)} errors occurred during import")
        print("   Check the import report for details")

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
