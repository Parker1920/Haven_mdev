"""
Archive Old and Unused Files
Moves old, unused, duplicate, or superseded files to Archive-Dump
"""

import shutil
import os
from pathlib import Path
from datetime import datetime

ROOT = Path("/Users/parkerstouffer/Desktop/Haven_mdev")

def create_archive_dir():
    """Create timestamped archive directory"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = ROOT / "Archive-Dump" / f"old_files_archive_{timestamp}"
    archive_dir.mkdir(parents=True, exist_ok=True)
    return archive_dir

def archive_file(file_path: Path, archive_base: Path, category: str) -> bool:
    """Archive a single file"""
    try:
        # Create category subdirectory
        category_dir = archive_base / category
        category_dir.mkdir(parents=True, exist_ok=True)

        # Preserve directory structure for some files
        if category in ["keeper_diagnostics", "keeper_migrations"]:
            relative_path = file_path.relative_to(ROOT / "docs/guides/Haven-lore/keeper-bot")
            target_path = category_dir / relative_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            target_path = category_dir / file_path.name

        # Move file
        shutil.move(str(file_path), str(target_path))
        return True
    except Exception as e:
        print(f"      ❌ ERROR: {e}")
        return False

def delete_pycache():
    """Delete all __pycache__ directories and .pyc files"""
    deleted_dirs = 0
    deleted_files = 0

    # Find all __pycache__ directories
    for pycache_dir in ROOT.rglob("__pycache__"):
        if "Archive-Dump" not in str(pycache_dir):
            try:
                shutil.rmtree(pycache_dir)
                deleted_dirs += 1
            except Exception as e:
                print(f"      ❌ Failed to delete {pycache_dir}: {e}")

    # Find all .pyc files
    for pyc_file in ROOT.rglob("*.pyc"):
        if "Archive-Dump" not in str(pyc_file):
            try:
                pyc_file.unlink()
                deleted_files += 1
            except Exception as e:
                print(f"      ❌ Failed to delete {pyc_file}: {e}")

    return deleted_dirs, deleted_files

def main():
    """Main archival process"""
    print("="*70)
    print("HAVEN OLD FILES ARCHIVAL")
    print("="*70)
    print()

    archive_base = create_archive_dir()
    print(f"📦 Archive directory: {archive_base.relative_to(ROOT)}\n")

    total_archived = 0
    total_deleted = 0
    total_size = 0

    # CATEGORY 1: Old Database Backups (keep only 3 most recent)
    print("📂 Category 1: Old Database Backups")
    print("-" * 70)

    backups_dir = ROOT / "data/backups"
    if backups_dir.exists():
        backup_files = sorted(backups_dir.glob("VH-Database_backup_*.db"), key=lambda p: p.stat().st_mtime, reverse=True)

        # Keep 3 most recent
        keep_count = 3
        to_archive = backup_files[keep_count:]

        print(f"   Found {len(backup_files)} backup files")
        print(f"   Keeping {keep_count} most recent")
        print(f"   Archiving {len(to_archive)} older backups\n")

        for backup_file in to_archive:
            size = backup_file.stat().st_size
            if archive_file(backup_file, archive_base, "database_backups"):
                total_archived += 1
                total_size += size
                print(f"   ✓ Archived: {backup_file.name} ({size/1024:.1f} KB)")

    # CATEGORY 2: Keeper-bot Diagnostic Scripts
    print(f"\n📂 Category 2: Keeper-bot Diagnostic Scripts")
    print("-" * 70)

    keeper_bot_dir = ROOT / "docs/guides/Haven-lore/keeper-bot"
    diagnostic_scripts = [
        "test_act_one_issues.py",
        "test_haven_integration.py",
        "verify_act_implementation.py",
        "verify_act_one_status.py",
        "verify_integration.py",
        "verify_phase4.py",
        "verify_setup.py"
    ]

    for script_name in diagnostic_scripts:
        script_path = keeper_bot_dir / script_name
        if script_path.exists():
            size = script_path.stat().st_size
            if archive_file(script_path, archive_base, "keeper_diagnostics"):
                total_archived += 1
                total_size += size
                print(f"   ✓ Archived: {script_name} ({size/1024:.1f} KB)")

    # CATEGORY 3: Keeper-bot Migration Scripts
    print(f"\n📂 Category 3: Keeper-bot Migration Scripts")
    print("-" * 70)

    migration_scripts = [
        "emergency_sync.py",
        "migrate_add_guild_id.py",
        "sync_discoveries.py"
    ]

    for script_name in migration_scripts:
        script_path = keeper_bot_dir / script_name
        if script_path.exists():
            size = script_path.stat().st_size
            if archive_file(script_path, archive_base, "keeper_migrations"):
                total_archived += 1
                total_size += size
                print(f"   ✓ Archived: {script_name} ({size/1024:.1f} KB)")

    # CATEGORY 4: Keeper-bot Discovery Backups
    print(f"\n📂 Category 4: Keeper-bot Discovery JSON Backups")
    print("-" * 70)

    keeper_data_dir = keeper_bot_dir / "data"
    if keeper_data_dir.exists():
        for backup_file in keeper_data_dir.glob("keeper_discoveries_backup_*.json"):
            size = backup_file.stat().st_size
            if archive_file(backup_file, archive_base, "keeper_json_backups"):
                total_archived += 1
                total_size += size
                print(f"   ✓ Archived: {backup_file.name} ({size/1024:.1f} KB)")

    # CATEGORY 5: Backup Files
    print(f"\n📂 Category 5: Backup Files (.bak, .backup)")
    print("-" * 70)

    backup_patterns = ["*.bak", "*.backup"]
    for pattern in backup_patterns:
        for backup_file in ROOT.rglob(pattern):
            if "Archive-Dump" not in str(backup_file):
                size = backup_file.stat().st_size
                if archive_file(backup_file, archive_base, "misc_backups"):
                    total_archived += 1
                    total_size += size
                    print(f"   ✓ Archived: {backup_file.relative_to(ROOT)} ({size/1024:.1f} KB)")

    # CATEGORY 6: Old Data Exports
    print(f"\n📂 Category 6: Old Data Export Files")
    print("-" * 70)

    old_exports = [
        ROOT / "data/clean_data.json",
        ROOT / "data/imports/haven_data_1762818638936.json",
        ROOT / "data/imports/test_import.json"
    ]

    for export_file in old_exports:
        if export_file.exists():
            size = export_file.stat().st_size
            if archive_file(export_file, archive_base, "old_data_exports"):
                total_archived += 1
                total_size += size
                print(f"   ✓ Archived: {export_file.relative_to(ROOT)} ({size/1024:.1f} KB)")

    # CATEGORY 7: Python Cache (Delete, not archive)
    print(f"\n📂 Category 7: Python Cache Files (DELETE)")
    print("-" * 70)

    dirs_deleted, files_deleted = delete_pycache()
    total_deleted += dirs_deleted + files_deleted
    print(f"   ✓ Deleted {dirs_deleted} __pycache__ directories")
    print(f"   ✓ Deleted {files_deleted} .pyc files")

    # CATEGORY 8: Duplicate Scripts
    print(f"\n📂 Category 8: Duplicate/Superseded Scripts")
    print("-" * 70)

    duplicate_script = ROOT / "scripts/utils/check_discoveries.py"
    if duplicate_script.exists():
        size = duplicate_script.stat().st_size
        if archive_file(duplicate_script, archive_base, "duplicate_scripts"):
            total_archived += 1
            total_size += size
            print(f"   ✓ Archived: {duplicate_script.relative_to(ROOT)} ({size/1024:.1f} KB)")
            print(f"      (Superseded by check_discovery.py)")

    # SUMMARY
    print(f"\n" + "="*70)
    print("ARCHIVAL COMPLETE")
    print("="*70)
    print(f"Files archived: {total_archived}")
    print(f"Files deleted: {total_deleted}")
    print(f"Total space: {total_size/1024:.1f} KB ({total_size/(1024*1024):.2f} MB)")
    print(f"\n📦 Archive location: {archive_base.relative_to(ROOT)}")
    print()

    # Create manifest
    manifest_path = archive_base / "MANIFEST.txt"
    with open(manifest_path, 'w') as f:
        f.write(f"Haven Old Files Archive\n")
        f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"\n")
        f.write(f"Files Archived: {total_archived}\n")
        f.write(f"Files Deleted: {total_deleted}\n")
        f.write(f"Total Size: {total_size/1024:.1f} KB\n")
        f.write(f"\n")
        f.write(f"Categories:\n")
        f.write(f"  - database_backups/\n")
        f.write(f"  - keeper_diagnostics/\n")
        f.write(f"  - keeper_migrations/\n")
        f.write(f"  - keeper_json_backups/\n")
        f.write(f"  - misc_backups/\n")
        f.write(f"  - old_data_exports/\n")
        f.write(f"  - duplicate_scripts/\n")

    print(f"✅ Manifest created: {manifest_path.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
