"""
Haven Starmap - No Man's Sky Star Mapping and Visualization Toolkit

A comprehensive desktop application and Python package for creating, managing,
and exporting star system data for No Man's Sky explorers.

Main Modules:
    - control_room: Main desktop UI application
    - system_entry_wizard: Two-page system entry interface
    - Beta_VH_Map: Interactive 3D star map generator

Common Modules:
    - common.paths: Cross-platform path management
    - common.validation: Data validation and schema verification
    - common.sanitize: Input sanitization for security
    - common.file_lock: Concurrent file access protection
    - common.progress: Progress dialog UI components

Example Usage:
    >>> from haven.control_room import ControlRoom
    >>> app = ControlRoom()
    >>> app.mainloop()
"""

__version__ = "3.0.0"
__author__ = "Haven Team"
__all__ = [
    "control_room",
    "system_entry_wizard",
    "Beta_VH_Map",
    "common",
]
