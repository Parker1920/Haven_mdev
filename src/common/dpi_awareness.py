"""
DPI Awareness Configuration for Windows
Prevents scaling issues on high-DPI displays (4K monitors, Surface devices, etc.)
"""

import sys
import ctypes
import logging

logger = logging.getLogger(__name__)

def set_dpi_awareness():
    """
    Enable DPI awareness on Windows to prevent blurry scaling issues.

    This ensures the application renders crisply on high-DPI displays
    and prevents Windows from bitmap-scaling the entire window.

    Should be called before creating any GUI windows.
    """
    if sys.platform != 'win32':
        # Only applies to Windows
        return

    try:
        # Try to set DPI awareness (Windows 8.1 and later)
        # SetProcessDpiAwareness values:
        #   0 = DPI unaware
        #   1 = System DPI aware
        #   2 = Per-monitor DPI aware
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        logger.info("DPI awareness enabled (Windows 8.1+ mode)")
    except AttributeError:
        # shcore.dll not available, try older method
        try:
            # Fallback for Windows Vista through Windows 8
            ctypes.windll.user32.SetProcessDPIAware()
            logger.info("DPI awareness enabled (legacy mode)")
        except Exception as e:
            logger.warning(f"Could not enable DPI awareness (legacy): {e}")
    except Exception as e:
        logger.warning(f"Could not enable DPI awareness: {e}")
