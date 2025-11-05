#!/usr/bin/env python3
"""Quick script to check if planets exist in database."""

from src.common.database import HavenDatabase

with HavenDatabase('data/haven.db') as db:
    systems = db.get_all_systems(include_planets=True)

print(f"\nTotal systems in database: {len(systems)}\n")
print("Systems with planets:")
print("=" * 60)

for system in systems:
    planet_count = len(system.get('planets', []))
    print(f"  {system['name']:<25} - {planet_count} planets")
    
    if planet_count > 0:
        for planet in system['planets']:
            moon_count = len(planet.get('moons', []))
            print(f"    └─ {planet['name']:<20} - {moon_count} moons")

print("\n" + "=" * 60)

# Count totals
total_planets = sum(len(s.get('planets', [])) for s in systems)
total_moons = sum(
    len(m) for s in systems 
    for p in s.get('planets', []) 
    for m in [p.get('moons', [])]
)

print(f"\nTotals: {total_planets} planets, {total_moons} moons")
