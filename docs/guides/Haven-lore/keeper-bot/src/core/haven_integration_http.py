"""
Haven Integration System - HTTP API Mode
Integrates The Keeper with Haven_mdev via HTTP API (for Railway deployment).
Falls back to direct database/JSON access when running locally.
"""

import json
import os
import logging
import sqlite3
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger('keeper.haven_integration')

class HavenIntegrationHTTP:
    """Handles integration with Haven_mdev via HTTP API or direct database access."""

    def __init__(self, haven_data_path: str = None):
        """Initialize Haven integration."""
        # Check if we should use HTTP API mode (for Railway deployment)
        self.api_url = os.getenv('HAVEN_SYNC_API_URL')  # e.g., https://abc123.ngrok.io/api
        self.api_key = os.getenv('HAVEN_API_KEY')

        # Determine mode
        if self.api_url and self.api_key:
            self.mode = 'http'
            logger.info(f"Haven integration mode: HTTP API ({self.api_url})")
        else:
            self.mode = 'direct'
            logger.info("Haven integration mode: Direct database/JSON access")

        # Direct database mode settings
        self.use_database = os.getenv('USE_HAVEN_DATABASE', 'true').lower() == 'true'

        if self.mode == 'direct':
            if self.use_database:
                self.db_path = self._find_haven_database()
                self.haven_data_path = None
            else:
                self.db_path = None
                self.haven_data_path = haven_data_path or self._find_haven_data()
        else:
            self.db_path = None
            self.haven_data_path = None

        self.haven_data = {}
        self.last_loaded = None
        self._db_connection = None
        self._http_session = None

    async def _get_http_session(self):
        """Get or create aiohttp session."""
        if self._http_session is None or self._http_session.closed:
            self._http_session = aiohttp.ClientSession(
                headers={'X-API-Key': self.api_key}
            )
        return self._http_session

    async def close(self):
        """Close HTTP session if open."""
        if self._http_session and not self._http_session.closed:
            await self._http_session.close()

    def _find_haven_data(self) -> Optional[str]:
        """Attempt to find Haven data.json file."""
        env_path = os.getenv('HAVEN_DATA_PATH')
        if env_path and os.path.exists(env_path):
            logger.info(f"Found Haven data from HAVEN_DATA_PATH: {env_path}")
            return env_path

        possible_paths = [
            os.path.join(os.path.expanduser("~"), "Desktop", "Haven_mdev", "data", "keeper_test_data.json"),
            os.path.join(os.path.expanduser("~"), "Desktop", "Haven_mdev", "data", "data.json"),
            os.path.join(os.path.expanduser("~"), "Desktop", "untitled folder", "Haven_mdev", "data", "data.json"),
            "../../../untitled folder/Haven_mdev/data/data.json",
            "../../Haven_mdev/data/data.json",
            "../Haven_mdev/data/data.json",
            "/Users/parkerstouffer/Desktop/untitled folder/Haven_mdev/data/data.json",
            os.path.expanduser("~/Desktop/untitled folder/Haven_mdev/data/data.json")
        ]

        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found Haven data at: {path}")
                return path

        logger.warning("Haven data.json not found in expected locations")
        return None

    def _find_haven_database(self) -> Optional[str]:
        """Attempt to find Haven VH-Database.db file."""
        env_path = os.getenv('HAVEN_DB_PATH')
        if env_path and os.path.exists(env_path):
            logger.info(f"Found Haven database from HAVEN_DB_PATH: {env_path}")
            return env_path

        possible_paths = [
            os.path.join(os.path.expanduser("~"), "Desktop", "Haven_mdev", "data", "VH-Database.db"),
            os.path.join(os.path.expanduser("~"), "Desktop", "untitled folder", "Haven_mdev", "data", "VH-Database.db"),
            "../../../Haven_mdev/data/VH-Database.db",
            "../../Haven_mdev/data/VH-Database.db",
            "../Haven_mdev/data/VH-Database.db",
            "/Users/parkerstouffer/Desktop/Haven_mdev/data/VH-Database.db",
            os.path.expanduser("~/Desktop/Haven_mdev/data/VH-Database.db")
        ]

        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found Haven database at: {path}")
                return path

        logger.warning("Haven VH-Database.db not found in expected locations")
        self.use_database = False
        return None

    async def load_haven_data(self) -> bool:
        """Load Haven star system data from HTTP API, database, or JSON."""
        if self.mode == 'http':
            return await self._load_from_http()
        elif self.use_database and self.db_path:
            return await self._load_from_database()
        elif self.haven_data_path and os.path.exists(self.haven_data_path):
            return await self._load_from_json()
        else:
            logger.warning("No Haven data source available")
            return False

    async def _load_from_http(self) -> bool:
        """Load Haven data from HTTP API."""
        try:
            session = await self._get_http_session()

            async with session.get(f"{self.api_url}/systems") as resp:
                if resp.status != 200:
                    logger.error(f"HTTP API returned status {resp.status}")
                    return False

                data = await resp.json()
                self.haven_data = data.get('systems', {})
                self.last_loaded = datetime.utcnow()

                logger.info(f"Loaded {len(self.haven_data)} Haven systems from HTTP API")
                return True

        except Exception as e:
            logger.error(f"Failed to load Haven data from HTTP API: {e}")
            return False

    async def _load_from_database(self) -> bool:
        """Load Haven data from SQLite database."""
        if not self.db_path or not os.path.exists(self.db_path):
            return False

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM systems")
            systems = cursor.fetchall()

            self.haven_data = {}
            for system_row in systems:
                system = dict(system_row)
                system_id = system['id']
                system_name = system['name']

                cursor.execute("SELECT * FROM planets WHERE system_id = ?", (system_id,))
                planets_rows = cursor.fetchall()

                planets = []
                for planet_row in planets_rows:
                    planet = dict(planet_row)
                    planet_id = planet['id']

                    cursor.execute("SELECT * FROM moons WHERE planet_id = ?", (planet_id,))
                    moons_rows = cursor.fetchall()

                    planet['moons'] = [dict(moon) for moon in moons_rows]
                    planets.append(planet)

                system['planets'] = planets
                self.haven_data[system_name] = system

            conn.close()
            self.last_loaded = datetime.utcnow()
            logger.info(f"Loaded {len(self.haven_data)} Haven systems from database")
            return True

        except Exception as e:
            logger.error(f"Failed to load Haven database: {e}")
            return False

    async def _load_from_json(self) -> bool:
        """Load Haven data from JSON file."""
        if not self.haven_data_path or not os.path.exists(self.haven_data_path):
            return False

        try:
            with open(self.haven_data_path, 'r', encoding='utf-8') as f:
                self.haven_data = json.load(f)

            self.last_loaded = datetime.utcnow()
            logger.info(f"Loaded {len(self.haven_data)} Haven systems from JSON")
            return True

        except Exception as e:
            logger.error(f"Failed to load Haven JSON data: {e}")
            return False

    def get_all_systems(self) -> Dict[str, Dict]:
        """Get all Haven star systems."""
        return {k: v for k, v in self.haven_data.items() if not k.startswith('_')}

    def get_system(self, system_name: str) -> Optional[Dict]:
        """Get a specific Haven system."""
        return self.haven_data.get(system_name)

    def get_systems_by_region(self, region: str) -> Dict[str, Dict]:
        """Get all systems in a specific region."""
        systems = self.get_all_systems()
        return {
            name: data for name, data in systems.items()
            if data.get('region', '').lower() == region.lower()
        }

    def find_systems_near(self, x: float, y: float, z: float, radius: float = 5.0) -> List[Tuple[str, Dict, float]]:
        """Find systems near given coordinates."""
        systems = self.get_all_systems()
        nearby = []

        for name, data in systems.items():
            if all(coord in data for coord in ['x', 'y', 'z']):
                distance = (
                    (data['x'] - x) ** 2 +
                    (data['y'] - y) ** 2 +
                    (data['z'] - z) ** 2
                ) ** 0.5

                if distance <= radius:
                    nearby.append((name, data, distance))

        return sorted(nearby, key=lambda x: x[2])

    def get_planets_in_system(self, system_name: str) -> List[Dict]:
        """Get all planets (and moons) in a system."""
        system = self.get_system(system_name)
        if not system:
            return []

        planets = []
        system_planets = system.get('planets', [])
        for planet in system_planets:
            planets.append({**planet, 'type': 'planet', 'system': system_name})

            moons = planet.get('moons', [])
            for moon in moons:
                planets.append({**moon, 'type': 'moon', 'system': system_name, 'parent_planet': planet.get('name')})

        return planets

    def get_space_anomaly_locations(self, system_name: str) -> List[Dict]:
        """Get potential space anomaly locations in a system."""
        system = self.get_system(system_name)
        if not system:
            return []

        anomalies = []

        if 'space_station' in system:
            station = system['space_station']
            anomalies.append({
                'name': station.get('name', 'Space Station'),
                'type': 'space_station',
                'coordinates': f"{station.get('x', 0)}, {station.get('y', 0)}, {station.get('z', 0)}",
                'system': system_name
            })

        anomalies.extend([
            {'name': 'Deep Space (Asteroid Field)', 'type': 'asteroid_field', 'system': system_name},
            {'name': 'Deep Space (Between Planets)', 'type': 'deep_space', 'system': system_name},
            {'name': 'Solar Vicinity', 'type': 'solar_vicinity', 'system': system_name},
            {'name': 'System Edge (Outer Orbit)', 'type': 'system_edge', 'system': system_name}
        ])

        return anomalies

    def create_discovery_location_choices(self, system_name: str) -> List[Dict]:
        """Create a list of location choices for discovery reports."""
        choices = []

        planets = self.get_planets_in_system(system_name)
        for planet in planets:
            if planet['type'] == 'planet':
                choices.append({
                    'label': f"🪐 {planet['name']} (Planet)",
                    'value': f"planet:{planet['name']}",
                    'description': f"Surface discoveries on {planet['name']}"
                })
            else:
                choices.append({
                    'label': f"🌙 {planet['name']} (Moon of {planet.get('parent_planet', 'Unknown')})",
                    'value': f"moon:{planet['name']}",
                    'description': f"Surface discoveries on {planet['name']}"
                })

        anomalies = self.get_space_anomaly_locations(system_name)
        for anomaly in anomalies:
            choices.append({
                'label': f"🌌 {anomaly['name']}",
                'value': f"space:{anomaly['type']}:{anomaly['name']}",
                'description': f"Space discoveries in {anomaly['name']}"
            })

        return choices

    async def write_discovery_to_database(self, discovery_data: Dict) -> Optional[int]:
        """
        Write a discovery to VH-Database.db (via HTTP API or direct access).

        Returns: Discovery ID if successful, None otherwise
        """
        if self.mode == 'http':
            return await self._write_discovery_via_http(discovery_data)
        elif self.use_database and self.db_path:
            return self._write_discovery_directly(discovery_data)
        else:
            logger.warning("Cannot write to database - no write method available")
            return None

    async def _write_discovery_via_http(self, discovery_data: Dict) -> Optional[int]:
        """Write discovery via HTTP API."""
        try:
            session = await self._get_http_session()

            async with session.post(
                f"{self.api_url}/discoveries",
                json=discovery_data
            ) as resp:
                if resp.status != 201:
                    error_text = await resp.text()
                    logger.error(f"HTTP API write failed ({resp.status}): {error_text}")
                    return None

                data = await resp.json()
                discovery_id = data.get('discovery_id')

                logger.info(f"✅ Discovery #{discovery_id} written via HTTP API")
                return discovery_id

        except Exception as e:
            logger.error(f"Failed to write discovery via HTTP API: {e}")
            return None

    def _write_discovery_directly(self, discovery_data: Dict) -> Optional[int]:
        """Write discovery directly to local database."""
        if not self.use_database or not self.db_path:
            logger.warning("Cannot write to database - not in database mode")
            return None

        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()

            # Resolve system_id
            system_name = discovery_data.get('system_name')
            system_id = None
            if system_name:
                cursor.execute("SELECT id FROM systems WHERE name = ?", (system_name,))
                result = cursor.fetchone()
                if result:
                    system_id = result[0]

            # Resolve planet_id and moon_id
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

            elif location_type == 'moon' and location_name and system_id:
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

            # Insert discovery (same as before)
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
                system_id, planet_id, moon_id,
                location_type, location_name,
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
                discovery_data.get('tags'), discovery_data.get('metadata'),
                discovery_data.get('species_type'), discovery_data.get('size_scale'),
                discovery_data.get('preservation_quality'), discovery_data.get('estimated_age'),
                discovery_data.get('language_status'), discovery_data.get('completeness'),
                discovery_data.get('author_origin'), discovery_data.get('key_excerpt'),
                discovery_data.get('structure_type'), discovery_data.get('architectural_style'),
                discovery_data.get('structural_integrity'), discovery_data.get('purpose_function'),
                discovery_data.get('tech_category'), discovery_data.get('operational_status'),
                discovery_data.get('power_source'), discovery_data.get('reverse_engineering'),
                discovery_data.get('species_name'), discovery_data.get('behavioral_notes'),
                discovery_data.get('habitat_biome'), discovery_data.get('threat_level'),
                discovery_data.get('resource_type'), discovery_data.get('deposit_richness'),
                discovery_data.get('extraction_method'), discovery_data.get('economic_value'),
                discovery_data.get('ship_class'), discovery_data.get('hull_condition'),
                discovery_data.get('salvageable_tech'), discovery_data.get('pilot_status'),
                discovery_data.get('hazard_type'), discovery_data.get('severity_level'),
                discovery_data.get('duration_frequency'), discovery_data.get('protection_required'),
                discovery_data.get('update_name'), discovery_data.get('feature_category'),
                discovery_data.get('gameplay_impact'), discovery_data.get('first_impressions'),
                discovery_data.get('story_type'), discovery_data.get('lore_connections'),
                discovery_data.get('creative_elements'), discovery_data.get('collaborative_work')
            ))

            conn.commit()
            discovery_id = cursor.lastrowid
            conn.close()

            logger.info(f"Successfully wrote discovery #{discovery_id} to VH-Database")
            return discovery_id

        except Exception as e:
            logger.error(f"Failed to write discovery to database: {e}")
            return None
