"""
Quick script to check recent discoveries in VH-Database.db
Run this after submitting a discovery to verify it was saved.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "VH-Database.db"

def check_recent_discoveries(limit=10):
    """Check the most recent discoveries in the database."""

    if not DB_PATH.exists():
        print(f"❌ Database not found at: {DB_PATH}")
        return

    print(f"📊 Checking VH-Database.db at: {DB_PATH}")
    print("=" * 80)
    print()

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get total count
        cursor.execute("SELECT COUNT(*) as total FROM discoveries")
        total = cursor.fetchone()['total']
        print(f"Total discoveries in database: {total}")
        print()

        # Get recent discoveries
        cursor.execute("""
            SELECT
                d.id,
                d.celestial_body_name,
                d.discovery_type,
                d.discoverer_name,
                d.discovery_date,
                d.created_at,
                s.name as system_name
            FROM discoveries d
            LEFT JOIN systems s ON d.system_id = s.id
            ORDER BY d.created_at DESC
            LIMIT ?
        """, (limit,))

        discoveries = cursor.fetchall()

        if discoveries:
            print(f"📝 Last {len(discoveries)} discoveries:")
            print("-" * 80)

            for disc in discoveries:
                print(f"ID: {disc['id']}")
                print(f"  Body: {disc['celestial_body_name']}")
                print(f"  Type: {disc['discovery_type']}")
                print(f"  System: {disc['system_name'] or 'N/A'}")
                print(f"  Discoverer: {disc['discoverer_name']}")
                print(f"  Discovery Date: {disc['discovery_date']}")
                print(f"  Added to DB: {disc['created_at']}")
                print()
        else:
            print("No discoveries found in database.")

        conn.close()

        print("=" * 80)
        print("✅ Database check complete!")

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_recent_discoveries()
    input("\nPress Enter to exit...")
