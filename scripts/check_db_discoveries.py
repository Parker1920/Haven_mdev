import sys, os
sys.path.insert(0, os.path.abspath('.'))
from src.common.database import HavenDatabase
from pathlib import Path

DB_PATH = Path('.') / 'Haven-UI' / 'data' / 'haven_ui.db'
print('Checking DB:', DB_PATH)

with HavenDatabase(str(DB_PATH)) as db:
    discoveries = db.get_discoveries(limit=1000)
    print('Total discoveries in DB:', len(discoveries))
    for d in discoveries:
        print(d['id'], d['discovery_type'], d.get('discovery_name'), 'sys=', d.get('system_id'), 'planet=', d.get('planet_id'), 'moon=', d.get('moon_id'))
