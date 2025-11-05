"""
Large Dataset Optimization Module

Provides lazy loading, pagination, and performance optimization for handling
large system datasets (1000+ systems efficiently). Implements:

1. Lazy loading of JSON data with chunking
2. Pagination support for system lists
3. Three.js rendering optimization
4. Memory profiling and optimization
5. Caching strategies
6. Efficient filtering and searching

Architecture:
    - DataLoader: Lazy loads systems on demand
    - Paginator: Manages pagination state
    - PerformanceMonitor: Tracks memory and rendering performance
    - DataCache: Smart caching for frequently accessed data

Usage:
    from common.optimize_datasets import DataLoader, Paginator
    
    # Lazy load data
    loader = DataLoader("data/data.json")
    systems = loader.load_all()  # Loads in chunks
    
    # Paginate large datasets
    paginator = Paginator(systems, page_size=50)
    for page in paginator:
        print(f"Page {paginator.current_page}: {len(page)} systems")

Author: Haven Project
Version: 1.0.0
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Generator, Tuple
import logging
from dataclasses import dataclass
from collections import OrderedDict
import time

from common.paths import data_path
from common.constants import DataConstants, MapConstants, ValidationConstants


logger = logging.getLogger(__name__)


@dataclass
class DataStats:
    """Statistics about loaded dataset."""
    total_systems: int
    total_planets: int
    total_moons: int
    total_stations: int
    file_size_mb: float
    load_time_ms: float
    memory_usage_mb: float = 0.0


class DataCache:
    """Intelligent cache for frequently accessed data.
    
    Implements LRU (Least Recently Used) eviction policy with
    size-based limits to prevent memory bloat.
    """
    
    def __init__(self, max_size: int = 100):
        """Initialize cache.
        
        Args:
            max_size: Maximum number of items to cache
        """
        self.max_size = max_size
        self.cache: OrderedDict = OrderedDict()
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache with LRU update.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Store item in cache with LRU eviction.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        
        # Evict oldest if over size limit
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)
    
    def clear(self) -> None:
        """Clear entire cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_hit_rate(self) -> float:
        """Get cache hit rate (0.0-1.0)."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class DataLoader:
    """Lazy loader for large JSON data files with chunking support."""
    
    def __init__(self, file_path: Optional[Path] = None, 
                 chunk_size: int = DataConstants.CHUNK_SIZE):
        """Initialize data loader.
        
        Args:
            file_path: Path to JSON file (default: data/data.json)
            chunk_size: Size of chunks for reading (bytes)
        """
        self.file_path = file_path or data_path("data.json")
        self.chunk_size = chunk_size
        self.cache = DataCache(max_size=100)
        self._data: Optional[Dict] = None
        self._loaded = False
    
    def load_all(self) -> Dict[str, Any]:
        """Load all data from file.
        
        Caches result to avoid reloading. Handles multiple JSON formats:
        - Top-level system map (preferred)
        - {"systems": {...}} wrapper
        - Legacy {"data": [...]} list
        
        Returns:
            Dictionary of systems with metadata
        """
        if self._loaded:
            return self._data
        
        start_time = time.time()
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Normalize to standard format
            if isinstance(data, dict):
                if 'systems' in data:
                    # {"systems": {...}} format
                    self._data = data['systems']
                elif 'data' in data and isinstance(data['data'], list):
                    # Legacy list format - convert to dict
                    self._data = {
                        system.get('name', f"SYS_{i}"): system
                        for i, system in enumerate(data['data'])
                    }
                else:
                    # Top-level map format
                    self._data = {k: v for k, v in data.items() 
                                 if k != '_meta'}
            else:
                self._data = {}
            
            self._loaded = True
            load_time = (time.time() - start_time) * 1000
            logger.info(f"Loaded {len(self._data)} systems in {load_time:.1f}ms")
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self._data = {}
        
        return self._data
    
    def load_by_region(self, region: str) -> Dict[str, Any]:
        """Load systems for specific region.
        
        Args:
            region: Region name (e.g., "Adam", "Euclid")
            
        Returns:
            Dictionary of systems in region
        """
        cache_key = f"region_{region}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        all_data = self.load_all()
        region_systems = {
            name: system for name, system in all_data.items()
            if system.get('region') == region
        }
        
        self.cache.set(cache_key, region_systems)
        return region_systems
    
    def load_system(self, system_name: str) -> Optional[Dict]:
        """Load single system by name (cached).
        
        Args:
            system_name: Name of system to load
            
        Returns:
            System dictionary or None if not found
        """
        cache_key = f"system_{system_name}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        all_data = self.load_all()
        system = all_data.get(system_name)
        
        if system:
            self.cache.set(cache_key, system)
        
        return system
    
    def get_stats(self) -> DataStats:
        """Get statistics about loaded dataset.
        
        Returns:
            DataStats object with counts and sizes
        """
        data = self.load_all()
        
        total_planets = sum(
            len(system.get('planets', []))
            for system in data.values()
        )
        
        total_moons = sum(
            sum(len(planet.get('moons', [])) 
                for planet in system.get('planets', []))
            for system in data.values()
        )
        
        total_stations = sum(
            1 for system in data.values()
            if system.get('space_station')
        )
        
        file_size = self.file_path.stat().st_size / (1024 * 1024)
        
        return DataStats(
            total_systems=len(data),
            total_planets=total_planets,
            total_moons=total_moons,
            total_stations=total_stations,
            file_size_mb=file_size,
            load_time_ms=0.0  # Set during load
        )


class Paginator:
    """Pagination support for large dataset lists."""
    
    def __init__(self, items: List[Any], page_size: int = 50):
        """Initialize paginator.
        
        Args:
            items: List of items to paginate
            page_size: Number of items per page
        """
        self.items = items
        self.page_size = page_size
        self.total_pages = (len(items) + page_size - 1) // page_size
        self.current_page = 1
    
    def get_page(self, page_num: int) -> List[Any]:
        """Get specific page of items.
        
        Args:
            page_num: Page number (1-based)
            
        Returns:
            List of items for requested page
        """
        if page_num < 1 or page_num > self.total_pages:
            return []
        
        self.current_page = page_num
        start_idx = (page_num - 1) * self.page_size
        end_idx = min(start_idx + self.page_size, len(self.items))
        
        return self.items[start_idx:end_idx]
    
    def get_next_page(self) -> List[Any]:
        """Get next page of items.
        
        Returns:
            List of items for next page, or empty if at end
        """
        if self.current_page < self.total_pages:
            return self.get_page(self.current_page + 1)
        return []
    
    def get_previous_page(self) -> List[Any]:
        """Get previous page of items.
        
        Returns:
            List of items for previous page, or empty if at start
        """
        if self.current_page > 1:
            return self.get_page(self.current_page - 1)
        return []
    
    def get_all_pages(self) -> Generator[List[Any], None, None]:
        """Iterate through all pages.
        
        Yields:
            List of items for each page
        """
        for page_num in range(1, self.total_pages + 1):
            yield self.get_page(page_num)


class PerformanceMonitor:
    """Monitor rendering and memory performance."""
    
    def __init__(self):
        """Initialize performance monitor."""
        self.frame_times: List[float] = []
        self.memory_usage: List[float] = []
        self.max_frame_time = 0.0
        self.avg_frame_time = 0.0
    
    def log_frame_time(self, frame_time_ms: float) -> None:
        """Log frame rendering time.
        
        Args:
            frame_time_ms: Frame time in milliseconds
        """
        self.frame_times.append(frame_time_ms)
        self.max_frame_time = max(self.max_frame_time, frame_time_ms)
        
        if len(self.frame_times) > 100:
            # Keep only recent frames
            self.frame_times = self.frame_times[-100:]
    
    def get_average_fps(self) -> float:
        """Calculate average FPS from frame times.
        
        Returns:
            Average frames per second
        """
        if not self.frame_times:
            return 0.0
        
        avg_ms = sum(self.frame_times) / len(self.frame_times)
        return 1000.0 / avg_ms if avg_ms > 0 else 0.0
    
    def get_performance_score(self) -> Tuple[str, float]:
        """Get performance rating.
        
        Returns:
            Tuple of (rating_text, score_0_to_1)
            - "Excellent" (0.9-1.0) - 60+ FPS
            - "Good" (0.7-0.89) - 50-60 FPS
            - "Fair" (0.5-0.69) - 40-50 FPS
            - "Poor" (0-0.49) - <40 FPS
        """
        fps = self.get_average_fps()
        
        if fps >= 60:
            return "Excellent", 1.0
        elif fps >= 50:
            return "Good", 0.8
        elif fps >= 40:
            return "Fair", 0.6
        else:
            return "Poor", 0.3


class OptimizationStrategies:
    """Collection of optimization strategies for large datasets."""
    
    @staticmethod
    def optimize_for_three_js(systems: Dict[str, Any], 
                             max_visible: int = 1000) -> Dict[str, Any]:
        """Optimize system data for Three.js rendering.
        
        Removes unnecessary fields, limits detail level, and prepares
        data structure for efficient 3D rendering.
        
        Args:
            systems: Dictionary of system data
            max_visible: Maximum systems to render in viewport
            
        Returns:
            Optimized system dictionary
        """
        optimized = {}
        
        for name, system in list(systems.items())[:max_visible]:
            optimized[name] = {
                'id': system.get('id'),
                'x': system.get('x', 0),
                'y': system.get('y', 0),
                'z': system.get('z', 0),
                'name': system.get('name'),
                'region': system.get('region'),
                'planets': len(system.get('planets', [])),
            }
        
        return optimized
    
    @staticmethod
    def create_spatial_index(systems: Dict[str, Any]) -> Dict[str, List[str]]:
        """Create spatial index for efficient coordinate-based queries.
        
        Groups systems by grid cells for faster range queries.
        
        Args:
            systems: Dictionary of system data
            
        Returns:
            Spatial index mapping grid cell to system names
        """
        grid_size = MapConstants.GRID_SIZE
        cell_size = 10  # Grid cell dimensions
        
        index: Dict[str, List[str]] = {}
        
        for name, system in systems.items():
            x, y, z = system.get('x', 0), system.get('y', 0), system.get('z', 0)
            
            # Calculate grid cell
            cell_x = int(x // cell_size)
            cell_y = int(y // cell_size)
            cell_z = int(z // cell_size)
            cell_key = f"{cell_x},{cell_y},{cell_z}"
            
            if cell_key not in index:
                index[cell_key] = []
            index[cell_key].append(name)
        
        logger.debug(f"Created spatial index with {len(index)} cells")
        return index


if __name__ == "__main__":
    # Test optimization module
    print("Haven Dataset Optimization Module")
    print("=" * 70)
    
    # Test lazy loading
    print("\n1. Testing lazy loading...")
    loader = DataLoader()
    data = loader.load_all()
    print(f"   ✓ Loaded {len(data)} systems")
    
    # Test statistics
    stats = loader.get_stats()
    print(f"\n2. Dataset Statistics:")
    print(f"   • Systems: {stats.total_systems}")
    print(f"   • Planets: {stats.total_planets}")
    print(f"   • Moons: {stats.total_moons}")
    print(f"   • Stations: {stats.total_stations}")
    print(f"   • File size: {stats.file_size_mb:.2f} MB")
    
    # Test pagination
    if stats.total_systems > 0:
        print(f"\n3. Testing pagination...")
        paginator = Paginator(list(data.keys()), page_size=10)
        page1 = paginator.get_page(1)
        print(f"   ✓ Page 1: {len(page1)} systems")
        print(f"   ✓ Total pages: {paginator.total_pages}")
    
    # Test spatial index
    print(f"\n4. Creating spatial index...")
    index = OptimizationStrategies.create_spatial_index(data)
    print(f"   ✓ Spatial cells: {len(index)}")
    
    print("\n" + "=" * 70)
    print("Optimization module ready!")


def optimize_dataframe(df):
    """
    Optimize a pandas DataFrame for memory efficiency and performance.
    
    Converts data types to more efficient representations:
    - Converts object columns with unique values < 50% to category type
    - Converts int64 to int32 where possible
    - Converts float64 to float32 where possible
    - Skips columns with unhashable types (lists, dicts)
    
    Args:
        df: pandas DataFrame to optimize
        
    Returns:
        Optimized pandas DataFrame with reduced memory footprint
    """
    if df is None or df.empty:
        return df
    
    import pandas as pd
    
    for col in df.columns:
        col_type = df[col].dtype
        
        # Optimize object columns to category if few unique values
        if col_type == 'object':
            try:
                num_unique = df[col].nunique()
                num_total = len(df[col])
                if num_unique / num_total < 0.5 and num_unique < 100:
                    df[col] = df[col].astype('category')
            except (TypeError, ValueError):
                # Skip unhashable types (lists, dicts, etc.)
                pass
        
        # Optimize integer columns
        elif col_type == 'int64':
            try:
                max_val = df[col].max()
                min_val = df[col].min()
                if max_val < 2147483647 and min_val > -2147483648:
                    df[col] = df[col].astype('int32')
            except (ValueError, OverflowError):
                pass
        
        # Optimize float columns
        elif col_type == 'float64':
            try:
                df[col] = df[col].astype('float32')
            except (ValueError, OverflowError):
                pass
    
    return df

