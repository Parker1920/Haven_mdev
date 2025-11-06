"""
Haven Control Room - User Edition

Simplified standalone version for end users.
Features:
- JSON-only data storage
- System Entry Wizard
- Map Generator
- Photo support
- No database, no advanced features
"""
from __future__ import annotations
import sys
import os

# SET USER EDITION ENVIRONMENT VARIABLE FIRST - BEFORE ANY PROJECT IMPORTS
# This must be done before importing paths.py or any modules that depend on it
os.environ['HAVEN_USER_EDITION'] = '1'

import subprocess
import threading
from datetime import datetime
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

import customtkinter as ctk
from tkinter import messagebox, filedialog
import runpy

# Use user edition settings
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings_user import (
    JSON_DATA_PATH, LOG_DIR, PHOTOS_DIR, MAP_OUTPUT_DIR,
    PROJECT_ROOT, DATA_DIR, IS_FROZEN,
    prompt_initial_data_file, initialize_data_file,
    get_data_provider, SHOW_SYSTEM_COUNT
)

from common.progress import ProgressDialog, IndeterminateProgressDialog

# Theme colors
COLORS = {
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
    'glow': '#00ffff'
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def _setup_logging():
    logger = logging.getLogger()
    if logger.handlers:
        return
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    try:
        LOG_DIR.mkdir(exist_ok=True)
        error_logs_path = LOG_DIR / 'error_logs'
        error_logs_path.mkdir(exist_ok=True)

        ts = datetime.now().strftime('%Y-%m-%d')

        fh = RotatingFileHandler(LOG_DIR / f'control-room-{ts}.log', maxBytes=2_000_000, backupCount=5, encoding='utf-8')
        fh.setFormatter(fmt)
        fh.setLevel(logging.INFO)
        logger.addHandler(fh)

        ts_full = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        error_fh = RotatingFileHandler(error_logs_path / f'control-room-errors-{ts_full}.log', maxBytes=2_000_000, backupCount=5, encoding='utf-8')
        error_fh.setFormatter(fmt)
        error_fh.setLevel(logging.ERROR)
        logger.addHandler(error_fh)

        logger.info(f"Logging initialized. Error logs: {error_logs_path}")
    except Exception as e:
        print(f"Failed to setup logging: {e}", file=sys.stderr)


_setup_logging()


class GlassCard(ctk.CTkFrame):
    def __init__(self, parent, title: str = "", **kwargs):
        super().__init__(
            parent,
            fg_color=(COLORS['glass'], COLORS['bg_card']),
            corner_radius=16,
            border_width=1,
            border_color=(COLORS['accent_cyan'], COLORS['accent_cyan']),
            **kwargs
        )
        if title:
            lbl = ctk.CTkLabel(
                self,
                text=title,
                font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
                text_color=COLORS['accent_cyan']
            )
            lbl.pack(pady=(16, 12), padx=20, anchor="w")


class ControlRoom(ctk.CTk):
    def __init__(self):
        try:
            logging.info("Creating ControlRoom User Edition window...")
            super().__init__()
            self.title("Haven Control Room")
            self.geometry("980x700")
            self.configure(fg_color=COLORS['bg_dark'])

            # Initialize data provider
            self.data_provider = get_data_provider()

            logging.info("Building UI...")
            self._build_ui()
            logging.info("ControlRoom User Edition initialization complete.")
        except Exception as e:
            logging.error(f"Error initializing ControlRoom: {e}", exc_info=True)
            raise

    def _build_ui(self):
        sidebar = ctk.CTkFrame(self, width=280, fg_color=COLORS['glass'], corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        title = ctk.CTkLabel(sidebar, text="✨ HAVEN\nCONTROL ROOM", justify="center",
                              font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
                              text_color=COLORS['accent_cyan'])
        title.pack(pady=(32, 20))

        ctk.CTkFrame(sidebar, height=2, fg_color=COLORS['accent_cyan']).pack(fill="x", padx=20, pady=(0, 20))

        # Quick Actions section - ONLY TOP 2 BUTTONS
        quick_label = ctk.CTkLabel(sidebar, text="QUICK ACTIONS",
                                   font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                                   text_color=COLORS['text_secondary'])
        quick_label.pack(padx=20, pady=(0, 8), anchor="w")

        qa_fg = "#1e3a5f"
        qa_hover = "#2a4a7c"
        self._mk_btn(sidebar, "🛰️ Launch System Entry (Wizard)", self.launch_wizard,
                     fg=qa_fg, hover=qa_hover, text_color=COLORS['text_primary']).pack(padx=20, pady=4, fill="x")
        self._mk_btn(sidebar, "🗺️ Generate Map", self.generate_map,
                     fg=qa_fg, hover=qa_hover, text_color=COLORS['text_primary']).pack(padx=20, pady=4, fill="x")
        self._mk_btn(sidebar, "🌐 Open Latest Map", self.open_latest_map,
                     fg=qa_fg, hover=qa_hover, text_color=COLORS['text_primary']).pack(padx=20, pady=4, fill="x")

        ctk.CTkFrame(sidebar, height=1, fg_color=COLORS['text_secondary']).pack(fill="x", padx=20, pady=(12, 12))

        # Data Info section
        data_label = ctk.CTkLabel(sidebar, text="DATA INFO",
                                  font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                                  text_color=COLORS['text_secondary'])
        data_label.pack(padx=20, pady=(0, 8), anchor="w")

        self.data_indicator = ctk.CTkLabel(
            sidebar,
            text=f"📊 Data: {JSON_DATA_PATH.name}",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=COLORS['success'],
            wraplength=240,
            justify="left"
        )
        self.data_indicator.pack(padx=20, anchor="w")

        # System count indicator
        if SHOW_SYSTEM_COUNT:
            try:
                count = self.data_provider.get_total_count()
                self.count_indicator = ctk.CTkLabel(
                    sidebar,
                    text=f"Systems: {count:,}",
                    font=ctk.CTkFont(family="Segoe UI", size=10),
                    text_color=COLORS['accent_cyan']
                )
                self.count_indicator.pack(padx=20, anchor="w", pady=(4, 0))
            except Exception as e:
                logging.warning(f"Failed to get system count: {e}")

        ctk.CTkFrame(sidebar, height=1, fg_color=COLORS['text_secondary']).pack(fill="x", padx=20, pady=(12, 12))

        # File Management section
        files_label = ctk.CTkLabel(sidebar, text="FILE MANAGEMENT",
                                   font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                                   text_color=COLORS['text_secondary'])
        files_label.pack(padx=20, pady=(0, 8), anchor="w")

        self._mk_btn(sidebar, "📁 Open Data Folder", lambda: self.open_path(DATA_DIR),
                     fg="#1e3a5f", hover="#2a4a7c", text_color=COLORS['text_primary']).pack(padx=20, pady=4, fill="x")
        self._mk_btn(sidebar, "🧭 Open Logs Folder", lambda: self.open_path(LOG_DIR),
                     fg="#1e3a5f", hover="#2a4a7c", text_color=COLORS['text_primary']).pack(padx=20, pady=4, fill="x")
        self._mk_btn(sidebar, "📸 Open Photos Folder", lambda: self.open_path(PHOTOS_DIR),
                     fg="#1e3a5f", hover="#2a4a7c", text_color=COLORS['text_primary']).pack(padx=20, pady=4, fill="x")

        ctk.CTkFrame(sidebar, height=1, fg_color=COLORS['text_secondary']).pack(fill="x", padx=20, pady=(12, 12))

        # Load File section
        load_label = ctk.CTkLabel(sidebar, text="LOAD DATA",
                                  font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                                  text_color=COLORS['text_secondary'])
        load_label.pack(padx=20, pady=(0, 8), anchor="w")

        self._mk_btn(sidebar, "📥 Load Different File", self.load_file,
                     fg=COLORS['accent_purple'], hover=COLORS['accent_pink']).pack(padx=20, pady=4, fill="x")

        # Content area
        content = ctk.CTkFrame(self, fg_color=COLORS['bg_dark'])
        content.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.status_card = GlassCard(content, title="📡 System Status")
        self.status_card.pack(fill="both", expand=True)

        self.status_label = ctk.CTkLabel(self.status_card, text="Ready.",
                                         font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                                         text_color=COLORS['accent_cyan'])
        self.status_label.pack(padx=24, pady=(0, 12), anchor="w")

        self.log_box = ctk.CTkTextbox(self.status_card, height=500, corner_radius=12,
                                      border_width=1, border_color=COLORS['accent_cyan'],
                                      fg_color=COLORS['bg_dark'],
                                      text_color=COLORS['text_primary'],
                                      font=ctk.CTkFont(family="Consolas", size=12))
        self.log_box.pack(padx=24, pady=(0, 24), fill="both", expand=True)
        self._log_ui("Control Room initialized.")
        self._log_ui(f"Data file: {JSON_DATA_PATH}")

    def _mk_btn(self, parent, text, cmd, fg=COLORS['bg_card'], hover=COLORS['glass'], text_color=COLORS['text_primary']):
        return ctk.CTkButton(
            parent,
            text=text,
            command=cmd,
            height=40,
            corner_radius=10,
            fg_color=fg,
            hover_color=hover,
            text_color=text_color,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        )

    def _log(self, msg: str):
        logging.info(msg)
        self._log_ui(msg)

    def _log_ui(self, msg: str):
        self.log_box.insert('end', f"{msg}\n")
        self.log_box.see('end')
        self.status_label.configure(text=msg)

    def open_path(self, path: Path):
        try:
            if sys.platform == 'win32':
                subprocess.Popen(['explorer', str(path)])
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', str(path)])
            else:
                subprocess.Popen(['xdg-open', str(path)])
            self._log(f"Opened: {path}")
        except Exception as e:
            self._log(f"Error opening path: {e}")
            messagebox.showerror("Error", f"Could not open {path}\n{e}")

    # ----------------------- Main Functions ----------------------

    def launch_wizard(self):
        """Launch System Entry Wizard"""
        self._log("Launching System Entry Wizard...")
        try:
            import os

            if IS_FROZEN:
                # IMPORTANT: Set environment variables BEFORE importing wizard
                # so IS_USER_EDITION is set correctly at import time
                os.environ['HAVEN_USER_EDITION'] = '1'
                os.environ['HAVEN_DATA_PATH'] = str(JSON_DATA_PATH)

                # Now import and run wizard (will open as separate window)
                import system_entry_wizard
                system_entry_wizard.main()
                self._log("System Entry Wizard closed.")
            else:
                # Development mode: launch as subprocess with environment
                env = os.environ.copy()
                env['HAVEN_USER_EDITION'] = '1'
                env['HAVEN_DATA_PATH'] = str(JSON_DATA_PATH)

                wizard_path = Path(__file__).parent / "system_entry_wizard.py"
                subprocess.Popen([sys.executable, str(wizard_path)], env=env)
                self._log("System Entry Wizard launched.")
        except Exception as e:
            self._log(f"Error launching wizard: {e}")
            logging.error(f"Error launching wizard: {e}", exc_info=True)
            messagebox.showerror("Error", f"Could not launch System Entry Wizard:\n{e}")

    def generate_map(self):
        """Generate 3D map visualization"""
        self._log("Generating map...")
        try:
            # Progress bar starts automatically in __init__
            progress = IndeterminateProgressDialog(self, "Generating Map", "Creating 3D visualization...")
            
            # Ensure maps directory exists
            MAP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            map_output_path = MAP_OUTPUT_DIR / "VH-Map.html"

            def run_map_gen():
                try:
                    # Run map generator with user edition data file and output path
                    if IS_FROZEN:
                        import Beta_VH_Map
                        # Pass the user edition data file path and output path to the map generator
                        Beta_VH_Map.main(["--data-file", str(JSON_DATA_PATH), "--out", str(map_output_path)])
                    else:
                        map_script = Path(__file__).parent / "Beta_VH_Map.py"
                        subprocess.run([sys.executable, str(map_script), "--data-file", str(JSON_DATA_PATH), "--out", str(map_output_path)], check=True)

                    self.after(0, lambda: progress.close_dialog())
                    self.after(0, lambda: self._log("Map generated successfully!"))
                    self.after(0, lambda: messagebox.showinfo("Success", "Map generated successfully!\nCheck the maps folder."))
                except Exception as e:
                    self.after(0, lambda: progress.close_dialog())
                    self.after(0, lambda: self._log(f"Map generation failed: {e}"))
                    self.after(0, lambda: messagebox.showerror("Error", f"Map generation failed:\n{e}"))
                    logging.error(f"Map generation error: {e}", exc_info=True)

            threading.Thread(target=run_map_gen, daemon=True).start()

        except Exception as e:
            self._log(f"Error starting map generation: {e}")
            logging.error(f"Error starting map generation: {e}", exc_info=True)
            messagebox.showerror("Error", f"Could not start map generation:\n{e}")

    def open_latest_map(self):
        """Open the most recently generated map in browser"""
        try:
            maps_dir = MAP_OUTPUT_DIR
            if not maps_dir.exists():
                self._log("No maps folder found. Generate a map first.")
                messagebox.showinfo("No Maps", "No maps found.\n\nGenerate a map first using 'Generate Map' button.")
                return

            # Look specifically for VH-Map.html (the main galaxy map)
            main_map = maps_dir / "VH-Map.html"
            if main_map.exists():
                # Open the main map in default browser
                import webbrowser
                webbrowser.open(str(main_map))
                self._log(f"Opened map: {main_map.name}")
            else:
                # Fallback: look for any HTML file
                map_files = list(maps_dir.glob("*.html"))
                if not map_files:
                    self._log("No map files found. Generate a map first.")
                    messagebox.showinfo("No Maps", "No map files found.\n\nGenerate a map first using 'Generate Map' button.")
                    return

                # Get the most recent file
                latest_map = max(map_files, key=lambda p: p.stat().st_mtime)

                # Open in default browser
                import webbrowser
                webbrowser.open(str(latest_map))
                self._log(f"Opened map: {latest_map.name}")

        except Exception as e:
            self._log(f"Error opening map: {e}")
            logging.error(f"Error opening map: {e}", exc_info=True)
            messagebox.showerror("Error", f"Could not open map:\n{e}")

    def load_file(self):
        """Allow user to load a different JSON data file"""
        try:
            filepath = filedialog.askopenfilename(
                title="Select JSON Data File",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialdir=PROJECT_ROOT
            )

            if not filepath:
                return

            source_path = Path(filepath)

            # Ask if they want to replace current data
            if JSON_DATA_PATH.exists():
                result = messagebox.askyesnocancel(
                    "Load File",
                    f"Load '{source_path.name}' and replace current data?\n\n"
                    "• YES - Replace current data (backup will be created)\n"
                    "• NO - Cancel"
                )
                if not result:
                    return

            # Create backup of current data
            if JSON_DATA_PATH.exists():
                import shutil
                backup_path = JSON_DATA_PATH.with_suffix('.json.bak')
                shutil.copy2(JSON_DATA_PATH, backup_path)
                self._log(f"Backup created: {backup_path.name}")

            # Copy selected file to data.json
            if initialize_data_file(source_path):
                self._log(f"Loaded data from: {source_path.name}")
                messagebox.showinfo("Success", f"Data loaded from {source_path.name}\n\nPlease restart the application.")
            else:
                self._log(f"Failed to load file: {source_path.name}")
                messagebox.showerror("Error", f"Could not load {source_path.name}\n\nPlease check the file format.")

        except Exception as e:
            self._log(f"Error loading file: {e}")
            logging.error(f"Error loading file: {e}", exc_info=True)
            messagebox.showerror("Error", f"Could not load file:\n{e}")


def main():
    """Main entry point for user edition"""
    # Environment variable already set at module level

    logging.info("=" * 70)
    logging.info("HAVEN CONTROL ROOM - USER EDITION")
    logging.info("=" * 70)
    logging.info(f"Mode: {'FROZEN EXE' if IS_FROZEN else 'DEVELOPMENT'}")
    logging.info(f"Data Path: {JSON_DATA_PATH}")

    # Check if this is first run or needs file selection
    if not JSON_DATA_PATH.exists() or JSON_DATA_PATH.stat().st_size < 100:
        logging.info("First run detected - prompting for initial data file")

        try:
            source_path = prompt_initial_data_file()

            if source_path is None:
                logging.info("User cancelled startup - exiting")
                return

            if not initialize_data_file(source_path):
                import tkinter as tk
                from tkinter import messagebox
                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                messagebox.showerror("Error", "Failed to initialize data file.\n\nApplication will exit.")
                root.destroy()
                return

            logging.info(f"Initialized with: {source_path}")
        except Exception as e:
            logging.error(f"Error during startup file selection: {e}", exc_info=True)
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            messagebox.showerror("Startup Error", f"Error during startup:\n{e}\n\nApplication will exit.")
            root.destroy()
            return

    # Launch Control Room
    try:
        app = ControlRoom()
        app.mainloop()
    except Exception as e:
        logging.error(f"Error launching Control Room: {e}", exc_info=True)
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        messagebox.showerror("Application Error", f"Error starting Control Room:\n{e}\n\nCheck logs for details.")
        root.destroy()


if __name__ == "__main__":
    main()
