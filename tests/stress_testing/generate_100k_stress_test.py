#!/usr/bin/env python3
"""
Generate 100K+ stress test data for Haven Starmap - Large Dataset Optimization Test
Creates 100,000+ systems with moons to test the optimize_dataframe() function.

This test is designed to trigger the large dataset optimization that was added to
optimize_datasets.py. The map generator will use this to demonstrate memory efficiency
and performance improvements.

Usage:
    python generate_100k_stress_test.py              # Creates 100K systems, 5K to 10K moons
    python generate_100k_stress_test.py --small      # Creates 50K systems (faster)
    python generate_100k_stress_test.py --massive    # Creates 250K+ systems (very large)

Then generate map with:
    python src/Beta_VH_Map.py --data-file tests/stress_testing/STRESS-100K.json --no-open
"""
import json
import random
import sys
from pathlib import Path
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

# Number of systems to generate (100K for standard, configurable)
NUM_SYSTEMS_DEFAULT = 100_000
NUM_SYSTEMS_SMALL = 50_000
NUM_SYSTEMS_MASSIVE = 250_000

# Coordinate ranges
COORD_X_RANGE = (-1000, 1000)
COORD_Y_RANGE = (-1000, 1000)
COORD_Z_RANGE = (-250, 250)

# Regions for distribution
REGIONS = [
    "Stress Sector Alpha",
    "Stress Sector Beta",
    "Stress Sector Gamma",
    "Stress Sector Delta",
    "Stress Sector Epsilon",
    "Stress Sector Zeta",
    "Stress Sector Eta",
    "Stress Sector Theta",
]

# System name prefixes (Greek letters for variety)
PREFIXES = [
    "ALPHA", "BETA", "GAMMA", "DELTA", "EPSILON", "ZETA", "ETA", "THETA",
    "IOTA", "KAPPA", "LAMBDA", "MU", "NU", "XI", "OMICRON", "PI",
    "RHO", "SIGMA", "TAU", "UPSILON", "PHI", "CHI", "PSI", "OMEGA"
]

# Attributes for moons and planets
SENTINELS = ["None", "Low", "Moderate", "Aggressive", "Hostile", "Extreme"]
FAUNA_LEVELS = ["None", "Low", "Moderate", "Abundant", "Rich", "Extreme diversity"]
FLORA_LEVELS = ["None", "Sparse", "Moderate", "Dense", "Abundant", "Lush vegetation"]
MATERIALS_LIST = [
    "Iron, Carbon, Silicon",
    "Gold, Platinum, Silver",
    "Copper, Aluminum, Titanium",
    "Rare Earth Elements, Uranium",
    "Diamonds, Emeralds, Exotic crystals",
    "Hydrogen, Helium, Deuterium",
    "Activated Indium, Cadmium, Emeril"
]

# ============================================================================
# GENERATOR FUNCTIONS
# ============================================================================

def generate_moon(index: int, planet_name: str) -> dict:
    """Generate a single moon with attributes."""
    return {
        "name": f"{planet_name}-M{index}",
        "sentinel": random.choice(SENTINELS),
        "fauna": random.choice(FAUNA_LEVELS),
        "flora": random.choice(FLORA_LEVELS),
        "materials": random.choice(MATERIALS_LIST),
        "x": random.uniform(*COORD_X_RANGE),
        "y": random.uniform(*COORD_Y_RANGE),
        "z": random.uniform(*COORD_Z_RANGE),
    }


def generate_planet(index: int, system_name: str, num_moons: int = None) -> dict:
    """Generate a planet with moons."""
    if num_moons is None:
        num_moons = random.randint(0, 5)
    
    planet_name = f"{system_name}-P{index}"
    
    moons = [generate_moon(m + 1, planet_name) for m in range(num_moons)]
    
    return {
        "name": planet_name,
        "sentinel": random.choice(SENTINELS),
        "fauna": random.choice(FAUNA_LEVELS),
        "flora": random.choice(FLORA_LEVELS),
        "materials": random.choice(MATERIALS_LIST),
        "x": random.uniform(*COORD_X_RANGE),
        "y": random.uniform(*COORD_Y_RANGE),
        "z": random.uniform(*COORD_Z_RANGE),
        "moons": moons if moons else []
    }


def generate_system(index: int) -> dict:
    """Generate a complete star system."""
    prefix = random.choice(PREFIXES)
    system_name = f"STRESS-{prefix}-{index:06d}"
    region = random.choice(REGIONS)
    
    # Random number of planets (0-15, most have 3-8)
    num_planets = random.choices(
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15],
        weights=[1, 2, 3, 8, 10, 10, 8, 6, 5, 3, 2, 1]
    )[0]
    
    planets = [generate_planet(p + 1, system_name) for p in range(num_planets)]
    
    return {
        "name": system_name,
        "region": region,
        "x": random.uniform(*COORD_X_RANGE),
        "y": random.uniform(*COORD_Y_RANGE),
        "z": random.uniform(*COORD_Z_RANGE),
        "sentinel": random.choice(SENTINELS),
        "fauna": random.choice(FAUNA_LEVELS),
        "flora": random.choice(FLORA_LEVELS),
        "materials": random.choice(MATERIALS_LIST),
        "planets": planets,
        "attributes": f"Test system #{index}: {random.choice(['Exploration target', 'Resource rich', 'Scientific interest', 'Colony candidate', 'Hostile territory'])}"
    }


def generate_dataset(num_systems: int, output_path: Path) -> None:
    """Generate and save large stress test dataset."""
    print(f"🚀 Generating {num_systems:,} stress test systems...")
    print(f"   (This may take a minute or two for 100K+)")
    
    systems = {}
    
    # Progress indicator
    checkpoint = max(1000, num_systems // 20)  # Show progress every 5%
    
    for i in range(num_systems):
        if i % checkpoint == 0 and i > 0:
            pct = (i / num_systems) * 100
            print(f"   ... {i:,} systems ({pct:.1f}%) - {datetime.now().strftime('%H:%M:%S')}")
        
        system = generate_system(i)
        systems[system["name"]] = system
    
    # Wrap in container format
    data = {"systems": systems}
    
    # Save to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"\n✅ Generated {num_systems:,} systems")
    print(f"   File: {output_path.name}")
    print(f"   Size: {file_size_mb:.1f} MB")
    print(f"   Location: {output_path}")


def print_usage() -> None:
    """Print usage information."""
    print(__doc__)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Parse command line arguments
    num_systems = NUM_SYSTEMS_DEFAULT
    
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "--help" or arg == "-h":
            print_usage()
            sys.exit(0)
        elif arg == "--small":
            num_systems = NUM_SYSTEMS_SMALL
            print(f"📊 Small dataset mode: {num_systems:,} systems")
        elif arg == "--massive":
            num_systems = NUM_SYSTEMS_MASSIVE
            print(f"📊 Massive dataset mode: {num_systems:,} systems")
        else:
            try:
                num_systems = int(arg)
                print(f"📊 Custom dataset: {num_systems:,} systems")
            except ValueError:
                print(f"❌ Unknown argument: {arg}")
                print_usage()
                sys.exit(1)
    
    # Generate the dataset
    output_file = Path(__file__).parent / f"STRESS-{num_systems//1000}K.json"
    
    try:
        generate_dataset(num_systems, output_file)
        
        print(f"\n🧪 To test with map generation:")
        print(f"   python src/Beta_VH_Map.py --data-file {output_file.relative_to(Path.cwd())} --no-open")
        print(f"\nℹ️  This will trigger optimize_dataframe() for memory optimization!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
