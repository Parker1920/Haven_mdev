"""
Haven Local Sync API Server
Runs on your local computer to expose VH-Database.db to the Railway-hosted bot.

This creates an HTTP API that the Discord bot on Railway can access
to read system data and write discoveries to your local database.

Usage:
    python local_sync_api.py

Then use ngrok to expose it:
    ngrok http 5000
"""

import os
import json
import sqlite3
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('haven_sync_api')

app = Flask(__name__)
CORS(app)  # Allow Railway bot to access this API

# Database path
VH_DATABASE_PATH = os.path.join(
    os.path.dirname(__file__),
    "data",
    "VH-Database.db"
)

# API Key for security (set this in your Railway environment)
API_KEY = os.getenv('HAVEN_API_KEY', 'your-secret-key-here-change-me')


def verify_api_key():
    """Verify the API key from request headers."""
    provided_key = request.headers.get('X-API-Key')
    if provided_key != API_KEY:
        return False
    return True


def get_db_connection():
    """Get a connection to VH-Database.db"""
    if not os.path.exists(VH_DATABASE_PATH):
        raise FileNotFoundError(f"VH-Database not found at {VH_DATABASE_PATH}")

    conn = sqlite3.connect(VH_DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'database_accessible': os.path.exists(VH_DATABASE_PATH),
        'timestamp': datetime.now(datetime.UTC).isoformat()
    })


@app.route('/api/systems', methods=['GET'])
def get_systems():
    """Get all Haven star systems."""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Load all systems
        cursor.execute("SELECT * FROM systems")
        systems_rows = cursor.fetchall()

        systems = {}
        for system_row in systems_rows:
            system = dict(system_row)
            system_id = system['id']
            system_name = system['name']

            # Load planets for this system
            cursor.execute("SELECT * FROM planets WHERE system_id = ?", (system_id,))
            planets_rows = cursor.fetchall()

            planets = []
            for planet_row in planets_rows:
                planet = dict(planet_row)
                planet_id = planet['id']

                # Load moons for this planet
                cursor.execute("SELECT * FROM moons WHERE planet_id = ?", (planet_id,))
                moons_rows = cursor.fetchall()

                planet['moons'] = [dict(moon) for moon in moons_rows]
                planets.append(planet)

            system['planets'] = planets
            systems[system_name] = system

        conn.close()

        logger.info(f"Served {len(systems)} systems to client")
        return jsonify({'systems': systems})

    except Exception as e:
        logger.error(f"Error getting systems: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/systems/<system_name>', methods=['GET'])
def get_system(system_name):
    """Get a specific system by name."""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get system
        cursor.execute("SELECT * FROM systems WHERE name = ?", (system_name,))
        system_row = cursor.fetchone()

        if not system_row:
            return jsonify({'error': 'System not found'}), 404

        system = dict(system_row)
        system_id = system['id']

        # Load planets
        cursor.execute("SELECT * FROM planets WHERE system_id = ?", (system_id,))
        planets_rows = cursor.fetchall()

        planets = []
        for planet_row in planets_rows:
            planet = dict(planet_row)
            planet_id = planet['id']

            # Load moons
            cursor.execute("SELECT * FROM moons WHERE planet_id = ?", (planet_id,))
            moons_rows = cursor.fetchall()

            planet['moons'] = [dict(moon) for moon in moons_rows]
            planets.append(planet)

        system['planets'] = planets
        conn.close()

        return jsonify({'system': system})

    except Exception as e:
        logger.error(f"Error getting system {system_name}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/discoveries', methods=['POST'])
def create_discovery():
    """Write a discovery to VH-Database.db"""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        discovery_data = request.json

        conn = get_db_connection()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        # Resolve system_id from system_name
        system_name = discovery_data.get('system_name')
        system_id = None
        if system_name:
            cursor.execute("SELECT id FROM systems WHERE name = ?", (system_name,))
            result = cursor.fetchone()
            if result:
                system_id = result[0]

        # Resolve planet_id and moon_id from location
        planet_id = None
        moon_id = None
        location_type = discovery_data.get('location_type', 'space')
        location_name = discovery_data.get('location_name')

        if location_type == 'planet' and location_name and system_id:
            cursor.execute(
                "SELECT id FROM planets WHERE system_id = ? AND name = ?",
                (system_id, location_name)
            )
            result = cursor.fetchone()
            if result:
                planet_id = result[0]
                logger.info(f"Resolved planet_id={planet_id} for planet '{location_name}'")

        elif location_type == 'moon' and location_name and system_id:
            # Get both moon_id and parent planet_id
            cursor.execute("""
                SELECT m.id, m.planet_id
                FROM moons m
                JOIN planets p ON m.planet_id = p.id
                WHERE p.system_id = ? AND m.name = ?
            """, (system_id, location_name))
            result = cursor.fetchone()
            if result:
                moon_id = result[0]
                planet_id = result[1]
                logger.info(f"Resolved moon_id={moon_id}, planet_id={planet_id} for moon '{location_name}'")

        # Insert discovery
        cursor.execute("""
            INSERT INTO discoveries (
                discovery_type, discovery_name, system_id, planet_id, moon_id,
                location_type, location_name, description, coordinates, condition,
                time_period, significance, photo_url, evidence_urls,
                discovered_by, discord_user_id, discord_guild_id,
                pattern_matches, mystery_tier, analysis_status, tags, metadata,
                species_type, size_scale, preservation_quality, estimated_age,
                language_status, completeness, author_origin, key_excerpt,
                structure_type, architectural_style, structural_integrity, purpose_function,
                tech_category, operational_status, power_source, reverse_engineering,
                species_name, behavioral_notes, habitat_biome, threat_level,
                resource_type, deposit_richness, extraction_method, economic_value,
                ship_class, hull_condition, salvageable_tech, pilot_status,
                hazard_type, severity_level, duration_frequency, protection_required,
                update_name, feature_category, gameplay_impact, first_impressions,
                story_type, lore_connections, creative_elements, collaborative_work
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                      ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                      ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            discovery_data.get('type') or discovery_data.get('discovery_type'),
            discovery_data.get('discovery_name'),
            system_id,
            planet_id,
            moon_id,
            location_type,
            location_name,
            discovery_data.get('description'),
            discovery_data.get('coordinates'),
            discovery_data.get('condition'),
            discovery_data.get('time_period'),
            discovery_data.get('significance'),
            discovery_data.get('photo_url') or discovery_data.get('evidence_url'),
            discovery_data.get('evidence_urls'),
            discovery_data.get('username') or discovery_data.get('discovered_by'),
            discovery_data.get('user_id') or discovery_data.get('discord_user_id'),
            discovery_data.get('guild_id') or discovery_data.get('discord_guild_id'),
            discovery_data.get('pattern_matches', 0),
            discovery_data.get('mystery_tier', 0),
            discovery_data.get('analysis_status', 'pending'),
            discovery_data.get('tags'),
            discovery_data.get('metadata'),
            # Type-specific fields
            discovery_data.get('species_type'),
            discovery_data.get('size_scale'),
            discovery_data.get('preservation_quality'),
            discovery_data.get('estimated_age'),
            discovery_data.get('language_status'),
            discovery_data.get('completeness'),
            discovery_data.get('author_origin'),
            discovery_data.get('key_excerpt'),
            discovery_data.get('structure_type'),
            discovery_data.get('architectural_style'),
            discovery_data.get('structural_integrity'),
            discovery_data.get('purpose_function'),
            discovery_data.get('tech_category'),
            discovery_data.get('operational_status'),
            discovery_data.get('power_source'),
            discovery_data.get('reverse_engineering'),
            discovery_data.get('species_name'),
            discovery_data.get('behavioral_notes'),
            discovery_data.get('habitat_biome'),
            discovery_data.get('threat_level'),
            discovery_data.get('resource_type'),
            discovery_data.get('deposit_richness'),
            discovery_data.get('extraction_method'),
            discovery_data.get('economic_value'),
            discovery_data.get('ship_class'),
            discovery_data.get('hull_condition'),
            discovery_data.get('salvageable_tech'),
            discovery_data.get('pilot_status'),
            discovery_data.get('hazard_type'),
            discovery_data.get('severity_level'),
            discovery_data.get('duration_frequency'),
            discovery_data.get('protection_required'),
            discovery_data.get('update_name'),
            discovery_data.get('feature_category'),
            discovery_data.get('gameplay_impact'),
            discovery_data.get('first_impressions'),
            discovery_data.get('story_type'),
            discovery_data.get('lore_connections'),
            discovery_data.get('creative_elements'),
            discovery_data.get('collaborative_work')
        ))

        conn.commit()
        discovery_id = cursor.lastrowid
        conn.close()

        logger.info(f"✅ Discovery #{discovery_id} written to VH-Database from Railway bot")

        return jsonify({
            'success': True,
            'discovery_id': discovery_id,
            'system_id': system_id,
            'planet_id': planet_id,
            'moon_id': moon_id
        }), 201

    except Exception as e:
        logger.error(f"Error creating discovery: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/discoveries/<int:discovery_id>', methods=['GET'])
def get_discovery(discovery_id):
    """Get a specific discovery by ID."""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM discoveries WHERE id = ?", (discovery_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({'error': 'Discovery not found'}), 404

        discovery = dict(row)
        return jsonify({'discovery': discovery})

    except Exception as e:
        logger.error(f"Error getting discovery {discovery_id}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get database statistics."""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Count systems
        cursor.execute("SELECT COUNT(*) FROM systems")
        system_count = cursor.fetchone()[0]

        # Count planets
        cursor.execute("SELECT COUNT(*) FROM planets")
        planet_count = cursor.fetchone()[0]

        # Count moons
        cursor.execute("SELECT COUNT(*) FROM moons")
        moon_count = cursor.fetchone()[0]

        # Count discoveries
        cursor.execute("SELECT COUNT(*) FROM discoveries")
        discovery_count = cursor.fetchone()[0]

        conn.close()

        return jsonify({
            'systems': system_count,
            'planets': planet_count,
            'moons': moon_count,
            'discoveries': discovery_count,
            'database_path': VH_DATABASE_PATH,
            'database_size_mb': os.path.getsize(VH_DATABASE_PATH) / 1024 / 1024 if os.path.exists(VH_DATABASE_PATH) else 0
        })

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Haven Local Sync API Server")
    logger.info("=" * 60)
    logger.info(f"Database: {VH_DATABASE_PATH}")
    logger.info(f"Database exists: {os.path.exists(VH_DATABASE_PATH)}")
    logger.info(f"API Key: {API_KEY[:10]}... (use this in Railway environment)")
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Keep this server running on your computer")
    logger.info("2. Run: ngrok http 5000")
    logger.info("3. Copy the ngrok URL (e.g., https://abc123.ngrok.io)")
    logger.info("4. Set HAVEN_SYNC_API_URL in Railway to: <ngrok_url>/api")
    logger.info("5. Set HAVEN_API_KEY in Railway to match the key above")
    logger.info("=" * 60)
    logger.info("")

    # Run the server
    app.run(host='0.0.0.0', port=5000, debug=False)
