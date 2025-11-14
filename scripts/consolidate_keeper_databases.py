"""
Consolidate Keeper Database Files
Merges all keeper.db files into the canonical location: docs/guides/Haven-lore/keeper-bot/data/keeper.db
"""

import sqlite3
import os
import shutil
from datetime import datetime

# Define paths
KEEPER_ROOT = "docs/guides/Haven-lore/keeper-bot"
CANONICAL_DB = f"{KEEPER_ROOT}/data/keeper.db"
ROOT_DB = f"{KEEPER_ROOT}/keeper.db"
SRC_DB = f"{KEEPER_ROOT}/src/data/keeper.db"

def backup_database(db_path):
    """Create a backup of a database file."""
    if os.path.exists(db_path) and os.path.getsize(db_path) > 0:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{db_path}.backup_{timestamp}"
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backed up {db_path} → {backup_path}")
        return backup_path
    return None

def get_table_counts(db_path):
    """Get record counts from all tables."""
    if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
        return {}

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    counts = {}
    tables = ['discoveries', 'patterns', 'investigations', 'user_stats',
              'pattern_discoveries', 'archive_entries', 'community_challenges',
              'challenge_submissions', 'user_achievements', 'community_events',
              'story_progression', 'pattern_contributions', 'server_config',
              'user_tier_progress']

    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = cursor.fetchone()[0]
        except sqlite3.OperationalError:
            # Table doesn't exist in this database
            pass

    conn.close()
    return counts

def copy_records(source_db, target_db, table_name):
    """Copy records from source to target, avoiding duplicates."""
    source_conn = sqlite3.connect(source_db)
    target_conn = sqlite3.connect(target_db)

    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()

    # Get all records from source
    source_cursor.execute(f"SELECT * FROM {table_name}")
    source_records = source_cursor.fetchall()

    # Get column names
    source_cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in source_cursor.fetchall()]

    # Get existing IDs from target (if table has an 'id' column)
    existing_ids = set()
    if 'id' in columns:
        try:
            target_cursor.execute(f"SELECT id FROM {table_name}")
            existing_ids = {row[0] for row in target_cursor.fetchall()}
        except sqlite3.OperationalError:
            pass

    # Copy non-duplicate records
    copied = 0
    skipped = 0

    for record in source_records:
        record_dict = dict(zip(columns, record))

        # Skip if record with this ID already exists
        if 'id' in columns and record_dict.get('id') in existing_ids:
            skipped += 1
            continue

        # Insert record
        placeholders = ','.join(['?' for _ in columns])
        column_names = ','.join(columns)

        try:
            target_cursor.execute(
                f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})",
                record
            )
            copied += 1
        except sqlite3.IntegrityError as e:
            print(f"   ⚠️  Skipping duplicate in {table_name}: {e}")
            skipped += 1

    target_conn.commit()
    source_conn.close()
    target_conn.close()

    return copied, skipped

def consolidate_databases():
    """Main consolidation logic."""
    print("\n" + "="*70)
    print("KEEPER DATABASE CONSOLIDATION")
    print("="*70 + "\n")

    # Analyze current state
    print("📊 Current State Analysis:")
    print("-" * 70)

    print(f"\n1. ROOT keeper.db ({ROOT_DB}):")
    root_counts = get_table_counts(ROOT_DB)
    if root_counts:
        for table, count in root_counts.items():
            if count > 0:
                print(f"   {table}: {count} records")
    else:
        print("   ❌ Empty or doesn't exist")

    print(f"\n2. DATA keeper.db ({CANONICAL_DB}) [CANONICAL TARGET]:")
    canonical_counts = get_table_counts(CANONICAL_DB)
    if canonical_counts:
        for table, count in canonical_counts.items():
            if count > 0:
                print(f"   {table}: {count} records")
    else:
        print("   ❌ Empty or doesn't exist")

    print(f"\n3. SRC keeper.db ({SRC_DB}):")
    src_counts = get_table_counts(SRC_DB)
    if src_counts:
        for table, count in src_counts.items():
            if count > 0:
                print(f"   {table}: {count} records")
    else:
        print("   ❌ Empty or doesn't exist")

    # Backup all databases
    print("\n" + "="*70)
    print("💾 Creating Backups:")
    print("-" * 70)
    backup_database(ROOT_DB)
    backup_database(CANONICAL_DB)
    backup_database(SRC_DB)

    # Ensure canonical database directory exists
    os.makedirs(os.path.dirname(CANONICAL_DB), exist_ok=True)

    # Initialize canonical database with schema if it doesn't exist
    if not os.path.exists(CANONICAL_DB) or os.path.getsize(CANONICAL_DB) == 0:
        print(f"\n⚠️  Canonical database is empty. Copying schema from src database...")
        shutil.copy2(SRC_DB, CANONICAL_DB)
        # Clear all data, keep schema
        conn = sqlite3.connect(CANONICAL_DB)
        cursor = conn.cursor()
        for table in src_counts.keys():
            try:
                cursor.execute(f"DELETE FROM {table}")
            except:
                pass
        conn.commit()
        conn.close()
        print(f"✅ Schema initialized in {CANONICAL_DB}")

    # Merge data from SRC to CANONICAL
    print("\n" + "="*70)
    print("🔄 Merging SRC database → CANONICAL:")
    print("-" * 70)

    if src_counts:
        for table, count in src_counts.items():
            if count > 0:
                print(f"\n📋 Merging {table}...")
                copied, skipped = copy_records(SRC_DB, CANONICAL_DB, table)
                print(f"   ✅ Copied: {copied} | Skipped (duplicates): {skipped}")

    # Merge data from ROOT to CANONICAL (if any)
    print("\n" + "="*70)
    print("🔄 Merging ROOT database → CANONICAL:")
    print("-" * 70)

    if root_counts and any(root_counts.values()):
        for table, count in root_counts.items():
            if count > 0:
                print(f"\n📋 Merging {table}...")
                copied, skipped = copy_records(ROOT_DB, CANONICAL_DB, table)
                print(f"   ✅ Copied: {copied} | Skipped (duplicates): {skipped}")
    else:
        print("   No data to merge from ROOT database")

    # Final verification
    print("\n" + "="*70)
    print("✅ FINAL STATE - Canonical Database:")
    print("-" * 70)

    final_counts = get_table_counts(CANONICAL_DB)
    total_records = 0
    for table, count in final_counts.items():
        if count > 0:
            print(f"   {table}: {count} records")
            total_records += count

    print(f"\n📊 Total Records: {total_records}")

    # Archive old databases
    print("\n" + "="*70)
    print("📦 Archiving Old Database Files:")
    print("-" * 70)

    archive_dir = "Archive-Dump/keeper_db_migration_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(archive_dir, exist_ok=True)

    if os.path.exists(ROOT_DB) and os.path.getsize(ROOT_DB) > 0:
        shutil.move(ROOT_DB, f"{archive_dir}/keeper_root.db")
        print(f"   ✅ Archived {ROOT_DB} → {archive_dir}/keeper_root.db")
    elif os.path.exists(ROOT_DB):
        os.remove(ROOT_DB)
        print(f"   ✅ Removed empty {ROOT_DB}")

    if os.path.exists(SRC_DB):
        shutil.move(SRC_DB, f"{archive_dir}/keeper_src.db")
        print(f"   ✅ Archived {SRC_DB} → {archive_dir}/keeper_src.db")
        # Remove the now-empty src/data directory if empty
        src_data_dir = os.path.dirname(SRC_DB)
        if os.path.exists(src_data_dir) and not os.listdir(src_data_dir):
            os.rmdir(src_data_dir)
            print(f"   ✅ Removed empty directory {src_data_dir}")

    print("\n" + "="*70)
    print("✅ CONSOLIDATION COMPLETE")
    print("="*70)
    print(f"\n📍 Canonical Database Location: {CANONICAL_DB}")
    print(f"📦 Archived Files Location: {archive_dir}")
    print(f"💾 Backups: *.backup_* files")
    print("\n⚠️  NEXT STEP: Update keeper_db.py to use correct path\n")

if __name__ == "__main__":
    consolidate_databases()
