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

from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="haven-starmap",
    version="3.0.0",
    description="No Man's Sky star mapping and visualization toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Haven Team",
    packages=find_packages(exclude=["tests", "Archive-Dump", "docs"]),
    python_requires=">=3.10",
    install_requires=[
        "pandas>=2.0",
        "customtkinter>=5.2",
        "jsonschema>=4.0",
        "filelock>=3.12.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "pytest-mock>=3.0",
            "mypy>=1.0",
            "black>=23.0",
        ],
        "build": [
            "pyinstaller>=6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "haven=haven.control_room:main",
            "haven-wizard=haven.system_entry_wizard:main",
            "haven-map=haven.Beta_VH_Map:main",
        ],
    },
    include_package_data=True,
    package_data={
        "haven": [
            "config/*.json",
            "themes/*.json",
            "static/**/*",
            "templates/**/*.html",
        ],
    },
    project_urls={
        "Documentation": "https://github.com/Parker1920/Haven_mdev",
        "Source": "https://github.com/Parker1920/Haven_mdev",
        "Issues": "https://github.com/Parker1920/Haven_mdev/issues",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Games/Entertainment",
    ],
)
