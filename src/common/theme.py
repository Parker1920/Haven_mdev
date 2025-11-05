"""
Haven Control Room - Centralized Theme Configuration

Provides unified theme management and color definitions for all UI components.
This module eliminates code duplication and ensures consistent styling across the application.
"""

import json
from pathlib import Path
from typing import Dict, Optional
import logging

from common.paths import project_root


# Default theme modes and color schemes
THEMES: Dict[str, tuple[str, str]] = {
    "Dark": ("dark", "blue"),
    "Light": ("light", "blue"),
    "Cosmic": ("dark", "green"),
    "Haven (Cyan)": ("dark", "blue"),
}

# Default color palette (used if JSON config not found)
DEFAULT_COLORS: Dict[str, str] = {
    'bg_dark': '#0a0e27',
    'bg_card': '#141b3d',
    'accent_cyan': '#00d9ff',
    'accent_purple': '#9d4edd',
    'accent_pink': '#ff006e',
    'text_primary': '#ffffff',
    'text_secondary': '#8892b0',
    'success': '#00ff88',
    'warning': '#ffb703',
    'error': '#ff006e',
    'glass': '#1a2342',
    'glow': '#00ffff',
}


def load_theme_colors() -> Dict[str, str]:
    """Load theme colors from JSON configuration or use defaults.
    
    Attempts to load colors from themes/haven_theme.json. Falls back to
    DEFAULT_COLORS if file not found or loading fails.
    
    Returns:
        Dictionary mapping color names to hex values (e.g., 'bg_dark': '#0a0e27')
        
    Raises:
        No exceptions - always returns valid color dict
        
    Example:
        colors = load_theme_colors()
        bg_color = colors['bg_dark']
    """
    try:
        theme_path = project_root() / 'themes' / 'haven_theme.json'
        if theme_path.exists():
            obj = json.loads(theme_path.read_text(encoding='utf-8'))
            colors = obj.get('colors', {})
            
            # Merge with defaults to ensure all keys present
            result = DEFAULT_COLORS.copy()
            result.update(colors)
            return result
    except Exception as e:
        logging.warning(f"Failed to load theme colors from JSON: {e}, using defaults")
    
    return DEFAULT_COLORS.copy()


def get_colors() -> Dict[str, str]:
    """Get the current color palette.
    
    Returns:
        Dictionary of color definitions for the application
    """
    return load_theme_colors()


def get_color(name: str, default: Optional[str] = None) -> str:
    """Get a specific color by name.
    
    Args:
        name: Color name (e.g., 'bg_dark', 'accent_cyan')
        default: Default value if color not found
        
    Returns:
        Hex color value or default if not found
        
    Example:
        dark_bg = get_color('bg_dark')
        custom_color = get_color('unknown_color', '#ffffff')
    """
    colors = get_colors()
    return colors.get(name, default or '#ffffff')


def update_theme_color(name: str, value: str) -> None:
    """Update a specific theme color in the configuration file.
    
    Args:
        name: Color name to update
        value: New hex color value
        
    Example:
        update_theme_color('accent_cyan', '#00ffff')
    """
    try:
        theme_path = project_root() / 'themes' / 'haven_theme.json'
        
        # Load existing config or create new one
        if theme_path.exists():
            obj = json.loads(theme_path.read_text(encoding='utf-8'))
        else:
            obj = {'colors': {}}
        
        # Ensure colors dict exists
        if 'colors' not in obj:
            obj['colors'] = {}
        
        # Update color
        obj['colors'][name] = value
        
        # Save back to file
        theme_path.write_text(json.dumps(obj, indent=2), encoding='utf-8')
        logging.info(f"Updated theme color {name} to {value}")
    except Exception as e:
        logging.error(f"Failed to update theme color: {e}")


def reset_to_defaults() -> None:
    """Reset all theme colors to default values."""
    try:
        theme_path = project_root() / 'themes' / 'haven_theme.json'
        obj = {'colors': DEFAULT_COLORS.copy()}
        theme_path.write_text(json.dumps(obj, indent=2), encoding='utf-8')
        logging.info("Reset theme colors to defaults")
    except Exception as e:
        logging.error(f"Failed to reset theme colors: {e}")


# Lazy-load colors on first import
COLORS: Dict[str, str] = load_theme_colors()


if __name__ == '__main__':
    # Self-test
    colors = get_colors()
    print(f"✅ Loaded {len(colors)} colors")
    print(f"  Sample: bg_dark = {get_color('bg_dark')}")
    print(f"  Available colors: {', '.join(colors.keys())}")
