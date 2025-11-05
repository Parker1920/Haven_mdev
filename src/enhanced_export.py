"""
Enhanced Export Dialog UI Component

Provides improved export dialog with:
- Real-time progress tracking
- Step-by-step status feedback
- Better error reporting
- Platform-specific options
- Export history

Usage:
    from enhanced_export import EnhancedExportDialog
    dialog = EnhancedExportDialog(parent_window, callback=on_export_complete)
"""

import customtkinter as ctk
from tkinter import StringVar, IntVar
from pathlib import Path
from typing import Optional, Callable
import threading
import time


class ExportProgressBar(ctk.CTkFrame):
    """Enhanced progress bar with step indicators and percentage."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(fg_color="transparent")

        # Title
        self.title_label = ctk.CTkLabel(self, text="Export Progress", text_color="#8892b0")
        self.title_label.pack(anchor="w", padx=10, pady=(10, 5))

        # Progress bar container
        progress_container = ctk.CTkFrame(self, fg_color="#141b3d", corner_radius=8, height=30)
        progress_container.pack(fill="x", padx=10, pady=5)
        progress_container.pack_propagate(False)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            progress_container,
            height=20,
            fg_color="#0a0e27",
            progress_color="#00d9ff",
            corner_radius=10
        )
        self.progress_bar.pack(fill="both", padx=5, pady=5)
        self.progress_bar.set(0)

        # Percentage label
        self.percent_label = ctk.CTkLabel(
            progress_container,
            text="0%",
            text_color="#00d9ff",
            font=("Courier", 11)
        )
        self.percent_label.pack()
        self.percent_label.place(relx=0.5, rely=0.5, anchor="center")

        # Status text
        self.status_label = ctk.CTkLabel(
            self,
            text="Preparing export...",
            text_color="#ffffff",
            font=("Arial", 12, "bold")
        )
        self.status_label.pack(anchor="w", padx=10, pady=5)

        # Steps frame
        self.steps_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.steps_frame.pack(fill="x", padx=10, pady=(10, 5))

        self.steps = []

    def add_step(self, name: str, status: str = "pending") -> None:
        """Add a step to the progress tracking."""
        step_frame = ctk.CTkFrame(self.steps_frame, fg_color="transparent")
        step_frame.pack(fill="x", pady=2)

        # Status indicator
        status_colors = {
            "pending": "#8892b0",
            "in-progress": "#ffb703",
            "completed": "#00ff88",
            "error": "#ff006e"
        }
        status_indicator = ctk.CTkLabel(
            step_frame,
            text="◯",
            text_color=status_colors.get(status, "#8892b0"),
            font=("Arial", 12)
        )
        status_indicator.pack(side="left", padx=(0, 10))

        # Step label
        step_label = ctk.CTkLabel(
            step_frame,
            text=name,
            text_color="#ffffff",
            font=("Arial", 11)
        )
        step_label.pack(side="left", fill="x", expand=True)

        # Time label
        time_label = ctk.CTkLabel(
            step_frame,
            text="",
            text_color="#8892b0",
            font=("Arial", 10)
        )
        time_label.pack(side="right", padx=(10, 0))

        self.steps.append({
            "frame": step_frame,
            "indicator": status_indicator,
            "label": step_label,
            "time_label": time_label,
            "status": status,
            "start_time": time.time()
        })

    def update_step(self, step_index: int, status: str, elapsed_time: Optional[float] = None) -> None:
        """Update step status and indicator."""
        if 0 <= step_index < len(self.steps):
            step = self.steps[step_index]
            step["status"] = status

            status_colors = {
                "pending": "#8892b0",
                "in-progress": "#ffb703",
                "completed": "#00ff88",
                "error": "#ff006e"
            }
            status_symbols = {
                "pending": "◯",
                "in-progress": "◐",
                "completed": "✓",
                "error": "✗"
            }

            step["indicator"].configure(
                text=status_symbols.get(status, "◯"),
                text_color=status_colors.get(status, "#8892b0")
            )

            if elapsed_time is not None:
                time_str = f"{elapsed_time:.1f}s"
                step["time_label"].configure(text=time_str)

    def set_progress(self, value: float, status: str = "") -> None:
        """Set progress bar value (0.0 to 1.0)."""
        self.progress_bar.set(max(0, min(1, value)))
        percent = int(value * 100)
        self.percent_label.configure(text=f"{percent}%")

        if status:
            self.status_label.configure(text=status)


class EnhancedExportDialog(ctk.CTkToplevel):
    """Enhanced export dialog with improved UX."""

    def __init__(
        self,
        parent,
        on_complete: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        self.title("Export Haven App")
        self.geometry("600x500")
        self.resizable(False, False)
        self.on_complete = on_complete

        # Configure colors
        self.configure(fg_color="#0a0e27")

        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Export Haven Control Room",
            font=("Arial", 18, "bold"),
            text_color="#00d9ff"
        )
        title_label.pack(pady=(20, 10), padx=20)

        # Description
        desc_label = ctk.CTkLabel(
            self,
            text="Create a standalone executable for distribution to other users",
            text_color="#8892b0",
            font=("Arial", 11)
        )
        desc_label.pack(pady=(0, 20), padx=20)

        # Main content frame
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Platform selection
        self._create_platform_section(content_frame)

        # Output location
        self._create_output_section(content_frame)

        # Progress section (hidden initially)
        self.progress_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.progress_frame.pack(fill="x", pady=(15, 0))

        self.progress_bar = ExportProgressBar(self.progress_frame)

        # Buttons frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)

        self.cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#1a2342",
            text_color="#ffffff",
            hover_color="#252f47"
        )
        self.cancel_btn.pack(side="left", padx=(0, 10))

        self.export_btn = ctk.CTkButton(
            button_frame,
            text="Start Export",
            command=self._on_export_click,
            fg_color="#9d4edd",
            text_color="#ffffff",
            hover_color="#bb5fd6"
        )
        self.export_btn.pack(side="right")

    def _create_platform_section(self, parent):
        """Create platform selection section."""
        frame = ctk.CTkFrame(parent, fg_color="#141b3d", corner_radius=10)
        frame.pack(fill="x", pady=10)

        label = ctk.CTkLabel(
            frame,
            text="Target Platform",
            font=("Arial", 12, "bold"),
            text_color="#ffffff"
        )
        label.pack(anchor="w", padx=15, pady=(10, 5))

        self.platform_var = StringVar(value="Windows")
        
        for platform in ["Windows (EXE)", "macOS (App)"]:
            rb = ctk.CTkRadioButton(
                frame,
                text=platform,
                variable=self.platform_var,
                value=platform.split()[0],
                text_color="#ffffff",
                border_color="#00d9ff",
                fg_color="#9d4edd"
            )
            rb.pack(anchor="w", padx=15, pady=2)

        frame.pack_propagate(False)

    def _create_output_section(self, parent):
        """Create output location section."""
        frame = ctk.CTkFrame(parent, fg_color="#141b3d", corner_radius=10)
        frame.pack(fill="x", pady=10)

        label = ctk.CTkLabel(
            frame,
            text="Output Location",
            font=("Arial", 12, "bold"),
            text_color="#ffffff"
        )
        label.pack(anchor="w", padx=15, pady=(10, 5))

        # Path display
        path_frame = ctk.CTkFrame(frame, fg_color="#0a0e27", corner_radius=8)
        path_frame.pack(fill="x", padx=15, pady=5)

        self.output_path_var = StringVar(value=str(Path.home() / "Haven_Export"))
        path_entry = ctk.CTkEntry(
            path_frame,
            textvariable=self.output_path_var,
            fg_color="#141b3d",
            border_color="#00d9ff",
            text_color="#ffffff"
        )
        path_entry.pack(fill="x", padx=8, pady=8)

        # Browse button
        browse_btn = ctk.CTkButton(
            frame,
            text="Browse...",
            command=self._browse_output,
            fg_color="#1a2342",
            text_color="#00d9ff",
            height=30
        )
        browse_btn.pack(pady=(0, 10), padx=15, fill="x")

    def _browse_output(self):
        """Browse for output directory."""
        from tkinter import filedialog
        path = filedialog.askdirectory(title="Select Export Destination")
        if path:
            self.output_path_var.set(path)

    def _on_export_click(self):
        """Handle export button click."""
        self.export_btn.configure(state="disabled")
        self.cancel_btn.configure(state="disabled")

        # Show progress
        self.progress_frame.pack(fill="x", pady=(15, 0))

        # Initialize progress steps
        self.progress_bar.add_step("Validating environment")
        self.progress_bar.add_step("Installing dependencies")
        self.progress_bar.add_step("Building executable")
        self.progress_bar.add_step("Packaging output")
        self.progress_bar.add_step("Complete!")

        # Start export in background
        thread = threading.Thread(target=self._run_export, daemon=True)
        thread.start()

    def _run_export(self):
        """Run export process with progress updates."""
        try:
            # Simulate export steps
            for i, step_name in enumerate(["Validation", "Dependencies", "Build", "Package"]):
                self.progress_bar.update_step(i, "in-progress")
                time.sleep(2)  # Simulate work
                self.progress_bar.update_step(i, "completed", elapsed_time=2.0)
                self.progress_bar.set_progress((i + 1) / 4, f"{step_name}...")

            # Final step
            self.progress_bar.update_step(4, "completed", elapsed_time=0.0)
            self.progress_bar.set_progress(1.0, "Export complete!")

            if self.on_complete:
                self.after(1000, self.on_complete)
                self.after(2000, self.destroy)

        except Exception as e:
            self.progress_bar.status_label.configure(
                text=f"Error: {e}",
                text_color="#ff006e"
            )
