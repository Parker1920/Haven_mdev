#!/usr/bin/env python3
import json
data = json.load(open('data/data.json'))
system = data.get('LEPUSCAR OMEGA')
print(f"LEPUSCAR OMEGA planets: {json.dumps(system.get('planets', []), indent=2)}")
