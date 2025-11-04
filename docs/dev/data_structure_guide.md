# Chapter 7: Data Structure & Schema

## Overview

Haven uses JSON as its primary data format, providing a flexible, human-readable structure for storing star system information. The system is designed to be **data-driven** - any field you add to your JSON automatically appears in maps and interfaces.

## Core Data File

### Location
```
data/data.json
```

This file contains your complete star system database and is the single source of truth for all Haven operations.

### Format Evolution
Haven supports multiple JSON formats for backward compatibility:

1. **Current Format** (Recommended):
```json
{
  "system_name": {
    "name": "System Name",
    "region": "Region Name",
    "x": 100.5,
    "y": -42.3,
    "z": 15.0,
    "attributes": "Trade hub; Rare resources",
    "planets": [...]
  }
}
```

2. **Legacy Wrapper Format**:
```json
{
  "systems": {
    "system_name": {...}
  }
}
```

3. **Array Format** (Oldest):
```json
{
  "data": [
    {
      "name": "System Name",
      "x": 100.5,
      "y": -42.3,
      "z": 15.0,
      ...
    }
  ]
}
```

## Schema Validation

### Schema File
```
data/data.schema.json
```

Defines the structure and validation rules for your data. The schema is automatically used by:
- System Entry Wizard for form validation
- Map generator for data parsing
- Import/export operations

### Key Validation Rules

#### System Level
- **name**: String, required
- **region**: String, optional
- **x, y, z**: Numbers (integers or floats), required
- **attributes**: String, optional
- **planets**: Array of planet objects, optional

#### Planet Level
- **name**: String, required
- **sentinel**: Enum ("N/A", "None", "Low", "Medium", "High", "Aggressive"), optional
- **fauna**: Enum or number (0-10), optional
- **flora**: Enum ("N/A", "None", "Low", "Mid", "High"), optional
- **properties**: String, optional
- **materials**: String, optional
- **base_location**: String, optional
- **photo**: String (relative path), optional
- **notes**: String, optional
- **moons**: Array of moon objects, optional

#### Moon Level
Same structure as planets but without moons array.

## Data Migration

### Automatic Migration
Haven automatically detects and migrates legacy formats:

1. **Detection**: Reads existing `data.json` and identifies format
2. **Conversion**: Transforms to current top-level map format
3. **Backup**: Creates `data.json.bak` before any changes
4. **Validation**: Ensures migrated data passes schema validation

### Manual Migration
For complex migrations or data recovery:
```bash
python scripts/migrate_to_systems_map.py
```

### Migration Examples

#### Array to Map Conversion
```json
// Before (array format)
{
  "data": [
    {"name": "Alpha", "x": 1, "y": 2, "z": 3},
    {"name": "Beta", "x": 4, "y": 5, "z": 6}
  ]
}

// After (map format)
{
  "Alpha": {
    "name": "Alpha",
    "x": 1, "y": 2, "z": 3
  },
  "Beta": {
    "name": "Beta", 
    "x": 4, "y": 5, "z": 6
  }
}
```

## Custom Fields

### Adding Custom Fields
You can add any fields to your data:

```json
{
  "system_name": {
    "name": "System Name",
    "x": 100, "y": 200, "z": 300,
    "custom_field": "Any value",
    "discovery_date": "2025-11-03",
    "explorer_notes": "Beautiful ringed planet"
  }
}
```

### Field Management
Use the System Entry Wizard to manage custom fields:
1. Launch System Entry Wizard
2. Click "⚙️ Manage Fields" button
3. Add, rename, or remove custom fields
4. Changes apply to all existing systems

## Photo Management

### Photo Storage
Photos are stored in the `photos/` folder with automatic naming:

```
photos/
├── system_name-portal.png
├── planet_name-surface.jpg
└── base_location-discovery.webp
```

### Path References
Photos are referenced using relative paths:
```json
{
  "photo": "photos/system_name-portal.png"
}
```

### Automatic Processing
When you select a photo in the System Entry Wizard:
1. File is copied to `photos/` folder
2. Name collision avoidance (adds numbers if needed)
3. Relative path stored in JSON
4. Original file remains untouched

## Backup System

### Automatic Backups
Before any data modification:
- Original `data.json` copied to `data.json.bak`
- Backup stored in `Archive-Dump/data/` for long-term retention
- Multiple backups maintained with timestamps

### Manual Backup
```bash
cp data/data.json data/backup-$(date +%Y%m%d-%H%M%S).json
```

## Data Integrity

### Validation Checks
- **Schema compliance**: All required fields present
- **Type validation**: Numbers, strings, arrays as expected
- **Reference integrity**: Photo files exist if referenced
- **Uniqueness**: System names are unique keys

### Error Reporting
Validation errors are reported in:
- Control Room status panel
- Log files (`logs/`)
- System Entry Wizard validation messages

## Import/Export

### JSON Export
All data can be exported as clean JSON:
- From Control Room: Data automatically saved
- From iOS PWA: "Export JSON" button
- Manual: Copy `data/data.json`

### JSON Import
- **iOS PWA**: "Import JSON" button accepts any valid JSON
- **Bulk import**: Replace `data.json` and restart applications
- **Merge import**: Manual JSON editing for combining datasets

## Performance Considerations

### Large Datasets
For datasets with 100+ systems:
- Map generation may take longer
- Consider splitting into region files
- Use SSD storage for better performance
- Close other applications during generation

### Memory Usage
- Data loading: ~10-50MB for typical datasets
- Map generation: ~200-500MB additional
- iOS export: ~100MB for embedding libraries

## Troubleshooting Data Issues

### Common Problems

#### "Invalid JSON" Errors
```
Check for trailing commas, missing quotes, or syntax errors
Use online JSON validator: jsonlint.com
```

#### Missing Required Fields
```
System Entry Wizard will highlight missing fields
Check logs for specific validation errors
```

#### Photo Path Issues
```
Ensure photos/ folder exists
Check file permissions
Verify relative paths are correct
```

#### Schema Validation Failures
```
Update data.schema.json if adding custom fields
Check enum values match allowed options
Verify number formats (no text in coordinate fields)
```

### Recovery Procedures

#### Restore from Backup
```bash
cp data/data.json.bak data/data.json
```

#### Manual Data Repair
1. Open `data.json` in text editor
2. Fix syntax errors
3. Validate with online JSON tools
4. Test with System Entry Wizard

#### Clean Start
```bash
# Backup existing data
mv data/data.json data/old-data.json

# Start fresh
# Add systems through wizard
```

## Advanced Data Operations

### Bulk Editing
For large-scale changes:
1. Export data to external editor
2. Make batch changes
3. Validate JSON syntax
4. Import back into Haven

### Data Analysis
Extract insights from your data:
```python
import json
with open('data/data.json') as f:
    data = json.load(f)

# Count systems per region
regions = {}
for system in data.values():
    region = system.get('region', 'Unknown')
    regions[region] = regions.get(region, 0) + 1

print(regions)
```

### Custom Processing Scripts
Create Python scripts for specialized data operations:
```python
# Example: Add discovery timestamps
import json
from datetime import datetime

with open('data/data.json') as f:
    data = json.load(f)

for system in data.values():
    if 'discovered' not in system:
        system['discovered'] = datetime.now().isoformat()

with open('data/data.json', 'w') as f:
    json.dump(data, f, indent=2)
```

## Schema Extensions

### Adding New Field Types
Extend `data.schema.json` for custom validation:

```json
{
  "properties": {
    "custom_field": {
      "type": "string",
      "enum": ["option1", "option2", "option3"]
    }
  }
}
```

### Version Management
Schema includes version information:
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Haven Star System Data",
  "version": "3.0.0"
}
```

## Next Steps

Understanding your data structure enables:
- [Chapter 4](system_entry_wizard_guide.md) for data entry best practices
- [Chapter 5](galaxy_map_guide.md) for visualization of your data
- [Chapter 8](troubleshooting_guide.md) for data recovery procedures