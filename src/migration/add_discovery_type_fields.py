"""
Migration: Add Type-Specific Fields to Discoveries Table
Adds custom columns for each of the 10 discovery types
"""

import sqlite3
from pathlib import Path

def migrate_discovery_fields(db_path: Path = None):
    """Add type-specific fields to discoveries table"""
    if db_path is None:
        db_path = Path(__file__).parent.parent.parent / "data" / "VH-Database.db"

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Type-specific columns to add
    new_columns = [
        # 🦴 Ancient Bones & Fossils
        "species_type TEXT",
        "size_scale TEXT",
        "preservation_quality TEXT",
        "estimated_age TEXT",

        # 📜 Text Logs & Documents
        "language_status TEXT",
        "completeness TEXT",
        "author_origin TEXT",
        "key_excerpt TEXT",

        # 🏛️ Ruins & Structures
        "structure_type TEXT",
        "architectural_style TEXT",
        "structural_integrity TEXT",
        "purpose_function TEXT",

        # ⚙️ Alien Technology
        "tech_category TEXT",
        "operational_status TEXT",
        "power_source TEXT",
        "reverse_engineering TEXT",

        # 🦗 Flora & Fauna
        "species_name TEXT",
        "behavioral_notes TEXT",
        "habitat_biome TEXT",
        "threat_level TEXT",

        # 💎 Minerals & Resources
        "resource_type TEXT",
        "deposit_richness TEXT",
        "extraction_method TEXT",
        "economic_value TEXT",

        # 🚀 Crashed Ships & Wrecks
        "ship_class TEXT",
        "hull_condition TEXT",
        "salvageable_tech TEXT",
        "pilot_status TEXT",

        # ⚡ Environmental Hazards
        "hazard_type TEXT",
        "severity_level TEXT",
        "duration_frequency TEXT",
        "protection_required TEXT",

        # 🆕 NMS Update Content
        "update_name TEXT",
        "feature_category TEXT",
        "gameplay_impact TEXT",
        "first_impressions TEXT",

        # 📖 Player-Created Lore
        "story_type TEXT",
        "lore_connections TEXT",
        "creative_elements TEXT",
        "collaborative_work TEXT"
    ]

    print(f"Adding {len(new_columns)} type-specific columns to discoveries table...")

    for column_def in new_columns:
        try:
            cursor.execute(f"ALTER TABLE discoveries ADD COLUMN {column_def}")
            print(f"  [OK] Added column: {column_def.split()[0]}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"  [-] Column already exists: {column_def.split()[0]}")
            else:
                print(f"  [ERROR] Error adding {column_def.split()[0]}: {e}")

    conn.commit()
    conn.close()

    print("\n[DONE] Migration complete!")

if __name__ == "__main__":
    migrate_discovery_fields()
