# Haven UI Consistency Audit

Summary: This audit identifies codebase inconsistencies that hurt the fluidity of the UI and backend, particularly around storage (JSON vs SQLite), multiple database filenames/locations, and deprecated code paths. Each finding includes where it was found and concise recommendations to fix it.

---

## 1) Multiple database filenames / duplicate storage

Problem:
- The codebase references multiple distinct database filenames/paths for the SQLite backend, which fragments the canonical 'memory' of the program and can cause inconsistent reads/writes across UI entry points.

Where found:
- `config/settings.py` -> `DATABASE_PATH = data/VH-Database.db` (canonical config)
- `src/common/database.py` -> default: `data/haven.db` (class-level default)
- `Haven-UI` local UI -> `HAVEN_UI_ROOT / 'data' / 'haven_ui.db'` (web UI local DB)
- Tests & migration scripts reference `data/haven.db`, `data/VH-Database.db` and `VH-Database.db`.

Why it hurts:
- Produces separate DBs in different parts of the app, making the app appear to 'have memory' in multiple places.
- Leads to confusion about where the canonical data is stored.
- Tests can pass in one context and fail in another due to different databases.

Recommendation:
- Standardize on a single `DATABASE_PATH` (preferably `data/VH-Database.db` since tests and scripts expect it).
- Change `src/common/database.py` default argument to import and use `config.settings.DATABASE_PATH` instead of a hardcoded `data/haven.db` string.
- Update tests/migration scripts to use settings.DATABASE_PATH or `data/VH-Database.db` explicitly.
- Add a `get_db_path()` helper in `src/common/paths.py` that returns the canonical database path (and use it across the repo).

Suggested code snippet (in `database.py`):
```py
from config.settings import DATABASE_PATH
class HavenDatabase:
    def __init__(self, db_path: str = None):
        self.db_path = Path(db_path or DATABASE_PATH)
```

---

## 2) `get_data_provider()` ignores `use_database` argument and returns DB-only provider

Problem:
- `src/common/data_provider.py` `get_data_provider()` unconditionally returns `DatabaseDataProvider`, ignoring `use_database` and `json_path` arguments.
- `JSONDataProvider` is intentionally marked deprecated and raises `NotImplementedError`, but many subsystems (user edition / tests/dev tools) still call `get_data_provider(use_database=False)` or call the JSON provider explicitly. This creates an API-level mismatch.

Where found:
- `src/common/data_provider.py`: `get_data_provider(...):` always returns `DatabaseDataProvider`
- `config/settings_user.py` and `src/control_room_user.py` expect a JSON data provider for the user edition.
- Tests call `get_data_provider(use_database=False)` expecting JSON behaviour.

Why it hurts:
- Creates confusion for callers. The function's signature suggests support for both backends, but it never returns JSON provider.
- User edition code continues to assume JSON provider exists, but the factory hides that.

Recommendation:
- Either re-enable the JSON provider by implementing a `LightweightJSONDataProvider` or keep `get_data_provider()` returning DB provider but update all callers to use `DatabaseDataProvider` (or `get_data_provider(use_database=True)` consistently).
- Update `config/settings_user.py.get_data_provider()` to not instantiate a deprecated `JSONDataProvider` but to call `get_data_provider(use_database=False)` and rely on a `LightWeightJSONDataProvider` implementation or a wrapper using database fallback.
- Make `get_data_provider()` honor `use_database` and implement `auto_detect_provider` accordingly.

Suggested code snippet (in `data_provider.py`):
```py
if use_database:
    return DatabaseDataProvider(db_path)
else:
    return JSONDataProvider(json_path)
```
- If JSON provider is intentionally deprecated, either fully remove JSON-specific code from `config/settings_user.py` and `control_room_user.py` or implement a working JSON provider.

---

## 3) `JSONDataProvider` is deprecated but still referenced by user edition code

Problem:
- `JSONDataProvider` in `src/common/data_provider.py` raises `NotImplementedError`, but `config/settings_user.py` (and `control_room_user.py`) rely on it for the user edition.

Where found:
- `src/common/data_provider.py` -> `class JSONDataProvider` raises NotImplementedError.
- `config/settings_user.py` -> `get_data_provider()` returns `JSONDataProvider(json_path=...)`.
- `control_room_user.py` uses `get_data_provider()` from `settings_user` to initialize UI provider.

Why it hurts:
- User edition will crash at runtime because the JSON provider can't be instantiated.

Recommendation:
- Implement `JSONDataProvider` for the user-flow or replace the user edition code so it relies on the unified `get_data_provider(use_database=False)` that returns a supported, working JSON provider (or a DB provider with JSON fallback configurations).
- Add tests ensuring `control_room_user` can be booted with user edition settings.

---

## 4) `DataSourceManager` vs `HavenDatabase` default path mismatch

Problem:
- `DataSourceManager` reads `config.settings.DATABASE_PATH` as the production path (VH-Database.db) while `HavenDatabase` defaults to `data/haven.db`. If the provider is instantiated without an explicit path, the wrong DB might be used.

Where found:
- `src/common/data_source_manager.py` uses `DATABASE_PATH` from `config/settings.py`.
- `src/common/database.py` default argument uses `data/haven.db`.

Why it hurts:
- Inconsistent code paths might write/read from different DB files.
- Migration & verification scripts may use one DB file while the app uses another.

Recommendation:
- Standardize the DB path as `config.settings.DATABASE_PATH`;
- Ensure `HavenDatabase` uses `DATABASE_PATH` unless a db_path is explicitly passed.
- Update tests/migration scripts to call `HavenDatabase(str(DATABASE_PATH))` or use helper `get_db_path()`.

---

## 5) `paths.py` user edition: `DATA_DIR` uses bundled path while `FILES_DIR` is writable

Problem:
- `src/common/paths.py` sets `DATA_DIR = BUNDLE_DIR / 'data'` when `IS_USER_EDITION` and `FROZEN` True (PyInstaller). `BUNDLE_DIR` points to the EXE's temporary extraction path while `FILES_DIR` (user-writable) is set to `PROJECT_ROOT / 'files'`. This leads to confusing behavior where the app reads bundled non-writable data but writes user photos/saves into `files/`, keeping files split between read-only bundle and the writable files directory.

Where found:
- `src/common/paths.py` (IS_USER_EDITION + FROZEN branch)

Why it hurts:
- The app may appear to use one dataset while users' new data is stored elsewhere. This is a probable source of 'missing' or 'disappearing' user changes.

Recommendation:
- For frozen (EXE) user edition, set `DATA_DIR` to `FILES_DIR` instead of `BUNDLE_DIR / 'data'` so both data writes and reads operate in the writable files directory.
- If the application requires a bundled default dataset, put a separate `clean_data.json` in the exe and implement an initialization step to copy to `FILES_DIR` on first run.

Suggested change in `paths.py` for frozen user edition:
```py
if IS_USER_EDITION and FROZEN:
    FILES_DIR = PROJECT_ROOT / 'files'
    DATA_DIR = FILES_DIR  # writable
    PHOTOS_DIR = FILES_DIR / 'photos'
``` 
(This ensures that admin actions and user changes end up in the same path.)

---

## 6) Duplicate `photos` and `logs` locations for Desktop vs Web UIs

Problem:
- Web UI (`control_room_api`) maps `HAVEN_UI_ROOT / 'photos'` and `HAVEN_UI_ROOT / 'logs'` as static and log directories while desktop & legacy UI uses `project_root / 'photos'` and `project_root / 'logs'`.

Where found:
- `src/control_room_api.py` mounts `HAVEN_UI_ROOT/photos` and sets cp.PHOTOS_DIR accordingly.
- Desktop `control_room_user` and `SystemEntryWizard` use `photos/` under `project_root`.

Why it hurts:
- Produces two separate photo directories; images uploaded via the web UI are stored in `Haven-UI/photos`, while desktop tools operate on `project_root/photos`. This causes deployed UIs to not see each other's photos.

Recommendation:
- Standardize on a single photos folder (either `project_root/photos` or `Haven-UI/photos`) and make `control_room_api` use the canonical shared location, or add documentation stating clearly which UI uses which photos folder.
- For web UI & API, consider using `DATA_DIR` (or `HAVEN_UI_ROOT` if purpose is local bundle) and add a config setting to unify photo storage.

---

## 7) Export & Packaging paths refer to `config/icons` but icons may be missing

Problem:
- Export scripts refer to icons in `config/icons` (macOS/Windows) but the folder only contains `README.txt`. The code checks `icon.exists()` and behaves accordingly, but missing icons are just allowed.

Where found:
- `src/control_room.py` (`_export_macos`) references `icon = (config_dir() / 'icons' / 'haven.icns')`.
- scripts & docs point to `config/vendor` for 3rd party assets.

Why it hurts:
- Not critical but can cause packaging to miss custom icons; however scripts already handle missing icons gracefully.

Recommendation:
- Add a standard `config/icons/haven.icns` and `haven.ico` to repository or document clearly that those resources are optional and where to place them.

---

## 8) Tests assume different behaviors for JSON provider and DB provider

Problem:
- Tests in `tests/` expect both `JSON` and `database` behaviors (and sometimes expect `JSON provider` to be deprecated). The current `get_data_provider` always returns `DatabaseDataProvider`, and `JSONDataProvider` is not implementable; tests that rely on JSON provider behavior will either be skipped or fail.

Where found:
- `tests/test_phase1.py`, `tests/test_map_data_access.py`, `tests/test_yh_database_integration.py`.

Recommendation:
- Decide on the canonical production mode; if database-only is the new canonical behavior, update tests and user edition to remove JSON provider assumptions; or keep JSON for the user edition but implement `JSONDataProvider` fully and update the factory.

---

## 9) Environment variables & multiple ways to set data directory create ambiguity

Problem:
- The code supports multiple ways of controlling data location (config.settings, `HAVEN_UI_DIR`, `HAVEN_DATA_PATH`, `HAVEN_USER_EDITION`) but these can be set inconsistently which leads to confusion.

Where found:
- `control_room_api.py` uses `HAVEN_UI_DIR` to override directories.
- `control_room_user.py` sets `HAVEN_USER_EDITION = '1'` and `HAVEN_DATA_PATH` sometimes.

Recommendation:
- Document the definitive chain of precedence for settings/env variables, and centralize logic in `src/common/paths.py` (or a new `config/env` module) so all entry points call one canonical function and do not attempt to overwrite `cp.DATA_DIR` directly.

---

## Next Steps & Implementation Plan

1. Create a short PR to standardize DB path and provider factory:
    - Update `HavenDatabase` to default to `config.settings.DATABASE_PATH`.
    - Fix `get_data_provider()` to respect `use_database` and `json_path`/`db_path` arguments.
    - Implement a lightweight JSON provider for user edition OR adjust `settings_user.py` to rely on `get_data_provider(use_database=False)`.

2. Unify photos & logs folder usage across the desktop & web UI, or document clearly the split and purpose.

3. Update `paths.py` for `IS_USER_EDITION` + `FROZEN` to use `FILES_DIR` as `DATA_DIR` to avoid read-only bundle confusion.

4. Update tests to reference `config.settings.DATABASE_PATH` instead of `data/haven.db` and add tests verifying that `get_data_provider(use_database=False)` returns either a JSON provider or a well-defined fallback.

5. Add a `README` or `docs/` short page: Data model & storage decisions (canonical DB filename, user edition folder, photo folder rules).

---

If you'd like, I can create a follow-up PR implementing the recommended changes (e.g., change `Database` default to use `DATABASE_PATH`, implement `get_data_provider` fix, and update `settings_user`), and add tests for these changes. Let me know if you want me to proceed with code modifications.
