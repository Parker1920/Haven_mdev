"""
Probe provider initialization and DB schema creation outside of the server process
"""
import os
from pathlib import Path
import logging
import sys
from pathlib import Path

# Ensure src is on sys.path for imports when running from scripts/
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))
from src.common.data_provider import get_data_provider

def run_probe():
    # Use Haven-UI DB path by default
    repo_root = Path(__file__).parent.parent
    ui_db = repo_root / 'Haven-UI' / 'data' / 'haven_ui.db'

    logging.basicConfig(level=logging.DEBUG)
    print(f"Using DB path: {ui_db}")
    provider = get_data_provider(use_database=True, db_path=str(ui_db), json_path=str(repo_root / 'Haven-UI' / 'data' / 'data.json'))
    print("Provider created. Querying stats...")
    try:
        total = provider.get_total_count()
        print(f"Total count from provider: {total}")
    except Exception as e:
        print(f"Provider get_total_count failed: {e}")

if __name__ == '__main__':
    run_probe()
