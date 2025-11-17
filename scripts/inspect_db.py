import sqlite3
from pathlib import Path
p = Path('Haven-UI/data/haven_ui.db')
if not p.exists():
    print('DB not found:', p)
    raise SystemExit(1)
conn = sqlite3.connect(str(p))
conn.row_factory = sqlite3.Row
cur = conn.cursor()
for t in ['systems','planets','moons','space_stations','discoveries']:
    try:
        cur.execute(f'SELECT COUNT(*) as c FROM {t}')
        print(t, cur.fetchone()['c'])
    except Exception as e:
        print(t, 'ERR', e)

print('\nSample systems:')
cur.execute('SELECT id,name,region,x,y,z FROM systems LIMIT 50')
for r in cur.fetchall():
    print(dict(r))

print('\nSample planets:')
cur.execute('SELECT id,system_id,name FROM planets LIMIT 50')
for r in cur.fetchall():
    print(dict(r))

print('\nSample moons:')
cur.execute('SELECT id,planet_id,name FROM moons LIMIT 50')
for r in cur.fetchall():
    print(dict(r))

print('\nSample discoveries:')
cur.execute('SELECT id,discovery_type,discovery_name,system_id,planet_id,moon_id FROM discoveries LIMIT 50')
for r in cur.fetchall():
    print(dict(r))

conn.close()
