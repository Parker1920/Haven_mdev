"""
Reset discoveries to clean slate - removes all discoveries while keeping systems intact
"""
import sqlite3
import json
import sys

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def reset_discoveries(db_path):
    """Delete all discoveries from the database"""
    print(f"\n{'='*60}")
    print(f"Processing: {db_path}")
    print('='*60)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Check if discoveries table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='discoveries'")
        if not cursor.fetchone():
            print("\n✓ No discoveries table - skipping")
            return

        # Check current state
        cursor.execute("SELECT COUNT(*) as count FROM discoveries")
        discovery_count = cursor.fetchone()[0]

        # Check if this is a Haven database (has systems table) or keeper database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='systems'")
        has_systems_table = cursor.fetchone() is not None

        if has_systems_table:
            cursor.execute("SELECT COUNT(*) as count FROM systems")
            system_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) as count FROM planets")
            planet_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) as count FROM moons")
            moon_count = cursor.fetchone()[0]

            print(f"\nCurrent state:")
            print(f"  Systems: {system_count}")
            print(f"  Planets: {planet_count}")
            print(f"  Moons: {moon_count}")
            print(f"  Discoveries: {discovery_count}")
        else:
            print(f"\nCurrent state:")
            print(f"  Discoveries: {discovery_count}")

        if discovery_count == 0:
            print("\n✓ No discoveries to delete")
            return

        # Delete all discoveries
        cursor.execute("DELETE FROM discoveries")
        deleted = cursor.rowcount

        # Commit changes
        conn.commit()

        print(f"\n✓ Deleted {deleted} discoveries")

        # Verify final state
        cursor.execute("SELECT COUNT(*) as count FROM discoveries")
        final_discoveries = cursor.fetchone()[0]

        if has_systems_table:
            cursor.execute("SELECT COUNT(*) as count FROM systems")
            final_systems = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) as count FROM planets")
            final_planets = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) as count FROM moons")
            final_moons = cursor.fetchone()[0]

            print(f"\nFinal state:")
            print(f"  Systems: {final_systems}")
            print(f"  Planets: {final_planets}")
            print(f"  Moons: {final_moons}")
            print(f"  Discoveries: {final_discoveries}")

            if final_systems == system_count and final_planets == planet_count and final_moons == moon_count:
                print("\n✓ Systems, planets, and moons remain intact")
            else:
                print("\n⚠ WARNING: System/planet/moon counts changed!")
        else:
            print(f"\nFinal state:")
            print(f"  Discoveries: {final_discoveries}")
            print("\n✓ Keeper database discoveries reset")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    # Reset both Haven databases
    reset_discoveries('data/VH-Database.db')
    reset_discoveries('data/haven_load_test.db')

    # Reset Discord bot's keeper database
    reset_discoveries('docs/guides/Haven-lore/keeper-bot/data/keeper.db')

    print(f"\n{'='*60}")
    print("✓ Discovery reset complete!")
    print("✓ All star systems preserved")
    print("✓ Discord bot ready for fresh start")
    print('='*60)
