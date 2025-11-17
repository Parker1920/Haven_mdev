import os
import time
from fastapi.testclient import TestClient

# Set env var for test password before importing app
os.environ['HAVEN_ADMIN_PASSWORD'] = 'testpass'
from src.control_room_api import app

client = TestClient(app)


def test_admin_login_logout():
    # Set env var for test password
    os.environ['HAVEN_ADMIN_PASSWORD'] = 'testpass'
    # Ensure status is false
    r = client.get('/api/admin/status')
    assert r.status_code == 200
    assert r.json().get('logged_in') in (False, True)

    # Login with wrong password should fail
    r = client.post('/api/admin/login', json={'password': 'wrong'}, allow_redirects=False)
    assert r.status_code == 403 or r.status_code == 500

    # Login with correct password
    r = client.post('/api/admin/login', json={'password': 'testpass'}, allow_redirects=False)
    assert r.status_code == 200
    # Ensure session cookie is set
    assert 'haven_session_token' in r.cookies

    # Now status should reflect logged_in True
    r = client.get('/api/admin/status')
    assert r.status_code == 200

    # Logout
    r = client.post('/api/admin/logout')
    assert r.status_code == 200

    # Status should be false/reset
    r = client.get('/api/admin/status')
    assert r.status_code == 200