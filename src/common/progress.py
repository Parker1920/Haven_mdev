"""
Progress Dialog Components for Haven Starmap Project

Provides a reusable modal progress dialog for long-running operations
like map generation, file exports, and data processing.
"""

import customtkinter as ctk
from typing import Callable, Optional


class ProgressDialog(ctk.CTkToplevel):
    """Modal progress dialog with progress bar and status updates.

    Shows a modal window with:
    - Title
    - Status message (updates during operation)
    - Progress bar (0-100%)
    - Prevents user interaction with parent window until complete

    Example:
        >>> def long_operation():
        ...     progress = ProgressDialog(parent, "Processing Data")
        ...     try:
        ...         progress.update(0, "Loading files...")
        ...         # ... do work ...
        ...         progress.update(50, "Processing...")
        ...         # ... more work ...
        ...         progress.update(100, "Complete!")
        ...         progress.close()
        ...     except Exception as e:
        ...         progress.close()
        ...         raise
    """

    def __init__(self, parent, title: str):
        """Initialize progress dialog.

        Args:
            parent: Parent window (will be blocked while dialog is open)
            title: Dialog window title
        """
        super().__init__(parent)
        self.title(title)
        self.geometry("500x180")

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Status label
        self.label = ctk.CTkLabel(
            self,
            text="Initializing...",
            font=("Rajdhani", 16)
        )
        self.label.grid(row=0, column=0, padx=20, pady=(30, 10), sticky="ew")

        # Progress bar
        self.progress = ctk.CTkProgressBar(self, width=450)
        self.progress.grid(row=1, column=0, padx=20, pady=10)
        self.progress.set(0)

        # Percentage label
        self.percent_label = ctk.CTkLabel(
            self,
            text="0%",
            font=("Rajdhani", 14),
            text_color=("#7eb8bb", "#7eb8bb")
        )
        self.percent_label.grid(row=2, column=0, padx=20, pady=(0, 20))

        # Force window to appear immediately
        self.update()

    def update_progress(self, percent: float, message: str = ""):
        """Update progress bar and status message.

        Args:
            percent: Progress percentage (0-100)
            message: Status message to display. If empty, keeps current message.
        """
        # Clamp percentage to valid range
        percent = max(0, min(100, percent))

        # Update progress bar
        self.progress.set(percent / 100)

        # Update percentage label
        self.percent_label.configure(text=f"{int(percent)}%")

        # Update message if provided
        if message:
            self.label.configure(text=message)

        # Force UI update
        self.update_idletasks()

    def close_dialog(self):
        """Close the progress dialog and release modal grab."""
        try:
            self.grab_release()
            self.destroy()
        except Exception:
            # Already destroyed or other error - ignore
            pass


class IndeterminateProgressDialog(ctk.CTkToplevel):
    """Indeterminate progress dialog for operations without known duration.

    Shows a modal window with animated progress bar when the duration
    of an operation is unknown or highly variable.

    Example:
        >>> progress = IndeterminateProgressDialog(parent, "Please wait...")
        >>> progress.set_message("Loading data...")
        >>> # ... perform operation ...
        >>> progress.close_dialog()
    """

    def __init__(self, parent, title: str, message: str = "Processing..."):
        """Initialize indeterminate progress dialog.

        Args:
            parent: Parent window
            title: Dialog window title
            message: Initial status message
        """
        super().__init__(parent)
        self.title(title)
        self.geometry("500x160")

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Status label
        self.label = ctk.CTkLabel(
            self,
            text=message,
            font=("Rajdhani", 16)
        )
        self.label.grid(row=0, column=0, padx=20, pady=(30, 10), sticky="ew")

        # Indeterminate progress bar
        self.progress = ctk.CTkProgressBar(self, width=450, mode="indeterminate")
        self.progress.grid(row=1, column=0, padx=20, pady=10)
        self.progress.start()

        # Status note
        self.note = ctk.CTkLabel(
            self,
            text="This may take a moment...",
            font=("Rajdhani", 12),
            text_color=("#7eb8bb", "#7eb8bb")
        )
        self.note.grid(row=2, column=0, padx=20, pady=(0, 20))

        # Force window to appear immediately
        self.update()

    def set_message(self, message: str):
        """Update the status message.

        Args:
            message: New status message to display
        """
        self.label.configure(text=message)
        self.update_idletasks()

    def close_dialog(self):
        """Close the progress dialog and release modal grab."""
        try:
            self.progress.stop()
            self.grab_release()
            self.destroy()
        except Exception:
            # Already destroyed or other error - ignore
            pass
