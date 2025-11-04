## Quick orientation for AI coding agents

This repo is the Haven Control Room — a Python desktop GUI (CustomTkinter) + map generator + iOS PWA exporter. The goal of this file is to give an AI agent the minimal, precise knowledge to be productive immediately.

Key components
- `src/control_room.py` — main desktop UI (entrypoint). Uses CustomTkinter and implements the Export / Generate Map actions. Supports alternate frozen entries via `--entry` (control/system/map).
- `src/system_entry_wizard.py` — two‑page System Entry UI (wizard) that reads/writes `data/data.json`. Uses helper widgets (`ModernEntry`, `ModernTextbox`, `PlanetMoonEditor`) and preserves backwards compatibility with legacy data shapes.
- `src/Beta_VH_Map.py` — map generator; produces `dist/VH-Map.html` (use `--no-open` to run headless).
- `src/generate_ios_pwa.py` — builds the iOS PWA HTML. Called by control room export logic.
- `src/common/paths.py` — canonical path helpers. Always use these helpers (`project_root()`, `data_dir()`, `data_path(name)`, `dist_dir()`, `logs_dir()`) instead of hard-coding paths.

Data model and migration notes
- Primary data file: `data/data.json`. The code accepts three discoverable formats:
  - New top-level map form (preferred): top-level keys are system names (value is an object with x,y,z,planets...)
  - `{"systems": {...}}` wrapper (older)
  - Legacy `{"data": [...]}` list
- Conversions and saving: `SystemEntryWizard.save_system()` prefers top-level map and creates `.json.bak` backups before overwriting.

Packaging and frozen (PyInstaller) behavior
- `common.paths.FROZEN` toggles behavior. When testing locally, `FROZEN` is False and `dist/` is used. When running a PyInstaller bundle, `FROZEN` is True and the executable's folder becomes the base.
- Hidden imports and packaging hints are embedded in `control_room._export_windows` / `_export_macos`. If you modify entry modules, add them to PyInstaller `--hidden-import` there.
- Alternate process entries when frozen: pass `--entry system` or `--entry map` to the EXE, or use `python src/control_room.py --entry system` when running from source.

Developer workflows (commands you can run locally)
- Create venv and install:
```bash
python -m venv .venv
source .venv/bin/activate   # zsh / macOS
pip install -r config/requirements.txt
```
- Run Control Room (source):
```bash
python src/control_room.py
```
- Run System Entry Wizard directly:
```bash
python src/system_entry_wizard.py
```
- Generate map headless:
```bash
python src/Beta_VH_Map.py --no-open
```
- Create iOS PWA bundle (writes to `dist/` by default):
```bash
python src/generate_ios_pwa.py   # or use Control Room Export → iOS
```
- Run tests (pytest):
```bash
pytest -q tests/   # repository contains validation tests under tests/
```

Patterns and conventions specific to this repo
- UI components: prefer existing small reusable widgets (`GlassCard`, `ModernEntry`, `ModernTextbox`) when adding new form fields so styling/validation is consistent.
- Validation: `ModernEntry.validate()` is used for numeric/required checks — call `.validate()` before saving coordinates or when programmatically setting values.
- File copies: user-supplied images are copied to `photos/` and referenced as `photos/<name>`; keep that pattern to avoid path breakage.
- Logging: modules use `logging` with rotating file handlers writing into `logs/`. Use `logging.info/debug/error` — logs are consumed by the UI for user-visible messages.
- Backups: when writing `data.json` the UI writes a `.json.bak` next to it. Preserve the backup step for safe edits.

Quick pointers for edits and PRs
- If you change the public data shape, update both `system_entry_wizard.get_existing_systems()` and `save_system()` to maintain migration heuristics and preserve legacy formats.
- When adding CLI flags or alternate entries, update `control_room.main()` argparse choices and add the necessary `runpy.run_module(...)` logic for frozen entry dispatch.
- When changing packaging or adding binary resources (icons, vendor libs), reference `config/icons/` and `config/vendor/` — `control_room._export_*` looks there.

Files to read first (examples)
- `src/control_room.py` — UI, exports, packaging examples
- `src/system_entry_wizard.py` — data flows, validations, legacy conversion
- `src/common/paths.py` — path handling and frozen vs source modes
- `data/data.json` and `data.schema.json` — canonical data and schema
- `README.md` and `docs/Comprehensive_User_Guide.md` — high-level workflows and expected UX

If anything in this file is unclear or you need extra examples (unit tests, common refactors, or typical PR templates), tell me which section to expand and I'll iterate.
