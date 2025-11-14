"""
Pytest configuration and fixtures for Haven Starmap tests.

This file is automatically discovered by pytest and provides:
- Shared fixtures for all tests
- Test configuration
- Custom markers and hooks
"""

import sys
from pathlib import Path
import pytest

# Add src and haven to path for imports
# conftest.py is in tests/, so go up one level to project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "haven"))
sys.path.insert(0, str(project_root))


@pytest.fixture
def data_dir():
    """Provide the data directory path."""
    return project_root / "data"


@pytest.fixture
def sample_system_data():
    """Provide sample system data for testing."""
    return {
        "id": "TEST_SYS_001",
        "name": "Test System",
        "region": "Test Region",
        "x": 10.5,
        "y": 20.3,
        "z": 5.1,
        "planets": [
            {
                "id": "PLANET_001",
                "name": "Test Planet",
                "type": "Rocky",
                "moons": [
                    {
                        "id": "MOON_001",
                        "name": "Test Moon",
                    }
                ],
            }
        ],
    }


@pytest.fixture
def sample_data_file(sample_system_data):
    """Provide sample data file structure for testing."""
    return {
        "_meta": {
            "version": "3.0.0",
            "last_modified": "2025-11-04T12:00:00Z",
        },
        "Test System": sample_system_data,
    }


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
