import os
import tempfile
from fastapi.testclient import TestClient


def test_discovery_post_and_get(tmp_path, monkeypatch):
    # Create a temp HAVEN_UI_DIR for the server to use
    tmp_ui = tmp_path / "haven_ui_tmp"
    tmp_ui.mkdir()
    monkeypatch.setenv('HAVEN_UI_DIR', str(tmp_ui))
    # Ensure admin token is set to test that admin auth flow works
    monkeypatch.setenv('HAVEN_ADMIN_TOKEN', 'test-admin-token')

    # Import app after environment is configured
    from src.control_room_api import app
    client = TestClient(app)

    # Verify status
    r = client.get('/api/status')
    assert r.status_code == 200
    j = r.json()
    assert 'status' in j and j['status'] == 'ok'

    # Create a minimal system to reference in discovery
    system_payload = {'name': 'TESTSYS', 'x': 0, 'y': 0, 'z': 0, 'region': 'TEST'}
    headers = {'X-HAVEN-ADMIN': 'test-admin-token'}
    resp = client.post('/api/systems', json=system_payload, headers=headers)
    assert resp.status_code == 200
    sys_id = resp.json().get('id')
    assert sys_id

    # Create a discovery referencing the system by id
    disc = {
        'discovery_type': 'test',
        'description': 'A test discovery',
        'location_type': 'space',
        'system_id': sys_id
    }
    headers = {'X-HAVEN-ADMIN': 'test-admin-token'}
    r = client.post('/api/discoveries', json=disc, headers=headers)
    assert r.status_code == 201
    jd = r.json()
    assert jd.get('success') is True
    did = jd.get('discovery_id')
    assert isinstance(did, int)

    # Fetch the created discovery
    gr = client.get(f'/api/discoveries/{did}')
    assert gr.status_code == 200
    gd = gr.json()
    assert gd.get('id') == did or 'id' in gd

    # Search using text query
    sr = client.get(f"/api/discoveries?q=test&limit=10")
    assert sr.status_code == 200
    results = sr.json().get('results', [])
    assert any(r['id'] == did for r in results)
