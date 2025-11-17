import os
import sys
from fastapi.testclient import TestClient
# Ensure repo root and src are on sys.path like server.py does
REPO_ROOT = os.path.abspath(os.getcwd())
if REPO_ROOT not in sys.path:
	sys.path.insert(0, REPO_ROOT)
src_dir = os.path.join(REPO_ROOT, 'src')
if src_dir not in sys.path:
	sys.path.insert(0, src_dir)
os.environ['HAVEN_UI_DIR'] = os.path.join(os.getcwd(), 'Haven-UI')
from src import control_room_api
client = TestClient(control_room_api.app)
print('Status:', client.get('/api/status').json())
print('Stats:', client.get('/api/stats').json())
