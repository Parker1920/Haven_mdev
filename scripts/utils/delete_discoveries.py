"""
Delete all discoveries from both VH-Database.db and keeper.db
Keeps all systems, planets, and moons intact
"""

import sqlite3
from pathlib import Path

def delete_all_discoveries():
    """Delete all discoveries from both databases"""

    # VH-Database.db
    vh_db_path = Path('data/VH-Database.db')
    keeper_db_path = Path('docs/guides/Haven-lore/keeper-bot/data/keeper.db')

    # Delete from VH-Database.db
    print("Deleting discoveries from VH-Database.db...")
    conn = sqlite3.connect(str(vh_db_path))
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM discoveries')
    count_before = cursor.fetchone()[0]
    print(f"  Discoveries before: {count_before}")

    cursor.execute('DELETE FROM discoveries')
    conn.commit()

    cursor.execute('SELECT COUNT(*) FROM discoveries')
    count_after = cursor.fetchone()[0]
    print(f"  Discoveries after: {count_after}")
    print(f"  Deleted: {count_before - count_after}")

    conn.close()

    # Delete from keeper.db
    print("\nDeleting discoveries from keeper.db...")
    if keeper_db_path.exists():
        conn = sqlite3.connect(str(keeper_db_path))
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT COUNT(*) FROM discoveries')
            count_before = cursor.fetchone()[0]
            print(f"  Discoveries before: {count_before}")

            cursor.execute('DELETE FROM discoveries')
            conn.commit()

            cursor.execute('SELECT COUNT(*) FROM discoveries')
            count_after = cursor.fetchone()[0]
            print(f"  Discoveries after: {count_after}")
            print(f"  Deleted: {count_before - count_after}")
        except sqlite3.OperationalError as e:
            print(f"  Error: {e}")

        conn.close()
    else:
        print(f"  keeper.db not found at {keeper_db_path}")

    print("\n[DONE] All discoveries deleted from both databases!")

if __name__ == "__main__":
    delete_all_discoveries()
