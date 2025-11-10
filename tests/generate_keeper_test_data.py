#!/usr/bin/env python3
"""
Generate Test Data for The Keeper Discord Bot
Creates 10 richly detailed star systems for testing discovery integration.

All systems placed in 20x20x5 area around 0,0,0 with full lore attributes.
"""

import json
import random
from datetime import datetime
from pathlib import Path
import uuid

# Configuration
OUTPUT_FILE = Path("data/keeper_test_data.json")
NUM_SYSTEMS = 10
COORDINATE_RANGE = {
    'x': (-10, 10),
    'y': (-10, 10),
    'z': (-2.5, 2.5)
}

# Lore-rich content pools
REGIONS = [
    "Euclid Core",
    "Hilbert Dimension", 
    "Calypso Expanse",
    "Eissentam Paradise",
    "Budullangr Void"
]

SYSTEM_PREFIXES = [
    "KEEPER", "ARCHIVE", "VESTIGE", "PHANTOM", "REMNANT",
    "ECHO", "CIPHER", "ORACLE", "NEXUS", "VAULT"
]

SYSTEM_SUFFIXES = [
    "PRIME", "SECUNDUS", "TERTIUS", "ALPHA", "BETA",
    "GAMMA", "EPSILON", "ZETA", "OMEGA", "NOVA"
]

SENTINEL_LEVELS = ["None", "Low", "Medium", "High", "Aggressive"]

FAUNA_LEVELS = [
    "None",
    "Low - Sparse wildlife",
    "Medium - Moderate populations", 
    "High - Abundant creatures",
    "Rich - Teeming with life"
]

FLORA_LEVELS = [
    "None",
    "Low - Barren landscapes",
    "Medium - Scattered vegetation",
    "High - Dense forests",
    "Lush - Paradise world flora"
]

MATERIALS_COMMON = [
    "Carbon", "Oxygen", "Ferrite Dust", "Di-Hydrogen", 
    "Sodium", "Condensed Carbon", "Pure Ferrite"
]

MATERIALS_UNCOMMON = [
    "Magnetised Ferrite", "Ionised Cobalt", "Silver",
    "Gold", "Platinum", "Chromatic Metal", "Copper"
]

MATERIALS_RARE = [
    "Activated Indium", "Activated Emeril", "Activated Cadmium",
    "Storm Crystals", "Gravitino Balls", "Salvaged Data",
    "Ancient Bones", "Vortex Cubes"
]

PLANET_TYPES = [
    "Lush Paradise",
    "Toxic Wasteland", 
    "Scorched Desert",
    "Frozen Tundra",
    "Radioactive Hellscape",
    "Dead Barren",
    "Exotic Anomaly",
    "Ocean World",
    "Volcanic Inferno",
    "Temperate Earth-like"
]

DISCOVERY_ATTRIBUTES = [
    "Ancient ruins detected on surface",
    "Unusual signal patterns detected",
    "High concentration of predator species",
    "Atmospheric anomalies present",
    "Remnant structures visible from orbit",
    "Frequent electrical storms",
    "Unusual gravitational readings",
    "Dense flora covers 80% of surface",
    "Multiple abandoned settlements",
    "Rare crystalline formations",
    "Deep underground cave systems",
    "Aggressive sentinel presence",
    "Korvax archaeological site",
    "Gek trading outpost established",
    "Vy'keen military remnants",
    "Atlas interface coordinates nearby"
]

BASE_LOCATIONS = [
    "Central Trading Hub",
    "Mining Outpost Delta",
    "Research Station Alpha",
    "Hidden Valley Base",
    "Mountain Peak Observatory",
    "Coastal Settlement",
    "Underground Bunker",
    "Floating Platform Station",
    "Ancient Temple Complex",
    "Abandoned Sentinel Depot",
    None  # Some systems have no base
]


def generate_material_list(include_rare=False):
    """Generate a random material list."""
    materials = []
    
    # Always include 2-3 common materials
    materials.extend(random.sample(MATERIALS_COMMON, random.randint(2, 3)))
    
    # Add 1-2 uncommon materials
    materials.extend(random.sample(MATERIALS_UNCOMMON, random.randint(1, 2)))
    
    # Optionally add rare materials
    if include_rare or random.random() > 0.7:
        materials.extend(random.sample(MATERIALS_RARE, random.randint(1, 2)))
    
    return ", ".join(materials)


def generate_moon(planet_name, moon_number):
    """Generate a moon with full attributes."""
    moon = {
        "name": f"{planet_name}-M{moon_number}",
        "sentinel": random.choice(SENTINEL_LEVELS),
        "fauna": random.choice(FAUNA_LEVELS),
        "flora": random.choice(FLORA_LEVELS),
        "properties": f"Moon {moon_number} - {random.choice(['Rocky', 'Icy', 'Barren', 'Volcanic', 'Cratered'])}",
        "materials": generate_material_list(include_rare=False)
    }
    
    # Some moons have discovery notes
    if random.random() > 0.6:
        moon["notes"] = random.choice([
            "Ancient fossil deposits detected",
            "Unusual text logs recovered from surface",
            "Mysterious ruins visible from orbit",
            "Abandoned technology discovered",
            "Strange biological readings",
            "High sentinel activity in northern hemisphere"
        ])
    
    return moon


def generate_planet(system_name, planet_number):
    """Generate a planet with full attributes and optional moons."""
    planet_type = random.choice(PLANET_TYPES)
    
    planet = {
        "name": f"{system_name}-{chr(65 + planet_number)}",  # A, B, C, etc.
        "sentinel": random.choice(SENTINEL_LEVELS),
        "fauna": random.choice(FAUNA_LEVELS),
        "flora": random.choice(FLORA_LEVELS),
        "properties": planet_type,
        "materials": generate_material_list(include_rare=random.random() > 0.5),
    }
    
    # Some planets have base locations
    if random.random() > 0.4:
        base = random.choice([b for b in BASE_LOCATIONS if b is not None])
        planet["base_location"] = base
    
    # Add discovery notes for lore
    if random.random() > 0.5:
        planet["notes"] = random.choice([
            "Multiple ancient bone deposits - potential pattern connection",
            "Text logs reference 'The First Spawn' - investigation needed",
            "Ruins contain Korvax historical data fragments",
            "Crashed freighter with encrypted logs",
            "Strange flora exhibits unusual growth patterns",
            "Predator species shows signs of genetic manipulation",
            "Boundary failure event detected 3 cycles ago",
            "Atlas interface coordinates embedded in local monument"
        ])
    
    # Add moons (0-3 per planet)
    num_moons = random.choices([0, 1, 2, 3], weights=[0.3, 0.4, 0.2, 0.1])[0]
    if num_moons > 0:
        planet["moons"] = [
            generate_moon(planet["name"], i + 1) 
            for i in range(num_moons)
        ]
    
    return planet


def generate_system(system_number):
    """Generate a complete star system with all attributes."""
    # Generate system name
    prefix = random.choice(SYSTEM_PREFIXES)
    suffix = random.choice(SYSTEM_SUFFIXES)
    system_name = f"{prefix} {suffix}"
    
    # Generate system ID
    system_id = f"SYS_KEEPER_TEST_{system_number:03d}"
    
    # Generate coordinates in specified range
    x = round(random.uniform(*COORDINATE_RANGE['x']), 2)
    y = round(random.uniform(*COORDINATE_RANGE['y']), 2)
    z = round(random.uniform(*COORDINATE_RANGE['z']), 2)
    
    # Select region
    region = random.choice(REGIONS)
    
    # Generate system-level attributes
    system = {
        "id": system_id,
        "name": system_name,
        "x": x,
        "y": y,
        "z": z,
        "region": region,
        "fauna": random.choice(FAUNA_LEVELS),
        "flora": random.choice(FLORA_LEVELS),
        "sentinel": random.choice(SENTINEL_LEVELS),
        "materials": generate_material_list(include_rare=True),
        "base_location": random.choice(BASE_LOCATIONS),
        "photo": None,  # Can be added later
        "attributes": ", ".join(random.sample(DISCOVERY_ATTRIBUTES, random.randint(2, 4))),
        "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "modified_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    # Generate planets (3-6 per system)
    num_planets = random.randint(3, 6)
    system["planets"] = [
        generate_planet(system_name, i) 
        for i in range(num_planets)
    ]
    
    return system_name, system


def generate_keeper_test_data():
    """Generate complete test dataset for The Keeper bot."""
    print("=" * 70)
    print("GENERATING KEEPER TEST DATA")
    print("=" * 70)
    print()
    print(f"Target: {NUM_SYSTEMS} star systems")
    print(f"Coordinate Range: X{COORDINATE_RANGE['x']}, Y{COORDINATE_RANGE['y']}, Z{COORDINATE_RANGE['z']}")
    print(f"Output: {OUTPUT_FILE}")
    print()
    
    # Create data structure
    data = {
        "_meta": {
            "version": "1.0.0",
            "description": "Test data for The Keeper Discord bot - richly detailed systems for discovery testing",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "last_modified": datetime.utcnow().isoformat() + "Z",
            "system_count": NUM_SYSTEMS,
            "purpose": "Discord bot testing with full lore integration",
            "coordinate_range": "20x20x5 area centered on origin (0,0,0)"
        }
    }
    
    # Generate systems
    total_planets = 0
    total_moons = 0
    
    print("Generating systems...")
    for i in range(NUM_SYSTEMS):
        system_name, system_data = generate_system(i + 1)
        data[system_name] = system_data
        
        # Count statistics
        num_planets = len(system_data["planets"])
        num_moons = sum(len(p.get("moons", [])) for p in system_data["planets"])
        total_planets += num_planets
        total_moons += num_moons
        
        print(f"  ✓ {system_name}")
        print(f"    - Coordinates: ({system_data['x']}, {system_data['y']}, {system_data['z']})")
        print(f"    - Region: {system_data['region']}")
        print(f"    - Planets: {num_planets} ({num_moons} moons)")
        print()
    
    # Save to file
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)
    print()
    print(f"✅ File created: {OUTPUT_FILE}")
    print(f"✅ Systems: {NUM_SYSTEMS}")
    print(f"✅ Total Planets: {total_planets}")
    print(f"✅ Total Moons: {total_moons}")
    print(f"✅ Total Celestial Bodies: {NUM_SYSTEMS + total_planets + total_moons}")
    print()
    print("📊 Statistics:")
    print(f"   - Average planets per system: {total_planets / NUM_SYSTEMS:.1f}")
    print(f"   - Average moons per planet: {total_moons / total_planets:.1f}")
    print()
    print("🎯 Ready for Keeper Bot Testing:")
    print("   - All systems have full lore attributes")
    print("   - Multiple discovery types available per system")
    print("   - Pattern recognition data included")
    print("   - Regional grouping enabled")
    print()
    print("Next Steps:")
    print(f"   1. Review generated data: {OUTPUT_FILE}")
    print("   2. Copy to Haven_mdev data folder if desired")
    print("   3. Update Keeper bot's HAVEN_DATA_PATH to point to this file")
    print("   4. Test discovery submission with /discovery-report command")
    print()


if __name__ == "__main__":
    generate_keeper_test_data()
