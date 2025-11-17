import os
os.environ.setdefault('HAVEN_ADMIN_TOKEN', 'test-admin-token')
import json
from starlette.testclient import TestClient
from src.control_room_api import app

client = TestClient(app)

def test_save_and_get_nested_system():
    sys_name = 'UT-TEST-SYS'
    payload = {
        'name': sys_name,
        'region': 'UNIT-TEST',
        'x': 0,
        'y': 0,
        'z': 0,
        'description': 'Test system with nested planets and moons',
        'planets': [
            {'name': 'Planet-A', 'sentinel': 'Low', 'moons': [{'name': 'Moon-A1'}]},
            {'name': 'Planet-B', 'sentinel': 'High', 'moons': []}
        ]
    }

    headers = {'X-HAVEN-ADMIN': os.environ.get('HAVEN_ADMIN_TOKEN', 'test-admin-token')}
    r = client.post('/api/save_system', json=payload, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data.get('status') in ('created', 'updated')

    # Fetch the system by name
    r2 = client.get(f'/api/systems/{sys_name}')
    assert r2.status_code == 200
    s = r2.json()
    assert s['name'] == sys_name
    assert 'planets' in s
    assert len(s['planets']) == 2
    assert s['planets'][0]['name'] == 'Planet-A'
    # ensure optional planet properties exist or are null
    assert 'fauna' in s['planets'][0]
    assert 'flora' in s['planets'][0]
    assert 'materials' in s['planets'][0]
    # moon orbit properties
    assert 'orbit_radius' in s['planets'][0]['moons'][0]
    assert 'orbit_speed' in s['planets'][0]['moons'][0]
    assert 'moons' in s['planets'][0]
    assert s['planets'][0]['moons'][0]['name'] == 'Moon-A1'

    # Cleanup
    # Delete by id if present
    sid = s.get('id') or s.get('name')
    if sid:
        client.delete(f'/api/systems/{sid}', headers=headers)
