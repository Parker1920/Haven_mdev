"""
JSON to SQLite Migration Script

Migrates data from data.json to SQLite database (haven.db).
This is a one-time migration for transitioning from JSON to database backend.

Usage:
    python src/migration/json_to_sqlite.py

Options:
    --json-path: Path to source JSON file (default: data/data.json)
    --db-path: Path to destination database (default: data/haven.db)
    --backup: Create backup of existing database (default: True)
    --verify: Verify migration after completion (default: True)
"""
import json
import sys
import os
from pathlib import Path
from datetime import datetime
import argparse
import shutil

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.common.database import HavenDatabase


class MigrationStats:
    """Track migration statistics"""
    def __init__(self):
        self.systems_total = 0
        self.systems_migrated = 0
        self.systems_failed = 0
        self.planets_migrated = 0
        self.moons_migrated = 0
        self.stations_migrated = 0
        self.errors = []

    def __str__(self):
        return f"""
Migration Statistics:
  Systems: {self.systems_migrated}/{self.systems_total} migrated ({self.systems_failed} failed)
  Planets: {self.planets_migrated}
  Moons: {self.moons_migrated}
  Space Stations: {self.stations_migrated}
  Errors: {len(self.errors)}
"""


class JSONToSQLiteMigrator:
    """Handles migration from JSON to SQLite database"""

    def __init__(self, json_path: str, db_path: str):
        """
        Initialize migrator

        Args:
            json_path: Path to source JSON file
            db_path: Path to destination database
        """
        self.json_path = Path(json_path)
        self.db_path = Path(db_path)
        self.stats = MigrationStats()
        self.force_overwrite = False  # Can be set externally

    def migrate(self, backup: bool = True, verify: bool = True) -> bool:
        """
        Perform migration

        Args:
            backup: Create backup of existing database
            verify: Verify migration after completion

        Returns:
            True if successful, False otherwise
        """
        print("=" * 70)
        print("HAVEN JSON TO SQLITE MIGRATION")
        print("=" * 70)

        # Step 1: Validate inputs
        print(f"\n[1/6] Validating inputs...")
        if not self._validate_inputs():
            return False

        # Step 2: Backup existing database if requested
        if backup and self.db_path.exists():
            print(f"\n[2/6] Backing up existing database...")
            if not self._backup_database():
                return False
        else:
            print(f"\n[2/6] No existing database to backup")

        # Step 3: Load JSON data
        print(f"\n[3/6] Loading JSON data from {self.json_path}...")
        json_data = self._load_json()
        if json_data is None:
            return False

        # Step 4: Migrate data
        print(f"\n[4/6] Migrating data to {self.db_path}...")
        if not self._migrate_data(json_data):
            return False

        # Step 5: Verify migration if requested
        if verify:
            print(f"\n[5/6] Verifying migration...")
            if not self._verify_migration(json_data):
                print("⚠️  Migration completed with verification warnings")
        else:
            print(f"\n[5/6] Skipping verification")

        # Step 6: Summary
        print(f"\n[6/6] Migration complete!")
        print(self.stats)
        print("=" * 70)

        if self.stats.systems_failed > 0:
            print("⚠️  Some systems failed to migrate. Check errors above.")
            print("    The database may be incomplete.")
            return False

        print("✓ Migration successful!")
        print(f"  Database created: {self.db_path}")
        print(f"  Systems migrated: {self.stats.systems_migrated}")
        print(f"  Total entities: {self.stats.systems_migrated + self.stats.planets_migrated + self.stats.moons_migrated}")

        return True

    def _validate_inputs(self) -> bool:
        """Validate input files"""
        # Check JSON exists
        if not self.json_path.exists():
            print(f"❌ ERROR: JSON file not found: {self.json_path}")
            return False

        print(f"  ✓ JSON file found: {self.json_path}")
        print(f"    Size: {self.json_path.stat().st_size / 1024:.1f} KB")

        # Check JSON is readable
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.stats.systems_total = sum(1 for k, v in data.items()
                                              if k != "_meta" and isinstance(v, dict))
                print(f"    Systems: {self.stats.systems_total}")
        except json.JSONDecodeError as e:
            print(f"❌ ERROR: Invalid JSON: {e}")
            return False
        except Exception as e:
            print(f"❌ ERROR: Failed to read JSON: {e}")
            return False

        # Check database path
        if self.db_path.exists():
            print(f"  ⚠️  Database already exists: {self.db_path}")
            print(f"    Size: {self.db_path.stat().st_size / (1024*1024):.1f} MB")
            if not self.force_overwrite:
                response = input("    Overwrite existing database? (y/N): ")
                if response.lower() != 'y':
                    print("  Migration cancelled by user")
                    return False
            else:
                print("    --force flag specified, overwriting...")
        else:
            print(f"  ✓ Database will be created: {self.db_path}")

        return True

    def _backup_database(self) -> bool:
        """Create backup of existing database"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.db_path.parent / f"haven_backup_{timestamp}.db"

        try:
            shutil.copy2(self.db_path, backup_path)
            print(f"  ✓ Backup created: {backup_path}")
            return True
        except Exception as e:
            print(f"  ❌ ERROR: Failed to create backup: {e}")
            return False

    def _load_json(self) -> dict:
        """Load JSON data"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"  ✓ JSON loaded successfully")
            return data

        except Exception as e:
            print(f"  ❌ ERROR: Failed to load JSON: {e}")
            return None

    def _migrate_data(self, json_data: dict) -> bool:
        """Migrate JSON data to database"""
        try:
            # Delete existing database to start fresh
            if self.db_path.exists():
                self.db_path.unlink()

            # Create new database connection
            with HavenDatabase(str(self.db_path)) as db:
                # Migrate each system
                for key, value in json_data.items():
                    if key == "_meta" or not isinstance(value, dict):
                        continue

                    try:
                        self._migrate_system(db, key, value)
                        self.stats.systems_migrated += 1

                        # Progress indicator
                        if self.stats.systems_migrated % 100 == 0:
                            print(f"    Migrated {self.stats.systems_migrated}/{self.stats.systems_total} systems...")

                    except Exception as e:
                        self.stats.systems_failed += 1
                        error_msg = f"Failed to migrate system '{key}': {e}"
                        self.stats.errors.append(error_msg)
                        print(f"    ⚠️  {error_msg}")

            print(f"  ✓ Data migration complete")
            return True

        except Exception as e:
            print(f"  ❌ ERROR: Migration failed: {e}")
            return False

    def _migrate_system(self, db: HavenDatabase, key: str, system_data: dict):
        """
        Migrate single system to database

        Args:
            db: Database connection
            key: System key from JSON
            system_data: System data dictionary
        """
        # Prepare system data
        system = {
            'id': system_data.get('id', f'SYS_{key}'),
            'name': system_data.get('name', key),
            'x': float(system_data.get('x', 0)),
            'y': float(system_data.get('y', 0)),
            'z': float(system_data.get('z', 0)),
            'region': system_data.get('region', 'Unknown'),
            'fauna': system_data.get('fauna'),
            'flora': system_data.get('flora'),
            'sentinel': system_data.get('sentinel'),
            'materials': system_data.get('materials'),
            'base_location': system_data.get('base_location'),
            'photo': system_data.get('photo'),
            'attributes': system_data.get('attributes'),
            'planets': system_data.get('planets', []),
            'space_station': system_data.get('space_station')
        }

        # Add system to database
        db.add_system(system)

        # Count planets and moons
        for planet in system.get('planets', []):
            self.stats.planets_migrated += 1
            self.stats.moons_migrated += len(planet.get('moons', []))

        # Count space station
        if system.get('space_station'):
            self.stats.stations_migrated += 1

    def _verify_migration(self, json_data: dict) -> bool:
        """
        Verify migration completed successfully

        Args:
            json_data: Original JSON data

        Returns:
            True if verification passed, False otherwise
        """
        try:
            with HavenDatabase(str(self.db_path)) as db:
                # Get database stats
                db_stats = db.get_statistics()

                print(f"  Database Statistics:")
                print(f"    Systems: {db_stats['total_systems']}")
                print(f"    Planets: {db_stats['total_planets']}")
                print(f"    Moons: {db_stats['total_moons']}")
                print(f"    Space Stations: {db_stats['total_stations']}")
                print(f"    Database Size: {db_stats['database_size_mb']:.2f} MB")

                # Verify system count
                json_system_count = sum(1 for k, v in json_data.items()
                                       if k != "_meta" and isinstance(v, dict))

                if db_stats['total_systems'] != json_system_count:
                    print(f"  ⚠️  WARNING: System count mismatch!")
                    print(f"    JSON: {json_system_count}, Database: {db_stats['total_systems']}")
                    return False

                # Spot check: Verify a few random systems
                print(f"\n  Spot checking systems...")
                systems_to_check = []
                for key, value in json_data.items():
                    if key != "_meta" and isinstance(value, dict):
                        systems_to_check.append(value.get('name', key))
                        if len(systems_to_check) >= 3:
                            break

                for system_name in systems_to_check:
                    db_system = db.get_system_by_name(system_name)
                    if db_system:
                        print(f"    ✓ {system_name}: Found in database")
                    else:
                        print(f"    ❌ {system_name}: NOT found in database")
                        return False

                print(f"  ✓ Verification passed")
                return True

        except Exception as e:
            print(f"  ❌ ERROR: Verification failed: {e}")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Migrate Haven data from JSON to SQLite")
    parser.add_argument('--json-path', default='data/data.json',
                       help='Path to source JSON file')
    parser.add_argument('--db-path', default='data/haven.db',
                       help='Path to destination database')
    parser.add_argument('--no-backup', action='store_true',
                       help='Skip backup of existing database')
    parser.add_argument('--no-verify', action='store_true',
                       help='Skip verification after migration')
    parser.add_argument('--force', action='store_true',
                       help='Force overwrite existing database without prompting')

    args = parser.parse_args()

    # Create migrator
    migrator = JSONToSQLiteMigrator(
        json_path=args.json_path,
        db_path=args.db_path
    )
    migrator.force_overwrite = args.force  # Set force flag

    # Run migration
    success = migrator.migrate(
        backup=not args.no_backup,
        verify=not args.no_verify
    )

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
