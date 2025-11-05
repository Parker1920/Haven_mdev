"""
Data Validation Module

Provides JSON schema validation for system data to ensure data integrity
and catch errors before they corrupt the database or cause map generation failures.

Usage:
    from common.validation import validate_system_data, validate_data_file

    # Validate a single system
    is_valid, error = validate_system_data(system_dict)
    if not is_valid:
        print(f"Validation error: {error}")

    # Validate entire data file
    is_valid, errors = validate_data_file(data_dict)
    if not is_valid:
        for error in errors:
            print(f"Error: {error}")
"""

from common.constants import CoordinateLimits, ValidationConstants

import json
import jsonschema
from pathlib import Path
from typing import Tuple, List, Dict, Any


# Cache the schema to avoid reloading
_SCHEMA_CACHE = None


def get_schema_validator() -> jsonschema.Draft7Validator:
    """Get or create a Draft7Validator instance for the schema.

    Returns:
        jsonschema.Draft7Validator instance

    Raises:
        FileNotFoundError: If schema file doesn't exist
    """
    schema = load_schema()
    return jsonschema.Draft7Validator(schema)


def validate_with_schema(
    data: Dict[str, Any], strict: bool = True
) -> Tuple[bool, List[str]]:
    """Comprehensive schema validation with detailed error reporting.

    Args:
        data: Data to validate
        strict: If True, treat warnings as errors

    Returns:
        Tuple of (is_valid, error_list)
    """
    errors: List[str] = []
    warnings: List[str] = []

    try:
        validator = get_schema_validator()

        # Collect all validation errors
        for error in validator.iter_errors(data):
            error_path = " -> ".join(str(p) for p in error.path) if error.path else "root"
            full_error = f"[{error.validator}] at '{error_path}': {error.message}"
            errors.append(full_error)

        # Additional custom validations
        if "_meta" in data:
            if "version" not in data["_meta"]:
                warnings.append("Missing version in _meta")

        if strict and warnings:
            errors.extend(f"Warning (strict mode): {w}" for w in warnings)
            return False, errors

        return len(errors) == 0, errors

    except jsonschema.SchemaError as e:
        errors.append(f"Schema error: {e.message}")
        return False, errors
    except Exception as e:
        errors.append(f"Unexpected validation error: {str(e)}")
        return False, errors



def load_schema() -> dict:
    """Load JSON schema from config directory.

    Returns:
        Dictionary containing the JSON schema

    Raises:
        FileNotFoundError: If schema file doesn't exist
        json.JSONDecodeError: If schema file is invalid JSON
    """
    global _SCHEMA_CACHE

    if _SCHEMA_CACHE is not None:
        return _SCHEMA_CACHE

    # Find schema file
    schema_path = Path(__file__).parent.parent.parent / 'config' / 'data_schema.json'

    if not schema_path.exists():
        raise FileNotFoundError(
            f"Schema file not found at {schema_path}. "
            f"Please ensure config/data_schema.json exists."
        )

    with open(schema_path, 'r', encoding='utf-8') as f:
        _SCHEMA_CACHE = json.load(f)

    return _SCHEMA_CACHE


def validate_system_data(system_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate a single system's data against the system schema.

    Args:
        system_data: Dictionary containing system data (id, name, region, x, y, z, etc.)

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if data is valid, False otherwise
        - error_message: Empty string if valid, error description if invalid

    Example:
        >>> system = {"id": "SYS_001", "name": "Test", "region": "Euclid", "x": 0, "y": 0, "z": 0, "planets": []}
        >>> is_valid, error = validate_system_data(system)
        >>> print(is_valid)
        True
    """
    try:
        schema = load_schema()

        # Get the system schema from patternProperties
        system_schema = schema["patternProperties"]["^(?!_meta$).*$"]

        # Validate
        jsonschema.validate(system_data, system_schema)
        return True, ""

    except jsonschema.ValidationError as e:
        # Extract a clean error message
        error_path = " -> ".join(str(p) for p in e.path) if e.path else "root"
        error_msg = f"Validation error at '{error_path}': {e.message}"
        return False, error_msg

    except jsonschema.SchemaError as e:
        return False, f"Schema error: {e.message}"

    except FileNotFoundError as e:
        return False, str(e)

    except Exception as e:
        return False, f"Unexpected error during validation: {str(e)}"


def validate_data_file(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate an entire data file against the complete schema.

    Args:
        data: Dictionary containing the entire data file
              (with _meta and system entries)

    Returns:
        Tuple of (is_valid, error_list)
        - is_valid: True if all data is valid, False otherwise
        - error_list: List of error messages (empty if valid)

    Example:
        >>> data = {"_meta": {"version": "3.0.0"}, "System1": {...}}
        >>> is_valid, errors = validate_data_file(data)
        >>> if not is_valid:
        ...     for error in errors:
        ...         print(error)
    """
    errors = []

    try:
        schema = load_schema()

        # Validate entire file structure
        jsonschema.validate(data, schema)
        return True, []

    except jsonschema.ValidationError as e:
        # Collect all validation errors
        error_path = " -> ".join(str(p) for p in e.path) if e.path else "root"
        errors.append(f"Validation error at '{error_path}': {e.message}")

        # Check for additional validation errors
        validator = jsonschema.Draft7Validator(schema)
        for error in validator.iter_errors(data):
            error_path = " -> ".join(str(p) for p in error.path) if error.path else "root"
            error_msg = f"Error at '{error_path}': {error.message}"
            if error_msg not in errors:
                errors.append(error_msg)

        return False, errors

    except jsonschema.SchemaError as e:
        errors.append(f"Schema error: {e.message}")
        return False, errors

    except FileNotFoundError as e:
        errors.append(str(e))
        return False, errors

    except Exception as e:
        errors.append(f"Unexpected error during validation: {str(e)}")
        return False, errors


def validate_coordinates(x: float, y: float, z: float) -> Tuple[bool, str]:
    """Validate system coordinates are within acceptable range.

    Args:
        x: X coordinate (should be -100 to 100)
        y: Y coordinate (should be -100 to 100)
        z: Z coordinate (should be -25 to 25)

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> is_valid, error = validate_coordinates(50, 50, 10)
        >>> print(is_valid)
        True
        >>> is_valid, error = validate_coordinates(150, 0, 0)
        >>> print(error)
        'X coordinate must be between -100 and 100 (got 150)'
    """
    if not isinstance(x, (int, float)):
        return False, f"X coordinate must be a number (got {type(x).__name__})"
    if not isinstance(y, (int, float)):
        return False, f"Y coordinate must be a number (got {type(y).__name__})"
    if not isinstance(z, (int, float)):
        return False, f"Z coordinate must be a number (got {type(z).__name__})"

    if not (CoordinateLimits.X_MIN <= x <= CoordinateLimits.X_MAX):
        return False, f"X coordinate must be between {CoordinateLimits.X_MIN} and {CoordinateLimits.X_MAX} (got {x})"
    if not (CoordinateLimits.Y_MIN <= y <= CoordinateLimits.Y_MAX):
        return False, f"Y coordinate must be between {CoordinateLimits.Y_MIN} and {CoordinateLimits.Y_MAX} (got {y})"
    if not (CoordinateLimits.Z_MIN <= z <= CoordinateLimits.Z_MAX):
        return False, f"Z coordinate must be between {CoordinateLimits.Z_MIN} and {CoordinateLimits.Z_MAX} (got {z})"

    return True, ""


def validate_system_name(name: str) -> Tuple[bool, str]:
    """Validate system name meets requirements.

    Args:
        name: System name to validate

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> is_valid, error = validate_system_name("Euclid Prime")
        >>> print(is_valid)
        True
    """
    if not isinstance(name, str):
        return False, f"System name must be a string (got {type(name).__name__})"

    if not name or not name.strip():
        return False, "System name cannot be empty"

    if len(name) > 100:
        return False, f"System name too long (max 100 characters, got {len(name)})"

    # Check for dangerous characters (basic sanitization check)
    dangerous_chars = ['<', '>', '"', '&', '\x00']
    for char in dangerous_chars:
        if char in name:
            return False, f"System name contains invalid character: '{char}'"

    return True, ""


def validate_planet_data(planet: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate a single planet's data.

    Args:
        planet: Dictionary containing planet data

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> planet = {"name": "Test Planet", "sentinel": "Low", "moons": []}
        >>> is_valid, error = validate_planet_data(planet)
        >>> print(is_valid)
        True
    """
    if not isinstance(planet, dict):
        return False, f"Planet data must be a dictionary (got {type(planet).__name__})"

    if 'name' not in planet:
        return False, "Planet must have a 'name' field"

    name = planet['name']
    if not isinstance(name, str) or not name.strip():
        return False, "Planet name must be a non-empty string"

    # Validate sentinel level if present
    if 'sentinel' in planet:
        valid_sentinels = ["None", "Low", "Medium", "High", "Aggressive"]
        if planet['sentinel'] not in valid_sentinels:
            return False, f"Invalid sentinel level: '{planet['sentinel']}' (must be one of {valid_sentinels})"

    # Validate moons if present
    if 'moons' in planet:
        if not isinstance(planet['moons'], list):
            return False, "Planet moons must be a list"

        for i, moon in enumerate(planet['moons']):
            if not isinstance(moon, dict):
                return False, f"Moon {i} must be a dictionary"
            if 'name' not in moon:
                return False, f"Moon {i} missing 'name' field"
            if not isinstance(moon['name'], str) or not moon['name'].strip():
                return False, f"Moon {i} name must be a non-empty string"

    return True, ""


# ============================================================================
# VALIDATION REPORT
# ============================================================================

def generate_validation_report(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a detailed validation report for a data file.

    Args:
        data: Dictionary containing the entire data file

    Returns:
        Dictionary containing validation results and statistics:
        {
            "valid": bool,
            "errors": List[str],
            "warnings": List[str],
            "stats": {
                "total_systems": int,
                "total_planets": int,
                "total_moons": int,
                "regions": List[str]
            }
        }

    Example:
        >>> report = generate_validation_report(data)
        >>> print(f"Valid: {report['valid']}")
        >>> print(f"Total systems: {report['stats']['total_systems']}")
    """
    report: Dict[str, Any] = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "stats": {
            "total_systems": 0,
            "total_planets": 0,
            "total_moons": 0,
            "regions": set()
        }
    }

    # Validate overall structure
    is_valid, errors = validate_data_file(data)
    report["valid"] = is_valid
    report["errors"].extend(errors)  # type: ignore[union-attr]

    if not is_valid:
        return report

    # Collect statistics
    stats: Dict[str, Any] = report["stats"]  # type: ignore[assignment]
    for key, value in data.items():
        if key == "_meta":
            continue

        if not isinstance(value, dict):
            continue

        stats["total_systems"] = int(stats["total_systems"]) + 1  # type: ignore[index]

        # Count planets and moons
        if "planets" in value and isinstance(value["planets"], list):
            stats["total_planets"] = int(stats["total_planets"]) + len(value["planets"])  # type: ignore[index]

            for planet in value["planets"]:
                if isinstance(planet, dict) and "moons" in planet:
                    if isinstance(planet["moons"], list):
                        stats["total_moons"] = int(stats["total_moons"]) + len(planet["moons"])  # type: ignore[index]

        # Collect regions
        if "region" in value:
            regions: set = stats["regions"]  # type: ignore[assignment]
            regions.add(value["region"])

    # Convert set to sorted list
    regions_set: set = stats["regions"]  # type: ignore[assignment]
    stats["regions"] = sorted(regions_set)

    # Check for warnings
    if stats["total_systems"] == 0:  # type: ignore[index]
        report["warnings"].append("No systems found in data file")  # type: ignore[union-attr]

    if stats["total_systems"] > 10000:  # type: ignore[index]
        report["warnings"].append(  # type: ignore[union-attr]
            f"Large dataset ({stats['total_systems']} systems) may have performance issues"  # type: ignore[index]
        )

    return report
