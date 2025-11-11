"""
Verify Keeper Bot is in Act One State
Checks both VH-Database.db and keeper.db
"""

import sqlite3
from pathlib import Path

def verify_act_one_state():
    """Verify the bot is ready for Act One"""

    print("=" * 60)
    print("KEEPER BOT ACT ONE STATUS VERIFICATION")
    print("=" * 60)
    print()

    # Check VH-Database.db (Haven Master Database)
    vh_db_path = Path('../../../data/VH-Database.db')
    print("1. Checking VH-Database.db (Haven Master)...")

    if vh_db_path.exists():
        conn = sqlite3.connect(str(vh_db_path))
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM discoveries')
        vh_discovery_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM systems')
        system_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM planets')
        planet_count = cursor.fetchone()[0]

        print(f"   Systems: {system_count}")
        print(f"   Planets: {planet_count}")
        print(f"   Discoveries: {vh_discovery_count}")

        if vh_discovery_count == 0:
            print("   [OK] No discoveries in VH-Database.db")
        else:
            print(f"   [WARNING] {vh_discovery_count} discoveries still exist!")

        conn.close()
    else:
        print("   [ERROR] VH-Database.db not found!")

    print()

    # Check keeper.db (Bot Internal Database)
    keeper_db_path = Path('keeper.db')
    print("2. Checking keeper.db (Bot Internal)...")

    if keeper_db_path.exists():
        conn = sqlite3.connect(str(keeper_db_path))
        cursor = conn.cursor()

        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()

        if not tables:
            print("   [OK] keeper.db is empty (will initialize on bot start)")
        else:
            print(f"   Found {len(tables)} tables:")

            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"     - {table_name}: {count} rows")

                if count > 0:
                    print(f"     [WARNING] {table_name} is not empty!")

        conn.close()
    else:
        print("   [OK] keeper.db does not exist (will be created on bot start)")

    print()

    # Determine Act State
    print("3. Determining Act State...")
    print()

    if not keeper_db_path.exists() or not Path(keeper_db_path).stat().st_size > 0:
        print("   Current Act: ACT I - The Awakening in Silence")
        print("   Status: READY")
        print()
        print("   Act I Requirements:")
        print("   - Discoveries: 0 (CLEAN)")
        print("   - Patterns: 0 (NONE DETECTED)")
        print("   - Bot State: Fresh Start")
        print()
        print("   Next Milestone:")
        print("   - Submit discoveries until first pattern emerges")
        print("   - Pattern detection unlocks Act II")
        print()
        act_one_ready = True
    else:
        conn = sqlite3.connect(str(keeper_db_path))
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT COUNT(*) FROM discoveries')
            keeper_discoveries = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM patterns')
            pattern_count = cursor.fetchone()[0]

            print(f"   Discoveries in keeper.db: {keeper_discoveries}")
            print(f"   Patterns detected: {pattern_count}")
            print()

            if keeper_discoveries == 0 and pattern_count == 0:
                print("   Current Act: ACT I - The Awakening in Silence")
                print("   Status: READY")
                act_one_ready = True
            elif pattern_count == 0:
                print("   Current Act: ACT I - In Progress")
                print(f"   Status: {keeper_discoveries} discoveries, awaiting pattern")
                act_one_ready = True
            elif pattern_count >= 1 and pattern_count < 3:
                print("   Current Act: ACT II - The Gathering of the Lost")
                print(f"   Status: {pattern_count} patterns detected")
                act_one_ready = False
            else:
                print("   Current Act: ACT III - Patterns in the Void")
                print(f"   Status: {pattern_count} patterns detected")
                act_one_ready = False

        except sqlite3.OperationalError:
            print("   Current Act: ACT I - The Awakening in Silence")
            print("   Status: READY (tables not yet created)")
            act_one_ready = True

        conn.close()

    print()
    print("=" * 60)

    if act_one_ready:
        print("RESULT: BOT IS IN ACT ONE STATE")
    else:
        print("RESULT: BOT IS BEYOND ACT ONE")

    print("=" * 60)

if __name__ == "__main__":
    verify_act_one_state()
