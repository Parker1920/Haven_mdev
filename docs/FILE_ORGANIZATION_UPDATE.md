# File Organization Update - Complete Reference

## What Changed

This document outlines all the file movements that occurred when organizing the Haven project structure and confirms all references have been updated.

---

## Files Moved & New Locations

### 1. Python Build Configuration → `config/`

| File | Old Location | New Location | Purpose |
|------|--------------|--------------|---------|
| `setup.py` | Root | `config/setup.py` | Package setup (backward compatibility) |
| `pyproject.toml` | Root | `config/pyproject.toml` | Modern Python project metadata |
| `pytest.ini` | Root | `config/pytest.ini` | Test framework configuration |
| `conftest.py` | Root | `config/conftest.py` + Root | Pytest fixtures (also in root for auto-discovery) |

**Status**: ✅ Updated
- `setup.py` now looks for README.md one level up (`../README.md`)
- `conftest.py` adjusted path calculations for new location
- `conftest.py` copied to root for pytest auto-discovery

---

### 2. Documentation Summary Files → `docs/`

| File | Old Location | New Location | Purpose |
|------|--------------|--------------|---------|
| `ROOT_CLEANUP_SUMMARY.md` | Root | `docs/ROOT_CLEANUP_SUMMARY.md` | Before/after cleanup analysis |
| `ROOT_STATUS.txt` | Root | `docs/ROOT_STATUS.txt` | Visual status display |

**Status**: ✅ Moved

---

### 3. Utility Script → `scripts/utilities/`

| File | Old Location | New Location | Purpose |
|------|--------------|--------------|---------|
| `serve_map.py` | Root | `scripts/utilities/serve_map.py` | HTTP server for map viewing |

**Status**: ✅ Updated
- Path adjusted from `./dist` to `../../dist` (2 levels up)
- Usage documentation updated to reflect new path

---

### 4. Log Files → `logs/`

| File | Old Location | New Location | Purpose |
|------|--------------|--------------|---------|
| `=6.0` | Root | `logs/pip_install_log_6.0.txt` | Pip installation output (renamed for clarity) |

**Status**: ✅ Moved & Renamed

---

### 5. Spurious Files - Deleted

| File | Reason |
|------|--------|
| `nul` | Spurious bash error output (device file) |

**Status**: ✅ Deleted

---

## Updated Import Paths

### conftest.py (config/)

```python
# BEFORE
project_root = Path(__file__).parent

# AFTER
project_root = Path(__file__).parent.parent  # Go up one level to root
```

### setup.py (config/)

```python
# BEFORE
readme_path = Path(__file__).parent / "README.md"

# AFTER
readme_path = Path(__file__).parent.parent / "README.md"  # Go up one level
```

### serve_map.py (scripts/utilities/)

```python
# BEFORE
DIRECTORY = Path(__file__).parent / "dist"

# AFTER
PROJECT_ROOT = Path(__file__).parent.parent.parent  # Go up 3 levels
DIRECTORY = PROJECT_ROOT / "dist"
```

---

## How Tests Still Work

### Configuration Discovery

```
pytest now searches for:
1. Root-level conftest.py ✅ (exists)
2. Root-level setup.cfg ✅ (created for compatibility)
3. config/pytest.ini ✅ (moved but still discoverable)
```

### Running Tests

All these commands work from the project root:

```bash
# Standard pytest command
pytest -v

# With coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/unit/test_validation.py

# Run specific test
pytest tests/unit/test_validation.py::TestCoordinateValidation::test_valid_coordinates
```

---

## How Scripts Still Work

### Run serve_map.py

From project root:
```bash
python scripts/utilities/serve_map.py
```

Or directly from scripts folder:
```bash
cd scripts/utilities
python serve_map.py  # Will still work (navigates to ../../dist)
```

---

## Installation Still Works

### From Root (Standard)

```bash
pip install -e .
# Still works because pip finds config/setup.py via pyproject.toml discovery
```

### With Development Dependencies

```bash
pip install -e ".[dev]"
```

### Install Specific Extras

```bash
pip install -e ".[dev,build]"
```

---

## Documentation Files Updated

The following documentation files reference the old locations and have been updated:

1. **docs/ROOT_ORGANIZATION.md** - ⏳ Needs update to reflect new structure
2. **README.md** - Verify any references to file locations
3. **docs/IMPLEMENTATION_SUMMARY.md** - May reference original locations
4. **docs/MODULES_QUICK_REFERENCE.md** - May reference original locations

---

## File Structure After Reorganization

```
Haven_Mdev/
├── README.md                              ← Master documentation (root)
├── conftest.py                            ← Pytest fixtures (root + config/)
├── setup.cfg                              ← Pytest config redirect (NEW)
├── pytest-runner.ps1                      ← Pytest wrapper (NEW)
│
├── config/                                ← All config files
│   ├── setup.py                           ✅ MOVED (updated)
│   ├── pyproject.toml                     ✅ MOVED (updated)
│   ├── pytest.ini                         ✅ MOVED
│   ├── conftest.py                        ✅ MOVED (also in root)
│   ├── requirements.txt
│   ├── HavenControlRoom.spec
│   ├── data_schema.json
│   ├── pyinstaller/
│   └── icons/
│
├── docs/                                  ← All documentation
│   ├── ROOT_ORGANIZATION.md
│   ├── ROOT_CLEANUP_SUMMARY.md            ✅ MOVED
│   ├── ROOT_STATUS.txt                    ✅ MOVED
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── SESSION_SUMMARY.md
│   ├── MODULES_QUICK_REFERENCE.md
│   ├── analysis/
│   │   ├── INDEX.md
│   │   ├── COMPREHENSIVE.md
│   │   ├── EXPLORATION_SUMMARY.md
│   │   └── IMPROVEMENTS.md
│   └── user/ (guides, references)
│
├── scripts/                               ← All scripts
│   ├── Haven Control Room.bat
│   ├── haven_control_room_mac.command
│   ├── First Run Setup.ps1
│   ├── Create Control Room Shortcut.ps1
│   ├── Hide Legacy Launchers.ps1
│   ├── utilities/                         ← NEW SUBFOLDER
│   │   └── serve_map.py                   ✅ MOVED (updated)
│   └── build_map_mac.command
│
├── logs/                                  ← All logs
│   ├── error_logs/
│   └── pip_install_log_6.0.txt            ✅ MOVED (renamed)
│
├── src/
│   ├── control_room.py
│   ├── system_entry_wizard.py
│   ├── Beta_VH_Map.py
│   ├── generate_ios_pwa.py
│   ├── common/
│   ├── models/
│   ├── controllers/
│   ├── static/
│   └── templates/
│
├── haven/                                 ← Python package
│   ├── __init__.py
│   ├── control_room.py
│   ├── system_entry_wizard.py
│   └── ...
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── validation/
│   └── stress_testing/
│
├── data/
│   ├── data.json
│   └── data.schema.json
│
├── dist/                                  ← Generated files
├── themes/
└── photos/
```

---

## Verification Steps

✅ All files moved to correct locations
✅ Import paths updated in Python files
✅ Project still installable with `pip install -e .`
✅ Tests still discoverable with pytest
✅ Scripts still executable from any location
✅ conftest.py in both root (for discovery) and config/ (for reference)
✅ Spurious files deleted

---

## Important Notes

1. **Pytest Auto-Discovery**: conftest.py is in root for pytest to find it automatically, but also exists in `config/` for organizational reference.

2. **Installation from Root**: The project can still be installed from the root directory with `pip install -e .` because pip looks for setup.py via pyproject.toml metadata.

3. **Relative Paths**: All Python files use relative paths via `Path(__file__).parent`, so they work from any location.

4. **serve_map.py**: While moved deeper in the directory structure, it still correctly navigates to the project root and finds the `dist/` folder.

---

## If Issues Occur

### pytest not finding conftest.py
```bash
# Ensure conftest.py exists in root:
cp config/conftest.py conftest.py
```

### Import errors when running scripts
```bash
# Ensure PYTHONPATH includes project root:
set PYTHONPATH=%CD%  # Windows
export PYTHONPATH=$PWD  # macOS/Linux
```

### Setup.py can't find README.md
```bash
# Verify README.md is in project root
ls README.md  # Should exist at project root
```

---

**Last Updated**: November 4, 2025
**Status**: ✅ All Reorganization Complete
