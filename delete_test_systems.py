"""
Delete test systems from VH-Database.db
Keeps only Tenex[VH] and The Diamond In The Rough[VH]
Deletes associated planets and moons via CASCADE
"""

import sqlite3
from pathlib import Path

def delete_test_systems():
    """Delete Alpha, W, and Zebungo ultra systems"""

    db_path = Path('data/VH-Database.db')

    # Systems to KEEP
    keep_systems = ['Tenex[VH]', 'The Diamond In The Rough[VH]']

    print("Deleting test systems from VH-Database.db...")
    print(f"Will keep: {', '.join(keep_systems)}")
    print()

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")  # Enable cascading deletes
    cursor = conn.cursor()

    # Get all systems
    cursor.execute('SELECT id, name FROM systems ORDER BY name')
    all_systems = cursor.fetchall()

    print(f"Found {len(all_systems)} systems:")
    for sys_id, sys_name in all_systems:
        print(f"  {sys_id}: {sys_name}")
    print()

    # Delete systems not in keep list
    deleted_count = 0
    for sys_id, sys_name in all_systems:
        if sys_name not in keep_systems:
            # Count planets and moons before deletion
            cursor.execute('SELECT COUNT(*) FROM planets WHERE system_id = ?', (sys_id,))
            planet_count = cursor.fetchone()[0]

            cursor.execute('''
                SELECT COUNT(*) FROM moons m
                JOIN planets p ON m.planet_id = p.id
                WHERE p.system_id = ?
            ''', (sys_id,))
            moon_count = cursor.fetchone()[0]

            print(f"Deleting system: {sys_name} (ID: {sys_id})")
            print(f"  - {planet_count} planets")
            print(f"  - {moon_count} moons")

            # Delete system (planets and moons will cascade)
            cursor.execute('DELETE FROM systems WHERE id = ?', (sys_id,))
            deleted_count += 1
            print(f"  [OK] Deleted")
            print()

    conn.commit()

    # Verify remaining systems
    cursor.execute('SELECT id, name FROM systems ORDER BY name')
    remaining = cursor.fetchall()

    print(f"\n[DONE] Deleted {deleted_count} test systems")
    print(f"\nRemaining systems ({len(remaining)}):")
    for sys_id, sys_name in remaining:
        # Count planets and moons
        cursor.execute('SELECT COUNT(*) FROM planets WHERE system_id = ?', (sys_id,))
        planet_count = cursor.fetchone()[0]

        cursor.execute('''
            SELECT COUNT(*) FROM moons m
            JOIN planets p ON m.planet_id = p.id
            WHERE p.system_id = ?
        ''', (sys_id,))
        moon_count = cursor.fetchone()[0]

        print(f"  {sys_name}")
        print(f"    - {planet_count} planets, {moon_count} moons")

    conn.close()

if __name__ == "__main__":
    delete_test_systems()
