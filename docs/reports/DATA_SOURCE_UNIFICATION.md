# Haven Control Room - Data Source Unification Analysis

## Problem Identified

There are **three separate functions** that pull data information, and they're **not consistently using the same source of truth**:

### 1. **System Entry Wizard Function** (`launch_gui()`)
   - Location: `src/control_room.py` lines 509-540
   - Currently: Launches wizard process but doesn't verify what data source it will use
   - Issue: Wizard may use different data provider than main control room

### 2. **Data Source File Selection** (`_on_data_source_change()`)
   - Location: `src/control_room.py` lines 441-487
   - Currently: Manages dropdown selection of production/testing/load_test
   - Reads from: Multiple locations (local JSON files, database)
   - Issue: Manual counting and inconsistent path references

### 3. **Advanced Tools - Database Statistics** (`show_database_stats()`)
   - Location: `src/control_room.py` lines 814-873
   - Currently: Queries database directly for statistics
   - Issue: May show different count than data_source_change if data is out of sync

---

## Root Causes

### A. Multiple Data Paths Being Checked
- **Line 454**: `tests/stress_testing/TESTING.json` (test data)
- **Line 466**: `data/haven_load_test.db` (load test)
- **Line 469**: Implicitly `data/data.json` (production)
- **Line 825**: `DATABASE_PATH` constant (production database)

### B. Inconsistent System Counting
- `_on_data_source_change()` manually counts systems from JSON
- `show_database_stats()` queries database directly
- No central counter that both agree on

### C. No Unified Data Source Registry
- Configuration spread across:
  - `config.settings` (USE_DATABASE, DATABASE_PATH, etc.)
  - `config/data_schema.json` (schema validation)
  - Multiple hardcoded paths in control_room.py

### D. Wizard Launch Doesn't Ensure Data Consistency
- Wizard is spawned as subprocess without passing current data source
- Wizard may initialize its own data provider independently
- No guarantee wizard and control room use same data

---

## Solution: Create Unified Data Source Manager

### Step 1: Create `src/common/data_source.py`

This will be the **single source of truth** for all data operations.

```python
# File: src/common/data_source.py

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class DataSourceInfo:
    """Immutable container for data source information"""
    name: str  # "production", "testing", "load_test"
    display_name: str  # User-friendly name
    path: Path  # Physical file/database path
    backend_type: str  # "json" or "database"
    system_count: int  # Cached system count
    description: str  # User-facing description
    size_mb: float  # File size in MB

class DataSourceManager:
    """Unified manager for all data sources - single source of truth"""
    
    _instance = None
    _sources: Dict[str, DataSourceInfo] = {}
    _current_source: str = "production"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._register_sources()
        self._cache_system_counts()
    
    def _register_sources(self):
        """Register all available data sources"""
        from config.settings import PROJECT_ROOT, DATABASE_PATH, USE_DATABASE
        
        # Production Source
        prod_path = PROJECT_ROOT / "data" / "data.json"
        prod_count = self._count_json_systems(prod_path)
        self._sources["production"] = DataSourceInfo(
            name="production",
            display_name="Production Data",
            path=prod_path,
            backend_type="database" if USE_DATABASE else "json",
            system_count=prod_count,
            description=f"Real production systems ({prod_count:,} systems)",
            size_mb=prod_path.stat().st_size / (1024 * 1024) if prod_path.exists() else 0
        )
        
        # Test Source
        test_path = PROJECT_ROOT / "tests" / "stress_testing" / "TESTING.json"
        test_count = self._count_json_systems(test_path)
        self._sources["testing"] = DataSourceInfo(
            name="testing",
            display_name="Test Data",
            path=test_path,
            backend_type="json",
            system_count=test_count,
            description=f"Stress test data ({test_count:,} systems)",
            size_mb=test_path.stat().st_size / (1024 * 1024) if test_path.exists() else 0
        )
        
        # Load Test Source
        loadtest_path = PROJECT_ROOT / "data" / "haven_load_test.db"
        loadtest_count = self._count_database_systems(loadtest_path)
        self._sources["load_test"] = DataSourceInfo(
            name="load_test",
            display_name="Load Test Database",
            path=loadtest_path,
            backend_type="database",
            system_count=loadtest_count,
            description="Billion-scale load test database",
            size_mb=loadtest_path.stat().st_size / (1024 * 1024) if loadtest_path.exists() else 0
        )
    
    def _count_json_systems(self, path: Path) -> int:
        """Count systems in JSON file"""
        if not path.exists():
            return 0
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return sum(1 for k, v in data.items() if k != "_meta" and isinstance(v, dict))
        except Exception as e:
            logging.warning(f"Failed to count systems in {path}: {e}")
            return 0
    
    def _count_database_systems(self, path: Path) -> int:
        """Count systems in database"""
        if not path.exists():
            return 0
        try:
            from src.common.database import HavenDatabase
            with HavenDatabase(str(path)) as db:
                return db.get_total_count()
        except Exception as e:
            logging.warning(f"Failed to count systems in database {path}: {e}")
            return 0
    
    def _cache_system_counts(self):
        """Update all system counts from their sources"""
        for source_info in self._sources.values():
            if source_info.backend_type == "json":
                source_info.system_count = self._count_json_systems(source_info.path)
            elif source_info.backend_type == "database":
                source_info.system_count = self._count_database_systems(source_info.path)
    
    def get_source(self, name: str) -> Optional[DataSourceInfo]:
        """Get information about a data source"""
        return self._sources.get(name)
    
    def get_all_sources(self) -> Dict[str, DataSourceInfo]:
        """Get all registered data sources"""
        return self._sources.copy()
    
    def set_current(self, name: str):
        """Set current active data source"""
        if name in self._sources:
            self._current_source = name
            logging.info(f"Data source changed to: {name}")
        else:
            logging.warning(f"Unknown data source: {name}")
    
    def get_current(self) -> DataSourceInfo:
        """Get current active data source info"""
        return self._sources.get(self._current_source)
    
    def get_current_name(self) -> str:
        """Get current source name"""
        return self._current_source
    
    def refresh_counts(self):
        """Refresh system counts from all sources (for updates)"""
        self._cache_system_counts()
        logging.info("Data source system counts refreshed")


# Singleton instance
_manager = None

def get_data_source_manager() -> DataSourceManager:
    """Get the singleton data source manager"""
    global _manager
    if _manager is None:
        _manager = DataSourceManager()
    return _manager
```

---

### Step 2: Update `src/control_room.py` to Use DataSourceManager

This ensures all three functions use the same data:

**Changes to `_get_data_source_description()`:**
```python
def _get_data_source_description(self):
    """Get descriptive text for current data source - NOW UNIFIED"""
    manager = get_data_source_manager()
    source = self.data_source.get()
    source_info = manager.get_source(source)
    
    if source_info:
        return source_info.description
    return ""
```

**Changes to `_on_data_source_change()`:**
```python
def _on_data_source_change(self, choice=None):
    """Handle data source dropdown change - NOW UNIFIED"""
    manager = get_data_source_manager()
    source = self.data_source.get()
    manager.set_current(source)
    
    source_info = manager.get_source(source)
    if not source_info:
        return
    
    # Update description label
    if hasattr(self, 'data_description'):
        self.data_description.configure(text=source_info.description)
    
    # Update data indicator
    color = {
        "production": COLORS['success'],
        "testing": COLORS['warning'],
        "load_test": COLORS['accent_cyan']
    }.get(source, COLORS['success'])
    
    self.data_indicator.configure(
        text=f"📊 {source_info.display_name}",
        text_color=color
    )
    
    # Update system count
    if hasattr(self, 'count_indicator') and SHOW_SYSTEM_COUNT:
        self.count_indicator.configure(text=f"Systems: {source_info.system_count:,}")
    
    self._log(f"Switched to {source} data source ({source_info.system_count:,} systems)")
```

**Changes to `show_database_stats()`:**
```python
def show_database_stats(self):
    """Show database statistics - NOW PULLS FROM UNIFIED MANAGER"""
    manager = get_data_source_manager()
    current_info = manager.get_current()
    
    if current_info.backend_type != 'database':
        messagebox.showinfo("Info", "Database statistics only available in database mode.")
        return
    
    try:
        from src.common.database import HavenDatabase
        
        with HavenDatabase(str(current_info.path)) as db:
            stats = db.get_statistics()
        
        # Dialog code... but use current_info.system_count for total
        stats_text = f"""Total Systems: {current_info.system_count:,}
Total Planets: {stats['total_planets']:,}
Total Moons: {stats['total_moons']:,}
...
"""
        # Rest of dialog code
```

**Changes to `launch_gui()` (System Entry Wizard):**
```python
def launch_gui(self):
    """Launch System Entry Wizard with current data context"""
    manager = get_data_source_manager()
    current_info = manager.get_current()
    
    self._log(f"Launching System Entry Wizard with {current_info.name} data…")
    
    def run():
        try:
            if self._frozen:
                cmd = [sys.executable, '--entry', 'system', 
                       '--data-source', current_info.name]  # Pass data source
                subprocess.Popen(cmd, cwd=str(project_root()))
            else:
                app = src_dir() / 'system_entry_wizard.py'
                env = os.environ.copy()
                env['HAVEN_DATA_SOURCE'] = current_info.name  # Set env var
                # ... rest of subprocess call with env=env
            
            self._log("System Entry Wizard launched.")
        except Exception as e:
            self._log(f"Launch failed: {e}")
    
    self._run_bg(run)
```

---

## Benefits of This Approach

✅ **Single Source of Truth**
- All three functions pull from `DataSourceManager`
- Consistent system counts everywhere
- No duplication of logic

✅ **No Data Mismatches**
- Same counts in Wizard launch, dropdown, and statistics
- All operations on same data context

✅ **Easy to Maintain**
- Add new data source? Update `_register_sources()` once
- All three functions automatically get it

✅ **Caching for Performance**
- System counts cached on startup
- Can refresh with `refresh_counts()`
- No repeated file reads/database queries

✅ **Type-Safe**
- `DataSourceInfo` dataclass ensures all needed info
- No missing properties

✅ **Testable**
- Manager can be tested independently
- Mock data sources easily
- Verify all three functions pull same data

---

## Implementation Order

1. Create `src/common/data_source.py` with `DataSourceManager`
2. Update `src/control_room.py` to import and use manager
3. Update wizard launch to pass data source via env var
4. Update system entry wizard to respect data source env var
5. Test all three functions show matching data
6. Document in codebase

---

## Before vs After

**BEFORE (Current):**
```
Dropdown: "production" → counts from tests/stress_testing/TESTING.json
Wizard: Launches without data source context
Stats: Queries data/haven.db directly
Result: User sees different counts! ❌
```

**AFTER (Unified):**
```
DataSourceManager registered sources on startup
Dropdown: "production" → DataSourceManager.get_source("production")
Wizard: Gets source from manager, uses same data context
Stats: Uses manager's cached count, queries same database
Result: User sees consistent counts! ✅
```

---

**Created:** November 6, 2025
**Status:** Ready for implementation
