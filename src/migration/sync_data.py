"""
Data Synchronization Utility

Ensures JSON and database backends stay in sync.
Can be used to:
1. Sync database from JSON (database = JSON)
2. Sync JSON from database (JSON = database)
3. Bidirectional sync (merge changes from both)

Usage:
    python src/migration/sync_data.py --mode json-to-db
    python src/migration/sync_data.py --mode db-to-json
    python src/migration/sync_data.py --mode check
"""
import json
import sys
from pathlib import Path
from datetime import datetime
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.common.data_provider import DatabaseDataProvider, JSONDataProvider
from config.settings import JSON_DATA_PATH, DATABASE_PATH


class DataSynchronizer:
    """Synchronize data between JSON and database"""

    def __init__(self, json_path: str = None, db_path: str = None):
        """
        Initialize synchronizer

        Args:
            json_path: Path to JSON file (default from settings)
            db_path: Path to database (default from settings)
        """
        self.json_path = Path(json_path or JSON_DATA_PATH)
        self.db_path = Path(db_path or DATABASE_PATH)
        self.json_provider = None
        self.db_provider = None

    def initialize_providers(self):
        """Initialize data providers"""
        try:
            self.json_provider = JSONDataProvider(str(self.json_path))
            self.db_provider = DatabaseDataProvider(str(self.db_path))
            return True
        except Exception as e:
            print(f"Error initializing providers: {e}")
            return False

    def check_sync_status(self) -> dict:
        """
        Check if JSON and database are in sync

        Returns:
            dict with sync status information
        """
        if not self.initialize_providers():
            return {"error": "Failed to initialize providers"}

        try:
            json_systems = self.json_provider.get_all_systems()
            db_systems = self.db_provider.get_all_systems()

            json_ids = {s['id']: s for s in json_systems}
            db_ids = {s['id']: s for s in db_systems}

            only_in_json = set(json_ids.keys()) - set(db_ids.keys())
            only_in_db = set(db_ids.keys()) - set(json_ids.keys())
            in_both = set(json_ids.keys()) & set(db_ids.keys())

            # Check for differences in systems that exist in both
            differences = []
            for sys_id in in_both:
                json_sys = json_ids[sys_id]
                db_sys = db_ids[sys_id]
                
                # Compare key fields
                if json_sys['name'] != db_sys['name']:
                    differences.append((sys_id, 'name', json_sys['name'], db_sys['name']))
                if json_sys.get('x') != db_sys.get('x') or \
                   json_sys.get('y') != db_sys.get('y') or \
                   json_sys.get('z') != db_sys.get('z'):
                    differences.append((sys_id, 'coordinates', 
                                      f"({json_sys.get('x')},{json_sys.get('y')},{json_sys.get('z')})",
                                      f"({db_sys.get('x')},{db_sys.get('y')},{db_sys.get('z')})"))

            return {
                "in_sync": len(only_in_json) == 0 and len(only_in_db) == 0 and len(differences) == 0,
                "json_count": len(json_systems),
                "db_count": len(db_systems),
                "only_in_json": len(only_in_json),
                "only_in_db": len(only_in_db),
                "in_both": len(in_both),
                "differences": len(differences),
                "only_in_json_ids": list(only_in_json)[:5],  # Show first 5
                "only_in_db_ids": list(only_in_db)[:5],
                "difference_details": differences[:5]
            }

        except Exception as e:
            return {"error": f"Failed to check sync status: {e}"}

    def sync_json_to_db(self, overwrite: bool = False) -> bool:
        """
        Sync database from JSON (database = JSON)

        Args:
            overwrite: If True, overwrite existing systems in DB

        Returns:
            True if successful
        """
        if not self.initialize_providers():
            return False

        try:
            print("\n[SYNC] JSON → Database")
            print("=" * 60)

            json_systems = self.json_provider.get_all_systems()
            print(f"Found {len(json_systems)} systems in JSON")

            synced = 0
            skipped = 0
            errors = 0

            for system in json_systems:
                try:
                    # Check if system exists in database
                    existing = self.db_provider.get_system_by_id(system['id'])
                    
                    if existing:
                        if overwrite:
                            # Update existing system
                            self.db_provider.update_system(system['id'], system)
                            synced += 1
                            print(f"  ✓ Updated: {system['name']}")
                        else:
                            skipped += 1
                            print(f"  - Skipped: {system['name']} (already exists)")
                    else:
                        # Add new system
                        self.db_provider.add_system(system)
                        synced += 1
                        print(f"  ✓ Added: {system['name']}")

                except Exception as e:
                    errors += 1
                    print(f"  ✗ Error with {system.get('name', 'unknown')}: {e}")

            print("\n" + "=" * 60)
            print(f"Sync complete: {synced} synced, {skipped} skipped, {errors} errors")
            return errors == 0

        except Exception as e:
            print(f"Sync failed: {e}")
            return False

    def sync_db_to_json(self, backup: bool = True) -> bool:
        """
        Sync JSON from database (JSON = database)

        Args:
            backup: Create backup of JSON before overwriting

        Returns:
            True if successful
        """
        if not self.initialize_providers():
            return False

        try:
            print("\n[SYNC] Database → JSON")
            print("=" * 60)

            # Backup JSON if requested
            if backup and self.json_path.exists():
                backup_path = self.json_path.with_suffix('.json.bak')
                import shutil
                shutil.copy2(self.json_path, backup_path)
                print(f"✓ Backup created: {backup_path}")

            # Get all systems INCLUDING planets and moons
            db_systems = self.db_provider.get_all_systems(include_planets=True)
            print(f"Found {len(db_systems)} systems in database")

            # Build JSON structure
            json_data = {"_meta": {
                "version": "1.0.0",
                "last_modified": datetime.now().isoformat(),
                "synced_from_database": True
            }}

            for system in db_systems:
                json_data[system['name']] = system

            # Write to JSON
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

            print(f"✓ Synced {len(db_systems)} systems to JSON")
            print("=" * 60)
            return True

        except Exception as e:
            print(f"Sync failed: {e}")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Synchronize data between JSON and database"
    )
    parser.add_argument(
        '--mode',
        choices=['check', 'json-to-db', 'db-to-json'],
        default='check',
        help='Sync mode'
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing systems (json-to-db mode only)'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip backup (db-to-json mode only)'
    )
    parser.add_argument(
        '--json-path',
        help='Path to JSON file (default from settings)'
    )
    parser.add_argument(
        '--db-path',
        help='Path to database (default from settings)'
    )

    args = parser.parse_args()

    syncer = DataSynchronizer(args.json_path, args.db_path)

    if args.mode == 'check':
        print("\n" + "=" * 70)
        print("DATA SYNC STATUS CHECK")
        print("=" * 70)
        status = syncer.check_sync_status()
        
        if "error" in status:
            print(f"\n✗ ERROR: {status['error']}")
            return 1

        print(f"\nJSON File: {syncer.json_path}")
        print(f"Database: {syncer.db_path}")
        print(f"\nJSON systems: {status['json_count']}")
        print(f"Database systems: {status['db_count']}")
        print(f"In both: {status['in_both']}")
        
        if status['in_sync']:
            print("\n✓ DATA IS IN SYNC")
        else:
            print("\n✗ DATA IS OUT OF SYNC")
            if status['only_in_json'] > 0:
                print(f"  - {status['only_in_json']} systems only in JSON")
                if status['only_in_json_ids']:
                    print(f"    Examples: {', '.join(status['only_in_json_ids'][:3])}")
            if status['only_in_db'] > 0:
                print(f"  - {status['only_in_db']} systems only in database")
                if status['only_in_db_ids']:
                    print(f"    Examples: {', '.join(status['only_in_db_ids'][:3])}")
            if status['differences'] > 0:
                print(f"  - {status['differences']} systems have differences")

        print("\nRecommended Actions:")
        if status['only_in_json'] > 0:
            print("  → Run: py src/migration/sync_data.py --mode json-to-db")
        if status['only_in_db'] > 0:
            print("  → Run: py src/migration/sync_data.py --mode db-to-json")
        if status['in_sync']:
            print("  → No action needed")

    elif args.mode == 'json-to-db':
        success = syncer.sync_json_to_db(overwrite=args.overwrite)
        return 0 if success else 1

    elif args.mode == 'db-to-json':
        success = syncer.sync_db_to_json(backup=not args.no_backup)
        return 0 if success else 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
