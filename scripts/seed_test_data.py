from pathlib import Path
import sys
import traceback

# Ensure repo src is on path when running this script from repo root
repo_root = Path.cwd()
src_path = repo_root / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from src.common.database import HavenDatabase

DB_PATH = repo_root / 'Haven-UI' / 'data' / 'haven_ui.db'

SAMPLE_SYSTEMS = [
    {
        'name': 'AURORA-7',
        'region': 'Aurora',
        'x': 12.3, 'y': -45.6, 'z': 78.9,
        'fauna': 'Sparse',
        'flora': 'Lush',
        'materials': 'Cadmium,Gold',
        'planets': [
            {'name': 'Aurora Prime', 'fauna': 'Exotic', 'materials': 'Cadmium,Emeril', 'moons': [
                {'name': 'Aurora Prime I', 'fauna': 'Tiny'},
                {'name': 'Aurora Prime II', 'fauna': 'None'}
            ]},
            {'name': 'Aurora Secondary', 'fauna': 'Common', 'moons': []}
        ],
        'space_station': {'name': 'Aurora Trade Hub', 'x': 12.4, 'y': -45.5, 'z': 79.0, 'race': 'Korvax', 'sell_percent': 90, 'buy_percent': 60}
    },
    {
        'name': 'NMS-OUTPOST-1',
        'region': 'Outlands',
        'x': -123.4, 'y': 55.1, 'z': -9.0,
        'fauna': 'Abundant',
        'flora': 'Sparse',
        'materials': 'Iron,Carbon',
        'planets': [
            {'name': 'Outpost Prime', 'fauna': 'None', 'moons': [{'name': 'Outpost Moon A'}]}
        ],
        'space_station': None
    },
    {
        'name': 'SERENITY-3',
        'region': 'Serenity',
        'x': 0.0, 'y': 0.0, 'z': 0.0,
        'fauna': 'Moderate',
        'flora': 'Moderate',
        'materials': 'Emeril,Gold',
        'planets': [
            {'name': 'Serenity I', 'fauna': 'Varied', 'moons': [{'name': 'Serenity I-A'}, {'name': 'Serenity I-B'}]},
        ],
        'space_station': {'name': 'Serenity Dock', 'x': 0.1, 'y': -0.1, 'z': 0.0, 'race': 'Gek', 'sell_percent': 70, 'buy_percent': 45}
    }
]

SAMPLE_DISCOVERIES = [
    # Will populate after systems added, referencing system names
    {
        'discovery_type': 'anomaly',
        'discovery_name': 'Weird Monolith',
        'location_type': 'space',
        'location_name': 'Near Aurora Prime',
        'description': 'Strange monolith emitting an unusual signal',
        'coordinates': '12.31,-45.62,78.95',
        'discovered_by': 'demo_user',
    },
    {
        'discovery_type': 'flora',
        'discovery_name': 'Blue Fern',
        'location_type': 'planet',
        'description': 'Bioluminescent fern found in fungal groves',
        'discovered_by': 'bot_ingest',
    },
    {
        'discovery_type': 'base',
        'discovery_name': 'Hidden Base',
        'location_type': 'moon',
        'description': 'Small hidden base tucked under cliffs',
        'discovered_by': 'demo_user',
    }
]


def main():
    print(f"Seeding DB at: {DB_PATH}")
    try:
        with HavenDatabase(str(DB_PATH)) as db:
            created = []
            for s in SAMPLE_SYSTEMS:
                try:
                    if db.system_exists(s['name']):
                        print(f"System already exists, skipping: {s['name']}")
                        continue
                    sid = db.add_system(s)
                    print(f"Added system {s['name']} -> id={sid}")
                    created.append(s['name'])
                except Exception as e:
                    print(f"Failed to add system {s['name']}: {e}")
                    traceback.print_exc()

            # Insert discoveries referencing systems / planets / moons
            # Map system names to IDs and planet/moon ids
            for sname in created:
                sys = db.get_system_by_name(sname)
                # Add one discovery per system if available
                if sys and sys.get('planets'):
                    planet = sys['planets'][0]
                    # discovery referencing planet
                    disc = {
                        'discovery_type': 'flora',
                        'discovery_name': f"Lush Patch on {planet['name']}",
                        'location_type': 'planet',
                        'system_id': sys['id'],
                        'planet_id': planet['id'],
                        'description': f"Notable vegetation discovered on {planet['name']}.",
                        'discovered_by': 'demo_user'
                    }
                    try:
                        did = db.add_discovery(disc)
                        print(f"Added discovery for {sys['name']} planet {planet['name']} id={did}")
                    except Exception as e:
                        print(f"Failed to add discovery for {sys['name']}: {e}")
                # Add a moon discovery if moons exist
                if sys and sys.get('planets'):
                    # find first moon if any
                    moon_id = None
                    for p in sys['planets']:
                        if p.get('moons'):
                            moon = p['moons'][0]
                            moon_id = moon['id']
                            planet_id = p['id']
                            break
                    if moon_id:
                        disc = {
                            'discovery_type': 'base',
                            'discovery_name': f"Hidden Base on {moon['name']}",
                            'location_type': 'moon',
                            'system_id': sys['id'],
                            'planet_id': planet_id,
                            'moon_id': moon_id,
                            'description': f"A small base found on moon {moon['name']}.",
                            'discovered_by': 'demo_user'
                        }
                        try:
                            did = db.add_discovery(disc)
                            print(f"Added moon discovery for {sys['name']} moon {moon['name']} id={did}")
                        except Exception as e:
                            print(f"Failed to add moon discovery for {sys['name']}: {e}")

            # Add a few standalone sample discoveries not tied to a planet
            for extra in SAMPLE_DISCOVERIES:
                # Try to attach to a system by name heuristics
                attached = False
                for sname in created:
                    if 'Aurora' in sname and not attached:
                        sys = db.get_system_by_name(sname)
                        if sys:
                            extra_copy = extra.copy()
                            extra_copy['system_id'] = sys['id']
                            try:
                                did = db.add_discovery(extra_copy)
                                print(f"Added extra discovery {extra_copy.get('discovery_name')} -> id={did}")
                                attached = True
                                break
                            except Exception as e:
                                print(f"Failed to add extra discovery: {e}")
                if not attached:
                    try:
                        did = db.add_discovery(extra)
                        print(f"Added extra discovery {extra.get('discovery_name')} -> id={did}")
                    except Exception as e:
                        print(f"Failed to add extra discovery without system: {e}")

            # Summary
            stats = db.get_statistics()
            print("\nDB Summary:")
            print(stats)
    except Exception as e:
        print(f"Failed to open DB: {e}")
        traceback.print_exc()


if __name__ == '__main__':
    main()
