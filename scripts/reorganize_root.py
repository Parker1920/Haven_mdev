"""
Root Directory Reorganization Script
Moves files from root into proper folder structure

Target: Keep ONLY these 3 files in root:
- Haven Control Room.bat
- haven_control_room_mac.command
- README.md

Move everything else to appropriate directories:
- Documentation (.md files) → docs/
- Utility scripts (.py files) → scripts/
- Other files → appropriate locations
"""

import shutil
import os
from pathlib import Path
from datetime import datetime

# Root directory
ROOT = Path("/Users/parkerstouffer/Desktop/Haven_mdev")

# Files to keep in root (ONLY these 3)
KEEP_IN_ROOT = {
    "Haven Control Room.bat",
    "haven_control_room_mac.command",
    "README.md"
}

# File organization rules
ORGANIZATION_RULES = {
    # Documentation files
    "AI_HANDOFF_DISCOVERIES.md": "docs/legacy-reports/",
    "BETA_CERTIFICATION_REPORT.md": "docs/legacy-reports/",
    "DELIVERY_SUMMARY.md": "docs/legacy-reports/",
    "DISCORD_BOT_RESET_SUMMARY.md": "docs/legacy-reports/",
    "DISCOVERIES_FIX_REPORT.md": "docs/legacy-reports/",
    "DISCOVERIES_QUICK_START.md": "docs/guides/",
    "DISCOVERY_IMPORT_FIX.md": "docs/legacy-reports/",
    "DISCOVERY_IMPORT_QUICK_FIX.md": "docs/legacy-reports/",
    "DISCOVERY_SYNC_GUIDE.md": "docs/guides/",
    "IMPORT_BUG_FIX_ANALYSIS.md": "docs/legacy-reports/",
    "IMPORT_FIX_COMPLETE.md": "docs/legacy-reports/",
    "IMPORT_FIX_REPORT.md": "docs/legacy-reports/",
    "KEEPER_DISCOVERIES_FORMAT_SUPPORT.md": "docs/guides/",
    "RAILWAY_ARCHITECTURE.md": "docs/deployment/",
    "RAILWAY_DEPLOYMENT_PLAN.md": "docs/deployment/",
    "RAILWAY_FILES_TO_CREATE.md": "docs/deployment/",
    "RAILWAY_INDEX.md": "docs/deployment/",
    "RAILWAY_QUICK_START.md": "docs/deployment/",
    "RAILWAY_SUMMARY.md": "docs/deployment/",
    "READ_ME_FIRST.md": "docs/",
    "START_HERE_RAILWAY.md": "docs/deployment/",
    "VISUAL_SUMMARY.md": "docs/",
    "WHAT_WAS_FIXED.md": "docs/legacy-reports/",

    # Utility scripts
    "check_discoveries.py": "scripts/utils/",
    "check_discovery.py": "scripts/utils/",
    "delete_discoveries.py": "scripts/utils/",
    "delete_test_systems.py": "scripts/utils/",
    "reset_discoveries.py": "scripts/utils/",
    "test_parse.py": "scripts/utils/",
}

def create_backup():
    """Create a backup of current root state"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = ROOT / "Archive-Dump" / f"root_backup_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    print(f"📦 Creating backup: {backup_dir}")

    # List all files in root
    for file in ROOT.iterdir():
        if file.is_file() and file.name not in KEEP_IN_ROOT:
            try:
                shutil.copy2(file, backup_dir / file.name)
            except Exception as e:
                print(f"   ⚠️  Failed to backup {file.name}: {e}")

    print(f"✅ Backup created: {backup_dir}")
    return backup_dir

def reorganize_files(dry_run=True):
    """Reorganize files according to rules"""
    print("\n" + "="*70)
    print("ROOT DIRECTORY REORGANIZATION")
    print("="*70 + "\n")

    if dry_run:
        print("🔍 DRY RUN MODE - No files will be moved\n")
    else:
        print("⚠️  LIVE MODE - Files will be moved\n")

    # Show what will be kept in root
    print("📌 Files to KEEP in root:")
    for filename in KEEP_IN_ROOT:
        file_path = ROOT / filename
        if file_path.exists():
            print(f"   ✓ {filename}")
        else:
            print(f"   ❌ {filename} (NOT FOUND)")

    print("\n" + "-"*70)
    print("📂 Files to MOVE:\n")

    moved_count = 0
    error_count = 0

    # Move files according to rules
    for filename, target_dir in ORGANIZATION_RULES.items():
        source = ROOT / filename

        if not source.exists():
            print(f"   ⊘ {filename} → {target_dir} (NOT FOUND)")
            continue

        target_path = ROOT / target_dir
        target_file = target_path / filename

        print(f"   {'→' if dry_run else '✓'} {filename}")
        print(f"      FROM: {source.relative_to(ROOT)}")
        print(f"      TO:   {target_file.relative_to(ROOT)}")

        if not dry_run:
            try:
                # Create target directory
                target_path.mkdir(parents=True, exist_ok=True)

                # Move file
                shutil.move(str(source), str(target_file))
                moved_count += 1

            except Exception as e:
                print(f"      ❌ ERROR: {e}")
                error_count += 1
        else:
            moved_count += 1

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Files to keep in root: {len(KEEP_IN_ROOT)}")
    print(f"Files {'to be moved' if dry_run else 'moved'}: {moved_count}")
    if error_count > 0:
        print(f"Errors: {error_count}")
    print()

    # List final root state
    if not dry_run:
        print("📂 Final root directory contents:")
        root_files = [f.name for f in ROOT.iterdir() if f.is_file()]
        for filename in sorted(root_files):
            marker = "✓" if filename in KEEP_IN_ROOT else "⚠️ "
            print(f"   {marker} {filename}")

        # Check for unexpected files
        unexpected = [f for f in root_files if f not in KEEP_IN_ROOT]
        if unexpected:
            print(f"\n⚠️  WARNING: {len(unexpected)} unexpected files remain in root:")
            for f in unexpected:
                print(f"   - {f}")

    return moved_count, error_count

def main():
    """Main reorganization process"""
    import sys

    print("="*70)
    print("HAVEN ROOT DIRECTORY CLEANUP")
    print("="*70)
    print()
    print("This script will reorganize the root directory:")
    print("  - Keep ONLY 3 files in root (launchers + README)")
    print("  - Move documentation to docs/")
    print("  - Move scripts to scripts/")
    print("  - Create backup before moving")
    print()

    # First, run dry run
    print("STEP 1: Dry Run (preview changes)")
    print("-"*70)
    moved_count, error_count = reorganize_files(dry_run=True)

    print()
    print("="*70)
    input("Press ENTER to proceed with actual reorganization, or Ctrl+C to cancel...")
    print()

    # Create backup
    print("STEP 2: Create Backup")
    print("-"*70)
    backup_dir = create_backup()

    # Actual reorganization
    print("\nSTEP 3: Reorganize Files")
    print("-"*70)
    moved_count, error_count = reorganize_files(dry_run=False)

    print()
    print("="*70)
    print("✅ REORGANIZATION COMPLETE")
    print("="*70)
    print(f"Backup location: {backup_dir}")
    print(f"Files moved: {moved_count}")
    if error_count > 0:
        print(f"⚠️  Errors: {error_count} (check output above)")
    print()
    print("Next step: Update imports in affected files")

if __name__ == "__main__":
    main()
