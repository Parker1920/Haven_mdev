#!/usr/bin/env python3
"""Debug script to check if planets are being prepared for the map."""

import pandas as pd
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent / 'config'))

from Beta_VH_Map import prepare_single_system_solar
from common.data_provider import DatabaseDataProvider

# Get system from database
db_provider = DatabaseDataProvider('data/haven.db')
systems = db_provider.get_all_systems(include_planets=True)

# Find LEPUSCAR OMEGA
lepuscar = None
for sys in systems:
    if sys['name'] == 'LEPUSCAR OMEGA':
        lepuscar = sys
        break

if not lepuscar:
    print("LEPUSCAR OMEGA not found!")
    sys.exit(1)

print(f"System data: {json.dumps(lepuscar, indent=2, default=str)}")
print("\n" + "="*60)
print("Calling prepare_single_system_solar:")
print("="*60 + "\n")

# Convert to dataframe row-like format
solar_data = prepare_single_system_solar(lepuscar)
print(f"Solar data returned: {json.dumps(solar_data, indent=2, default=str)}")
