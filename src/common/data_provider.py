"""
Data Provider Abstraction Layer

Provides unified interface for accessing system data from either:
1. JSON files (public EXE version)
2. SQLite database (master version)

This allows the Control Room, Wizard, and Map Generator to work
with either backend without code changes.
"""
from typing import List, Dict, Optional, Protocol
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DataProvider(Protocol):
    """
    Abstract interface for data providers

    All data providers must implement these methods.
    This allows Control Room and other components to work
    with any backend (JSON, SQLite, PostgreSQL, etc.)
    """

    def get_all_systems(self, region: Optional[str] = None) -> List[Dict]:
        """Get all systems, optionally filtered by region"""
        ...

    def get_systems_paginated(self, page: int = 1, per_page: int = 100,
                             region: Optional[str] = None) -> Dict:
        """Get systems with pagination"""
        ...

    def get_system_by_name(self, name: str) -> Optional[Dict]:
        """Get single system by name"""
        ...

    def search_systems(self, query: str, limit: int = 50) -> List[Dict]:
        """Search systems"""
        ...

    def add_system(self, system_data: Dict) -> str:
        """Add new system"""
        ...

    def update_system(self, system_id: str, updates: Dict):
        """Update system"""
        ...

    def delete_system(self, system_id: str):
        """Delete system"""
        ...

    def get_regions(self) -> List[str]:
        """Get all regions"""
        ...

    def get_total_count(self) -> int:
        """Get total system count"""
        ...

    def system_exists(self, name: str) -> bool:
        """Check if system exists"""
        ...


class JSONDataProvider:
    """
    JSON-based data provider (for public EXE version)

    Reads/writes to data.json file.
    Simple, portable, version-controllable.
    Suitable for < 10,000 systems.
    """

    def __init__(self, json_path: str = "data/data.json"):
        """
        Initialize JSON data provider

        Args:
            json_path: Path to data.json file
        """
        self.json_path = Path(json_path)
        logger.info(f"Initialized JSON data provider: {self.json_path}")

    def _load_data(self) -> Dict:
        """Load entire JSON file"""
        if not self.json_path.exists():
            logger.warning(f"JSON file not found: {self.json_path}, creating empty data")
            return {"_meta": {"version": "1.0.0", "last_modified": ""}}

        with open(self.json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_data(self, data: Dict):
        """Save entire JSON file"""
        # Update metadata
        from datetime import datetime
        if "_meta" in data:
            data["_meta"]["last_modified"] = datetime.now().isoformat()

        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_all_systems(self, region: Optional[str] = None) -> List[Dict]:
        """Get all systems, optionally filtered by region"""
        data = self._load_data()

        systems = []
        for key, value in data.items():
            if key == "_meta" or not isinstance(value, dict):
                continue

            system = value.copy()
            # Ensure system has name field
            if 'name' not in system:
                system['name'] = key

            if region is None or system.get('region') == region:
                systems.append(system)

        return sorted(systems, key=lambda s: s.get('name', ''))

    def get_systems_paginated(self, page: int = 1, per_page: int = 100,
                             region: Optional[str] = None) -> Dict:
        """
        Get systems with pagination

        For JSON backend, this still loads all systems but returns paginated view.
        This maintains API compatibility with database version.
        """
        all_systems = self.get_all_systems(region=region)
        total = len(all_systems)

        # Calculate pagination
        start = (page - 1) * per_page
        end = start + per_page
        systems = all_systems[start:end]

        return {
            'systems': systems,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page if total > 0 else 1
        }

    def get_system_by_name(self, name: str) -> Optional[Dict]:
        """Get single system by name"""
        data = self._load_data()

        # Try direct key lookup first
        if name in data and isinstance(data[name], dict):
            system = data[name].copy()
            if 'name' not in system:
                system['name'] = name
            return system

        # Try case-insensitive search
        for key, value in data.items():
            if isinstance(value, dict) and value.get('name', '').lower() == name.lower():
                system = value.copy()
                if 'name' not in system:
                    system['name'] = key
                return system

        return None

    def search_systems(self, query: str, limit: int = 50) -> List[Dict]:
        """Search systems by name, materials, or attributes"""
        query_lower = query.lower()
        all_systems = self.get_all_systems()

        matches = []
        for system in all_systems:
            # Search in name
            if query_lower in system.get('name', '').lower():
                matches.append(system)
                continue

            # Search in materials
            materials = system.get('materials', '')
            if materials and query_lower in materials.lower():
                matches.append(system)
                continue

            # Search in attributes
            attributes = system.get('attributes', '')
            if attributes and query_lower in attributes.lower():
                matches.append(system)
                continue

        return matches[:limit]

    def add_system(self, system_data: Dict) -> str:
        """Add new system"""
        data = self._load_data()

        # Use system name as key
        name = system_data['name']

        # Check if exists
        if name in data:
            raise ValueError(f"System '{name}' already exists")

        # Add system
        data[name] = system_data
        self._save_data(data)

        return system_data.get('id', name)

    def update_system(self, system_id: str, updates: Dict):
        """
        Update system

        For JSON, system_id can be either the key or the system name
        """
        data = self._load_data()

        # Find system by ID or name
        system_key = None
        for key, value in data.items():
            if key == "_meta":
                continue
            if isinstance(value, dict):
                if key == system_id or value.get('id') == system_id or value.get('name') == system_id:
                    system_key = key
                    break

        if not system_key:
            raise ValueError(f"System '{system_id}' not found")

        # Update system
        data[system_key].update(updates)
        self._save_data(data)

    def delete_system(self, system_id: str):
        """Delete system"""
        data = self._load_data()

        # Find and delete system
        deleted = False
        for key in list(data.keys()):
            if key == "_meta":
                continue
            value = data[key]
            if isinstance(value, dict):
                if key == system_id or value.get('id') == system_id or value.get('name') == system_id:
                    del data[key]
                    deleted = True
                    break

        if not deleted:
            raise ValueError(f"System '{system_id}' not found")

        self._save_data(data)

    def get_regions(self) -> List[str]:
        """Get all unique regions"""
        all_systems = self.get_all_systems()
        regions = set()
        for system in all_systems:
            region = system.get('region')
            if region:
                regions.add(region)
        return sorted(list(regions))

    def get_total_count(self) -> int:
        """Get total system count"""
        data = self._load_data()
        count = sum(1 for k, v in data.items() if k != "_meta" and isinstance(v, dict))
        return count

    def system_exists(self, name: str) -> bool:
        """Check if system exists"""
        return self.get_system_by_name(name) is not None


class DatabaseDataProvider:
    """
    Database-based data provider (for master version)

    Uses SQLite database via HavenDatabase wrapper.
    Scalable to billions of systems.
    Suitable for > 1,000 systems.
    """

    def __init__(self, db_path: str = "data/haven.db"):
        """
        Initialize database data provider

        Args:
            db_path: Path to SQLite database
        """
        from src.common.database import HavenDatabase
        self.db_path = db_path
        self.db_class = HavenDatabase
        logger.info(f"Initialized database data provider: {db_path}")

    def get_all_systems(self, region: Optional[str] = None, include_planets: bool = False) -> List[Dict]:
        """Get all systems"""
        with self.db_class(self.db_path) as db:
            return db.get_all_systems(region=region, include_planets=include_planets)

    def get_systems_paginated(self, page: int = 1, per_page: int = 100,
                             region: Optional[str] = None) -> Dict:
        """Get systems with pagination"""
        with self.db_class(self.db_path) as db:
            return db.get_systems_paginated(page, per_page, region)

    def get_system_by_name(self, name: str) -> Optional[Dict]:
        """Get single system by name"""
        with self.db_class(self.db_path) as db:
            return db.get_system_by_name(name)

    def search_systems(self, query: str, limit: int = 50) -> List[Dict]:
        """Search systems"""
        with self.db_class(self.db_path) as db:
            return db.search_systems(query, limit)

    def add_system(self, system_data: Dict) -> str:
        """Add new system"""
        with self.db_class(self.db_path) as db:
            return db.add_system(system_data)

    def update_system(self, system_id: str, updates: Dict):
        """Update system"""
        with self.db_class(self.db_path) as db:
            db.update_system(system_id, updates)

    def delete_system(self, system_id: str):
        """Delete system"""
        with self.db_class(self.db_path) as db:
            db.delete_system(system_id)

    def get_regions(self) -> List[str]:
        """Get all regions"""
        with self.db_class(self.db_path) as db:
            return db.get_regions()

    def get_total_count(self) -> int:
        """Get total system count"""
        with self.db_class(self.db_path) as db:
            return db.get_total_count()

    def system_exists(self, name: str) -> bool:
        """Check if system exists"""
        with self.db_class(self.db_path) as db:
            return db.system_exists(name)

    def get_statistics(self) -> Dict:
        """Get database statistics (database-specific feature)"""
        with self.db_class(self.db_path) as db:
            return db.get_statistics()


def get_data_provider(use_database: bool = False,
                     json_path: str = "data/data.json",
                     db_path: str = "data/haven.db") -> DataProvider:
    """
    Factory function to create appropriate data provider

    This is the main entry point for Control Room and other components.

    Args:
        use_database: If True, use database provider; if False, use JSON
        json_path: Path to JSON file (if using JSON provider)
        db_path: Path to database file (if using database provider)

    Returns:
        DataProvider instance (JSON or Database)

    Example:
        # In Control Room:
        from config.settings import USE_DATABASE
        provider = get_data_provider(use_database=USE_DATABASE)
        systems = provider.get_all_systems()
    """
    if use_database:
        logger.info("Using DATABASE data provider")
        return DatabaseDataProvider(db_path)
    else:
        logger.info("Using JSON data provider")
        return JSONDataProvider(json_path)


def auto_detect_provider(json_path: str = "data/data.json",
                        db_path: str = "data/haven.db",
                        threshold: int = 1000) -> DataProvider:
    """
    Automatically detect which provider to use based on dataset size

    Strategy:
    1. If database exists and has > threshold systems, use database
    2. If JSON exists and has < threshold systems, use JSON
    3. Otherwise, use JSON as default

    Args:
        json_path: Path to JSON file
        threshold: System count threshold for switching to database

    Returns:
        DataProvider instance
    """
    db_path_obj = Path(db_path)
    json_path_obj = Path(json_path)

    # Check if database exists and get count
    if db_path_obj.exists():
        try:
            with DatabaseDataProvider(db_path).db_class(db_path) as db:
                db_count = db.get_total_count()
                if db_count >= threshold:
                    logger.info(f"Auto-detected DATABASE provider ({db_count:,} systems)")
                    return DatabaseDataProvider(db_path)
        except Exception as e:
            logger.warning(f"Failed to read database: {e}")

    # Check JSON
    if json_path_obj.exists():
        try:
            json_provider = JSONDataProvider(json_path)
            json_count = json_provider.get_total_count()

            if json_count < threshold:
                logger.info(f"Auto-detected JSON provider ({json_count:,} systems)")
                return json_provider
            else:
                logger.warning(f"JSON has {json_count:,} systems (>= threshold {threshold}), "
                             "consider migrating to database")
                return json_provider
        except Exception as e:
            logger.warning(f"Failed to read JSON: {e}")

    # Default to JSON
    logger.info("Auto-detected JSON provider (default)")
    return JSONDataProvider(json_path)


# ========== USAGE EXAMPLES ==========

def example_usage():
    """Example usage of data providers"""

    # Example 1: Manual selection
    print("=== Example 1: Manual Selection ===")
    provider = get_data_provider(use_database=False)  # Use JSON
    systems = provider.get_all_systems()
    print(f"Found {len(systems)} systems")

    # Example 2: Auto-detection
    print("\n=== Example 2: Auto-Detection ===")
    provider = auto_detect_provider(threshold=1000)
    systems = provider.get_all_systems(region="Adam")
    print(f"Found {len(systems)} systems in Adam region")

    # Example 3: Search
    print("\n=== Example 3: Search ===")
    results = provider.search_systems("Gold")
    print(f"Found {len(results)} systems with 'Gold'")
    for system in results[:3]:
        print(f"  - {system['name']}")

    # Example 4: Pagination
    print("\n=== Example 4: Pagination ===")
    page = provider.get_systems_paginated(page=1, per_page=5)
    print(f"Page {page['page']} of {page['total_pages']} ({page['total']} total systems)")
    for system in page['systems']:
        print(f"  - {system['name']}")


if __name__ == "__main__":
    example_usage()
