"""
Data Source Manager - Single Source of Truth for All Data Operations

This module provides a unified manager that ensures the System Entry Wizard,
data source selection dropdown, and database statistics all pull from the
same authoritative source, preventing data mismatches and confusing users.

Key Components:
- DataSourceInfo: Immutable container for data source metadata
- DataSourceManager: Singleton that manages all data sources and their state
- get_data_source_manager(): Factory function for singleton instance
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DataSourceInfo:
    """
    Immutable container for data source information.
    Ensures all parts of the app see the exact same data about each source.
    """
    name: str  # "production", "testing", "load_test"
    display_name: str  # User-friendly: "Production Data"
    path: Path  # Physical file/database path
    backend_type: str  # "json" or "database"
    system_count: int  # Number of systems in this source
    description: str  # User-facing: "Real production systems (N systems)"
    size_mb: float  # File size in megabytes
    icon: str = "📊"  # Emoji icon for UI display


class DataSourceManager:
    """
    Unified manager for all data sources - SINGLE SOURCE OF TRUTH.
    
    This is a singleton that ensures the three main functions always see
    consistent data:
    1. System Entry Wizard - uses current source context
    2. Data source dropdown - selects from registered sources
    3. Database statistics - shows stats from current source
    
    Key guarantee: If two functions both call get_current(), they get
    the EXACT same DataSourceInfo object.
    """
    
    _instance = None
    _sources: Dict[str, DataSourceInfo] = {}
    _current_source_name: str = "production"
    _initialized: bool = False
    
    def __new__(cls):
        """Singleton pattern: ensure only one instance exists"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize on first instantiation"""
        if self._initialized:
            return
        
        self._initialized = True
        self._register_sources()
        self._cache_system_counts()
        logger.info("DataSourceManager initialized with sources: %s", 
                    ", ".join(self._sources.keys()))
    
    def _register_sources(self):
        """
        Register all available data sources.
        Called once on initialization to populate _sources dict.
        """
        try:
            from config.settings import PROJECT_ROOT, DATABASE_PATH, USE_DATABASE
        except ImportError:
            logger.warning("Could not import settings; using defaults")
            PROJECT_ROOT = Path.cwd()
            DATABASE_PATH = PROJECT_ROOT / "data" / "haven.db"
            USE_DATABASE = False
        
        # ==================== PRODUCTION SOURCE ====================
        prod_path = PROJECT_ROOT / "data" / "data.json"
        prod_count = self._count_json_systems(prod_path)
        prod_size = self._get_file_size_mb(prod_path)
        
        backend = "database" if USE_DATABASE else "json"
        self._sources["production"] = DataSourceInfo(
            name="production",
            display_name="Production Data",
            path=prod_path,
            backend_type=backend,
            system_count=prod_count,
            description=f"Real production systems ({prod_count:,} systems)" 
                       if prod_count > 0 else "Production data (empty)",
            size_mb=prod_size,
            icon="📊"
        )
        
        # ==================== TEST SOURCE ====================
        test_path = PROJECT_ROOT / "tests" / "stress_testing" / "TESTING.json"
        test_count = self._count_json_systems(test_path)
        test_size = self._get_file_size_mb(test_path)
        
        self._sources["testing"] = DataSourceInfo(
            name="testing",
            display_name="Test Data",
            path=test_path,
            backend_type="json",
            system_count=test_count,
            description=f"Stress test data ({test_count:,} systems)" 
                       if test_count > 0 else "Test data (file not found)",
            size_mb=test_size,
            icon="🧪"
        )
        
        # ==================== LOAD TEST SOURCE ====================
        loadtest_path = PROJECT_ROOT / "data" / "haven_load_test.db"
        loadtest_count = self._count_database_systems(loadtest_path)
        loadtest_size = self._get_file_size_mb(loadtest_path)
        
        self._sources["load_test"] = DataSourceInfo(
            name="load_test",
            display_name="Load Test Database",
            path=loadtest_path,
            backend_type="database",
            system_count=loadtest_count,
            description="Billion-scale load test database" 
                       if loadtest_count > 0 else "Load test database (not found)",
            size_mb=loadtest_size,
            icon="🔬"
        )
        
        # ==================== YH-DATABASE SOURCE (OFFICIAL MAP) ====================
        vh_db_path = PROJECT_ROOT / "data" / "VH-Database.db"
        vh_db_count = self._count_database_systems(vh_db_path)
        vh_db_size = self._get_file_size_mb(vh_db_path)
        
        self._sources["yh_database"] = DataSourceInfo(
            name="yh_database",
            display_name="YH-Database (Official Map)",
            path=vh_db_path,
            backend_type="database",
            system_count=vh_db_count,
            description="Official Haven Map - Ready for 1 billion+ star systems" 
                       if vh_db_count >= 0 else "YH-Database (not found)",
            size_mb=vh_db_size,
            icon="🌍"
        )
    
    @staticmethod
    def _get_file_size_mb(path: Path) -> float:
        """Get file size in megabytes"""
        try:
            if path.exists():
                return path.stat().st_size / (1024 * 1024)
        except Exception as e:
            logger.warning(f"Could not get file size for {path}: {e}")
        return 0.0
    
    @staticmethod
    def _count_json_systems(path: Path) -> int:
        """
        Count systems in JSON file.
        All three functions use this same count.
        """
        if not path.exists():
            logger.debug(f"JSON file not found: {path}")
            return 0
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Count all keys except "_meta"
            count = sum(1 for k, v in data.items() 
                       if k != "_meta" and isinstance(v, dict))
            logger.debug(f"Counted {count} systems in {path}")
            return count
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in {path}: {e}")
            return 0
        except Exception as e:
            logger.warning(f"Failed to count systems in {path}: {e}")
            return 0
    
    @staticmethod
    def _count_database_systems(path: Path) -> int:
        """
        Count systems in database.
        All three functions use this same count.
        """
        if not path.exists():
            logger.debug(f"Database file not found: {path}")
            return 0
        
        try:
            from src.common.database import HavenDatabase
            
            with HavenDatabase(str(path)) as db:
                count = db.get_total_count()
            logger.debug(f"Counted {count} systems in database {path}")
            return count
        except ImportError:
            logger.warning("HavenDatabase module not available")
            return 0
        except Exception as e:
            logger.warning(f"Failed to count systems in database {path}: {e}")
            return 0
    
    def _cache_system_counts(self):
        """
        Update all system counts from their sources.
        Called on initialization and when refresh_counts() is called.
        """
        for source_name, source_info in list(self._sources.items()):
            if source_info.backend_type == "json":
                count = self._count_json_systems(source_info.path)
            elif source_info.backend_type == "database":
                count = self._count_database_systems(source_info.path)
            else:
                count = 0
            
            # Create new immutable object with updated count
            self._sources[source_name] = DataSourceInfo(
                name=source_info.name,
                display_name=source_info.display_name,
                path=source_info.path,
                backend_type=source_info.backend_type,
                system_count=count,
                description=source_info.description,
                size_mb=source_info.size_mb,
                icon=source_info.icon
            )
    
    # ==================== PUBLIC API ====================
    
    def get_source(self, name: str) -> Optional[DataSourceInfo]:
        """
        Get information about a specific data source.
        
        Args:
            name: Source name ("production", "testing", "load_test")
        
        Returns:
            DataSourceInfo if found, None otherwise
        
        Example:
            manager = get_data_source_manager()
            prod_info = manager.get_source("production")
            print(f"Production has {prod_info.system_count} systems")
        """
        return self._sources.get(name)
    
    def get_all_sources(self) -> Dict[str, DataSourceInfo]:
        """
        Get all registered data sources.
        
        Returns:
            Dictionary mapping source names to DataSourceInfo
        
        Example:
            manager = get_data_source_manager()
            for name, info in manager.get_all_sources().items():
                print(f"{info.display_name}: {info.system_count} systems")
        """
        return self._sources.copy()
    
    def set_current(self, name: str) -> bool:
        """
        Set current active data source.
        Used by data source dropdown to switch sources.
        
        Args:
            name: Source name ("production", "testing", "load_test")
        
        Returns:
            True if successful, False if source not found
        
        Example:
            manager = get_data_source_manager()
            manager.set_current("testing")
        """
        if name in self._sources:
            self._current_source_name = name
            logger.info(f"Data source changed to: {name} ({self._sources[name].system_count:,} systems)")
            return True
        else:
            logger.warning(f"Unknown data source: {name}")
            return False
    
    def get_current(self) -> DataSourceInfo:
        """
        Get current active data source info.
        Used by Wizard, statistics, and other functions to know what
        data context they should operate on.
        
        Returns:
            DataSourceInfo for currently active source
        
        Guarantee: All three functions get the SAME object
        
        Example:
            manager = get_data_source_manager()
            current = manager.get_current()
            print(f"Currently using {current.display_name}")
            print(f"System count: {current.system_count}")
        """
        return self._sources.get(self._current_source_name)
    
    def get_current_name(self) -> str:
        """
        Get name of currently active data source.
        
        Returns:
            Source name ("production", "testing", "load_test")
        
        Example:
            manager = get_data_source_manager()
            name = manager.get_current_name()
            print(f"Current source: {name}")
        """
        return self._current_source_name
    
    def refresh_counts(self):
        """
        Refresh system counts from all sources.
        Call this after you know data has changed (e.g., after import).
        
        This ensures all three functions see the latest counts.
        
        Example:
            # After importing data or running sync
            manager = get_data_source_manager()
            manager.refresh_counts()
            # Now get_current() returns updated counts
        """
        logger.info("Refreshing system counts from all sources...")
        self._cache_system_counts()
        logger.info("System counts refreshed")


# ==================== SINGLETON FACTORY ====================

_manager_instance = None


def get_data_source_manager() -> DataSourceManager:
    """
    Get the singleton DataSourceManager instance.
    
    This is the main entry point. Call this from any part of the code
    to get access to the unified data source manager.
    
    Returns:
        DataSourceManager singleton instance
    
    Example:
        # In System Entry Wizard launch
        manager = get_data_source_manager()
        current_source = manager.get_current()
        
        # In data source dropdown change handler
        manager = get_data_source_manager()
        manager.set_current("production")
        info = manager.get_current()
        
        # In database statistics dialog
        manager = get_data_source_manager()
        current = manager.get_current()
        if current.backend_type == "database":
            # Show stats from that database
    """
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = DataSourceManager()
    return _manager_instance


# ==================== CONVENIENCE FUNCTIONS ====================

def get_current_source() -> DataSourceInfo:
    """Shorthand for getting current source"""
    return get_data_source_manager().get_current()


def get_all_sources() -> Dict[str, DataSourceInfo]:
    """Shorthand for getting all sources"""
    return get_data_source_manager().get_all_sources()


def set_current_source(name: str) -> bool:
    """Shorthand for setting current source"""
    return get_data_source_manager().set_current(name)


def refresh_data_sources():
    """Shorthand for refreshing all counts"""
    return get_data_source_manager().refresh_counts()
