import sqlite3
import json

conn = sqlite3.connect('data/VH-Database.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Find Luzhilar system
cursor.execute("SELECT id, name FROM systems WHERE name LIKE '%Luzhilar%'")
row = cursor.fetchone()
if row:
    system = dict(row)
    print('System:', json.dumps(system, indent=2))

    # Find planets in this system
    cursor.execute('SELECT id, name, system_id FROM planets WHERE system_id = ?', (system['id'],))
    planets = [dict(r) for r in cursor.fetchall()]
    print('\nPlanets:', json.dumps(planets, indent=2))

    # Find discovery
    cursor.execute('SELECT id, discovery_type, system_id, planet_id, moon_id, location_name, location_type FROM discoveries WHERE system_id = ?', (system['id'],))
    discoveries = [dict(r) for r in cursor.fetchall()]
    print('\nDiscoveries:', json.dumps(discoveries, indent=2))
else:
    print('System not found')

conn.close()
