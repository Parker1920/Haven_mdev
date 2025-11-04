from __future__ import annotations
import sys
import subprocess
import threading
import shlex
from datetime import datetime
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

import customtkinter as ctk
from tkinter import messagebox, filedialog
import runpy
import argparse

from common.paths import project_root, data_dir, logs_dir, dist_dir, config_dir, docs_dir, src_dir

# Theme and colors (load from themes/haven_theme.json if available)
THEMES = {
    "Dark": ("dark", "blue"),
    "Light": ("light", "blue"),
    "Cosmic": ("dark", "green"),
    "Haven (Cyan)": ("dark", "blue"),
}

def _load_theme_colors():
    try:
        theme_path = project_root() / 'themes' / 'haven_theme.json'
        if theme_path.exists():
            import json
            obj = json.loads(theme_path.read_text(encoding='utf-8'))
            colors = obj.get('colors', {})
            return {
                'bg_dark': colors.get('bg_dark', '#0a0e27'),
                'bg_card': colors.get('bg_card', '#141b3d'),
                'accent_cyan': colors.get('accent_cyan', '#00d9ff'),
                'accent_purple': colors.get('accent_purple', '#9d4edd'),
                'accent_pink': colors.get('accent_pink', '#ff006e'),
                'text_primary': colors.get('text_primary', '#ffffff'),
                'text_secondary': colors.get('text_secondary', '#8892b0'),
                'success': colors.get('success', '#00ff88'),
                'warning': colors.get('warning', '#ffb703'),
                'error': colors.get('error', '#ff006e'),
                'glass': colors.get('glass', '#1a2342'),
                'glow': colors.get('glow', '#00ffff'),
            }
    except Exception:
        pass
    return {
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

COLORS = _load_theme_colors()

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
        logs_dir().mkdir(exist_ok=True)
        ts = datetime.now().strftime('%Y-%m-%d')
        fh = RotatingFileHandler(logs_dir() / f'control-room-{ts}.log', maxBytes=2_000_000, backupCount=5, encoding='utf-8')
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    except Exception:
        pass


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
        super().__init__()
        self.title("Haven Control Room")
        self.geometry("980x700")
        self.configure(fg_color=COLORS['bg_dark'])
        self._frozen = getattr(sys, 'frozen', False)
        self._build_ui()

    # -------------------------- UI --------------------------
    def _build_ui(self):
        sidebar = ctk.CTkFrame(self, width=280, fg_color=COLORS['glass'], corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        title = ctk.CTkLabel(sidebar, text="✨ HAVEN\nCONTROL ROOM", justify="center",
                              font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
                              text_color=COLORS['accent_cyan'])
        title.pack(pady=(32, 20))

        ctk.CTkFrame(sidebar, height=2, fg_color=COLORS['accent_cyan']).pack(fill="x", padx=20, pady=(0, 20))

        # Quick Actions section
        quick_label = ctk.CTkLabel(sidebar, text="QUICK ACTIONS",
                                   font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                                   text_color=COLORS['text_secondary'])
        quick_label.pack(padx=20, pady=(0, 8), anchor="w")

        # Use high-contrast dark buttons with light text for readability
        qa_fg = "#1e3a5f"      # deep blue
        qa_hover = "#2a4a7c"   # lighter blue
        self._mk_btn(sidebar, "🛰️ Launch System Entry (Wizard)", self.launch_gui,
                     fg=qa_fg, hover=qa_hover, text_color=COLORS['text_primary']).pack(padx=20, pady=4, fill="x")
        self._mk_btn(sidebar, "🗺️ Generate Map", self.generate_map,
                     fg=qa_fg, hover=qa_hover, text_color=COLORS['text_primary']).pack(padx=20, pady=4, fill="x")
        self._mk_btn(sidebar, "🌐 Open Latest Map", self.open_latest_map,
                     fg=qa_fg, hover=qa_hover, text_color=COLORS['text_primary']).pack(padx=20, pady=4, fill="x")

        ctk.CTkFrame(sidebar, height=1, fg_color=COLORS['text_secondary']).pack(fill="x", padx=20, pady=(12, 12))

        # File Management section
        files_label = ctk.CTkLabel(sidebar, text="FILE MANAGEMENT",
                                   font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                                   text_color=COLORS['text_secondary'])
        files_label.pack(padx=20, pady=(0, 8), anchor="w")

        self._mk_btn(sidebar, "📁 Data Folder", lambda: self.open_path(data_dir()),
                     fg="#1e3a5f", hover="#2a4a7c", text_color=COLORS['text_primary']).pack(padx=20, pady=4, fill="x")
        self._mk_btn(sidebar, "🧭 Logs Folder", lambda: self.open_path(logs_dir()),
                     fg="#1e3a5f", hover="#2a4a7c", text_color=COLORS['text_primary']).pack(padx=20, pady=4, fill="x")
        self._mk_btn(sidebar, "📖 Documentation", lambda: self.open_path(docs_dir()),
                     fg="#1e3a5f", hover="#2a4a7c", text_color=COLORS['text_primary']).pack(padx=20, pady=4, fill="x")

        ctk.CTkFrame(sidebar, height=1, fg_color=COLORS['text_secondary']).pack(fill="x", padx=20, pady=(12, 12))

        # Advanced Tools section - hidden in standalone EXE
        if not self._frozen:
            advanced_label = ctk.CTkLabel(sidebar, text="ADVANCED TOOLS",
                                          font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                                          text_color=COLORS['text_secondary'])
            advanced_label.pack(padx=20, pady=(0, 8), anchor="w")

            self._mk_btn(sidebar, "🔧 Update Dependencies", self.update_deps,
                         fg=COLORS['accent_purple'], hover=COLORS['accent_pink']).pack(padx=20, pady=4, fill="x")
            # Export button opens a small modal to choose platform and output folder
            self._mk_btn(sidebar, "📦 Export App (EXE/.app)", self.open_export_dialog,
                         fg=COLORS['warning'], hover="#cc9602").pack(padx=20, pady=4, fill="x")

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

    # ----------------------- Utilities ----------------------
    def _log(self, msg: str):
        logging.info(msg)
        self._log_ui(msg)

    def _log_ui(self, msg: str):
        self.log_box.insert('end', f"{msg}\n")
        self.log_box.see('end')
        self.status_label.configure(text=msg)

    def _confirm(self, title: str, msg: str) -> bool:
        return messagebox.askyesno(title, msg)

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
            self._log(f"Failed to open path: {e}")

    def _run_bg(self, target, *args, **kwargs):
        t = threading.Thread(target=target, args=args, kwargs=kwargs, daemon=True)
        t.start()
        return t

    # ----------------------- Actions ------------------------
    def launch_gui(self):
        self._log("Launching System Entry Wizard…")
        def run():
            try:
                if self._frozen:
                    # Relaunch the same EXE with a different entry to isolate Tk roots
                    cmd = [sys.executable, '--entry', 'system']
                    subprocess.Popen(cmd, cwd=str(project_root()))
                else:
                    app = src_dir() / 'system_entry_wizard.py'
                    if sys.platform == 'darwin':
                        # macOS: Use 'open' command with pythonw to launch GUI properly
                        # Create a temporary shell script to run the wizard
                        import tempfile
                        script_content = f'''#!/bin/bash
cd "{project_root()}"
"{sys.executable}" "{app}"
'''
                        fd, script_path = tempfile.mkstemp(suffix='.command', text=True)
                        with open(fd, 'w') as f:
                            f.write(script_content)
                        import os
                        os.chmod(script_path, 0o755)
                        subprocess.Popen(['open', '-a', 'Terminal', script_path])
                    else:
                        cmd = [sys.executable, str(app)]
                        subprocess.Popen(cmd, cwd=str(project_root()))
                self._log("System Entry Wizard launched.")
            except Exception as e:
                self._log(f"Launch failed: {e}")
        self._run_bg(run)

    def generate_map(self):
        self._log("Generating map…")
        def run():
            try:
                ts = datetime.now().strftime('%Y-%m-%d_%H%M%S')
                logs_dir().mkdir(exist_ok=True)
                if self._frozen:
                    # Spawn same EXE to run the map generator entry
                    with open(logs_dir() / f'map-gen-{ts}.log', 'w', encoding='utf-8') as lf:
                        cmd = [sys.executable, '--entry', 'map', '--no-open']
                        proc = subprocess.run(cmd, cwd=str(project_root()), text=True, stdout=lf, stderr=lf)
                else:
                    map_script = src_dir() / 'Beta_VH_Map.py'
                    with open(logs_dir() / f'map-gen-{ts}.log', 'w', encoding='utf-8') as lf:
                        cmd = [sys.executable, str(map_script), '--no-open']
                        proc = subprocess.run(cmd, cwd=str(project_root()), text=True, stdout=lf, stderr=lf)
                if proc.returncode == 0:
                    self._log("Map generation complete.")
                else:
                    self._log(f"Map generation failed (exit {proc.returncode}). See logs.")
            except Exception as e:
                self._log(f"Map generation error: {e}")
        self._run_bg(run)

    def open_latest_map(self):
        try:
            dist = dist_dir()
            if not dist.exists():
                self._log("No dist folder yet.")
                return
            # Prefer VH-Map.html
            vh = dist / 'VH-Map.html'
            target = vh if vh.exists() else None
            if not target:
                # fallback to newest html file
                htmls = sorted(dist.glob('*.html'), key=lambda p: p.stat().st_mtime, reverse=True)
                target = htmls[0] if htmls else None
            if not target:
                self._log("No map HTML found in dist/.")
                return
            if sys.platform == 'win32':
                subprocess.Popen(['cmd', '/c', 'start', '', str(target)])
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', str(target)])
            else:
                subprocess.Popen(['xdg-open', str(target)])
            self._log(f"Opened: {target.name}")
        except Exception as e:
            self._log(f"Failed to open map: {e}")

    def update_deps(self):
        if self._frozen:
            self._log("Dependency updates are unavailable in the standalone EXE.")
            return
        if not self._confirm("Update Dependencies", "Run pip install -r config/requirements.txt?\nThis may take a few minutes."):
            return
        self._log("Updating dependencies…")
        def run():
            try:
                req = config_dir() / 'requirements.txt'
                cmd = [sys.executable, '-m', 'pip', 'install', '-r', str(req)]
                ts = datetime.now().strftime('%Y-%m-%d_%H%M%S')
                with open(logs_dir() / f'update-deps-{ts}.log', 'w', encoding='utf-8') as lf:
                    proc = subprocess.run(cmd, cwd=str(project_root()), text=True, stdout=lf, stderr=lf)
                if proc.returncode == 0:
                    self._log("Dependencies updated.")
                else:
                    self._log(f"Dependency update failed (exit {proc.returncode}). See logs.")
            except Exception as e:
                self._log(f"Update error: {e}")
        self._run_bg(run)

    def open_export_dialog(self):
        if self._frozen:
            self._log("Export is not available from within the standalone app. Run from source to export.")
            return
        ExportDialog(self)

    def _export_windows(self, output_dir: Path, zip_after: bool = True):
        self._log(f"Exporting Windows EXE to: {output_dir}")
        def run():
            try:
                name = 'HavenControlRoom'
                script = src_dir() / 'control_room.py'
                icon = (config_dir() / 'icons' / 'haven.ico')
                spec_dir = config_dir() / 'pyinstaller'
                try:
                    spec_dir.mkdir(parents=True, exist_ok=True)
                except Exception:
                    pass
                # Use a temp work path outside OneDrive to avoid file locking
                import tempfile, shutil
                workpath = Path(tempfile.gettempdir()) / 'haven_build_win'
                try:
                    if workpath.exists():
                        shutil.rmtree(workpath, ignore_errors=True)
                except Exception:
                    pass
                # Best effort: remove repo build folder if present
                try:
                    repo_build = project_root() / 'build'
                    if repo_build.exists():
                        shutil.rmtree(repo_build, ignore_errors=True)
                except Exception:
                    pass
                # Ensure output dir exists and direct distpath there
                output_dir.mkdir(parents=True, exist_ok=True)
                # Build command with hidden imports for packaged entries
                cmd = [
                    sys.executable, '-m', 'PyInstaller',
                    '--noconfirm', '--clean', '--windowed', '--onefile',
                    '--name', name,
                    '--specpath', str(spec_dir),
                    '--workpath', str(workpath),
                    '--distpath', str(output_dir),
                    '--hidden-import', 'system_entry_wizard',
                    '--hidden-import', 'Beta_VH_Map',
                    str(script)
                ]
                if icon.exists():
                    cmd[ cmd.index('--onefile')+1:cmd.index('--onefile')+1 ] = ['--icon', str(icon)]
                ts = datetime.now().strftime('%Y-%m-%d_%H%M%S')
                build_log = logs_dir() / f'export-windows-{ts}.log'
                with open(build_log, 'w', encoding='utf-8') as lf:
                    proc = subprocess.run(cmd, cwd=str(project_root()), text=True, stdout=lf, stderr=lf)
                if proc.returncode != 0:
                    self._log(f"Windows export failed (exit {proc.returncode}). See {build_log.name}")
                    return
                exe = output_dir / f'{name}.exe'
                if not exe.exists():
                    self._log("Build finished, but EXE not found. See logs.")
                    return
                # Optional ZIP with instructions for email
                if zip_after:
                    import shutil, tempfile
                    readme_text = (
                        "Haven Control Room (Windows)\r\n\r\n"
                        "Run: Double-click HavenControlRoom.exe\r\n"
                        "Notes: Windows may show a SmartScreen prompt. Click 'More info' > 'Run anyway'.\r\n"
                    )
                    tmpdir = Path(tempfile.mkdtemp())
                    (tmpdir / 'HavenControlRoom.exe').write_bytes(exe.read_bytes())
                    (tmpdir / 'README.txt').write_text(readme_text, encoding='utf-8')
                    zip_path = output_dir / f'HavenControlRoom_Windows_{ts}.zip'
                    shutil.make_archive(str(zip_path.with_suffix('')), 'zip', str(tmpdir))
                self._log(f"Windows export complete: {exe}")
            except Exception as e:
                self._log(f"Windows export error: {e}")
        self._run_bg(run)

    def _export_macos(self, output_dir: Path):
        # Building macOS app requires running on macOS
        if sys.platform != 'darwin':
            self._log("Cannot build macOS app on this OS. Generating a Mac Build Kit ZIP with instructions.")
            def run():
                try:
                    import tempfile, shutil
                    ts = datetime.now().strftime('%Y-%m-%d_%H%M%S')
                    kit_dir = Path(tempfile.mkdtemp()) / 'Haven_Mac_BuildKit'
                    kit_dir.mkdir(parents=True, exist_ok=True)
                    # Instructions
                    instr = (
                        "# Haven Mac Build Kit\n\n"
                        "Requirements: macOS with Python 3.11+, pip, and PyInstaller installed.\n\n"
                        "Build steps:\n"
                        "1) python3 -m pip install --upgrade pip\n"
                        "2) python3 -m pip install pyinstaller\n"
                        "3) python3 -m PyInstaller --noconfirm --clean --windowed --onefile \n"
                        "   --name HavenControlRoom --hidden-import system_entry_wizard --hidden-import Beta_VH_Map \n"
                        "   src/control_room.py\n\n"
                        "Output: dist/HavenControlRoom (macOS app).\n"
                    )
                    (kit_dir / 'MAC_BUILD_INSTRUCTIONS.md').write_text(instr, encoding='utf-8')
                    # Include minimal project needed to build
                    root = project_root()
                    # Copy src, config (icons), and a tiny README
                    for folder in ('src', 'config'):
                        src_path = root / folder
                        if src_path.exists():
                            shutil.copytree(src_path, kit_dir / folder, dirs_exist_ok=True)
                    (kit_dir / 'README.txt').write_text('Use MAC_BUILD_INSTRUCTIONS.md to build the macOS app.', encoding='utf-8')
                    output_dir.mkdir(parents=True, exist_ok=True)
                    zip_path = output_dir / f'HavenControlRoom_Mac_BuildKit_{ts}.zip'
                    shutil.make_archive(str(zip_path.with_suffix('')), 'zip', str(kit_dir))
                    self._log(f"Mac Build Kit created: {zip_path}")
                except Exception as e:
                    self._log(f"Mac export error: {e}")
            self._run_bg(run)
            return
        else:
            # On macOS, attempt to build the app
            self._log(f"Exporting macOS app to: {output_dir}")
            def run():
                try:
                    name = 'HavenControlRoom'
                    script = src_dir() / 'control_room.py'
                    icon = (config_dir() / 'icons' / 'haven.icns')
                    spec_dir = config_dir() / 'pyinstaller'
                    try:
                        spec_dir.mkdir(parents=True, exist_ok=True)
                    except Exception:
                        pass
                    import tempfile, shutil
                    workpath = Path(tempfile.gettempdir()) / 'haven_build_mac'
                    try:
                        if workpath.exists():
                            shutil.rmtree(workpath, ignore_errors=True)
                    except Exception:
                        pass
                    output_dir.mkdir(parents=True, exist_ok=True)
                    cmd = [
                        sys.executable, '-m', 'PyInstaller',
                        '--noconfirm', '--clean', '--windowed', '--onefile',
                        '--name', name,
                        '--specpath', str(spec_dir),
                        '--workpath', str(workpath),
                        '--distpath', str(output_dir),
                        '--hidden-import', 'system_entry_wizard',
                        '--hidden-import', 'Beta_VH_Map',
                        str(script)
                    ]
                    if icon.exists():
                        cmd[ cmd.index('--onefile')+1:cmd.index('--onefile')+1 ] = ['--icon', str(icon)]
                    ts = datetime.now().strftime('%Y-%m-%d_%H%M%S')
                    build_log = logs_dir() / f'export-macos-{ts}.log'
                    with open(build_log, 'w', encoding='utf-8') as lf:
                        proc = subprocess.run(cmd, cwd=str(project_root()), text=True, stdout=lf, stderr=lf)
                    if proc.returncode != 0:
                        self._log(f"macOS export failed (exit {proc.returncode}). See {build_log.name}")
                        return
                    app = output_dir / name
                    self._log(f"macOS export complete: {app}")
                except Exception as e:
                    self._log(f"macOS export error: {e}")
            self._run_bg(run)

    # iOS PWA export removed - archived in Archive-Dump
    # Use Haven_Mobile_Map.html instead (located in dist/ folder)


class ExportDialog(ctk.CTkToplevel):
    def __init__(self, parent: ControlRoom):
        super().__init__(parent)
        self.title("Export Application")
        self.geometry("480x260")
        self.configure(fg_color=COLORS['bg_card'])
        self.parent = parent
        self.resizable(False, False)
        self.grab_set()

        ctk.CTkLabel(self, text="Choose platform and output folder:",
                     font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                     text_color=COLORS['text_primary']).pack(pady=(20,10))

        self.platform_var = ctk.StringVar(value='Windows')
        options = ctk.CTkOptionMenu(
            self,
            values=['Windows', 'macOS'],
            variable=self.platform_var,
            fg_color=COLORS['glass'],
            button_color=COLORS['accent_cyan'],
            text_color=COLORS['text_primary']
        )
        options.pack(pady=6)

        path_frame = ctk.CTkFrame(self, fg_color='transparent')
        path_frame.pack(fill='x', padx=20, pady=10)
        self.path_var = ctk.StringVar(value=str(dist_dir()))
        entry = ctk.CTkEntry(path_frame, textvariable=self.path_var, width=320)
        entry.pack(side='left', padx=(0,10))
        browse = ctk.CTkButton(
            path_frame,
            text='Browse…',
            command=self._pick_dir,
            fg_color=COLORS['accent_cyan'],
            text_color=COLORS['bg_dark']
        )
        browse.pack(side='left')

        btns = ctk.CTkFrame(self, fg_color='transparent')
        btns.pack(pady=20)
        ctk.CTkButton(btns, text='Cancel', command=self.destroy, width=120,
                      fg_color=COLORS['glass']).pack(side='left', padx=10)
        ctk.CTkButton(btns, text='Export', command=self._export, width=160,
                      fg_color=COLORS['warning']).pack(side='left', padx=10)

    def _pick_dir(self):
        d = filedialog.askdirectory(title='Choose export output folder')
        if d:
            self.path_var.set(d)

    def _export(self):
        out = Path(self.path_var.get()).expanduser()
        platform = self.platform_var.get()
        if platform == 'Windows':
            self.parent._export_windows(out, zip_after=True)
        elif platform == 'macOS':
            self.parent._export_macos(out)
        self.destroy()


def main():
    # Support dispatching alternate entries when frozen
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--entry', choices=['control', 'system', 'map'])
    parser.add_argument('--no-open', action='store_true')
    args, unknown = parser.parse_known_args()

    entry = args.entry or 'control'
    if entry == 'system':
        # Run the System Entry UI as a separate process entrypoint
        # Use runpy to invoke module as __main__
        runpy.run_module('system_entry_wizard', run_name='__main__')
        return
    if entry == 'map':
        # Forward args to map generator
        sys.argv = ['Beta_VH_Map.py'] + (['--no-open'] if args.no_open else [])
        runpy.run_module('Beta_VH_Map', run_name='__main__')
        return
    # Default: Control Room UI
    app = ControlRoom()
    app.mainloop()


if __name__ == '__main__':
    main()
