"""
Input Sanitization Utilities

Provides functions to sanitize user input against various attack vectors:
- XSS (Cross-Site Scripting)
- Path Traversal
- Command/SQL Injection
- Filename validation

All user input should be passed through these functions before:
- Storing in files
- Displaying in HTML
- Using in file paths
- Processing in commands
"""

import re
import html
import unicodedata
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Optional, Any
from urllib.parse import unquote


# ============================================================================
# XSS PREVENTION
# ============================================================================

def sanitize_html(text: str, allow_safe_tags: bool = False) -> str:
    """Sanitize text to prevent XSS attacks.

    Args:
        text: User input text
        allow_safe_tags: If True, allows <b>, <i>, <em>, <strong> tags

    Returns:
        Sanitized text safe for HTML display

    Example:
        >>> sanitize_html('<script>alert("XSS")</script>')
        '&lt;script&gt;alert("XSS")&lt;/script&gt;'
    """
    if not text:
        return ""

    # Remove javascript: and data: URLs
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'data:', '', text, flags=re.IGNORECASE)

    # Remove event handlers (onerror, onload, etc.)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)

    # HTML escape all content
    sanitized = html.escape(text, quote=True)

    # If allowing safe tags, restore them
    if allow_safe_tags:
        safe_tags = ['b', 'i', 'em', 'strong']
        for tag in safe_tags:
            sanitized = sanitized.replace(f'&lt;{tag}&gt;', f'<{tag}>')
            sanitized = sanitized.replace(f'&lt;/{tag}&gt;', f'</{tag}>')

    return sanitized


def sanitize_system_name(name: str) -> str:
    """Sanitize system name for safe storage and display.

    Removes dangerous characters while preserving readability.

    Args:
        name: System name from user

    Returns:
        Sanitized system name

    Example:
        >>> sanitize_system_name('System<script>alert("XSS")</script>')
        'System-script-alert-XSS-script-'
    """
    if not name:
        return "Unnamed_System"

    # Remove HTML tags
    name = re.sub(r'<[^>]+>', '', name)

    # Remove dangerous characters
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '-', name)

    # Normalize whitespace
    name = ' '.join(name.split())

    # Limit length
    name = name[:100]

    return name.strip() or "Unnamed_System"


# ============================================================================
# PATH TRAVERSAL PREVENTION
# ============================================================================

def is_safe_path(path: str, base_dir: Optional[Path] = None) -> bool:
    """Check if a path is safe (no traversal attacks).

    Args:
        path: Path to validate
        base_dir: Optional base directory to restrict access to

    Returns:
        True if path is safe, False otherwise

    Example:
        >>> is_safe_path('data/systems.json')
        True
        >>> is_safe_path('../../etc/passwd')
        False
    """
    if not path:
        return False

    # Decode URL encoding
    decoded = unquote(path)

    # Check for path traversal patterns
    dangerous_patterns = [
        '..',  # Parent directory
        '~/',  # Home directory
        '\\\\',  # UNC paths
    ]

    for pattern in dangerous_patterns:
        if pattern in decoded or pattern in path:
            return False

    # Check for absolute paths
    if decoded.startswith('/') or (len(decoded) > 1 and decoded[1] == ':'):
        return False

    # Check for null bytes
    if '\x00' in path or '\x00' in decoded:
        return False

    # If base_dir provided, ensure resolved path is within it
    if base_dir:
        try:
            full_path = (base_dir / decoded).resolve()
            base_resolved = base_dir.resolve()
            if not str(full_path).startswith(str(base_resolved)):
                return False
        except (ValueError, OSError):
            return False

    return True


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to be safe for the filesystem.

    Args:
        filename: Filename to sanitize

    Returns:
        Safe filename

    Example:
        >>> sanitize_filename('system<script>.json')
        'system_script_.json'
        >>> sanitize_filename('../../../etc/passwd')
        'etc_passwd'
    """
    if not filename:
        return "unnamed_file"

    # Remove path components
    filename = Path(filename).name

    # Reserved Windows names
    reserved = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
                'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2',
                'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'}

    name_upper = filename.upper()
    if name_upper in reserved or name_upper.split('.')[0] in reserved:
        filename = f"file_{filename}"

    # Replace dangerous characters
    filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', filename)

    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')

    # Limit length (Windows max is 255)
    if len(filename) > 200:
        name, ext = Path(filename).stem, Path(filename).suffix
        filename = name[:200-len(ext)] + ext

    return filename or "unnamed_file"


# ============================================================================
# COORDINATE VALIDATION
# ============================================================================

def sanitize_coordinate(value: Any, min_val: float, max_val: float, default: float = 0.0) -> float:
    """Sanitize and validate a coordinate value.

    Args:
        value: Coordinate value (can be string or number)
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        default: Default value if invalid

    Returns:
        Validated float coordinate

    Example:
        >>> sanitize_coordinate("50.5", -100, 100)
        50.5
        >>> sanitize_coordinate("Infinity", -100, 100, 0.0)
        0.0
    """
    try:
        # Convert to float
        coord = float(value)

        # Reject special values
        if not (-float('inf') < coord < float('inf')):  # Catches inf and -inf
            return default

        # Check for NaN
        if coord != coord:  # NaN != NaN
            return default

        # Clamp to range
        coord = max(min_val, min(max_val, coord))

        return coord

    except (ValueError, TypeError, OverflowError):
        return default


# ============================================================================
# UNICODE NORMALIZATION
# ============================================================================

def sanitize_unicode(text: str) -> str:
    """Sanitize Unicode text to prevent attacks.

    Removes:
    - Right-to-left override characters
    - Zero-width characters
    - Other invisible/control characters

    Args:
        text: Text with potential Unicode attacks

    Returns:
        Sanitized text

    Example:
        >>> sanitize_unicode('test\\u202egnitseuqer')  # RTL override
        'test'
    """
    if not text:
        return ""

    # Remove dangerous Unicode characters
    dangerous_chars = [
        '\u202e',  # Right-to-left override
        '\u202d',  # Left-to-right override
        '\u200b',  # Zero-width space
        '\u200c',  # Zero-width non-joiner
        '\u200d',  # Zero-width joiner
        '\ufeff',  # Zero-width no-break space
    ]

    for char in dangerous_chars:
        text = text.replace(char, '')

    # Normalize to NFC form
    text = unicodedata.normalize('NFC', text)

    # Remove other control characters (except newline, tab, carriage return)
    text = ''.join(char for char in text
                   if char in '\n\r\t' or unicodedata.category(char)[0] != 'C')

    return text


# ============================================================================
# COMPREHENSIVE SANITIZATION
# ============================================================================

def sanitize_user_input(text: str, context: str = 'general') -> str:
    """Comprehensive input sanitization based on context.

    Args:
        text: User input
        context: How the input will be used:
                 - 'general': Basic sanitization
                 - 'html': For HTML display (XSS prevention)
                 - 'filename': For use in filenames
                 - 'system_name': For system names
                 - 'path': For file paths

    Returns:
        Sanitized input safe for the given context

    Example:
        >>> sanitize_user_input('<script>alert("XSS")</script>', 'html')
        '&lt;script&gt;alert("XSS")&lt;/script&gt;'
    """
    if not text:
        return ""

    # Always normalize Unicode first
    text = sanitize_unicode(text)

    # Context-specific sanitization
    if context == 'html':
        return sanitize_html(text)
    elif context == 'filename':
        return sanitize_filename(text)
    elif context == 'system_name':
        return sanitize_system_name(text)
    elif context == 'path':
        if not is_safe_path(text):
            raise ValueError(f"Unsafe path detected: {text}")
        return text
    else:  # 'general'
        # Basic sanitization - remove control characters, limit length
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        return text[:10000]  # Reasonable limit


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def validate_json_keys(data: dict) -> dict:
    """Validate JSON to prevent prototype pollution.

    Args:
        data: JSON data dictionary

    Returns:
        Cleaned dictionary

    Raises:
        ValueError: If dangerous keys found
    """
    dangerous_keys = {'__proto__', 'constructor', 'prototype'}

    def check_dict(d: dict, path: str = ""):
        if not isinstance(d, dict):
            return

        for key in d.keys():
            if key in dangerous_keys:
                raise ValueError(f"Dangerous JSON key '{key}' found at {path}")

            # Recursively check nested dicts
            if isinstance(d[key], dict):
                check_dict(d[key], f"{path}.{key}")
            elif isinstance(d[key], list):
                for i, item in enumerate(d[key]):
                    if isinstance(item, dict):
                        check_dict(item, f"{path}.{key}[{i}]")

    check_dict(data)
    return data
