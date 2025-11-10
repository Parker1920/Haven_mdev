"""
Haven Integration System
Integrates The Keeper with the Haven_mdev star mapping system.
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger('keeper.haven_integration')

class HavenIntegration:
    """Handles integration with the Haven_mdev star mapping system."""
    
    def __init__(self, haven_data_path: str = None):
        """Initialize Haven integration."""
        self.haven_data_path = haven_data_path or self._find_haven_data()
        self.haven_data = {}
        self.last_loaded = None
        
    def _find_haven_data(self) -> Optional[str]:
        """Attempt to find Haven data.json file."""
        # First check environment variable
        env_path = os.getenv('HAVEN_DATA_PATH')
        if env_path and os.path.exists(env_path):
            logger.info(f"Found Haven data from HAVEN_DATA_PATH: {env_path}")
            return env_path
        
        # Common paths to check (cross-platform)
        possible_paths = [
            # TEST DATA PATH (priority for testing)
            os.path.join(os.path.expanduser("~"), "Desktop", "Haven_mdev", "data", "keeper_test_data.json"),
            # Windows paths
            os.path.join(os.path.expanduser("~"), "Desktop", "Haven_mdev", "data", "data.json"),
            os.path.join(os.path.expanduser("~"), "Desktop", "untitled folder", "Haven_mdev", "data", "data.json"),
            # Relative paths
            "../../../untitled folder/Haven_mdev/data/data.json",
            "../../Haven_mdev/data/data.json",
            "../Haven_mdev/data/data.json",
            # macOS/Linux paths (kept for compatibility)
            "/Users/parkerstouffer/Desktop/untitled folder/Haven_mdev/data/data.json",
            os.path.expanduser("~/Desktop/untitled folder/Haven_mdev/data/data.json")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found Haven data at: {path}")
                return path
        
        logger.warning("Haven data.json not found in expected locations")
        logger.info("Bot will run in standalone mode without Haven integration")
        return None
    
    async def load_haven_data(self) -> bool:
        """Load Haven star system data."""
        if not self.haven_data_path or not os.path.exists(self.haven_data_path):
            return False
        
        try:
            with open(self.haven_data_path, 'r', encoding='utf-8') as f:
                self.haven_data = json.load(f)
            
            self.last_loaded = datetime.utcnow()
            logger.info(f"Loaded {len(self.haven_data)} Haven systems")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load Haven data: {e}")
            return False
    
    def get_all_systems(self) -> Dict[str, Dict]:
        """Get all Haven star systems."""
        # Filter out metadata
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
        
        # Get direct planets
        system_planets = system.get('planets', [])
        for planet in system_planets:
            planets.append({**planet, 'type': 'planet', 'system': system_name})
            
            # Add moons if they exist
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
        
        # Add space station as potential anomaly location
        if 'space_station' in system:
            station = system['space_station']
            anomalies.append({
                'name': station.get('name', 'Space Station'),
                'type': 'space_station',
                'coordinates': f"{station.get('x', 0)}, {station.get('y', 0)}, {station.get('z', 0)}",
                'system': system_name
            })
        
        # Add general space locations
        anomalies.extend([
            {
                'name': 'Deep Space (Asteroid Field)',
                'type': 'asteroid_field', 
                'system': system_name
            },
            {
                'name': 'Deep Space (Between Planets)',
                'type': 'deep_space',
                'system': system_name
            },
            {
                'name': 'Solar Vicinity',
                'type': 'solar_vicinity',
                'system': system_name
            },
            {
                'name': 'System Edge (Outer Orbit)',
                'type': 'system_edge',
                'system': system_name
            }
        ])
        
        return anomalies
    
    def create_discovery_location_choices(self, system_name: str) -> List[Dict]:
        """Create a list of location choices for discovery reports."""
        choices = []
        
        # Add planets and moons
        planets = self.get_planets_in_system(system_name)
        for planet in planets:
            if planet['type'] == 'planet':
                choices.append({
                    'label': f"🪐 {planet['name']} (Planet)",
                    'value': f"planet:{planet['name']}",
                    'description': f"Surface discoveries on {planet['name']}"
                })
            else:  # moon
                choices.append({
                    'label': f"🌙 {planet['name']} (Moon of {planet.get('parent_planet', 'Unknown')})",
                    'value': f"moon:{planet['name']}",
                    'description': f"Surface discoveries on {planet['name']}"
                })
        
        # Add space anomaly locations
        anomalies = self.get_space_anomaly_locations(system_name)
        for anomaly in anomalies:
            choices.append({
                'label': f"🌌 {anomaly['name']}",
                'value': f"space:{anomaly['type']}:{anomaly['name']}",
                'description': f"Space discoveries in {anomaly['name']}"
            })
        
        return choices
    
    def export_discovery_to_haven(self, discovery_data: Dict) -> Dict:
        """Export a discovery in Haven format for import."""
        # This creates a JSON structure that can be used to update Haven data
        haven_export = {
            'discovery_id': discovery_data.get('id'),
            'timestamp': discovery_data.get('submission_timestamp'),
            'system': discovery_data.get('system_name'),
            'location_type': discovery_data.get('location_type'),
            'location_name': discovery_data.get('location_name'),
            'discovery': {
                'type': discovery_data.get('type'),
                'description': discovery_data.get('description'),
                'condition': discovery_data.get('condition'),
                'significance': discovery_data.get('significance'),
                'keeper_analysis': discovery_data.get('keeper_analysis'),
                'evidence_photo': discovery_data.get('evidence_url'),
                'explorer': discovery_data.get('username'),
                'coordinates': discovery_data.get('coordinates')
            }
        }
        
        return haven_export
    
    def suggest_haven_system_creation(self, discovery_data: Dict) -> Dict:
        """Suggest a new Haven system entry based on discovery data."""
        # Parse location data to suggest system coordinates
        location = discovery_data.get('location', '')
        
        # Try to extract coordinates if provided
        coordinates = {'x': 0, 'y': 0, 'z': 0}
        if 'coordinates' in discovery_data and discovery_data['coordinates']:
            coord_str = discovery_data['coordinates']
            # Parse various coordinate formats
            # This is a simplified parser - could be enhanced
            
        suggestion = {
            'suggested_name': discovery_data.get('planet_name', 'Unknown System'),
            'coordinates': coordinates,
            'region': discovery_data.get('galaxy_name', 'Unknown Region'),
            'initial_discovery': {
                'type': discovery_data.get('type'),
                'description': discovery_data.get('description'),
                'explorer': discovery_data.get('username')
            },
            'note': f"System suggested based on Keeper discovery #{discovery_data.get('id')}"
        }
        
        return suggestion
    
    def get_regional_statistics(self, region: str) -> Dict:
        """Get statistics for a specific galactic region."""
        systems = self.get_systems_by_region(region)
        
        stats = {
            'region': region,
            'system_count': len(systems),
            'total_planets': 0,
            'total_moons': 0,
            'fauna_distribution': {},
            'sentinel_levels': {},
            'common_materials': {}
        }
        
        for system_name, system_data in systems.items():
            planets = self.get_planets_in_system(system_name)
            
            for planet in planets:
                if planet['type'] == 'planet':
                    stats['total_planets'] += 1
                else:
                    stats['total_moons'] += 1
                
                # Track fauna
                fauna = planet.get('fauna', 'Unknown')
                stats['fauna_distribution'][fauna] = stats['fauna_distribution'].get(fauna, 0) + 1
                
                # Track sentinels
                sentinel = planet.get('sentinel', 'Unknown')
                stats['sentinel_levels'][sentinel] = stats['sentinel_levels'].get(sentinel, 0) + 1
                
                # Track materials
                materials = planet.get('materials', '')
                if materials:
                    for material in materials.split(','):
                        material = material.strip()
                        if material:
                            stats['common_materials'][material] = stats['common_materials'].get(material, 0) + 1
        
        return stats
    
    def backup_keeper_discoveries(self, discoveries: List[Dict], backup_path: str = None) -> str:
        """Create a backup of Keeper discoveries in Haven-compatible format."""
        if not backup_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"./data/keeper_discoveries_backup_{timestamp}.json"
        
        backup_data = {
            '_meta': {
                'backup_type': 'keeper_discoveries',
                'timestamp': datetime.utcnow().isoformat(),
                'discovery_count': len(discoveries),
                'format_version': '1.0.0'
            },
            'discoveries': discoveries,
            'haven_exports': [self.export_discovery_to_haven(d) for d in discoveries]
        }
        
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Backup created: {backup_path}")
        return backup_path