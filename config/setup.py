"""
Setup configuration for Haven Starmap package.

This file provides backward compatibility with older pip installations
that don't support pyproject.toml. Modern installations use pyproject.toml.

To install in development mode:
    pip install -e .

To install with development dependencies:
    pip install -e ".[dev]"

To build distributions:
    pip install build
    python -m build
"""

# Minimal setup.py for backward compatibility
# All configuration is in pyproject.toml
from setuptools import setup

setup()

