"""
Sync discoveries from VH-Database.db (master) to keeper.db
This ensures the bot's internal database has all discoveries.
"""

import sqlite3
import os
import sys
import json

# Ensure UTF-8 output
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Database paths
HAVEN_DB_PATH = r'C:\Users\parke\OneDrive\Desktop\Haven_mdev\data\VH-Database.db'
KEEPER_DB_PATH = r'C:\Users\parke\OneDrive\Desktop\Haven_mdev\docs\guides\Haven-lore\keeper-bot\src\data\keeper.db'

def get_location_name(haven_cursor, location_type, location_id):
    """Get location name from Haven database."""
    if not location_id:
        return "Unknown"

    if location_type == 'planet':
        haven_cursor.execute("SELECT name FROM planets WHERE id = ?", (location_id,))
    elif location_type == 'moon':
        haven_cursor.execute("SELECT name FROM moons WHERE id = ?", (location_id,))
    elif location_type == 'system':
        haven_cursor.execute("SELECT name FROM systems WHERE id = ?", (location_id,))
    else:
        return "Unknown"

    result = haven_cursor.fetchone()
    return result[0] if result else "Unknown"

def sync_discoveries():
    """Sync all discoveries from Haven DB to Keeper DB."""

    print("🔄 Starting discovery sync from VH-Database.db to keeper.db...")

    # Connect to both databases
    haven_conn = sqlite3.connect(HAVEN_DB_PATH)
    haven_conn.row_factory = sqlite3.Row
    keeper_conn = sqlite3.connect(KEEPER_DB_PATH)

    haven_cursor = haven_conn.cursor()
    keeper_cursor = keeper_conn.cursor()

    # Get all discoveries from Haven DB
    haven_cursor.execute("""
        SELECT * FROM discoveries ORDER BY id
    """)

    haven_discoveries = haven_cursor.fetchall()
    print(f"📊 Found {len(haven_discoveries)} discoveries in VH-Database.db")

    # Check existing discoveries in keeper.db
    keeper_cursor.execute("SELECT COUNT(*) FROM discoveries")
    keeper_count_before = keeper_cursor.fetchone()[0]
    print(f"📊 Currently {keeper_count_before} discoveries in keeper.db")

    synced = 0
    skipped = 0
    errors = 0

    for disc in haven_discoveries:
        try:
            # Check if this discovery already exists in keeper.db
            # Match by guild_id, user_id, and timestamp
            keeper_cursor.execute("""
                SELECT id FROM discoveries
                WHERE guild_id = ? AND user_id = ? AND submission_timestamp = ?
            """, (disc['discord_guild_id'], disc['discord_user_id'], disc['submission_timestamp']))

            existing = keeper_cursor.fetchone()

            if existing:
                skipped += 1
                continue

            # Get location name
            location_name = get_location_name(haven_cursor, disc['location_type'], disc['planet_id'] or disc['moon_id'])

            # Get system name
            system_name = "Unknown"
            if disc['system_id']:
                haven_cursor.execute("SELECT name FROM systems WHERE id = ?", (disc['system_id'],))
                sys_result = haven_cursor.fetchone()
                system_name = sys_result[0] if sys_result else "Unknown"

            # Build metadata JSON from type-specific fields
            metadata = {}
            type_fields_map = {
                '🦴': ['species_type', 'size_scale', 'preservation_quality', 'estimated_age'],
                '🏛️': ['structure_type', 'architectural_style', 'structural_integrity', 'purpose_function'],
                '⚙️': ['tech_category', 'operational_status', 'power_source', 'reverse_engineering'],
                '🦗': ['species_name', 'behavioral_notes', 'habitat_biome', 'threat_level'],
                '💎': ['resource_type', 'deposit_richness', 'extraction_method', 'economic_value'],
                '🚀': ['ship_class', 'hull_condition', 'salvageable_tech', 'pilot_status'],
                '⚡': ['hazard_type', 'severity_level', 'duration_frequency', 'protection_required'],
                '🆕': ['update_name', 'feature_category', 'gameplay_impact', 'first_impressions'],
                '📜': ['key_excerpt', 'language_status', 'completeness', 'author_origin'],
                '📖': ['story_type', 'lore_connections', 'creative_elements', 'collaborative_work']
            }

            # Add type-specific fields to metadata
            if disc['discovery_type'] in type_fields_map:
                for field in type_fields_map[disc['discovery_type']]:
                    if disc[field]:
                        metadata[field] = disc[field]

            # Insert discovery into keeper.db
            keeper_cursor.execute("""
                INSERT INTO discoveries (
                    user_id, username, guild_id, discovery_type,
                    location, system_name, time_period, condition,
                    description, significance, evidence_url, coordinates,
                    planet_name, galaxy_name, submission_timestamp,
                    analysis_status, pattern_matches, mystery_tier, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                disc['discord_user_id'],
                disc['discovered_by'],
                disc['discord_guild_id'],
                disc['discovery_type'],
                location_name,  # location
                system_name,
                disc['time_period'] or 'Unknown',
                disc['condition'] or 'Unknown',
                disc['description'] or '',
                disc['significance'] or '',
                disc['photo_url'] or '',
                disc['coordinates'] or '',
                location_name,  # planet_name (same as location)
                'Euclid',  # galaxy_name (default)
                disc['submission_timestamp'],
                disc['analysis_status'] or 'pending',
                disc['pattern_matches'] or '',
                disc['mystery_tier'] or 1,
                json.dumps(metadata) if metadata else '{}'
            ))

            synced += 1
            print(f"✅ Synced: {disc['discovery_type']} {disc['discovery_name']} at {location_name}")

        except Exception as e:
            errors += 1
            print(f"❌ Error syncing discovery {disc['id']}: {e}")
            continue

    # Commit changes
    keeper_conn.commit()

    # Check final count
    keeper_cursor.execute("SELECT COUNT(*) FROM discoveries")
    keeper_count_after = keeper_cursor.fetchone()[0]

    print(f"\n📊 Sync Complete!")
    print(f"   Before: {keeper_count_before} discoveries")
    print(f"   After:  {keeper_count_after} discoveries")
    print(f"   Synced: {synced} new discoveries")
    print(f"   Skipped: {skipped} existing discoveries")
    print(f"   Errors: {errors}")

    # Close connections
    haven_conn.close()
    keeper_conn.close()

    print("\n✅ keeper.db is now synced with VH-Database.db master!")
    return synced > 0

if __name__ == "__main__":
    try:
        sync_discoveries()
    except Exception as e:
        print(f"\n❌ Error during sync: {e}")
        import traceback
        traceback.print_exc()
