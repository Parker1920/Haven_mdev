#!/usr/bin/env python3
"""
Generate comprehensive stress test data for Haven Starmap
Creates 500 systems with varied configurations for performance testing
"""
import json
import random
from datetime import datetime

# Configuration
NUM_SYSTEMS = 500
COORD_X_RANGE = (-100, 100)
COORD_Y_RANGE = (-100, 100)
COORD_Z_RANGE = (-25, 25)

# Regions for distribution
REGIONS = [
    "Test Alpha Sector",
    "Test Beta Sector",
    "Test Gamma Sector",
    "Test Delta Sector",
    "Test Epsilon Sector",
    "Test Zeta Sector"
]

# System name prefixes
PREFIXES = ["ALPHA", "BETA", "GAMMA", "DELTA", "EPSILON", "ZETA", "ETA", "THETA",
            "IOTA", "KAPPA", "LAMBDA", "MU", "NU", "XI", "OMICRON", "PI"]

# Planet/Moon attributes
SENTINELS = ["None", "Low", "Moderate", "Aggressive", "Hostile", "Extreme"]
FAUNA_LEVELS = ["None", "Low", "Moderate", "Abundant", "Rich", "Extreme diversity"]
FLORA_LEVELS = ["None", "Sparse", "Moderate", "Dense", "Abundant", "Lush vegetation"]
MATERIALS = [
    "Iron, Carbon, Silicon",
    "Gold, Platinum, Silver",
    "Copper, Aluminum, Titanium",
    "Rare Earth Elements, Uranium",
    "Diamonds, Emeralds, Exotic crystals",
    "Hydrogen, Helium, Deuterium",
    "Activated Indium, Cadmium, Emeril"
]

def generate_moon(index, planet_name):
    """Generate a single moon"""
    return {
        "name": f"{planet_name} Moon-{index}",
        "sentinel": random.choice(SENTINELS),
        "fauna": random.choice(FAUNA_LEVELS),
        "flora": random.choice(FLORA_LEVELS),
        "properties": random.choice([
            "Rocky, airless",
            "Ice world",
            "Volcanic activity",
            "Thin atmosphere",
            "Dense atmosphere",
            "Tidally locked"
        ]),
        "materials": random.choice(MATERIALS),
        "base_location": f"Coordinates: {random.uniform(-90, 90):.2f}, {random.uniform(-180, 180):.2f}",
        "photo": f"moon_{index}.jpg",
        "notes": f"Moon {index} orbiting {planet_name}"
    }

def generate_planet(index, system_name, num_moons):
    """Generate a single planet with moons"""
    planet_name = f"{system_name}-P{index}"

    moons = []
    for m in range(num_moons):
        moons.append(generate_moon(m + 1, planet_name))

    return {
        "name": planet_name,
        "sentinel": random.choice(SENTINELS),
        "fauna": random.choice(FAUNA_LEVELS),
        "flora": random.choice(FLORA_LEVELS),
        "properties": random.choice([
            "Terrestrial, breathable atmosphere",
            "Gas giant, massive storms",
            "Desert world, extreme temperatures",
            "Ocean world, deep seas",
            "Ice planet, frozen surface",
            "Volcanic world, active tectonics",
            "Barren, no atmosphere",
            "Earth-like, habitable conditions"
        ]),
        "materials": random.choice(MATERIALS),
        "base_location": f"Settlement-{index}: {random.uniform(-90, 90):.2f}, {random.uniform(-180, 180):.2f}",
        "photo": f"planet_{index}.jpg",
        "notes": f"Planet {index} in {system_name} system. {random.choice(['Colonization candidate', 'Resource rich', 'Scientific interest', 'Hostile environment', 'Exploration ongoing'])}",
        "moons": moons
    }

def generate_system(index):
    """Generate a complete star system"""
    prefix = random.choice(PREFIXES)
    system_name = f"STRESS-{prefix}-{index:03d}"
    region = random.choice(REGIONS)

    # Coordinates within specified ranges
    x = round(random.uniform(*COORD_X_RANGE), 2)
    y = round(random.uniform(*COORD_Y_RANGE), 2)
    z = round(random.uniform(*COORD_Z_RANGE), 2)

    # Determine system complexity
    # 90% of systems have 20+ planets (stress test)
    # 10% have normal amount (3-5 planets)
    if random.random() < 0.9:
        # Stress test: many planets
        num_planets = random.randint(20, 30)
    else:
        # Normal system
        num_planets = random.randint(3, 5)

    # Generate planets
    planets = []
    planet_names = []

    for p in range(num_planets):
        # Determine moons: most have 0-5, some have 10+
        if random.random() < 0.85:
            num_moons = random.randint(0, 5)
        else:
            num_moons = random.randint(10, 15)

        planet = generate_planet(p + 1, system_name, num_moons)
        planets.append(planet)
        planet_names.append(planet["name"])

    return {
        "id": f"SYS_STRESS_{index:04d}",
        "name": system_name,
        "x": x,
        "y": y,
        "z": z,
        "region": region,
        "fauna": random.choice(FAUNA_LEVELS),
        "flora": random.choice(FLORA_LEVELS),
        "sentinel": random.choice(SENTINELS),
        "materials": random.choice(MATERIALS),
        "base_location": f"Station coordinates: {random.uniform(-90, 90):.2f}, {random.uniform(-180, 180):.2f}",
        "planets": planets,
        "planets_names": planet_names
    }

def main():
    print(f"Generating {NUM_SYSTEMS} test systems...")
    print(f"Coordinate bounds: X({COORD_X_RANGE}), Y({COORD_Y_RANGE}), Z({COORD_Z_RANGE})")
    print()

    # Generate all systems
    data = {
        "_meta": {
            "version": "1.0.0",
            "last_modified": datetime.now().isoformat() + "Z",
            "purpose": "Comprehensive stress testing dataset for Haven Starmap system",
            "stats": {
                "total_systems": NUM_SYSTEMS,
                "coordinate_bounds": {
                    "x": COORD_X_RANGE,
                    "y": COORD_Y_RANGE,
                    "z": COORD_Z_RANGE
                }
            }
        }
    }

    total_planets = 0
    total_moons = 0

    for i in range(NUM_SYSTEMS):
        system = generate_system(i + 1)
        data[system["name"]] = system

        # Track stats
        total_planets += len(system["planets"])
        for planet in system["planets"]:
            total_moons += len(planet.get("moons", []))

        if (i + 1) % 100 == 0:
            print(f"Generated {i + 1}/{NUM_SYSTEMS} systems...")

    print()
    print(f"✓ Generation complete!")
    print(f"  Total systems: {NUM_SYSTEMS}")
    print(f"  Total planets: {total_planets}")
    print(f"  Total moons: {total_moons}")
    print(f"  Total objects: {NUM_SYSTEMS + total_planets + total_moons}")
    print()

    # Write to file
    output_file = "TESTING.json"
    print(f"Writing to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    file_size_mb = len(json.dumps(data)) / (1024 * 1024)
    print(f"✓ File written: {file_size_mb:.2f} MB")
    print()
    print("Stress test data generation complete!")

if __name__ == "__main__":
    main()
