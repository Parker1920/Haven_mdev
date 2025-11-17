"""
Small helper to inspect sqlite DB and list tables and schema.
Usage: python scripts/db_inspect.py [path_to_db]
If path is omitted, defaults to Haven-UI/data/haven_ui.db
"""
import sqlite3
import sys
from pathlib import Path


def inspect_db(db_path: Path):
    print(f"Inspecting DB: {db_path}")
    if not db_path.exists():
        print("DB file does not exist")
        return

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]
    print("Tables:")
    for t in tables:
        print(f"  - {t}")
        cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (t,))
        row = cur.fetchone()
        if row and row[0]:
            print(f"    Schema: {row[0][:200]}{'...' if len(row[0])>200 else ''}")

    conn.close()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        db = Path(sys.argv[1])
    else:
        db = Path(__file__).parent.parent / 'Haven-UI' / 'data' / 'haven_ui.db'
    inspect_db(db)
