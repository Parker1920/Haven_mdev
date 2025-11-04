"""
Haven System Entry - Modern Sci-Fi Glassmorphism Interface
Built with CustomTkinter for 2025 aesthetics
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
import logging
import sys
from logging.handlers import RotatingFileHandler

# Initialize CustomTkinter

# Theme options (UI appearance + base CTk color theme)
THEMES = {
    "Dark": ("dark", "blue"),
    "Light": ("light", "blue"),
    "Cosmic": ("dark", "green"),
    "Haven (Cyan)": ("dark", "blue")  # CTk theme stays close to default; we apply custom tokens below
}
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

from common.paths import data_path, logs_dir, project_root

# Optional token-based theme overlay for our in-app COLORS
def apply_theme_tokens(theme_name: str):
    """Apply color tokens from themes/*.json to override COLORS in-app.
    This does not change CTk's own widget theme; it updates our palette used for fg/border colors.
    """
    try:
        if theme_name == "Haven (Cyan)":
            theme_file = project_root() / "themes" / "haven_theme.json"
            if theme_file.exists():
                with open(theme_file, "r", encoding="utf-8") as f:
                    obj = json.load(f)
                    if isinstance(obj, dict) and isinstance(obj.get("colors"), dict):
                        COLORS.update(obj["colors"])  # override keys we know
    except Exception:
        logging.exception("Failed to apply theme tokens for %s", theme_name)

# Settings persistence
SETTINGS_FILE = project_root() / "settings.json"

def load_settings():
    try:
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        logging.exception("Failed to load settings.json")
    return {"theme": "Dark"}

def save_settings(data: dict):
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception:
        logging.exception("Failed to save settings.json")

# Apply saved theme on startup
_settings = load_settings()
_theme = _settings.get("theme", "Dark")
if _theme in THEMES:
    mode, color = THEMES[_theme]
    ctk.set_appearance_mode(mode)
    # color may be a CTk built-in name; we keep built-in and use token overlay for our widget colors
    ctk.set_default_color_theme(color)
    # Apply our token palette overlay (affects widgets we style with COLORS)
    apply_theme_tokens(_theme)

# Color Palette - Sci-Fi Cosmic Theme
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

def _excepthook(exc_type, exc, tb):
    logging.exception("Uncaught exception", exc_info=(exc_type, exc, tb))
    # Also show a friendly message
    try:
        messagebox.showerror("Unexpected Error", f"{exc_type.__name__}: {exc}")
    except Exception:
        pass

sys.excepthook = _excepthook


class AnimatedBackground(ctk.CTkCanvas):
    """Animated starfield background"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS['bg_dark'], highlightthickness=0, **kwargs)
        self.stars = []
        self.width = 1200
        self.height = 800
        self.create_stars()
        self.animate()
    
    def create_stars(self):
        """Create twinkling stars"""
        import random
        for _ in range(100):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(1, 3)
            star = self.create_oval(x, y, x+size, y+size, 
                                   fill='white', outline='')
            self.stars.append({
                'id': star,
                'brightness': random.random(),
                'direction': random.choice([-1, 1])
            })
    
    def animate(self):
        """Animate star twinkling"""
        for star in self.stars:
            star['brightness'] += 0.05 * star['direction']
            if star['brightness'] >= 1 or star['brightness'] <= 0.3:
                star['direction'] *= -1
            
            opacity = int(255 * star['brightness'])
            color = f'#{opacity:02x}{opacity:02x}{opacity:02x}'
            self.itemconfig(star['id'], fill=color)
        
        self.after(50, self.animate)


class GlassCard(ctk.CTkFrame):
    """Glassmorphic card with hover effects"""
    def __init__(self, parent, title="", **kwargs):
        super().__init__(
            parent,
            fg_color=(COLORS['glass'], COLORS['bg_card']),
            corner_radius=16,
            border_width=1,
            border_color=(COLORS['accent_cyan'], COLORS['accent_cyan']),
            **kwargs
        )
        
        self.title = title
        if title:
            self.title_label = ctk.CTkLabel(
                self,
                text=title,
                font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
                text_color=COLORS['accent_cyan']
            )
            self.title_label.pack(pady=(16, 12), padx=20, anchor="w")
        
        # Hover effects
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def on_enter(self, e):
        """Glow effect on hover"""
        self.configure(border_color=COLORS['glow'])
    
    def on_leave(self, e):
        """Remove glow effect"""
        self.configure(border_color=COLORS['accent_cyan'])


class ModernEntry(ctk.CTkFrame):
    """Custom styled entry with floating label and validation"""
    def __init__(self, parent, label="", placeholder="", validate_type=None, **kwargs):
        super().__init__(parent, fg_color="transparent")
        
        self.validate_type = validate_type  # 'number', 'required', or None
        self.is_valid = True
        
        self.label = ctk.CTkLabel(
            self,
            text=label,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS['text_secondary']
        )
        self.label.pack(anchor="w", padx=4, pady=(0, 4))
        
        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            height=45,
            corner_radius=10,
            border_width=2,
            border_color=COLORS['accent_cyan'],
            fg_color=COLORS['bg_card'],
            font=ctk.CTkFont(family="Segoe UI", size=13),
            **kwargs
        )
        self.entry.pack(fill="x", padx=4)
        
        # Error label (hidden by default)
        self.error_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS['error']
        )
        
        # Bind validation events
        self.entry.bind('<KeyRelease>', self.validate)
        self.entry.bind('<FocusOut>', self.validate)
        self.tooltip = None

    def validate(self, event=None):
        """Validate field and show/hide error"""
        value = self.get().strip()
        error_msg = ""
        
        # Check required
        if self.label.cget('text').endswith('*') and not value:
            error_msg = "This field is required."
            self.is_valid = False
        # Check numeric
        elif self.validate_type == 'number' and value:
            try:
                float(value)
                self.is_valid = True
            except ValueError:
                error_msg = "Enter a valid number (e.g., 42 or -13.5)"
                self.is_valid = False
        else:
            self.is_valid = True
        
        # Update UI
        if error_msg:
            self.entry.configure(border_color=COLORS['error'])
            self.error_label.configure(text=error_msg)
            if self.error_label.winfo_manager() == "":
                self.error_label.pack(anchor="w", padx=4, pady=(2, 0))
        else:
            self.entry.configure(border_color=COLORS['accent_cyan'])
            self.error_label.pack_forget()
        
        return self.is_valid

    def show_tooltip(self, text=None):
        if not text:
            text = self.label.cget('text')
        if self.tooltip:
            self.tooltip.destroy()
        x = self.entry.winfo_rootx() + 10
        y = self.entry.winfo_rooty() + self.entry.winfo_height() + 5
        self.tooltip = ctk.CTkToplevel(self)
        self.tooltip.overrideredirect(True)
        self.tooltip.geometry(f"+{x}+{y}")
        label = ctk.CTkLabel(self.tooltip, text=text, fg_color=COLORS['bg_card'], text_color=COLORS['warning'], font=ctk.CTkFont(size=11))
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
    
    def get(self):
        return self.entry.get()
    
    def set(self, value):
        self.entry.delete(0, 'end')
        self.entry.insert(0, value)
        self.validate()  # Revalidate after programmatic set


class ModernTextbox(ctk.CTkFrame):
    """Custom styled textbox with floating label"""
    def __init__(self, parent, label="", placeholder="", height=100, **kwargs):
        super().__init__(parent, fg_color="transparent")
        
        self.label = ctk.CTkLabel(
            self,
            text=label,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS['text_secondary']
        )
        self.label.pack(anchor="w", padx=4, pady=(0, 4))
        
        self.textbox = ctk.CTkTextbox(
            self,
            height=height,
            corner_radius=10,
            border_width=2,
            border_color=COLORS['accent_cyan'],
            fg_color=COLORS['bg_card'],
            font=ctk.CTkFont(family="Segoe UI", size=13),
            **kwargs
        )
        self.textbox.pack(fill="both", expand=True, padx=4)
    
    def get(self):
        return self.textbox.get("1.0", "end-1c")
    
    def set(self, value):
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", value)


class FieldManagerDialog(ctk.CTkToplevel):
    """Modern field management dialog"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_app = parent
        
        self.title("Field Manager")
        self.geometry("600x500")
        self.configure(fg_color=COLORS['bg_dark'])
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Header
        header = ctk.CTkLabel(
            self,
            text="⚙️ Field Manager",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=COLORS['accent_cyan']
        )
        header.pack(pady=(20, 10))
        
        subtitle = ctk.CTkLabel(
            self,
            text="Add, rename, or remove custom fields",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS['text_secondary']
        )
        subtitle.pack(pady=(0, 20))
        
        # Tab view
        self.tabview = ctk.CTkTabview(
            self,
            width=560,
            height=350,
            fg_color=COLORS['glass'],
            segmented_button_fg_color=COLORS['bg_card'],
            segmented_button_selected_color=COLORS['accent_cyan']
        )
        self.tabview.pack(padx=20, pady=(0, 20), fill="both", expand=True)
        
        # Create tabs
        self.tabview.add("Add Field")
        self.tabview.add("Rename Field")
        self.tabview.add("Remove Field")
        self.tabview.add("View All")
        
        self.setup_add_tab()
        self.setup_rename_tab()
        self.setup_remove_tab()
        self.setup_view_tab()
        
        # Close button
        close_btn = ctk.CTkButton(
            self,
            text="Close",
            command=self.destroy,
            height=45,
            corner_radius=10,
            fg_color=COLORS['bg_card'],
            hover_color=COLORS['accent_purple'],
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        )
        close_btn.pack(pady=(0, 20), padx=20, fill="x")
    
    def setup_add_tab(self):
        """Setup add field tab"""
        tab = self.tabview.tab("Add Field")
        
        card = GlassCard(tab, title="")
        card.pack(padx=20, pady=20, fill="both", expand=True)
        
        self.new_field_entry = ModernEntry(
            card,
            label="New Field Name",
            placeholder="e.g., Population, Technology Level"
        )
        self.new_field_entry.pack(padx=20, pady=(10, 20), fill="x")
        
        add_btn = ctk.CTkButton(
            card,
            text="➕ Add Field",
            command=self.add_field,
            height=45,
            corner_radius=10,
            fg_color=COLORS['accent_cyan'],
            hover_color=COLORS['glow'],
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        )
        add_btn.pack(padx=20, pady=(0, 20), fill="x")
    
    def setup_rename_tab(self):
        """Setup rename field tab"""
        tab = self.tabview.tab("Rename Field")
        
        card = GlassCard(tab, title="")
        card.pack(padx=20, pady=20, fill="both", expand=True)
        
        self.old_field_entry = ModernEntry(
            card,
            label="Current Field Name",
            placeholder="e.g., Population"
        )
        self.old_field_entry.pack(padx=20, pady=(10, 10), fill="x")
        
        self.new_name_entry = ModernEntry(
            card,
            label="New Field Name",
            placeholder="e.g., Total Population"
        )
        self.new_name_entry.pack(padx=20, pady=(0, 20), fill="x")
        
        rename_btn = ctk.CTkButton(
            card,
            text="✏️ Rename Field",
            command=self.rename_field,
            height=45,
            corner_radius=10,
            fg_color=COLORS['accent_purple'],
            hover_color=COLORS['accent_pink'],
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        )
        rename_btn.pack(padx=20, pady=(0, 20), fill="x")
    
    def setup_remove_tab(self):
        """Setup remove field tab"""
        tab = self.tabview.tab("Remove Field")
        
        card = GlassCard(tab, title="")
        card.pack(padx=20, pady=20, fill="both", expand=True)
        
        self.remove_field_entry = ModernEntry(
            card,
            label="Field Name to Remove",
            placeholder="e.g., Technology Level"
        )
        self.remove_field_entry.pack(padx=20, pady=(10, 20), fill="x")
        
        warning = ctk.CTkLabel(
            card,
            text="⚠️ This will remove the field from all systems",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS['warning']
        )
        warning.pack(padx=20, pady=(0, 10))
        
        remove_btn = ctk.CTkButton(
            card,
            text="🗑️ Remove Field",
            command=self.remove_field,
            height=45,
            corner_radius=10,
            fg_color=COLORS['error'],
            hover_color="#cc0055",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        )
        remove_btn.pack(padx=20, pady=(0, 20), fill="x")
    
    def setup_view_tab(self):
        """Setup view all fields tab"""
        tab = self.tabview.tab("View All")
        
        card = GlassCard(tab, title="")
        card.pack(padx=20, pady=20, fill="both", expand=True)
        
        self.fields_textbox = ctk.CTkTextbox(
            card,
            height=250,
            corner_radius=10,
            fg_color=COLORS['bg_dark'],
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.fields_textbox.pack(padx=20, pady=(10, 20), fill="both", expand=True)
        
        self.refresh_fields_view()
    
    def refresh_fields_view(self):
        """Refresh the fields view"""
        self.fields_textbox.delete("1.0", "end")
        
        data = self.parent_app.load_data()
        all_fields = set()
        
        # Data is a flat list
        for item in data:
            if item.get("type") != "region":
                all_fields.update(item.keys())
        
        # Remove standard fields
        standard = {'id', 'name', 'region', 'x', 'y', 'z', 'type', 'properties', 'materials'}
        custom = sorted(all_fields - standard)
        
        if custom:
            self.fields_textbox.insert("1.0", "Custom Fields:\n\n")
            for i, field in enumerate(custom, 1):
                self.fields_textbox.insert("end", f"{i}. {field}\n")
        else:
            self.fields_textbox.insert("1.0", "No custom fields defined yet.")
    
    def add_field(self):
        """Add a new custom field"""
        field_name = self.new_field_entry.get().strip()
        
        if not field_name:
            messagebox.showerror("Error", "Please enter a field name")
            return
        
        data = self.parent_app.load_data()
        
        # Add field to all systems (flat list structure)
        for item in data:
            if item.get("type") != "region":
                if field_name not in item:
                    item[field_name] = ""
        
        self.parent_app.save_data(data)
        self.parent_app.refresh_custom_fields()
        
        messagebox.showinfo("Success", f"Field '{field_name}' added successfully!")
        self.new_field_entry.set("")
        self.refresh_fields_view()
    
    def rename_field(self):
        """Rename an existing field"""
        old_name = self.old_field_entry.get().strip()
        new_name = self.new_name_entry.get().strip()
        
        if not old_name or not new_name:
            messagebox.showerror("Error", "Please enter both field names")
            return
        
        data = self.parent_app.load_data()
        found = False
        
        # Flat list structure
        for item in data:
            if item.get("type") != "region":
                if old_name in item:
                    item[new_name] = item.pop(old_name)
                    found = True
        
        if not found:
            messagebox.showerror("Error", f"Field '{old_name}' not found")
            return
        
        self.parent_app.save_data(data)
        self.parent_app.refresh_custom_fields()
        
        messagebox.showinfo("Success", f"Field renamed from '{old_name}' to '{new_name}'!")
        self.old_field_entry.set("")
        self.new_name_entry.set("")
        self.refresh_fields_view()
    
    def remove_field(self):
        """Remove a custom field"""
        field_name = self.remove_field_entry.get().strip()
        
        if not field_name:
            messagebox.showerror("Error", "Please enter a field name")
            return
        
        confirm = messagebox.askyesno(
            "Confirm Removal",
            f"Are you sure you want to remove '{field_name}' from all systems?"
        )
        
        if not confirm:
            return
        
        data = self.parent_app.load_data()
        found = False
        
        # Flat list structure
        for item in data:
            if item.get("type") != "region":
                if field_name in item:
                    del item[field_name]
                    found = True
        
        if not found:
            messagebox.showerror("Error", f"Field '{field_name}' not found")
            return
        
        self.parent_app.save_data(data)
        self.parent_app.refresh_custom_fields()
        
        messagebox.showinfo("Success", f"Field '{field_name}' removed successfully!")
        self.remove_field_entry.set("")
        self.refresh_fields_view()


class SystemEntryApp(ctk.CTk):
    """Main application window"""
    def __init__(self):
        super().__init__()
        self.title("Haven System Entry - Sci-Fi Edition")
        self.geometry("1200x800")
        self.configure(fg_color=COLORS['bg_dark'])
        # Undo/redo stacks
        self.undo_stack = []
        self.redo_stack = []
        # Keyboard shortcuts
        self.bind_all('<Control-z>', lambda e: self.undo())
        self.bind_all('<Control-y>', lambda e: self.redo())
        self.bind_all('<Control-s>', lambda e: self.save_system())
        self.bind_all('<Control-n>', lambda e: self.clear_form())
        # Data file path
        self.data_file = data_path("data.json")
        # Schema file path
        self.schema_file = project_root() / "data" / "data.schema.json"
        self.schema = self.load_schema()
        self.schema_hints = self.build_schema_hints()
        # Custom fields dictionary
        self.custom_fields = {}
        # Draft autosave path
        self.draft_file = project_root() / "data" / ".draft_system.json"
        # Setup UI
        self.setup_ui()
        # Load custom fields
        self.refresh_custom_fields()
        # Initialize planets model and photo path
        self.planets = []
        # Photo (relative path under photos/ or URL/N/A)
        self.photo_rel_path = ""
        # Check for draft and restore if exists
        self.restore_draft_if_exists()
        # Auto-save timer (every 30 seconds)
        self.after(30000, self.auto_save_draft)

    # ----------------------- Schema helpers -----------------------
    def load_schema(self):
        try:
            if self.schema_file.exists():
                with open(self.schema_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            logging.exception("Failed to load schema")
        return None

    def build_schema_hints(self):
        """Extract simple hints for system fields from the JSON schema.
        Returns dict like { field: {required: bool, type: str, enum: list|None} }
        """
        hints = {}
        try:
            s = self.schema
            if not s:
                return hints
            # Find the 'system' object schema: the oneOf item that requires 'id','name','region','x','y','z'
            items = s.get('properties', {}).get('data', {}).get('items', {})
            one_of = items.get('oneOf', []) if isinstance(items, dict) else []
            system_schema = None
            for candidate in one_of:
                req = set(candidate.get('required', []))
                if {'id', 'name', 'region', 'x', 'y', 'z'}.issubset(req):
                    system_schema = candidate
                    break
            if not system_schema:
                return hints
            props = system_schema.get('properties', {})
            required_set = set(system_schema.get('required', []))
            for field, meta in props.items():
                t = meta.get('type') if isinstance(meta, dict) else None
                enum = meta.get('enum') if isinstance(meta, dict) else None
                hints[field] = {
                    'required': field in required_set,
                    'type': t,
                    'enum': enum
                }
        except Exception:
            logging.exception("Failed to build schema hints")
        return hints

    def get_schema_help(self, field_key: str, fallback_title: str, fallback_body: str):
        """Compose help title/body using schema hints where available."""
        info = self.schema_hints.get(field_key)
        if not info:
            return fallback_title, fallback_body
        parts = []
        if info.get('required'):
            parts.append("Required field.")
        t = info.get('type')
        if t:
            parts.append(f"Type: {t}.")
        enum = info.get('enum')
        if enum:
            enum_str = ", ".join(map(str, enum))
            parts.append(f"Allowed values: {enum_str}.")
        body = fallback_body
        if parts:
            body = body + "\n\nSchema: " + " ".join(parts)
        # Title: prefer fallback but annotate with key
        title = f"{fallback_title}"
        return title, body

    def snapshot_form(self):
        """Take a snapshot of the current form state for undo/redo."""
        state = {
            'name': self.name_entry.get(),
            'region': self.region_entry.get(),
            'x': self.x_entry.get(),
            'y': self.y_entry.get(),
            'z': self.z_entry.get(),
            'properties': self.properties_textbox.get(),
            'materials': self.materials_textbox.get(),
            'custom': {k: v.get() for k, v in self.custom_fields.items()}
        }
        return state

    def restore_form(self, state):
        """Restore form state from a snapshot."""
        self.name_entry.set(state['name'])
        self.region_entry.set(state['region'])
        self.x_entry.set(state['x'])
        self.y_entry.set(state['y'])
        self.z_entry.set(state['z'])
        self.properties_textbox.set(state['properties'])
        self.materials_textbox.set(state['materials'])
        for k, v in state['custom'].items():
            if k in self.custom_fields:
                self.custom_fields[k].set(v)

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.snapshot_form())
            state = self.undo_stack.pop()
            self.restore_form(state)

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.snapshot_form())
            state = self.redo_stack.pop()
            self.restore_form(state)
    
    def validate_form(self):
        """Validate all required fields; return True if all valid."""
        valid = True
        # Name required
        if not self.name_entry.get().strip():
            valid = False
        # Region required
        if not self.region_entry.get().strip():
            valid = False
        # Coordinates: validate and check
        if not self.x_entry.validate():
            valid = False
        if not self.y_entry.validate():
            valid = False
        if not self.z_entry.validate():
            valid = False
        return valid
    
    def auto_save_draft(self):
        """Periodically save form state to draft file."""
        try:
            state = self.snapshot_form()
            state['planets'] = list(self.planets)
            state['photo'] = self.photo_rel_path
            with open(self.draft_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
        except Exception:
            logging.exception("Auto-save draft failed")
        # Schedule next auto-save
        self.after(30000, self.auto_save_draft)
    
    def restore_draft_if_exists(self):
        """Prompt user to restore draft if it exists."""
        try:
            if not self.draft_file.exists():
                return
            confirm = messagebox.askyesno(
                "Restore Draft",
                "A draft system entry was found. Would you like to restore it?"
            )
            if not confirm:
                self.draft_file.unlink()
                return
            with open(self.draft_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            # Restore form
            self.name_entry.set(state.get('name', ''))
            self.region_entry.set(state.get('region', ''))
            self.x_entry.set(state.get('x', ''))
            self.y_entry.set(state.get('y', ''))
            self.z_entry.set(state.get('z', ''))
            self.properties_textbox.set(state.get('properties', ''))
            self.materials_textbox.set(state.get('materials', ''))
            # Restore planets
            self.planets = state.get('planets', [])
            self.render_planets()
            # Restore photo
            photo = state.get('photo', '')
            if photo:
                self.photo_rel_path = photo
                self.photo_path_label.configure(text=photo)
            # Restore custom fields
            for k, v in state.get('custom', {}).items():
                if k in self.custom_fields:
                    self.custom_fields[k].set(v)
        except Exception:
            logging.exception("Failed to restore draft")
    
    def open_settings(self):
        """Open the settings/preferences dialog for theme switching."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Settings & Preferences")
        dialog.geometry("400x300")
        dialog.configure(fg_color=COLORS['bg_dark'])

        label = ctk.CTkLabel(
            dialog,
            text="Theme:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['accent_cyan']
        )
        label.pack(pady=(30, 10))

        # Load current theme from settings
        current_theme = load_settings().get("theme", "Dark")
        theme_var = ctk.StringVar(value=current_theme if current_theme in THEMES else "Dark")

        def set_theme():
            choice = theme_var.get()
            mode, color = THEMES.get(choice, ("dark", "blue"))
            ctk.set_appearance_mode(mode)
            ctk.set_default_color_theme(color)
            save_settings({"theme": choice})
            # Apply token overlay now; full effect may require restart
            apply_theme_tokens(choice)
            try:
                messagebox.showinfo("Theme Applied", "Theme saved. Some elements may update on next launch.")
            except Exception:
                pass

        for theme in THEMES:
            btn = ctk.CTkRadioButton(
                dialog,
                text=theme,
                variable=theme_var,
                value=theme,
                command=set_theme
            )
            btn.pack(anchor="w", padx=40)

        close_btn = ctk.CTkButton(
            dialog,
            text="Close",
            command=dialog.destroy,
            height=40,
            corner_radius=10,
            fg_color=COLORS['bg_card'],
            hover_color=COLORS['accent_purple']
        )
        close_btn.pack(pady=(40, 10), padx=20, fill="x")
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # Main container with animated background
        main_container = ctk.CTkFrame(self, fg_color=COLORS['bg_dark'])
        main_container.pack(fill="both", expand=True)
        
        # Left sidebar
        sidebar = ctk.CTkFrame(
            main_container,
            width=250,
            fg_color=COLORS['glass'],
            corner_radius=0
        )
        sidebar.pack(side="left", fill="y", padx=0, pady=0)
        sidebar.pack_propagate(False)
        
        # Logo/Title in sidebar
        logo_label = ctk.CTkLabel(
            sidebar,
            text="✨ HAVEN\nSYSTEM ENTRY",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=COLORS['accent_cyan'],
            justify="center"
        )
        logo_label.pack(pady=(40, 20))
        
        divider = ctk.CTkFrame(sidebar, height=2, fg_color=COLORS['accent_cyan'])
        divider.pack(fill="x", padx=20, pady=10)
        
        # Sidebar buttons
        btn_save = ctk.CTkButton(
            sidebar,
            text="💾 Save System",
            command=self.save_system,
            height=50,
            corner_radius=10,
            fg_color=COLORS['success'],
            hover_color="#00cc70",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        )
        btn_save.pack(padx=20, pady=10, fill="x")

        btn_fields = ctk.CTkButton(
            sidebar,
            text="⚙️ Manage Fields",
            command=self.open_field_manager,
            height=50,
            corner_radius=10,
            fg_color=COLORS['accent_purple'],
            hover_color=COLORS['accent_pink'],
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        )
        btn_fields.pack(padx=20, pady=10, fill="x")

        btn_clear = ctk.CTkButton(
            sidebar,
            text="🔄 Clear Form",
            command=self.clear_form,
            height=50,
            corner_radius=10,
            fg_color=COLORS['bg_card'],
            hover_color=COLORS['glass'],
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        )
        btn_clear.pack(padx=20, pady=10, fill="x")

        btn_settings = ctk.CTkButton(
            sidebar,
            text="🛠️ Settings",
            command=self.open_settings,
            height=50,
            corner_radius=10,
            fg_color=COLORS['accent_cyan'],
            hover_color=COLORS['accent_purple'],
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        )
        btn_settings.pack(padx=20, pady=10, fill="x")
        
        # Regen map checkbox
        self.regen_var = ctk.BooleanVar(value=True)
        regen_check = ctk.CTkCheckBox(
            sidebar,
            text="Auto-regenerate map",
            variable=self.regen_var,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=COLORS['accent_cyan'],
            hover_color=COLORS['glow']
        )
        regen_check.pack(padx=20, pady=(40, 10))

        # Accessibility toggle
        self.a11y_var = ctk.BooleanVar(value=False)
        def toggle_a11y():
            try:
                ctk.set_widget_scaling(1.2 if self.a11y_var.get() else 1.0)
            except Exception:
                pass
        a11y_check = ctk.CTkCheckBox(
            sidebar,
            text="Large text (A11y)",
            variable=self.a11y_var,
            command=toggle_a11y,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=COLORS['accent_cyan'],
            hover_color=COLORS['glow']
        )
        a11y_check.pack(padx=20, pady=(0, 10))
        
        # Stats at bottom
        stats_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        stats_frame.pack(side="bottom", padx=20, pady=20)
        
        stats_label = ctk.CTkLabel(
            stats_frame,
            text="📊 Statistics",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS['text_secondary']
        )
        stats_label.pack(pady=(0, 10))
        
        self.stats_text = ctk.CTkLabel(
            stats_frame,
            text="Loading...",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS['text_secondary'],
            justify="left"
        )
        self.stats_text.pack()
        
        # Right content area with scrollable form and a contextual help panel
        content_container = ctk.CTkFrame(main_container, fg_color=COLORS['bg_dark'])
        content_container.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkLabel(
            content_container,
            text="🌌 Add New Star System",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=COLORS['text_primary']
        )
        header.pack(pady=(0, 5), anchor="w")
        
        subtitle = ctk.CTkLabel(
            content_container,
            text="Enter system data and custom attributes",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS['text_secondary']
        )
        subtitle.pack(pady=(0, 20), anchor="w")
        
        # Two-column: left scrollable form, right help panel
        holder = ctk.CTkFrame(content_container, fg_color="transparent")
        holder.pack(fill="both", expand=True)

        self.scroll_frame = ctk.CTkScrollableFrame(
            holder,
            fg_color="transparent",
            width=800,
            scrollbar_button_color=COLORS['accent_cyan'],
            scrollbar_button_hover_color=COLORS['glow']
        )
        self.scroll_frame.pack(side="left", fill="both", expand=True)

        # Contextual help panel (updates on field focus)
        help_panel = GlassCard(holder, title="❓ Help & Examples")
        help_panel.pack(side="right", fill="y", padx=(12, 0))
        self.help_title = ctk.CTkLabel(
            help_panel,
            text="Focus a field to see tips",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS['accent_cyan']
        )
        self.help_title.pack(padx=16, pady=(8, 6), anchor="w")
        self.help_body = ctk.CTkTextbox(
            help_panel,
            height=300,
            corner_radius=10,
            fg_color=COLORS['bg_dark'],
            text_color=COLORS['text_secondary'],
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.help_body.pack(padx=16, pady=(0, 16), fill="both", expand=True)
        
        # Default help content with keyboard shortcuts
        default_help = """📋 Quick Start Guide

• Focus any field to see specific tips
• All required fields marked with *
• Use N/A for unknown/empty values

⌨️ Keyboard Shortcuts:
  Ctrl+S  →  Save system
  Ctrl+Z  →  Undo changes
  Ctrl+Y  →  Redo changes
  Ctrl+N  →  Clear form
  Tab     →  Navigate fields
  Enter   →  Add planet (on planet input)

💾 Auto-save:
  Draft saved every 30 seconds
  Restore prompt on next launch

✨ Tips:
  • Coordinates accept decimals (e.g., -1.5)
  • Validation runs in real-time
  • Red border = invalid input
  • Photo auto-copies to photos/ folder
"""
        self.help_body.insert("1.0", default_help)
        self.help_body.configure(state="disabled")

        def register_help(widget, field_key, title, body):
            def on_focus(_e=None):
                try:
                    self.help_body.configure(state="normal")
                    self.help_body.delete("1.0", "end")
                    t, b = self.get_schema_help(field_key, title, body)
                    self.help_title.configure(text=t)
                    self.help_body.insert("1.0", b)
                finally:
                    self.help_body.configure(state="disabled")
            widget.bind('<FocusIn>', on_focus)
        
        # Basic Info Card
        basic_card = GlassCard(self.scroll_frame, title="📝 Basic Information")
        basic_card.pack(fill="x", pady=(0, 20))
        
        basic_grid = ctk.CTkFrame(basic_card, fg_color="transparent")
        basic_grid.pack(padx=20, pady=(0, 20), fill="x")
        
        self.name_entry = ModernEntry(
            basic_grid,
            label="System Name *",
            placeholder="e.g., Alpha Centauri"
        )
        self.name_entry.pack(fill="x", pady=(0, 15))
        register_help(self.name_entry.entry, "name", "System Name", "Name of the star system.\nExample: OOTLEFAR V")
        
        self.region_entry = ModernEntry(
            basic_grid,
            label="Region *",
            placeholder="e.g., Core Worlds"
        )
        self.region_entry.pack(fill="x", pady=(0, 15))
        register_help(self.region_entry.entry, "region", "Region", "Grouping of systems used in the Galaxy view.\nExample: Adam")
        
        # Coordinates Card
        coords_card = GlassCard(self.scroll_frame, title="🎯 Coordinates")
        coords_card.pack(fill="x", pady=(0, 20))
        
        coords_grid = ctk.CTkFrame(coords_card, fg_color="transparent")
        coords_grid.pack(padx=20, pady=(0, 20), fill="x")
        
        coords_row = ctk.CTkFrame(coords_grid, fg_color="transparent")
        coords_row.pack(fill="x")
        
        coord_frame_x = ctk.CTkFrame(coords_row, fg_color="transparent")
        coord_frame_x.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        self.x_entry = ModernEntry(coord_frame_x, label="X Coordinate *", placeholder="0.0", validate_type="number")
        self.x_entry.pack(fill="x")
        register_help(self.x_entry.entry, "x", "X Coordinate", "Cartesian X coordinate (decimal).\nExample: 1.0")
        
        coord_frame_y = ctk.CTkFrame(coords_row, fg_color="transparent")
        coord_frame_y.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        self.y_entry = ModernEntry(coord_frame_y, label="Y Coordinate *", placeholder="0.0", validate_type="number")
        self.y_entry.pack(fill="x")
        register_help(self.y_entry.entry, "y", "Y Coordinate", "Cartesian Y coordinate (decimal).\nExample: -3.0")
        
        coord_frame_z = ctk.CTkFrame(coords_row, fg_color="transparent")
        coord_frame_z.pack(side="left", expand=True, fill="x")
        
        self.z_entry = ModernEntry(coord_frame_z, label="Z Coordinate *", placeholder="0.0", validate_type="number")
        self.z_entry.pack(fill="x")
        register_help(self.z_entry.entry, "z", "Z Coordinate", "Cartesian Z coordinate (decimal).\nExample: 2.0")

        # Environment Card (Sentinel, Fauna, Flora)
        env_card = GlassCard(self.scroll_frame, title="🛰️ Environment & Conditions")
        env_card.pack(fill="x", pady=(0, 20))

        env_grid = ctk.CTkFrame(env_card, fg_color="transparent")
        env_grid.pack(padx=20, pady=(0, 20), fill="x")

        # Sentinel dropdown
        sentinel_row = ctk.CTkFrame(env_grid, fg_color="transparent")
        sentinel_row.pack(fill="x", pady=(0, 10))
        sentinel_label = ctk.CTkLabel(sentinel_row, text="Sentinel Level *", text_color=COLORS['text_secondary'])
        sentinel_label.pack(anchor="w")
        self.sentinel_var = ctk.StringVar(value="Low")
        self.sentinel_menu = ctk.CTkOptionMenu(
            sentinel_row,
            values=["None", "Low", "Medium", "High", "Aggressive", "N/A"],
            variable=self.sentinel_var,
            fg_color=COLORS['bg_card'],
            button_color=COLORS['accent_cyan']
        )
        self.sentinel_menu.pack(fill="x")
        register_help(self.sentinel_menu, "sentinel", "Sentinel Level", "Presence and aggressiveness of sentinels.\nChoose from: None, Low, Medium, High, Aggressive, N/A")

        # Fauna dropdown
        fauna_row = ctk.CTkFrame(env_grid, fg_color="transparent")
        fauna_row.pack(fill="x", pady=(0, 10))
        fauna_label = ctk.CTkLabel(fauna_row, text="Fauna *", text_color=COLORS['text_secondary'])
        fauna_label.pack(anchor="w")
        self.fauna_var = ctk.StringVar(value="N/A")
        self.fauna_menu = ctk.CTkOptionMenu(
            fauna_row,
            values=["N/A", "None", "Low", "Mid", "High", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
            variable=self.fauna_var,
            fg_color=COLORS['bg_card'],
            button_color=COLORS['accent_cyan']
        )
        self.fauna_menu.pack(fill="x")
        register_help(self.fauna_menu, "fauna", "Fauna", "Quantity or level of wildlife.\nPick a value or 'N/A'.")

        # Flora dropdown
        flora_row = ctk.CTkFrame(env_grid, fg_color="transparent")
        flora_row.pack(fill="x", pady=(0, 10))
        flora_label = ctk.CTkLabel(flora_row, text="Flora *", text_color=COLORS['text_secondary'])
        flora_label.pack(anchor="w")
        self.flora_var = ctk.StringVar(value="N/A")
        self.flora_menu = ctk.CTkOptionMenu(
            flora_row,
            values=["N/A", "None", "Low", "Mid", "High"],
            variable=self.flora_var,
            fg_color=COLORS['bg_card'],
            button_color=COLORS['accent_cyan']
        )
        self.flora_menu.pack(fill="x")
        register_help(self.flora_menu, "flora", "Flora", "Plant life level.\nPick: None, Low, Mid, High, N/A")

        # Planets Card (interactive list)
        planets_card = GlassCard(self.scroll_frame, title="🪐 Planets")
        planets_card.pack(fill="x", pady=(0, 20))

        planets_grid = ctk.CTkFrame(planets_card, fg_color="transparent")
        planets_grid.pack(padx=20, pady=(0, 10), fill="x")
        self.planet_entry = ModernEntry(planets_grid, label="Add Planet", placeholder="e.g., Terra")
        self.planet_entry.pack(fill="x")
        btn_row = ctk.CTkFrame(planets_grid, fg_color="transparent")
        btn_row.pack(fill="x", pady=(8, 0))
        add_btn = ctk.CTkButton(btn_row, text="➕ Add Planet", command=self.add_planet, height=36, corner_radius=8,
                                 fg_color=COLORS['accent_cyan'], hover_color=COLORS['glow'])
        add_btn.pack(side="left")
        clear_btn = ctk.CTkButton(btn_row, text="🗑️ Clear List", command=self.clear_planets, height=36, corner_radius=8,
                                   fg_color=COLORS['bg_card'], hover_color=COLORS['accent_purple'])
        clear_btn.pack(side="left", padx=(8, 0))
        self.planets_list_container = ctk.CTkFrame(planets_card, fg_color="transparent")
        self.planets_list_container.pack(padx=20, pady=(8, 16), fill="x")
        register_help(self.planet_entry.entry, "planets", "Planets", "Add planets one at a time (press Add).\nThey will appear as a list below.")
        
        # Properties Card
        props_card = GlassCard(self.scroll_frame, title="🔮 Properties")
        props_card.pack(fill="x", pady=(0, 20))
        
        self.properties_textbox = ModernTextbox(
            props_card,
            label="System Properties",
            placeholder="e.g., Habitable planets, space stations, trade routes...",
            height=100
        )
        self.properties_textbox.pack(padx=20, pady=(0, 20), fill="x")
        register_help(self.properties_textbox.textbox, "properties", "Properties", "Freeform notes about notable features.\nExample: 'Trade hub; 2 stations'. Use 'N/A' if none.")
        
        # Materials Card
        materials_card = GlassCard(self.scroll_frame, title="⚗️ Resources & Materials")
        materials_card.pack(fill="x", pady=(0, 20))
        
        self.materials_textbox = ModernTextbox(
            materials_card,
            label="Available Materials",
            placeholder="e.g., Ore deposits, rare elements, energy sources...",
            height=100
        )
        self.materials_textbox.pack(padx=20, pady=(0, 20), fill="x")
        register_help(self.materials_textbox.textbox, "materials", "Materials", "Important resources available.\nExample: 'Magnetized ferrite, Gold, Cadmium'. Use 'N/A' if unknown.")

        # Base & Photo Card
        base_card = GlassCard(self.scroll_frame, title="🏠 Base & Photo")
        base_card.pack(fill="x", pady=(0, 20))

        base_grid = ctk.CTkFrame(base_card, fg_color="transparent")
        base_grid.pack(padx=20, pady=(0, 10), fill="x")

        self.base_entry = ModernEntry(base_grid, label="Base Location *", placeholder="e.g., VH (+3.86, -129.37) or N/A")
        self.base_entry.pack(fill="x", pady=(0, 10))
        register_help(self.base_entry.entry, "base_location", "Base Location", "Where your base is in this system.\nExample: 'VH (+3.86, -129.37)'. Use 'N/A' if none.")

        photo_row = ctk.CTkFrame(base_card, fg_color="transparent")
        photo_row.pack(padx=20, pady=(6, 10), fill="x")
        photo_label = ctk.CTkLabel(photo_row, text="System Photo", text_color=COLORS['text_secondary'])
        photo_label.pack(anchor="w")

        btns = ctk.CTkFrame(base_card, fg_color="transparent")
        btns.pack(padx=20, pady=(0, 6), fill="x")
        choose_local = ctk.CTkButton(btns, text="📂 Choose from photos/", command=self.pick_photo_from_photos,
                                     height=36, corner_radius=8, fg_color=COLORS['bg_card'], hover_color=COLORS['accent_purple'])
        choose_local.pack(side="left")
        browse_any = ctk.CTkButton(btns, text="🖼️ Browse…", command=self.browse_any_photo,
                                   height=36, corner_radius=8, fg_color=COLORS['accent_cyan'], hover_color=COLORS['glow'])
        browse_any.pack(side="left", padx=(8, 0))
        self.photo_path_label = ctk.CTkLabel(base_card, text="No photo selected (use N/A if none)",
                                             text_color=COLORS['text_secondary'])
        self.photo_path_label.pack(padx=20, pady=(4, 12), anchor="w")
        register_help(choose_local, "photo", "Photo", "Choose a PNG/JPG from the local 'photos/' folder, or browse to any file.\nWe'll copy it into 'photos/' and link it as photos/<name>.")
        
        # Custom Fields Card (dynamically populated)
        self.custom_card = GlassCard(self.scroll_frame, title="✨ Custom Fields")
        self.custom_card.pack(fill="x", pady=(0, 20))
        
        self.custom_fields_container = ctk.CTkFrame(self.custom_card, fg_color="transparent")
        self.custom_fields_container.pack(padx=20, pady=(0, 20), fill="x")
        
        # Update stats
        self.update_stats()
    
    def load_data(self):
        """Load data from JSON file (returns data array only)"""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                obj = json.load(f)
                return obj.get('data', [])
        return []
    
    def save_data(self, data):
        """Save data to JSON file with backup, preserving _meta"""
        # Create backup
        if self.data_file.exists():
            backup_file = self.data_file.with_suffix('.json.bak')
            shutil.copy2(self.data_file, backup_file)
        # Load meta if present
        meta = {"version": "1.0.0"}
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                try:
                    obj = json.load(f)
                    if isinstance(obj, dict) and '_meta' in obj:
                        meta = obj['_meta']
                except Exception:
                    pass
        # Save data
        with open(self.data_file, 'w') as f:
            json.dump({"_meta": meta, "data": data}, f, indent=2)
    
    def refresh_custom_fields(self):
        """Refresh custom fields UI"""
        # Clear existing custom fields
        for widget in self.custom_fields_container.winfo_children():
            widget.destroy()
        
        self.custom_fields.clear()
        
        # Get all custom fields from data
        data = self.load_data()
        custom_field_names = set()
        
        # Data is a flat list
        for item in data:
            if item.get("type") != "region":  # Skip region markers
                for key in item.keys():
                    if key not in ['id', 'name', 'region', 'x', 'y', 'z', 'type', 'properties', 'materials']:
                        custom_field_names.add(key)
        
        # Create UI for each custom field
        if custom_field_names:
            for field_name in sorted(custom_field_names):
                entry = ModernEntry(
                    self.custom_fields_container,
                    label=field_name,
                    placeholder=f"Enter {field_name}..."
                )
                entry.pack(fill="x", pady=(0, 15))
                self.custom_fields[field_name] = entry
        else:
            no_fields_label = ctk.CTkLabel(
                self.custom_fields_container,
                text="No custom fields yet. Use 'Manage Fields' to add some!",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=COLORS['text_secondary']
            )
            no_fields_label.pack(pady=20)
    
    def update_stats(self):
        """Update statistics display"""
        data = self.load_data()
        
        # Count regions and systems from flat list
        regions = set()
        systems = 0
        
        for item in data:
            if item.get("type") == "region":
                regions.add(item.get("region"))
            else:
                systems += 1
                if item.get("region"):
                    regions.add(item.get("region"))
        
        stats_text = f"Regions: {len(regions)}\nSystems: {systems}"
        self.stats_text.configure(text=stats_text)
    
    def save_system(self):
        """Save the current system"""
        # Validate all fields
        if not self.validate_form():
            messagebox.showerror("Validation Error", "Please fix the errors highlighted in red before saving.")
            return
        
        # Validate required fields
        name = self.name_entry.get().strip()
        region = self.region_entry.get().strip()
        
        if not name or not region:
            messagebox.showerror("Error", "System name and region are required!")
            return
        
        # Validate coordinates (should already be validated, but double-check)
        try:
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
            z = float(self.z_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Coordinates must be valid numbers!")
            return
        
        # Build system data (flat structure)
        system_data = {
            "id": f"SYS_{region.upper().replace(' ', '_')}_{int(time.time())}",
            "name": name,
            "region": region,
            "x": x,
            "y": y,
            "z": z
        }

        # Environment (required by policy: ensure values)
        sentinel = (self.sentinel_var.get() or "N/A").strip()
        fauna = (self.fauna_var.get() or "N/A").strip()
        flora = (self.flora_var.get() or "N/A").strip()
        system_data["sentinel"] = sentinel or "N/A"
        system_data["fauna"] = fauna or "N/A"
        system_data["flora"] = flora or "N/A"
        
        # Add optional fields if not empty
        properties = self.properties_textbox.get().strip() or "N/A"
        system_data["properties"] = properties

        materials = self.materials_textbox.get().strip() or "N/A"
        system_data["materials"] = materials

        # Base location (required by policy; allow N/A)
        base_loc = self.base_entry.get().strip() or "N/A"
        system_data["base_location"] = base_loc

        # Planets list (allow empty list)
        if self.planets:
            system_data["planets"] = list(self.planets)

        # Photo
        photo_value = (self.photo_rel_path or "").strip()
        if photo_value:
            system_data["photo"] = photo_value
        else:
            system_data["photo"] = "N/A"
        
        # Add custom fields
        for field_name, entry in self.custom_fields.items():
            value = entry.get().strip()
            if value:
                system_data[field_name] = value
        
        # Load existing data
        data = self.load_data()

        # Check if region marker exists
        region_exists = False
        for item in data:
            if item.get("type") == "region" and item.get("region") == region:
                region_exists = True
                break

        # If not, create a region marker (default coords 0.0)
        if not region_exists:
            region_marker = {
                "type": "region",
                "region": region,
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            }
            data.append(region_marker)

        # Check for duplicate system
        for i, item in enumerate(data):
            if item.get("name") == name and item.get("region") == region and item.get("type") != "region":
                confirm = messagebox.askyesno(
                    "Duplicate System",
                    f"System '{name}' already exists in '{region}'. Overwrite?"
                )
                if confirm:
                    data[i] = system_data
                    self.save_data(data)
                    self.show_success_animation()
                    if self.regen_var.get():
                        self.regenerate_map()
                    self.clear_form()
                    self.update_stats()
                return

        # Add new system to flat list
        data.append(system_data)

        # Save data
        self.save_data(data)
        
        # Delete draft on successful save
        try:
            if self.draft_file.exists():
                self.draft_file.unlink()
        except Exception:
            logging.exception("Failed to delete draft file")

        # Show success with animation
        self.show_success_animation()

        # Regenerate map if requested
        if self.regen_var.get():
            self.regenerate_map()

        # Clear form
        self.clear_form()
        # Reset model extras
        self.planets = []
        self.render_planets()
        self.photo_rel_path = ""
        self.photo_path_label.configure(text="No photo selected (use N/A if none)")

        # Update stats
        self.update_stats()
    
    def show_success_animation(self):
        """Show success message with fade effect"""
        success_window = ctk.CTkToplevel(self)
        success_window.title("")
        success_window.geometry("400x200")
        success_window.configure(fg_color=COLORS['bg_dark'])
        success_window.attributes('-topmost', True)
        
        # Center on screen
        success_window.update_idletasks()
        x = (success_window.winfo_screenwidth() // 2) - 200
        y = (success_window.winfo_screenheight() // 2) - 100
        success_window.geometry(f"+{x}+{y}")
        
        icon = ctk.CTkLabel(
            success_window,
            text="✅",
            font=ctk.CTkFont(size=60)
        )
        icon.pack(pady=(30, 10))
        
        msg = ctk.CTkLabel(
            success_window,
            text="System saved successfully!",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLORS['success']
        )
        msg.pack()
        
        # Auto-close after 1.5 seconds
        success_window.after(1500, success_window.destroy)
    
    def regenerate_map(self):
        """Regenerate the map in background"""
        def regen_thread():
            try:
                # Run with current venv interpreter if possible
                map_script = Path(__file__).parent / "Beta_VH_Map.py"
                cmd = [sys.executable, str(map_script), "--no-open"]
                logs_dir().mkdir(exist_ok=True)
                ts = datetime.now().strftime('%Y-%m-%d_%H%M%S')
                with open(logs_dir() / f'map-regen-{ts}.log', 'w', encoding='utf-8') as lf:
                    proc = subprocess.run(cmd, check=False, stdout=lf, stderr=lf, text=True)
                    if proc.returncode != 0:
                        logging.error("Map regeneration failed with exit code %s", proc.returncode)
            except Exception as e:
                logging.exception("Map regeneration error: %s", e)
        
        thread = threading.Thread(target=regen_thread, daemon=True)
        thread.start()
    
    def clear_form(self):
        """Clear all form fields (with undo support)"""
        self.undo_stack.append(self.snapshot_form())
        self.redo_stack.clear()
        self.name_entry.set("")
        self.region_entry.set("")
        self.x_entry.set("")
        self.y_entry.set("")
        self.z_entry.set("")
        self.properties_textbox.set("")
        self.materials_textbox.set("")
        # Reset environment defaults
        if hasattr(self, 'sentinel_var'):
            self.sentinel_var.set("Low")
        if hasattr(self, 'fauna_var'):
            self.fauna_var.set("N/A")
        if hasattr(self, 'flora_var'):
            self.flora_var.set("N/A")
        if hasattr(self, 'base_entry'):
            self.base_entry.set("")
        for entry in self.custom_fields.values():
            entry.set("")
    
    def open_field_manager(self):
        """Open the field manager dialog"""
        FieldManagerDialog(self)

    # ----------------------- Planets helpers -----------------------
    def add_planet(self):
        name = self.planet_entry.get().strip()
        if not name:
            return
        self.planets.append(name)
        self.planet_entry.set("")
        self.render_planets()

    def clear_planets(self):
        self.planets = []
        self.render_planets()

    def remove_planet(self, name):
        try:
            self.planets.remove(name)
        except ValueError:
            pass
        self.render_planets()

    def render_planets(self):
        for w in self.planets_list_container.winfo_children():
            w.destroy()
        if not self.planets:
            lbl = ctk.CTkLabel(self.planets_list_container, text="No planets added.", text_color=COLORS['text_secondary'])
            lbl.pack(anchor="w")
            return
        for p in self.planets:
            row = ctk.CTkFrame(self.planets_list_container, fg_color="transparent")
            row.pack(fill="x", pady=4)
            lbl = ctk.CTkLabel(row, text=p)
            lbl.pack(side="left")
            btn = ctk.CTkButton(row, text="✖", width=36, height=28, corner_radius=6,
                                 command=lambda n=p: self.remove_planet(n),
                                 fg_color=COLORS['bg_card'], hover_color=COLORS['accent_pink'])
            btn.pack(side="right")

    # ----------------------- Photo helpers -----------------------
    def _photos_dir(self) -> Path:
        # photos/ at project root
        return project_root() / 'photos'

    def _ensure_photos_dir(self):
        try:
            d = self._photos_dir()
            d.mkdir(parents=True, exist_ok=True)
        except Exception:
            logging.exception("Failed to ensure photos directory")

    def pick_photo_from_photos(self):
        self._ensure_photos_dir()
        initial = str(self._photos_dir())
        file = filedialog.askopenfilename(
            title="Choose photo",
            initialdir=initial,
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.webp"), ("All files", "*.*")]
        )
        if not file:
            return
        try:
            # If inside photos/, keep relative path
            file_path = Path(file)
            photos = self._photos_dir()
            try:
                rel = file_path.relative_to(photos)
                self.photo_rel_path = f"photos/{rel.as_posix()}"
            except ValueError:
                # Outside photos/: copy
                self.photo_rel_path = self._copy_to_photos(file_path)
            self.photo_path_label.configure(text=self.photo_rel_path)
        except Exception:
            logging.exception("Photo selection error")

    def browse_any_photo(self):
        file = filedialog.askopenfilename(
            title="Browse image",
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.webp"), ("All files", "*.*")]
        )
        if not file:
            return
        try:
            p = Path(file)
            self._ensure_photos_dir()
            self.photo_rel_path = self._copy_to_photos(p)
            self.photo_path_label.configure(text=self.photo_rel_path)
        except Exception:
            logging.exception("Photo copy error")

    def _copy_to_photos(self, source: Path) -> str:
        photos = self._photos_dir()
        photos.mkdir(parents=True, exist_ok=True)
        name = source.name
        dest = photos / name
        # If collision, add numeric suffix
        stem = dest.stem
        suffix = dest.suffix
        i = 1
        while dest.exists():
            dest = photos / f"{stem}_{i}{suffix}"
            i += 1
        shutil.copy2(str(source), str(dest))
        return f"photos/{dest.name}"


def main():
    """Main entry point"""
    app = SystemEntryApp()
    app.mainloop()


if __name__ == "__main__":
    main()
