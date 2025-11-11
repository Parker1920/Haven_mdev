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
import logging
import sqlite3
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

    def _is_keeper_format(self, data: dict) -> bool:
        """
        Check if JSON is in Keeper bot discoveries format
        
        Keeper format has:
        - "discoveries" key with list of discovery objects
        - "metadata" or other non-system keys
        - No standard system fields (name, x, y, z, region)
        
        Returns:
            True if appears to be Keeper format
        """
        # Check if this looks like Keeper discoveries format
        if 'discoveries' in data and isinstance(data.get('discoveries'), list):
            return True
        
        # Check if file has no systems but has discovery-like structure
        has_systems = any(
            k != "_meta" and isinstance(v, dict) and 
            all(field in v for field in ['name', 'x', 'y', 'z', 'region'])
            for k, v in data.items()
        )
        
        return not has_systems and len(data) > 1

    def _import_keeper_discoveries(self, data: dict, file_path: Path) -> bool:
        """
        Import discoveries from Keeper bot format
        
        Keeper bot exports discoveries as a list with associated metadata.
        Converts Keeper format to database schema format.
        """
        print(f"Detected Keeper discoveries format")
        
        if not self.use_database:
            print(f"⚠️  Keeper discoveries require database backend")
            return False
        
        try:
            from src.common.database import HavenDatabase
            import time
            
            discoveries_list = data.get('discoveries', [])
            if not discoveries_list:
                print(f"⚠️  No discoveries found in {file_path.name}")
                return True
            
            print(f"✓ Found {len(discoveries_list)} discoveries to import")
            
            imported_count = 0
            failed_count = 0
            
            # Retry logic for database locks (Control Room might be using it)
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    with HavenDatabase(str(DATABASE_PATH)) as db:
                        for idx, disc_data in enumerate(discoveries_list):
                            if not isinstance(disc_data, dict):
                                continue
                            
                            try:
                                # Convert Keeper format to database schema
                                converted = self._convert_keeper_discovery(disc_data, db)
                                
                                # Add to database
                                db.add_discovery(converted)
                                imported_count += 1
                                
                            except Exception as e:
                                print(f"  ❌ Discovery {idx+1} failed: {str(e)[:100]}")
                                logging.error(f"Failed to import discovery {idx+1}: {e}", exc_info=True)
                                failed_count += 1
                    
                    # Success - break out of retry loop
                    break
                    
                except sqlite3.OperationalError as e:
                    if "locked" in str(e).lower():
                        retry_count += 1
                        if retry_count < max_retries:
                            wait_time = 2 ** retry_count  # Exponential backoff: 2s, 4s, 8s
                            print(f"⚠️  Database locked, retrying in {wait_time}s... ({retry_count}/{max_retries})")
                            time.sleep(wait_time)
                        else:
                            print(f"❌ Database remains locked after {max_retries} retries")
                            print(f"   Ensure Control Room is not running during import")
                            self.stats.errors.append(f"{file_path.name}: Database locked - close Control Room and retry")
                            return False
                    else:
                        raise
                        
            print(f"✓ Keeper discoveries imported: {imported_count}")
            if failed_count > 0:
                print(f"⚠️  Failed: {failed_count}")
            
            self.stats.systems_imported += imported_count
            return True
            
        except Exception as e:
            print(f"❌ ERROR importing Keeper discoveries: {e}")
            self.stats.errors.append(f"{file_path.name}: Keeper import failed - {e}")
            return False

    def _convert_keeper_discovery(self, keeper_disc: dict, db) -> dict:
        """
        Convert Keeper bot discovery format to Haven database format
        
        Maps:
        - keeper fields → database fields
        - Lists → JSON strings
        - None → appropriate defaults
        - Finds planet_id from planet_name
        """
        import json
        
        converted = {}
        
        # Required fields - handle None values
        disc_type = keeper_disc.get('type')
        converted['discovery_type'] = (disc_type.strip() if disc_type else 'unknown') or 'unknown'
        
        desc = keeper_disc.get('description')
        converted['description'] = (desc.strip() if desc else 'No description') or 'No description'
        
        converted['location_type'] = 'planet'  # Keeper bot discoveries are planet-based
        
        # Map discovery name - handle None
        location = keeper_disc.get('location')
        converted['discovery_name'] = (location.strip() if location else None)
        
        # Location info - handle None
        converted['location_name'] = (location.strip() if location else None)
        
        # System info - handle None
        system_name = keeper_disc.get('system_name')
        if system_name:
            # Find system by name
            try:
                cursor = db.conn.cursor()
                cursor.execute("SELECT id FROM systems WHERE name = ?", (system_name.strip() if isinstance(system_name, str) else system_name,))
                sys_row = cursor.fetchone()
                if sys_row:
                    converted['system_id'] = sys_row[0]
            except:
                pass
        
        # Planet info - handle None
        planet_name = keeper_disc.get('planet_name')
        if planet_name and 'system_id' in converted:
            # Find planet by name in this system
            try:
                cursor = db.conn.cursor()
                cursor.execute(
                    "SELECT id FROM planets WHERE system_id = ? AND name = ?",
                    (converted['system_id'], planet_name.strip() if isinstance(planet_name, str) else planet_name)
                )
                planet_row = cursor.fetchone()
                if planet_row:
                    converted['planet_id'] = planet_row[0]
            except:
                pass
        
        # Optional fields with None-safe type conversion
        coords = keeper_disc.get('coordinates')
        converted['coordinates'] = (coords.strip() if coords else None)
        
        cond = keeper_disc.get('condition')
        converted['condition'] = (cond.strip() if cond else None)
        
        time_p = keeper_disc.get('time_period')
        converted['time_period'] = (time_p.strip() if time_p else None)
        
        sig = keeper_disc.get('significance')
        converted['significance'] = (sig.strip() if sig else None)
        
        evidence = keeper_disc.get('evidence_url')
        converted['photo_url'] = (evidence.strip() if evidence else None)
        
        # User info - handle None
        username = keeper_disc.get('username')
        converted['discovered_by'] = (username.strip() if username else None)
        
        user_id = keeper_disc.get('user_id')
        converted['discord_user_id'] = (str(user_id).strip() if user_id else None)
        
        guild_id = keeper_disc.get('guild_id')
        converted['discord_guild_id'] = (str(guild_id).strip() if guild_id else None)
        
        # Convert lists to JSON strings for database storage
        # Tags: list → JSON string
        tags = keeper_disc.get('tags', [])
        if isinstance(tags, list) and tags:
            converted['tags'] = json.dumps(tags)
        else:
            converted['tags'] = None
        
        # Metadata: dict/list → JSON string
        metadata = keeper_disc.get('metadata', {})
        if isinstance(metadata, (dict, list)) and metadata:
            converted['metadata'] = json.dumps(metadata)
        else:
            converted['metadata'] = None
        
        # Status fields - handle None
        analysis = keeper_disc.get('analysis_status')
        converted['analysis_status'] = (analysis.strip() if analysis else 'pending') or 'pending'
        
        pattern = keeper_disc.get('pattern_matches')
        converted['pattern_matches'] = pattern if isinstance(pattern, int) else 0
        
        mystery = keeper_disc.get('mystery_tier')
        converted['mystery_tier'] = mystery if isinstance(mystery, int) else 0
        
        # Submission timestamp
        converted['submission_timestamp'] = keeper_disc.get('submission_timestamp') or None
        
        return converted

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

        # Check if this is Keeper bot discoveries format
        if self._is_keeper_format(data):
            return self._import_keeper_discoveries(data, file_path)

        # Validate standard format
        if not skip_validation:
            if not self._validate_data(data, file_path.name):
                return False

        # Import systems (standard format)
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

    def _extract_and_import_discoveries(self, system_id: str, system_data: dict):
        """
        Extract discoveries from system data and import them to database
        
        Discoveries can be nested under planets or at system level.
        Format from Keeper bot:
        - discoveries: [{...}, {...}] at system level, or
        - discoveries: [{...}] under each planet
        
        Args:
            system_id: ID of the system being imported
            system_data: System data dictionary
        """
        if not self.use_database:
            return  # Only import discoveries to database
        
        try:
            # Get database connection
            from src.common.database import HavenDatabase
            
            with HavenDatabase(str(DATABASE_PATH)) as db:
                # Check for system-level discoveries
                system_discoveries = system_data.get('discoveries', [])
                if system_discoveries and isinstance(system_discoveries, list):
                    for disc_data in system_discoveries:
                        if not isinstance(disc_data, dict):
                            continue
                        # Ensure system_id is set
                        disc_data['system_id'] = system_id
                        try:
                            db.add_discovery(disc_data)
                        except Exception as e:
                            logging.warning(f"Failed to import system-level discovery: {e}")
                
                # Check for discoveries under planets
                planets = system_data.get('planets', [])
                for planet in planets:
                    if not isinstance(planet, dict):
                        continue
                    
                    planet_name = planet.get('name')
                    planet_discoveries = planet.get('discoveries', [])
                    
                    if planet_discoveries and isinstance(planet_discoveries, list):
                        # Get planet ID from database
                        cursor = db.conn.cursor()
                        cursor.execute(
                            "SELECT id FROM planets WHERE system_id = ? AND name = ?",
                            (system_id, planet_name)
                        )
                        planet_row = cursor.fetchone()
                        
                        if planet_row:
                            planet_id = planet_row[0]
                            for disc_data in planet_discoveries:
                                if not isinstance(disc_data, dict):
                                    continue
                                # Set both system and planet IDs
                                disc_data['system_id'] = system_id
                                disc_data['planet_id'] = planet_id
                                try:
                                    db.add_discovery(disc_data)
                                except Exception as e:
                                    logging.warning(f"Failed to import discovery for {planet_name}: {e}")
                
        except Exception as e:
            logging.error(f"Error importing discoveries for system {system_id}: {e}")

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
                system_id = None
                
                # Handle ID: check if it conflicts with existing IDs
                if 'id' in system_copy:
                    system_id = system_copy['id']
                    # Check if this ID already exists in the database
                    try:
                        # Try to add with the existing ID
                        returned_id = self.provider.add_system(system_copy)
                        system_id = returned_id  # Use the returned ID
                    except Exception as id_error:
                        # If it's a UNIQUE constraint error on ID, generate a new one
                        if "UNIQUE constraint failed" in str(id_error) or "UNIQUE" in str(id_error):
                            print(f"    ⚠ Warning: System ID conflict, generating new ID")
                            del system_copy['id']
                            returned_id = self.provider.add_system(system_copy)
                            system_id = returned_id
                        else:
                            raise  # Re-raise if it's a different error
                else:
                    # No ID provided, let provider generate one
                    returned_id = self.provider.add_system(system_copy)
                    system_id = returned_id
                
                # After system is added, import any discoveries
                if system_id:
                    self._extract_and_import_discoveries(system_id, system_data)
                
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
