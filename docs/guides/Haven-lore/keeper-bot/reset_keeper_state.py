"""
Reset Keeper Bot to Act One State
Clears all pattern recognition data and discoveries from keeper.db
"""

import sqlite3
from pathlib import Path

def reset_keeper_to_act_one():
    """Reset keeper.db to Act One (no discoveries, no patterns)"""

    db_path = Path('data/keeper.db')

    if not db_path.exists():
        print("keeper.db does not exist yet - will be created on bot startup")
        return

    print("Resetting Keeper Bot to Act One state...")
    print()

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Check what tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()

    if not tables:
        print("No tables found in keeper.db - database is empty")
        conn.close()
        return

    print(f"Found {len(tables)} tables:")
    for table in tables:
        print(f"  - {table[0]}")
    print()

    # Count current data
    table_counts = {}
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        table_counts[table_name] = count
        if count > 0:
            print(f"{table_name}: {count} rows")

    print()

    # Reset each table
    if 'discoveries' in table_counts:
        print(f"Clearing {table_counts['discoveries']} discoveries...")
        cursor.execute("DELETE FROM discoveries")
        print("  [OK] Discoveries cleared")

    if 'patterns' in table_counts:
        print(f"Clearing {table_counts['patterns']} patterns...")
        cursor.execute("DELETE FROM patterns")
        print("  [OK] Patterns cleared")

    if 'pattern_discoveries' in table_counts:
        print(f"Clearing {table_counts['pattern_discoveries']} pattern-discovery links...")
        cursor.execute("DELETE FROM pattern_discoveries")
        print("  [OK] Pattern-discovery links cleared")

    if 'investigations' in table_counts:
        print(f"Clearing {table_counts.get('investigations', 0)} investigations...")
        cursor.execute("DELETE FROM investigations")
        print("  [OK] Investigations cleared")

    # Reset story progression to Act I (CRITICAL - this is what shows Act state in /story-info)
    if 'story_progression' in table_counts:
        print(f"Resetting story progression to Act I...")
        cursor.execute("""
            UPDATE story_progression
            SET current_act = 1,
                act_1_complete = 0,
                act_2_complete = 0,
                act_3_complete = 0,
                act_1_timestamp = NULL,
                act_2_timestamp = NULL,
                act_3_timestamp = NULL,
                total_discoveries = 0,
                total_patterns = 0,
                story_milestone_count = 0,
                last_updated = CURRENT_TIMESTAMP
        """)
        print("  [OK] Story progression reset to Act I")

    # Reset auto-increment counters
    cursor.execute("DELETE FROM sqlite_sequence")
    print("  [OK] Reset auto-increment counters")

    conn.commit()

    # Verify empty state
    print()
    print("Verifying Act One state:")
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  {table_name}: {count} rows")

    conn.close()

    print()
    print("[DONE] Keeper Bot reset to Act One state!")
    print()
    print("The bot will now:")
    print("  - Have 0 discoveries logged")
    print("  - Have 0 patterns detected")
    print("  - Be waiting for first discovery submission")
    print("  - Start pattern recognition from scratch")

if __name__ == "__main__":
    reset_keeper_to_act_one()
