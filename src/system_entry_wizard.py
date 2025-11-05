"""
Haven System Entry - Two-Page Wizard with Planet/Moon Editors
Complete star system entry with nested planets and moons
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
import subprocess
import customtkinter as ctk
from tkinter import messagebox, StringVar, filedialog
import threading
import time
import uuid
import logging
import sys
from logging.handlers import RotatingFileHandler

# Theme setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

from common.paths import data_path, logs_dir, project_root
from common.file_lock import FileLock
from common.validation import validate_system_data, validate_coordinates

# Phase 3: Database integration imports
# Ensure project root is in sys.path so config/ can be imported
_proj_root = project_root()
if str(_proj_root) not in sys.path:
    sys.path.insert(0, str(_proj_root))

try:
    from config.settings import (
        USE_DATABASE, get_data_provider, get_current_backend,
        SHOW_BACKEND_STATUS, SHOW_SYSTEM_COUNT
    )
    PHASE3_ENABLED = True
except ImportError as e:
    # Fallback if Phase 3 modules not available
    PHASE3_ENABLED = False
    USE_DATABASE = False
    print(f"[WARN] Phase 3 disabled - config.settings import failed: {e}", file=sys.stderr)

# Settings
SETTINGS_FILE = project_root() / "settings.json"

def load_settings():
    try:
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        logging.exception("Failed to load settings")
    return {"theme": "Dark"}

def save_settings(data: dict):
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception:
        logging.exception("Failed to save settings")

# Apply saved theme
_settings = load_settings()
_theme = _settings.get("theme", "Dark")
THEMES = {"Dark": ("dark", "blue"), "Light": ("light", "blue"), "Cosmic": ("dark", "green"), "Haven (Cyan)": ("dark", "blue")}
if _theme in THEMES:
    mode, color = THEMES[_theme]
    ctk.set_appearance_mode(mode)
    ctk.set_default_color_theme(color)

def _load_theme_colors():
    try:
        theme_path = project_root() / 'themes' / 'haven_theme.json'
        if theme_path.exists():
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

# Color palette
COLORS = _load_theme_colors()

# Logging setup
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
        fh = RotatingFileHandler(logs_dir() / f'gui-{ts}.log', maxBytes=2_000_000, backupCount=5, encoding='utf-8')
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    except Exception:
        pass

_setup_logging()

sys.excepthook = lambda exc_type, exc, tb: logging.exception("Uncaught exception", exc_info=(exc_type, exc, tb))


class GlassCard(ctk.CTkFrame):
    """Glassmorphic card"""
    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, fg_color=(COLORS['glass'], COLORS['bg_card']), corner_radius=16,
                         border_width=1, border_color=(COLORS['accent_cyan'], COLORS['accent_cyan']), **kwargs)
        if title:
            self.title_label = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
                                            text_color=COLORS['accent_cyan'])
            self.title_label.pack(pady=(16, 12), padx=20, anchor="w")
        self.bind("<Enter>", lambda e: self.configure(border_color=COLORS['glow']))
        self.bind("<Leave>", lambda e: self.configure(border_color=COLORS['accent_cyan']))


class ModernEntry(ctk.CTkFrame):
    """Entry with validation"""
    def __init__(self, parent, label="", placeholder="", validate_type=None, **kwargs):
        super().__init__(parent, fg_color="transparent")
        self.validate_type = validate_type
        self.is_valid = True
        
        self.label = ctk.CTkLabel(self, text=label, font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                  text_color=COLORS['text_secondary'])
        self.label.pack(anchor="w", padx=4, pady=(0, 4))
        
        self.entry = ctk.CTkEntry(self, placeholder_text=placeholder, height=45, corner_radius=10, border_width=2,
                                  border_color=COLORS['accent_cyan'], fg_color=COLORS['bg_card'],
                                  font=ctk.CTkFont(family="Segoe UI", size=13), **kwargs)
        self.entry.pack(fill="x", padx=4)
        
        self.error_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(family="Segoe UI", size=11),
                                        text_color=COLORS['error'])
        
        self.entry.bind('<KeyRelease>', self.validate)
        self.entry.bind('<FocusOut>', self.validate)

    def validate(self, event=None):
        value = self.get().strip()
        error_msg = ""
        
        if self.label.cget('text').endswith('*') and not value:
            error_msg = "This field is required."
            self.is_valid = False
        elif self.validate_type == 'number' and value:
            try:
                float(value)
                self.is_valid = True
            except ValueError:
                error_msg = "Enter a valid number (e.g., 42 or -13.5)"
                self.is_valid = False
        else:
            self.is_valid = True
        
        if error_msg:
            self.entry.configure(border_color=COLORS['error'])
            self.error_label.configure(text=error_msg)
            if self.error_label.winfo_manager() == "":
                self.error_label.pack(anchor="w", padx=4, pady=(2, 0))
        else:
            self.entry.configure(border_color=COLORS['accent_cyan'])
            self.error_label.pack_forget()
        
        return self.is_valid

    def get(self):
        return self.entry.get()
    
    def set(self, value):
        self.entry.delete(0, 'end')
        self.entry.insert(0, value)
        self.validate()


class ModernTextbox(ctk.CTkFrame):
    """Textbox with label"""
    def __init__(self, parent, label="", placeholder="", height=100, **kwargs):
        super().__init__(parent, fg_color="transparent")
        
        self.label = ctk.CTkLabel(self, text=label, font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                                  text_color=COLORS['text_secondary'])
        self.label.pack(anchor="w", padx=4, pady=(0, 4))
        
        self.textbox = ctk.CTkTextbox(self, height=height, corner_radius=10, border_width=2,
                                      border_color=COLORS['accent_cyan'], fg_color=COLORS['bg_card'],
                                      font=ctk.CTkFont(family="Segoe UI", size=13), **kwargs)
        self.textbox.pack(fill="both", expand=True, padx=4)
    
    def get(self):
        return self.textbox.get("1.0", "end-1c")
    
    def set(self, value):
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", value)


class PlanetMoonEditor(ctk.CTkToplevel):
    """Editor for planet or moon with all fields"""
    def __init__(self, parent, is_moon=False, planet_data=None):
        super().__init__(parent)
        self.parent_app = parent
        self.is_moon = is_moon
        self.planet_data = planet_data or {}
        self.moons = list(self.planet_data.get('moons', []))
        self.photo_path = self.planet_data.get('photo', '')
        self.result = None
        
        title = "Moon Editor" if is_moon else "Planet Editor"
        self.title(title)
        self.geometry("900x700")
        self.configure(fg_color=COLORS['bg_dark'])
        
        self.transient(parent)
        self.grab_set()
        
        self.build_ui()
        self.load_data()
    
    def build_ui(self):
        # Header
        header = ctk.CTkLabel(self, text="🪐 " + ("Moon Details" if self.is_moon else "Planet Details"),
                              font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
                              text_color=COLORS['accent_cyan'])
        header.pack(pady=(20, 10))
        
        # Scrollable form
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", width=850, height=500)
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Basic card
        basic_card = GlassCard(scroll, title="📝 Basic Information")
        basic_card.pack(fill="x", pady=(0, 15))
        basic_grid = ctk.CTkFrame(basic_card, fg_color="transparent")
        basic_grid.pack(padx=20, pady=(0, 20), fill="x")
        
        self.name_entry = ModernEntry(basic_grid, label="Name *", placeholder="e.g., Terra Prime")
        self.name_entry.pack(fill="x", pady=(0, 10))
        
        # Environment card
        env_card = GlassCard(scroll, title="🛰️ Environment")
        env_card.pack(fill="x", pady=(0, 15))
        env_grid = ctk.CTkFrame(env_card, fg_color="transparent")
        env_grid.pack(padx=20, pady=(0, 20), fill="x")
        
        sent_row = ctk.CTkFrame(env_grid, fg_color="transparent")
        sent_row.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(sent_row, text="Sentinel Level", text_color=COLORS['text_secondary']).pack(anchor="w")
        self.sentinel_var = ctk.StringVar(value="N/A")
        self.sentinel_menu = ctk.CTkOptionMenu(sent_row, values=["N/A", "None", "Low", "Medium", "High", "Aggressive"],
                                               variable=self.sentinel_var, fg_color=COLORS['bg_card'],
                                               button_color=COLORS['accent_cyan'])
        self.sentinel_menu.pack(fill="x")
        
        fauna_row = ctk.CTkFrame(env_grid, fg_color="transparent")
        fauna_row.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(fauna_row, text="Fauna", text_color=COLORS['text_secondary']).pack(anchor="w")
        self.fauna_var = ctk.StringVar(value="N/A")
        self.fauna_menu = ctk.CTkOptionMenu(fauna_row, values=["N/A", "None", "Low", "Mid", "High", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
                                            variable=self.fauna_var, fg_color=COLORS['bg_card'],
                                            button_color=COLORS['accent_cyan'])
        self.fauna_menu.pack(fill="x")
        
        flora_row = ctk.CTkFrame(env_grid, fg_color="transparent")
        flora_row.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(flora_row, text="Flora", text_color=COLORS['text_secondary']).pack(anchor="w")
        self.flora_var = ctk.StringVar(value="N/A")
        self.flora_menu = ctk.CTkOptionMenu(flora_row, values=["N/A", "None", "Low", "Mid", "High"],
                                            variable=self.flora_var, fg_color=COLORS['bg_card'],
                                            button_color=COLORS['accent_cyan'])
        self.flora_menu.pack(fill="x")
        
        # Details card
        details_card = GlassCard(scroll, title="📋 Details")
        details_card.pack(fill="x", pady=(0, 15))
        
        self.properties_textbox = ModernTextbox(details_card, label="Properties", placeholder="e.g., Lush forests, mild climate", height=80)
        self.properties_textbox.pack(padx=20, pady=(0, 10), fill="x")
        
        self.materials_textbox = ModernTextbox(details_card, label="Materials", placeholder="e.g., Gold, Carbon, Oxygen", height=80)
        self.materials_textbox.pack(padx=20, pady=(0, 10), fill="x")
        
        self.base_entry = ModernEntry(details_card, label="Base Location", placeholder="e.g., (+12.34, -56.78) or N/A")
        self.base_entry.pack(padx=20, pady=(0, 10), fill="x")
        
        self.notes_textbox = ModernTextbox(details_card, label="Notes", placeholder="Additional observations", height=80)
        self.notes_textbox.pack(padx=20, pady=(0, 20), fill="x")
        
        # Photo card
        photo_card = GlassCard(scroll, title="🖼️ Photo")
        photo_card.pack(fill="x", pady=(0, 15))
        
        photo_btns = ctk.CTkFrame(photo_card, fg_color="transparent")
        photo_btns.pack(padx=20, pady=(0, 10), fill="x")
        ctk.CTkButton(photo_btns, text="📂 Choose Photo", command=self.choose_photo, height=36,
                      fg_color=COLORS['accent_cyan'], hover_color=COLORS['glow']).pack(side="left")
        self.photo_label = ctk.CTkLabel(photo_card, text="No photo selected", text_color=COLORS['text_secondary'])
        self.photo_label.pack(padx=20, pady=(0, 15), anchor="w")
        
        # Moons section (planets only)
        if not self.is_moon:
            moons_card = GlassCard(scroll, title="🌙 Moons")
            moons_card.pack(fill="x", pady=(0, 15))
            
            moon_btns = ctk.CTkFrame(moons_card, fg_color="transparent")
            moon_btns.pack(padx=20, pady=(0, 10), fill="x")
            ctk.CTkButton(moon_btns, text="➕ Add Moon", command=self.add_moon, height=36,
                          fg_color=COLORS['accent_cyan'], hover_color=COLORS['glow']).pack(side="left")
            
            self.moons_list_container = ctk.CTkFrame(moons_card, fg_color="transparent")
            self.moons_list_container.pack(padx=20, pady=(0, 15), fill="x")
            self.render_moons()
        
        # Action buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(0, 20), padx=20, fill="x")
        
        ctk.CTkButton(btn_frame, text="Cancel", command=self.cancel, height=45, corner_radius=10,
                      fg_color=COLORS['bg_card'], hover_color=COLORS['accent_purple'],
                      font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(btn_frame, text="💾 Save", command=self.save, height=45, corner_radius=10,
                      fg_color=COLORS['success'], hover_color="#00cc70",
                      font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")).pack(side="right")
    
    def load_data(self):
        if self.planet_data:
            self.name_entry.set(self.planet_data.get('name', ''))
            self.sentinel_var.set(self.planet_data.get('sentinel', 'N/A'))
            self.fauna_var.set(self.planet_data.get('fauna', 'N/A'))
            self.flora_var.set(self.planet_data.get('flora', 'N/A'))
            self.properties_textbox.set(self.planet_data.get('properties', ''))
            self.materials_textbox.set(self.planet_data.get('materials', ''))
            self.base_entry.set(self.planet_data.get('base_location', ''))
            self.notes_textbox.set(self.planet_data.get('notes', ''))
            if self.photo_path:
                self.photo_label.configure(text=self.photo_path)
    
    def choose_photo(self):
        file = filedialog.askopenfilename(title="Choose photo", filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.webp"), ("All files", "*.*")])
        if not file:
            return
        try:
            file_path = Path(file)
            photos_dir = project_root() / 'photos'
            photos_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy to photos/
            dest = photos_dir / file_path.name
            stem = dest.stem
            suffix = dest.suffix
            i = 1
            while dest.exists():
                dest = photos_dir / f"{stem}_{i}{suffix}"
                i += 1
            shutil.copy2(str(file_path), str(dest))
            
            self.photo_path = f"photos/{dest.name}"
            self.photo_label.configure(text=self.photo_path)
        except Exception:
            logging.exception("Photo copy error")
            messagebox.showerror("Error", "Failed to copy photo")
    
    def add_moon(self):
        editor = PlanetMoonEditor(self, is_moon=True)
        self.wait_window(editor)
        if editor.result:
            self.moons.append(editor.result)
            self.render_moons()
    
    def edit_moon(self, index):
        editor = PlanetMoonEditor(self, is_moon=True, planet_data=self.moons[index])
        self.wait_window(editor)
        if editor.result:
            self.moons[index] = editor.result
            self.render_moons()
    
    def remove_moon(self, index):
        self.moons.pop(index)
        self.render_moons()
    
    def render_moons(self):
        for w in self.moons_list_container.winfo_children():
            w.destroy()
        if not self.moons:
            ctk.CTkLabel(self.moons_list_container, text="No moons added", text_color=COLORS['text_secondary']).pack(anchor="w")
            return
        for i, moon in enumerate(self.moons):
            row = ctk.CTkFrame(self.moons_list_container, fg_color=COLORS['bg_card'], corner_radius=8)
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=f"🌙 {moon['name']}", font=ctk.CTkFont(size=13)).pack(side="left", padx=10, pady=8)
            ctk.CTkButton(row, text="✏️", width=36, height=28, command=lambda idx=i: self.edit_moon(idx),
                          fg_color=COLORS['accent_cyan'], hover_color=COLORS['glow']).pack(side="right", padx=(0, 5))
            ctk.CTkButton(row, text="✖", width=36, height=28, command=lambda idx=i: self.remove_moon(idx),
                          fg_color=COLORS['bg_card'], hover_color=COLORS['accent_pink']).pack(side="right")
    
    def save(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required!")
            return
        
        self.result = {
            'name': name,
            'sentinel': self.sentinel_var.get() or "N/A",
            'fauna': self.fauna_var.get() or "N/A",
            'flora': self.flora_var.get() or "N/A",
            'properties': self.properties_textbox.get().strip() or "N/A",
            'materials': self.materials_textbox.get().strip() or "N/A",
            'base_location': self.base_entry.get().strip() or "N/A",
            'photo': self.photo_path or "N/A",
            'notes': self.notes_textbox.get().strip() or "N/A"
        }
        if not self.is_moon:
            self.result['moons'] = self.moons
        self.destroy()
    
    def cancel(self):
        self.destroy()


class SystemEntryWizard(ctk.CTk):
    """Two-page wizard for complete system entry"""
    def __init__(self):
        super().__init__()
        self.title("Haven System Entry - Wizard")
        self.geometry("1400x900")
        self.configure(fg_color=COLORS['bg_dark'])

        # Data
        self.data_file = data_path("data.json")
        self.planets = []
        self.current_page = 1

        # Phase 3: Initialize data provider
        self.data_provider = None
        self.current_backend = 'json'
        if PHASE3_ENABLED:
            self._init_data_provider()

        # System fields (Page 1)
        self.system_name = ""
        self.region = ""
        self.x_coord = ""
        self.y_coord = ""
        self.z_coord = ""
        # System-level simplified metadata
        self.attributes = ""

        self.build_ui()

    def _init_data_provider(self):
        """Initialize data provider based on configuration (Phase 3)"""
        try:
            self.data_provider = get_data_provider()
            self.current_backend = get_current_backend()
            logging.info(f"Wizard data provider initialized: {self.current_backend}")
        except Exception as e:
            logging.error(f"Failed to initialize data provider: {e}")
            self.data_provider = None
            self.current_backend = 'json'

    def build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=COLORS['glass'], height=80)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        
        title = ctk.CTkLabel(header, text="✨ HAVEN SYSTEM ENTRY WIZARD",
                             font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
                             text_color=COLORS['accent_cyan'])
        title.pack(side="left", padx=30, pady=20)

        # Phase 3: Backend status indicators
        if PHASE3_ENABLED:
            status_frame = ctk.CTkFrame(header, fg_color="transparent")
            status_frame.pack(side="right", padx=15)

            if SHOW_BACKEND_STATUS:
                backend_label = ctk.CTkLabel(status_frame,
                                            text=f"Backend: {self.current_backend.upper()}",
                                            font=ctk.CTkFont(family="Segoe UI", size=12),
                                            text_color=COLORS['accent_cyan'])
                backend_label.pack(side="top", pady=(10, 2))

            if SHOW_SYSTEM_COUNT and self.data_provider:
                try:
                    count = self.data_provider.get_total_count()
                    count_label = ctk.CTkLabel(status_frame,
                                              text=f"Systems: {count:,}",
                                              font=ctk.CTkFont(family="Segoe UI", size=12),
                                              text_color=COLORS['text_secondary'])
                    count_label.pack(side="top", pady=(2, 10))
                except Exception as e:
                    logging.warning(f"Failed to get system count: {e}")

        self.page_indicator = ctk.CTkLabel(header, text="Page 1 of 2: System Information",
                                           font=ctk.CTkFont(family="Segoe UI", size=14),
                                           text_color=COLORS['text_secondary'])
        self.page_indicator.pack(side="right", padx=30)
        
        # Main content (stacked frames)
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Page 1
        self.page1_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.build_page1()
        
        # Page 2
        self.page2_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.build_page2()
        
        # Footer with navigation (create before show_page)
        footer = ctk.CTkFrame(self, fg_color=COLORS['glass'], height=80)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        
        self.back_btn = ctk.CTkButton(footer, text="⬅ Back", command=self.go_back, height=45, width=150,
                                      corner_radius=10, fg_color=COLORS['bg_card'],
                                      hover_color=COLORS['accent_purple'],
                                      font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"))
        self.back_btn.pack(side="left", padx=30, pady=17)
        
        self.next_btn = ctk.CTkButton(footer, text="Next ➡", command=self.go_next, height=45, width=150,
                                      corner_radius=10, fg_color=COLORS['accent_cyan'],
                                      hover_color=COLORS['glow'],
                                      font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"))
        self.next_btn.pack(side="right", padx=30, pady=17)
        
        # Show page 1 (after buttons are created)
        self.show_page(1)
    
    def build_page1(self):
        # Scrollable form
        scroll = ctk.CTkScrollableFrame(self.page1_frame, fg_color="transparent", width=1300, height=700)
        scroll.pack(fill="both", expand=True)
        
        # Edit mode selector
        edit_card = GlassCard(scroll, title="📂 Load Existing System (Optional)")
        edit_card.pack(fill="x", pady=(0, 20))
        
        edit_row = ctk.CTkFrame(edit_card, fg_color="transparent")
        edit_row.pack(padx=20, pady=(0, 15), fill="x")
        
        ctk.CTkLabel(edit_row, text="Edit existing:", text_color=COLORS['text_secondary']).pack(side="left", padx=(0, 10))
        
        self.edit_system_var = ctk.StringVar(value="(New System)")
        systems = self.get_existing_systems()
        self.edit_system_menu = ctk.CTkOptionMenu(edit_row, values=["(New System)"] + systems,
                                                   variable=self.edit_system_var, command=self.load_existing_system,
                                                   fg_color=COLORS['bg_card'], button_color=COLORS['accent_cyan'])
        self.edit_system_menu.pack(side="left", fill="x", expand=True)

        # Basic info
        basic_card = GlassCard(scroll, title="📝 System Information")
        basic_card.pack(fill="x", pady=(0, 20))
        basic_grid = ctk.CTkFrame(basic_card, fg_color="transparent")
        basic_grid.pack(padx=20, pady=(0, 20), fill="x")
        
        self.name_entry = ModernEntry(basic_grid, label="System Name *", placeholder="e.g., ZENITH PRIME")
        self.name_entry.pack(fill="x", pady=(0, 10))
        
        self.region_entry = ModernEntry(basic_grid, label="Region", placeholder="e.g., Core Worlds")
        self.region_entry.pack(fill="x", pady=(0, 10))
        
        # Coordinates
        coords_card = GlassCard(scroll, title="🎯 Coordinates")
        coords_card.pack(fill="x", pady=(0, 20))
        coords_grid = ctk.CTkFrame(coords_card, fg_color="transparent")
        coords_grid.pack(padx=20, pady=(0, 20), fill="x")
        
        coords_row = ctk.CTkFrame(coords_grid, fg_color="transparent")
        coords_row.pack(fill="x")
        
        x_frame = ctk.CTkFrame(coords_row, fg_color="transparent")
        x_frame.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.x_entry = ModernEntry(x_frame, label="X *", placeholder="0.0", validate_type="number")
        self.x_entry.pack(fill="x")
        
        y_frame = ctk.CTkFrame(coords_row, fg_color="transparent")
        y_frame.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.y_entry = ModernEntry(y_frame, label="Y *", placeholder="0.0", validate_type="number")
        self.y_entry.pack(fill="x")
        
        z_frame = ctk.CTkFrame(coords_row, fg_color="transparent")
        z_frame.pack(side="left", expand=True, fill="x")
        self.z_entry = ModernEntry(z_frame, label="Z *", placeholder="0.0", validate_type="number")
        self.z_entry.pack(fill="x")
        
        # System attributes (single box)
        attr_card = GlassCard(scroll, title="⭐ System Attributes (Optional)")
        attr_card.pack(fill="x", pady=(0, 20))
        self.attributes_textbox = ModernTextbox(attr_card, label="Attributes",
                                                placeholder="e.g., Trade hub; Rare resources; Pirate activity",
                                                height=80)
        self.attributes_textbox.pack(padx=20, pady=(0, 10), fill="x")
    
    def build_page2(self):
        # Two-column layout: left = controls, right = upload list
        holder = ctk.CTkFrame(self.page2_frame, fg_color="transparent")
        holder.pack(fill="both", expand=True)
        
        left_panel = ctk.CTkFrame(holder, fg_color="transparent", width=700)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        right_panel = ctk.CTkFrame(holder, fg_color="transparent", width=600)
        right_panel.pack(side="right", fill="both")
        
        # Left: Add planet button and instructions
        add_card = GlassCard(left_panel, title="🪐 Add Planets")
        add_card.pack(fill="x", pady=(0, 20))
        
        instructions = ctk.CTkLabel(add_card, text="Click 'Add Planet' to open the planet editor.\nAdd moons inside the planet editor.\nEach planet is added to the Upload List on the right.",
                                    font=ctk.CTkFont(family="Segoe UI", size=13), text_color=COLORS['text_secondary'],
                                    justify="left")
        instructions.pack(padx=20, pady=(0, 10), anchor="w")
        
        ctk.CTkButton(add_card, text="➕ Add Planet", command=self.add_planet, height=50,
                      corner_radius=10, fg_color=COLORS['success'], hover_color="#00cc70",
                      font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")).pack(padx=20, pady=(0, 20), fill="x")
        
        # Right: Upload list
        list_card = GlassCard(right_panel, title="📋 Upload List")
        list_card.pack(fill="both", expand=True)
        
        self.upload_list_scroll = ctk.CTkScrollableFrame(list_card, fg_color="transparent", width=550, height=600)
        self.upload_list_scroll.pack(padx=20, pady=(0, 20), fill="both", expand=True)
        
        self.render_upload_list()
    
    def add_planet(self):
        editor = PlanetMoonEditor(self, is_moon=False)
        self.wait_window(editor)
        if editor.result:
            # Check uniqueness
            if any(p['name'] == editor.result['name'] for p in self.planets):
                messagebox.showerror("Error", f"Planet '{editor.result['name']}' already exists!")
                return
            self.planets.append(editor.result)
            self.render_upload_list()
    
    def edit_planet(self, index):
        editor = PlanetMoonEditor(self, is_moon=False, planet_data=self.planets[index])
        self.wait_window(editor)
        if editor.result:
            self.planets[index] = editor.result
            self.render_upload_list()
    
    def remove_planet(self, index):
        confirm = messagebox.askyesno("Confirm", f"Remove planet '{self.planets[index]['name']}'?")
        if confirm:
            self.planets.pop(index)
            self.render_upload_list()
    
    def render_upload_list(self):
        for w in self.upload_list_scroll.winfo_children():
            w.destroy()
        
        if not self.planets:
            ctk.CTkLabel(self.upload_list_scroll, text="No planets added yet.\nAdd planets from the left panel.",
                         text_color=COLORS['text_secondary'], justify="center").pack(pady=50)
            return
        
        for i, planet in enumerate(self.planets):
            card = ctk.CTkFrame(self.upload_list_scroll, fg_color=COLORS['bg_card'], corner_radius=12, border_width=1, border_color=COLORS['accent_cyan'])
            card.pack(fill="x", pady=8)
            
            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=15, pady=(12, 5))
            
            name_label = ctk.CTkLabel(top, text=f"🪐 {planet['name']}", font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                                      text_color=COLORS['accent_cyan'])
            name_label.pack(side="left")
            
            moon_count = len(planet.get('moons', []))
            if moon_count > 0:
                moon_label = ctk.CTkLabel(top, text=f"🌙 {moon_count} moon{'s' if moon_count != 1 else ''}",
                                          font=ctk.CTkFont(family="Segoe UI", size=12), text_color=COLORS['text_secondary'])
                moon_label.pack(side="left", padx=(10, 0))
            
            btn_row = ctk.CTkFrame(card, fg_color="transparent")
            btn_row.pack(fill="x", padx=15, pady=(0, 12))
            
            ctk.CTkButton(btn_row, text="✏️ Edit", width=80, height=32, command=lambda idx=i: self.edit_planet(idx),
                          fg_color=COLORS['accent_cyan'], hover_color=COLORS['glow']).pack(side="left", padx=(0, 5))
            ctk.CTkButton(btn_row, text="✖ Remove", width=80, height=32, command=lambda idx=i: self.remove_planet(idx),
                          fg_color=COLORS['error'], hover_color="#cc0055").pack(side="left")
    
    def get_existing_systems(self):
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    obj = json.load(f)
                    systems = []
                    # New schema: { systems: { name: {...} } }
                    if isinstance(obj, dict) and isinstance(obj.get('systems'), dict):
                        systems = [k for k in obj['systems'].keys()]
                        return sorted(systems)
                    # Legacy wrapper: { _meta, data: [...] }
                    data = obj.get('data')
                    if isinstance(data, list):
                        systems = [item.get('name') for item in data if isinstance(item, dict) and item.get('type') != 'region']
                        return sorted([s for s in systems if s])
                    # Heuristic map: { name: {x,y,z,...} }
                    if isinstance(obj, dict):
                        vals = list(obj.values())
                        if vals and all(isinstance(v, dict) for v in vals) and any(('x' in v or 'y' in v or 'z' in v or 'planets' in v) for v in vals):
                            return sorted(list(obj.keys()))
        except Exception:
            logging.exception("Failed to load systems")
        return []
    
    def load_existing_system(self, choice):
        if choice == "(New System)":
            self.clear_page1()
            return
        
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    obj = json.load(f)
                    sys_obj = None
                    # New schema
                    if isinstance(obj, dict) and isinstance(obj.get('systems'), dict):
                        sys_obj = obj['systems'].get(choice)
                    # Legacy wrapper
                    if sys_obj is None and isinstance(obj, dict) and isinstance(obj.get('data'), list):
                        for item in obj['data']:
                            if isinstance(item, dict) and item.get('name') == choice and item.get('type') != 'region':
                                sys_obj = item; break
                    # Heuristic map
                    if sys_obj is None and isinstance(obj, dict):
                        v = obj.get(choice)
                        if isinstance(v, dict):
                            sys_obj = v
                    if not sys_obj:
                        return
                    # Load fields
                    item = sys_obj
                    self.name_entry.set(item.get('name', choice))
                    self.region_entry.set(item.get('region', ''))
                    self.x_entry.set(str(item.get('x', '')))
                    self.y_entry.set(str(item.get('y', '')))
                    self.z_entry.set(str(item.get('z', '')))
                    self.attributes_textbox.set(item.get('attributes', ''))
                    planets_data = item.get('planets', [])
                    self.planets = []
                    if planets_data and isinstance(planets_data, list):
                        if planets_data and isinstance(planets_data[0], dict):
                            self.planets = list(planets_data)
                        elif planets_data and isinstance(planets_data[0], str):
                            self.planets = [{'name': name, 'sentinel': 'N/A', 'fauna': 'N/A', 'flora': 'N/A',
                                            'properties': 'N/A', 'materials': 'N/A', 'base_location': 'N/A',
                                            'photo': 'N/A', 'notes': 'N/A', 'moons': []} for name in planets_data]
        except Exception:
            logging.exception("Failed to load system")
            messagebox.showerror("Error", "Failed to load system")
    
    def clear_page1(self):
        self.name_entry.set('')
        self.region_entry.set('')
        self.x_entry.set('')
        self.y_entry.set('')
        self.z_entry.set('')
        self.attributes_textbox.set('')
        self.planets = []
    
    def show_page(self, page):
        self.current_page = page
        
        if page == 1:
            self.page1_frame.pack(fill="both", expand=True)
            self.page2_frame.pack_forget()
            self.page_indicator.configure(text="Page 1 of 2: System Information")
            self.back_btn.configure(state="disabled")
            self.next_btn.configure(text="Next ➡")
        else:
            self.page1_frame.pack_forget()
            self.page2_frame.pack(fill="both", expand=True)
            self.page_indicator.configure(text="Page 2 of 2: Planets & Moons")
            self.back_btn.configure(state="normal")
            self.next_btn.configure(text="💾 Finish & Save")
            self.render_upload_list()
    
    def go_back(self):
        if self.current_page == 2:
            self.show_page(1)
    
    def go_next(self):
        if self.current_page == 1:
            # Validate page 1
            if not self.validate_page1():
                return
            # Capture page 1 data
            self.capture_page1()
            self.show_page(2)
        else:
            # Save entire system
            self.save_system()
    
    def validate_page1(self):
        if not self.name_entry.get().strip():
            messagebox.showerror("Error", "System Name is required!")
            return False
        # Region optional per new spec
        if not self.x_entry.validate() or not self.y_entry.validate() or not self.z_entry.validate():
            messagebox.showerror("Error", "Valid coordinates are required!")
            return False
        return True
    
    def capture_page1(self):
        self.system_name = self.name_entry.get().strip()
        self.region = self.region_entry.get().strip()
        self.x_coord = self.x_entry.get().strip()
        self.y_coord = self.y_entry.get().strip()
        self.z_coord = self.z_entry.get().strip()
        self.attributes = self.attributes_textbox.get().strip() or "N/A"
    
    def save_system(self):
        try:
            x = float(self.x_coord)
            y = float(self.y_coord)
            z = float(self.z_coord)
        except ValueError:
            messagebox.showerror("Error", "Invalid coordinates!")
            return

        # Validate coordinates before proceeding
        is_valid, error = validate_coordinates(x, y, z)
        if not is_valid:
            messagebox.showerror("Validation Error", f"Invalid coordinates:\n{error}")
            return

        try:
            # Generate unique ID using UUID instead of timestamp to prevent collisions
            unique_id = uuid.uuid4().hex[:8].upper()
            system_data = {
                "id": f"SYS_{self.region.upper().replace(' ', '_')}_{unique_id}",
                "name": self.system_name,
                "region": self.region,
                "x": x,
                "y": y,
                "z": z,
                "attributes": self.attributes,
                "planets": self.planets,
                # Keep legacy planets_names inside each system for backward compat if needed
                "planets_names": [p['name'] for p in self.planets]
            }

            # Validate system data against schema
            is_valid, error = validate_system_data(system_data)
            if not is_valid:
                messagebox.showerror("Validation Error", f"System data validation failed:\n{error}")
                logging.error(f"System validation failed: {error}")
                return

            # Phase 3: Use data provider if available, otherwise fall back to JSON
            if PHASE3_ENABLED and self.data_provider and self.current_backend == 'database':
                self._save_system_via_provider(system_data)
            else:
                self._save_system_via_json(system_data)

        except Exception:
            logging.exception("Save failed")
            messagebox.showerror("Error", "Failed to save system!")

    def _save_system_via_provider(self, system_data: dict):
        """Save system using data provider (Phase 3)"""
        try:
            # Check if system exists
            existing = self.data_provider.get_system_by_name(system_data['name'])
            if existing:
                confirm = messagebox.askyesno("Overwrite", f"System '{system_data['name']}' exists. Overwrite?")
                if not confirm:
                    return
                # Delete existing system before adding new one
                # This ensures we replace planets/moons/stations completely
                self.data_provider.delete_system(existing['id'])

            # Add system (either new or replacement)
            self.data_provider.add_system(system_data)

            messagebox.showinfo("Success", f"System '{self.system_name}' saved with {len(self.planets)} planet(s)!")

            # Clear and reset
            self.clear_page1()
            self.planets = []
            self.edit_system_var.set("(New System)")
            self.show_page(1)

        except Exception as e:
            logging.exception(f"Failed to save via data provider: {e}")
            messagebox.showerror("Error", f"Failed to save system: {e}")

    def _save_system_via_json(self, system_data: dict):
        """Save system using JSON file (backward compatibility)"""
        try:
            # Load existing data with new schema preference (top-level map)
            obj: dict = {"_meta": {"version": "3.0.0"}}

            # Use file locking to prevent concurrent access issues
            with FileLock(self.data_file, timeout=10.0):
                if self.data_file.exists():
                    with open(self.data_file, 'r', encoding='utf-8') as f:
                        try:
                            existing = json.load(f)
                            # Already top-level map?
                            if isinstance(existing, dict):
                                vals = [v for k,v in existing.items() if k != '_meta']
                                if vals and all(isinstance(v, dict) for v in vals) and any(('x' in v or 'y' in v or 'z' in v or 'planets' in v) for v in vals):
                                    obj = existing
                                elif isinstance(existing.get('systems'), dict):
                                    # unwrap to top-level
                                    obj = {"_meta": existing.get('_meta', obj.get('_meta'))}
                                    for name, it in existing['systems'].items():
                                        if isinstance(it, dict):
                                            cp = dict(it); cp.setdefault('name', name)
                                            obj[name] = cp
                                elif isinstance(existing.get('data'), list):
                                    obj = {"_meta": existing.get('_meta', obj.get('_meta'))}
                                    for it in existing['data']:
                                        if isinstance(it, dict) and it.get('type') != 'region':
                                            # Use UUID for fallback name instead of timestamp
                                            name = (it.get('name') or f"SYS_{uuid.uuid4().hex[:8].upper()}")
                                            cp = dict(it); cp.pop('type', None)
                                            obj[name] = cp
                        except Exception:
                            pass

                # Duplicate / overwrite prompt
                key = self.system_name
                if key in obj:
                    confirm = messagebox.askyesno("Overwrite", f"System '{key}' exists. Overwrite?")
                    if not confirm:
                        return
                obj[key] = system_data

                # Save with backup
                if self.data_file.exists():
                    backup = self.data_file.with_suffix('.json.bak')
                    shutil.copy2(self.data_file, backup)

                # Write data while holding the file lock
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump(obj, f, indent=2)

            messagebox.showinfo("Success", f"System '{self.system_name}' saved with {len(self.planets)} planet(s)!")

            # Clear and reset
            self.clear_page1()
            self.planets = []
            self.edit_system_var.set("(New System)")
            self.show_page(1)

        except Exception as e:
            logging.exception(f"Failed to save via JSON: {e}")
            messagebox.showerror("Error", f"Failed to save system: {e}")



def main():
    app = SystemEntryWizard()
    app.mainloop()


if __name__ == "__main__":
    main()
