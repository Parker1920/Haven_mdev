"""
Haven Control Room - Named Constants Module

This module consolidates all hardcoded values throughout the project into
named constants for easier configuration, maintenance, and understanding.

Constants are organized by category:
- UI/Window dimensions
- Data validation ranges
- Coordinate system limits
- 3D map visualization
- Performance tuning
- Server configuration
- File handling
- Timing and delays
- Color and styling (shared with themes)

Usage:
    from common.constants import UIConstants, CoordinateLimits, MapConstants
    
    window_width = UIConstants.WINDOW_WIDTH
    max_x = CoordinateLimits.X_MAX
    grid_size = MapConstants.GRID_SIZE
"""

from typing import Dict, Tuple


class UIConstants:
    """CustomTkinter UI window and component dimensions."""

    # Main window dimensions
    WINDOW_WIDTH = 980
    WINDOW_HEIGHT = 700
    
    # Common frame dimensions (scrollable frames, panels, etc)
    SCROLLABLE_FRAME_WIDTH = 1300
    SCROLLABLE_FRAME_HEIGHT = 700
    
    # Dialog window sizes
    EXPORT_DIALOG_WIDTH = 480
    EXPORT_DIALOG_HEIGHT = 260
    SYSTEM_EDITOR_WIDTH = 400
    SYSTEM_EDITOR_HEIGHT = 450
    
    # Padding and spacing (in pixels)
    PADDING_STANDARD = 20
    PADDING_SMALL = 4
    PADDING_LARGE = 40
    
    # Border radius for modern elements
    BORDER_RADIUS = 4
    BORDER_RADIUS_LARGE = 12


class CoordinateLimits:
    """Valid coordinate ranges for galactic systems."""
    
    # X coordinate bounds
    X_MIN = -100
    X_MAX = 100
    X_RANGE = X_MAX - X_MIN
    
    # Y coordinate bounds
    Y_MIN = -100
    Y_MAX = 100
    Y_RANGE = Y_MAX - Y_MIN
    
    # Z coordinate bounds (altitude/depth)
    Z_MIN = -25
    Z_MAX = 25
    Z_RANGE = Z_MAX - Z_MIN
    
    @classmethod
    def is_valid_x(cls, x: float) -> bool:
        """Check if X coordinate is within valid range."""
        return cls.X_MIN <= x <= cls.X_MAX
    
    @classmethod
    def is_valid_y(cls, y: float) -> bool:
        """Check if Y coordinate is within valid range."""
        return cls.Y_MIN <= y <= cls.Y_MAX
    
    @classmethod
    def is_valid_z(cls, z: float) -> bool:
        """Check if Z coordinate is within valid range."""
        return cls.Z_MIN <= z <= cls.Z_MAX
    
    @classmethod
    def clamp_x(cls, x: float) -> float:
        """Clamp X coordinate to valid range."""
        return max(cls.X_MIN, min(cls.X_MAX, x))
    
    @classmethod
    def clamp_y(cls, y: float) -> float:
        """Clamp Y coordinate to valid range."""
        return max(cls.Y_MIN, min(cls.Y_MAX, y))
    
    @classmethod
    def clamp_z(cls, z: float) -> float:
        """Clamp Z coordinate to valid range."""
        return max(cls.Z_MIN, min(cls.Z_MAX, z))


class MapConstants:
    """Constants for 3D map visualization (Three.js)."""
    
    # Grid settings
    GRID_SIZE = 200
    GRID_MAJOR_DIVISIONS = 16
    GRID_MINOR_DIVISIONS = 80
    
    # Object sizes (Three.js sphere geometry)
    SYSTEM_SIZE = 0.8
    PLANET_SIZE = 0.8
    MOON_SIZE = 0.4  # Half of planet size
    STATION_SIZE = 0.27
    SUN_SIZE = 0.5
    
    # 3D Colors (hex values for Three.js Color constructor)
    # These match the theme colors where applicable
    COLOR_SYSTEM = 0x008b8d  # Teal/Cyan
    COLOR_PLANET = 0x008b8d  # Teal/Cyan
    COLOR_MOON = 0xb4b4c8    # Lavender/Gray
    COLOR_STATION = 0x9400d3  # Purple
    COLOR_SUN = 0xffd700     # Gold
    
    # Orbit visualization
    ORBIT_RING_SEGMENTS = 64
    ORBIT_LINE_WIDTH = 1
    
    # Camera settings
    CAMERA_FOV = 60  # Field of view in degrees
    CAMERA_NEAR = 0.1  # Near clipping plane
    CAMERA_FAR = 10000  # Far clipping plane
    CAMERA_DEFAULT_DISTANCE = 50  # Default distance from origin
    CAMERA_DEFAULT_POSITION: Tuple[float, float, float] = (30, 30, 30)
    
    # Camera interaction speeds
    PAN_SPEED = 0.1
    ZOOM_SPEED = 0.01
    ROTATION_SENSITIVITY = 0.01
    
    # Performance settings
    MAX_SYSTEMS_FOR_SMOOTH_RENDERING = 5000
    RENDERERS_PIXEL_RATIO = 1  # Set to window.devicePixelRatio for HiDPI
    
    # Raycaster for picking objects
    RAYCASTER_FAR = 1000
    
    # Animation
    ANIMATION_FRAME_RATE = 60  # Target FPS


class ValidationConstants:
    """Input validation limits and constraints."""
    
    # System name constraints
    SYSTEM_NAME_MIN_LENGTH = 1
    SYSTEM_NAME_MAX_LENGTH = 100
    
    # Planet name constraints
    PLANET_NAME_MIN_LENGTH = 1
    PLANET_NAME_MAX_LENGTH = 100
    
    # Moon name constraints
    MOON_NAME_MIN_LENGTH = 1
    MOON_NAME_MAX_LENGTH = 100
    
    # Description constraints
    DESCRIPTION_MAX_LENGTH = 1000
    
    # Number of planets/moons constraints
    MAX_PLANETS_PER_SYSTEM = 50
    MAX_MOONS_PER_PLANET = 50
    
    # JSON field size limits
    MAX_FIELD_SIZE = 10_000  # Characters per field


class DataConstants:
    """Data file and storage constants."""
    
    # Data file locations and naming
    DATA_FILE_NAME = "data.json"
    DATA_SCHEMA_FILE = "data.schema.json"
    DATA_BACKUP_EXTENSION = ".bak"
    
    # File encoding
    FILE_ENCODING = "utf-8"
    
    # JSON serialization
    JSON_INDENT = 2
    
    # Backup settings
    MAX_BACKUPS_TO_KEEP = 10
    BACKUP_PREFIX = "data"
    BACKUP_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
    
    # File locking
    FILELOCK_TIMEOUT = 10.0  # seconds
    FILELOCK_POLL_INTERVAL = 0.1  # seconds
    
    # Large dataset handling
    CHUNK_SIZE = 8192  # bytes for reading large files


class ServerConstants:
    """HTTP server and network configuration."""
    
    # HTTP server
    DEFAULT_PORT = 8000
    DEFAULT_HOST = "localhost"
    DEFAULT_BIND_ADDRESS = ""  # Binds to all interfaces
    
    # Server timeouts
    REQUEST_TIMEOUT = 30  # seconds
    CONNECT_TIMEOUT = 5  # seconds
    
    # File serving
    DEFAULT_CONTENT_TYPE = "text/html"
    CHARSET = "utf-8"


class ProcessingConstants:
    """Performance and processing configuration."""
    
    # Threading
    THREAD_POOL_SIZE = 4
    THREAD_POOL_MAX_WORKERS = 8
    
    # Timeouts
    EXPORT_TIMEOUT = 300  # seconds (5 minutes)
    MAP_GENERATION_TIMEOUT = 120  # seconds (2 minutes)
    FILE_READ_TIMEOUT = 30  # seconds
    
    # Progress reporting
    PROGRESS_UPDATE_INTERVAL = 0.1  # seconds
    PROGRESS_REPORTING_THRESHOLD = 100  # items before reporting
    
    # JSON parsing
    MAX_JSON_SIZE = 100 * 1024 * 1024  # 100 MB
    
    # Undo/Redo
    UNDO_REDO_HISTORY_SIZE = 100  # Maximum undo stack size


class ImportConstants:
    """Constants for data importing and exporting."""
    
    # Supported export formats
    EXPORT_FORMAT_WINDOWS = "Windows"
    EXPORT_FORMAT_MACOS = "macOS"
    EXPORT_FORMAT_IOS_PWA = "iOS PWA"
    
    # Default export settings
    DEFAULT_EXPORT_FORMAT = EXPORT_FORMAT_WINDOWS


class GUITextConstants:
    """Common GUI text strings and labels."""
    
    # Main window
    WINDOW_TITLE = "Haven Control Room"
    WINDOW_SUBTITLE = "Galactic System Management"
    
    # Button labels
    BTN_LAUNCH_WIZARD = "🛰️ Launch System Entry (Wizard)"
    BTN_GENERATE_MAP = "🗺️ Generate Map"
    BTN_OPEN_MAP = "🌐 Open Latest Map"
    BTN_EXPORT = "Export"
    BTN_IMPORT = "Import"
    BTN_SETTINGS = "Settings"
    BTN_CANCEL = "Cancel"
    BTN_SAVE = "Save"
    BTN_DELETE = "Delete"
    BTN_NEW = "New"
    BTN_BROWSE = "Browse…"
    
    # Labels
    LBL_DATA_SOURCE = "DATA SOURCE"
    LBL_USE_TEST_DATA = "Use Test Data"
    LBL_PRODUCTION_DATA = "Production Data"
    LBL_TESTING_DATA = "Testing Data"
    
    # Tooltips
    TIP_PRODUCTION_DATA = "📊 Production Data (data/data.json)"
    TIP_TESTING_DATA = "🧪 Testing Data (test_data.json)"


class FileSystemConstants:
    """File system paths and patterns (relative to project root)."""
    
    # Directory names
    DIR_SRC = "src"
    DIR_DATA = "data"
    DIR_LOGS = "logs"
    DIR_DIST = "dist"
    DIR_PHOTOS = "photos"
    DIR_THEMES = "themes"
    DIR_DOCS = "docs"
    DIR_TESTS = "tests"
    DIR_CONFIG = "config"
    DIR_SCRIPTS = "scripts"
    
    # File patterns
    PYTHON_FILE_PATTERN = "*.py"
    JSON_FILE_PATTERN = "*.json"
    HTML_FILE_PATTERN = "*.html"
    
    # Log files
    LOG_FILE_ROTATION_SIZE = 1024 * 1024  # 1 MB
    LOG_FILE_BACKUP_COUNT = 5


class LoggingConstants:
    """Logging configuration constants."""
    
    # Log level (use logging.DEBUG, logging.INFO, etc.)
    DEFAULT_LOG_LEVEL = "INFO"
    
    # Log format
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # File logging
    LOG_FILE_NAME = "haven-control-room.log"
    LOG_MAX_BYTES = 1024 * 1024  # 1 MB
    LOG_BACKUP_COUNT = 5
    
    # Rotation
    LOG_ROTATION_WHEN = "midnight"  # Rotate logs at midnight
    LOG_ROTATION_INTERVAL = 1  # 1 day


class ThreeJSConstants:
    """Three.js specific constants (for JavaScript generation)."""
    
    # Math constants
    PI = 3.141592653589793
    TWO_PI = 2 * PI
    
    # Scene lighting
    AMBIENT_LIGHT_INTENSITY = 0.6
    DIRECTIONAL_LIGHT_INTENSITY = 0.8
    LIGHT_COLOR = 0xffffff
    
    # Fog
    FOG_COLOR = 0x0a0e27  # Match background
    FOG_NEAR = 0.1
    FOG_FAR = 1000


# Convenience mappings for UI color references
COLOR_REFERENCE_MAP: Dict[str, str] = {
    "system": "accent_cyan",
    "planet": "accent_cyan",
    "moon": "glow",
    "station": "accent_purple",
    "sun": "warning",
    "background": "bg_dark",
    "card": "bg_card",
    "text": "text_primary",
}


def get_coordinate_error_messages() -> Dict[str, str]:
    """Get standard error messages for coordinate validation.
    
    Returns:
        Dictionary mapping coordinate names to error message templates.
    """
    return {
        "X": f"X coordinate must be between {CoordinateLimits.X_MIN} and {CoordinateLimits.X_MAX}",
        "Y": f"Y coordinate must be between {CoordinateLimits.Y_MIN} and {CoordinateLimits.Y_MAX}",
        "Z": f"Z coordinate must be between {CoordinateLimits.Z_MIN} and {CoordinateLimits.Z_MAX}",
    }


def get_all_constants() -> Dict[str, object]:
    """Get all constant classes as a dictionary for introspection.
    
    Useful for configuration loading and debugging.
    
    Returns:
        Dictionary mapping constant class names to class objects.
    """
    return {
        "UIConstants": UIConstants,
        "CoordinateLimits": CoordinateLimits,
        "MapConstants": MapConstants,
        "ValidationConstants": ValidationConstants,
        "DataConstants": DataConstants,
        "ServerConstants": ServerConstants,
        "ProcessingConstants": ProcessingConstants,
        "ImportConstants": ImportConstants,
        "GUITextConstants": GUITextConstants,
        "FileSystemConstants": FileSystemConstants,
        "LoggingConstants": LoggingConstants,
        "ThreeJSConstants": ThreeJSConstants,
    }


if __name__ == "__main__":
    # Simple validation script
    print("Haven Control Room - Constants Module")
    print("=" * 70)
    print(f"Window dimensions: {UIConstants.WINDOW_WIDTH}x{UIConstants.WINDOW_HEIGHT}")
    print(f"Coordinate limits: X({CoordinateLimits.X_MIN}..{CoordinateLimits.X_MAX}), "
          f"Y({CoordinateLimits.Y_MIN}..{CoordinateLimits.Y_MAX}), "
          f"Z({CoordinateLimits.Z_MIN}..{CoordinateLimits.Z_MAX})")
    print(f"Map grid size: {MapConstants.GRID_SIZE}")
    print(f"Server port: {ServerConstants.DEFAULT_PORT}")
    print(f"File lock timeout: {DataConstants.FILELOCK_TIMEOUT}s")
    print("=" * 70)
    print("All constants loaded successfully!")
