# 🚀 Quick Reference Guide - New Modules

## Module Overview

### 1. **async_io.py** - Asynchronous File Operations
**Location:** `src/common/async_io.py`

**Purpose:** High-performance async I/O for JSON and file operations

**Key Functions:**
```python
async_read_json(file_path) → Dict[str, Any]
async_write_json(data, file_path, backup=True) → None
async_copy_file(src, dst, progress_callback=None) → None
async_load_multiple_json(file_paths) → Dict
async_batch_write_json(data_dict, output_dir) → None
sync_read_json(file_path) → Dict[str, Any]  # Backward compat
sync_write_json(data, file_path, backup=True) → None  # Backward compat
```

**Example:**
```python
import asyncio
from common.async_io import async_read_json, async_write_json

async def process_data():
    data = await async_read_json('data.json')
    data['newkey'] = 'value'
    await async_write_json(data, 'data.json')

asyncio.run(process_data())
```

---

### 2. **system_model.py** - Data Models (MVC)
**Location:** `src/models/system_model.py`

**Purpose:** Data models with validation and serialization

**Classes:**
- `MoonModel` - Represents a moon
- `PlanetModel` - Represents a planet (contains moons)
- `SystemModel` - Represents a star system (contains planets)

**Key Methods:**
```python
# All models have these methods:
model.validate() → Tuple[bool, str]  # Validation result
model.to_dict() → Dict[str, Any]     # Serialize to JSON
Model.from_dict(data) → Model        # Deserialize from JSON

# SystemModel additional methods:
system.add_planet(planet) → None
system.remove_planet(planet_id) → bool
system.update_timestamp() → None

# PlanetModel additional methods:
planet.add_moon(moon) → None
planet.remove_moon(moon_id) → bool
```

**Example:**
```python
from models.system_model import SystemModel, PlanetModel, MoonModel

# Create system
system = SystemModel(
    name="Euclid Prime",
    region="Euclid",
    x=50.5, y=20.3, z=5.1
)

# Add planet
planet = PlanetModel(name="Tropical Paradise")
system.add_planet(planet)

# Add moon
moon = MoonModel(name="Little Moon")
planet.add_moon(moon)

# Validate
is_valid, error = system.validate()
if is_valid:
    data = system.to_dict()
```

---

### 3. **system_controller.py** - Business Logic (MVC)
**Location:** `src/controllers/system_controller.py`

**Purpose:** Handle system data operations with file locking

**Class:** `SystemEntryController`

**Key Methods:**
```python
controller = SystemEntryController()

# Load/Save operations
systems = controller.load_all_systems() → Dict[str, SystemModel]
success, msg = controller.save_system(system) → Tuple[bool, str]
success, msg = controller.delete_system(name) → Tuple[bool, str]
success, msg = controller.duplicate_system(src, dst) → Tuple[bool, str]

# Export operations
success, msg = controller.export_systems_json(systems, path) → Tuple[bool, str]
```

**Example:**
```python
from controllers.system_controller import SystemEntryController
from models.system_model import SystemModel

controller = SystemEntryController()

# Load all systems
systems = controller.load_all_systems()
print(f"Found {len(systems)} systems")

# Create and save new system
system = SystemModel(
    name="New System",
    region="Euclid",
    x=10, y=20, z=5
)

success, message = controller.save_system(system)
if success:
    print(message)
else:
    print(f"Error: {message}")
```

---

### 4. **enhanced_export.py** - Enhanced Export UI
**Location:** `src/enhanced_export.py`

**Purpose:** Professional export dialog with progress tracking

**Classes:**
- `ExportProgressBar` - Progress visualization component
- `EnhancedExportDialog` - Main export dialog window

**Key Features:**
```python
# Create dialog
dialog = EnhancedExportDialog(
    parent_window,
    on_complete=callback_function
)

# Progress bar updates
progress_bar.add_step(name) → None
progress_bar.update_step(index, status, elapsed_time) → None
progress_bar.set_progress(value_0_to_1, status_text) → None
```

**Usage:**
```python
from enhanced_export import EnhancedExportDialog

def export_complete():
    print("Export finished!")

dialog = EnhancedExportDialog(root, on_complete=export_complete)
```

**Status Values:**
- `"pending"` - Not started (gray)
- `"in-progress"` - Currently running (amber)
- `"completed"` - Done (green)
- `"error"` - Failed (red)

---

## Enhanced Existing Modules

### validation.py - New Functions

**New Functions:**
```python
from common.validation import get_schema_validator, validate_with_schema

# Get validator instance
validator = get_schema_validator()

# Comprehensive validation with strict mode
is_valid, errors = validate_with_schema(data, strict=False)
if not is_valid:
    for error in errors:
        print(error)
```

---

## Testing Infrastructure

### pytest.ini - Test Configuration
Located at project root

**Markers Available:**
```bash
# Run only unit tests
pytest -m unit

# Run integration tests
pytest -m integration

# Run GUI tests
pytest -m gui

# Skip slow tests
pytest -m "not slow"
```

### conftest.py - Test Fixtures
Located at project root

**Available Fixtures:**
```python
def test_something(data_dir):
    """data_dir provides path to data directory"""
    
def test_something_else(sample_system_data):
    """sample_system_data provides test system"""
    
def test_with_full_data(sample_data_file):
    """sample_data_file provides full test data file"""
```

---

## Package Structure

### Import Paths

**Models:**
```python
from models import SystemModel, PlanetModel, MoonModel
from models.system_model import SystemModel
```

**Controllers:**
```python
from controllers import SystemEntryController
from controllers.system_controller import SystemEntryController
```

**Common:**
```python
from common.async_io import async_read_json, async_write_json
from common.validation import validate_system_data
from common.file_lock import FileLock
```

**Enhanced UI:**
```python
from enhanced_export import EnhancedExportDialog, ExportProgressBar
```

---

## Backward Compatibility

### Still Works (Old Code)
```python
# Old method still works
import json
with open('data.json', 'r') as f:
    data = json.load(f)
```

### New Recommended Way
```python
# New async method (better performance)
from common.async_io import sync_read_json
data = sync_read_json('data.json')

# Or fully async
from common.async_io import async_read_json
import asyncio
data = asyncio.run(async_read_json('data.json'))
```

---

## Error Handling

### Model Validation
```python
from models.system_model import SystemModel

system = SystemModel(name="", region="", x=150, y=0, z=0)
is_valid, error = system.validate()
if not is_valid:
    print(f"Validation Error: {error}")
    # Output: "Validation Error: System name cannot be empty"
```

### Controller Operations
```python
from controllers.system_controller import SystemEntryController

controller = SystemEntryController()
success, message = controller.save_system(system)
if not success:
    print(f"Save Failed: {message}")
    # Handle error
```

### File Operations
```python
from common.async_io import async_read_json

try:
    data = await async_read_json('missing.json')
except FileNotFoundError:
    print("File not found")
except Exception as e:
    print(f"Error: {e}")
```

---

## Performance Tips

### Use Async for Multiple Files
```python
from common.async_io import async_load_multiple_json

# Fast: Load multiple files concurrently
files = ['data1.json', 'data2.json', 'data3.json']
results = await async_load_multiple_json(files)
```

### Use Batch Operations
```python
from common.async_io import async_batch_write_json

# Fast: Write multiple files concurrently
data_dict = {
    'systems.json': systems_data,
    'metadata.json': meta_data,
    'config.json': config_data
}
await async_batch_write_json(data_dict, 'output_dir')
```

### File Locking for Concurrent Access
```python
from common.file_lock import FileLock

# Thread-safe file access
with FileLock('data.json', timeout=10):
    # Multiple processes can safely read/write
    with open('data.json', 'r') as f:
        data = json.load(f)
```

---

## Testing

### Run All Tests
```bash
pytest -v
```

### Run With Coverage
```bash
pytest --cov=haven --cov=src --cov-report=html
```

### Run Specific Test
```bash
pytest tests/unit/test_validation.py::TestCoordinateValidation::test_valid_coordinates -v
```

### Run Only Unit Tests
```bash
pytest -m unit
```

---

## Debugging

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Debug info")
```

### Type Checking
```bash
mypy src/
mypy src/models/system_model.py
```

### Test with Verbose Output
```bash
pytest -vv --tb=long
```

---

## Common Workflows

### Create and Save a System
```python
from models.system_model import SystemModel, PlanetModel
from controllers.system_controller import SystemEntryController

# Create system
system = SystemModel(
    name="New System",
    region="Euclid",
    x=50, y=20, z=5
)

# Add planet
planet = PlanetModel(name="My Planet")
system.add_planet(planet)

# Validate
is_valid, error = system.validate()
if is_valid:
    # Save
    controller = SystemEntryController()
    success, msg = controller.save_system(system)
    print(msg)
else:
    print(f"Validation error: {error}")
```

### Load and Export Systems
```python
from controllers.system_controller import SystemEntryController
from pathlib import Path

controller = SystemEntryController()

# Load all
systems = controller.load_all_systems()

# Export selected
systems_to_export = list(systems.values())[:5]
success, msg = controller.export_systems_json(
    systems_to_export,
    Path('export.json')
)
```

---

**End of Quick Reference**

For detailed information, see IMPLEMENTATION_SUMMARY.md
