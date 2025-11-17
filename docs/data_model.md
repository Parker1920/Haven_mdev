# Haven Data Model & Storage Layout

This document describes the canonical data layout for the Haven Control Room project, including where data is stored, the primary file names and directories, and recommended developer practices to avoid inconsistencies.

## Canonical File & Directory Locations ✅
- Database (recommended production): `data/VH-Database.db` (use `config.settings.DATABASE_PATH` to override)
- JSON (compatible/legacy): `data/data.json`
- Data schema: `data/data.schema.json`
- Static assets (photos): `photos/`
- Distribution & builds: `dist/` and `Haven-UI/dist/`
- Logs: `logs/`

## Helpful path helpers 🔧
Use the path helpers in `src/common/paths.py` whenever you need a path in the codebase:
- `project_root()` -> Root of repo
- `data_dir()` -> `PROJECT_ROOT / 'data'`
- `data_path(name)` -> `PROJECT_ROOT / 'data' / name`
- `photos_dir()` -> `PROJECT_ROOT / 'photos'`
- `database_path()` -> canonical DB path (respects `config.settings.DATABASE_PATH` and `HAVEN_UI_DIR` overrides)

Developer pattern: prefer `database_path()` over `"data/VH-Database.db"` literals.

## Database vs JSON model 💡
- Production (large datasets) should use SQLite database via `src.common.database.HavenDatabase` and `src.common.data_provider.DatabaseDataProvider`.
- The legacy JSON provider still exists for user-edition flows and the public EXE; `JSONDataProvider` reads/writes `data/data.json`. For tests, the JSON provider is optional.
- Use `get_data_provider(use_database=True)` to obtain a DB-backed provider, and `get_data_provider(use_database=False)` for JSON fallback.

## HAVEN-UI (web UI) behavior 🌐
- The web UI can be served locally with `HAVEN_UI_DIR` env var; this isolates the UI to `HAVEN-UI/data` and `Haven-UI/dist`.
- For local web tests, `src/control_room_api.py` may use `HAVEN_UI_DIR / 'data' / 'haven_ui.db'` to separate web UI DB from master DB.

## Tests & Scripts Guidance 🧪
- Prefer `from src.common.paths import database_path` and create DBs with `HavenDatabase(str(database_path()))` in tests and scripts.
- Avoid hard-coded `"data/haven.db"` or `"data/VH-Database.db"` strings; use `database_path()` for consistency.
- If tests need an isolated DB for deterministic assertions, create a test DB under `tests/data/` and inject its path via `HavenDatabase(test_db_path)`.

## Migration & Backups 🔁
- Migration tools reside in `Archive-Dump/` and `src/migration/`.
- When writing the `data.json` or `data/VH-Database.db`, the UI code creates backups `data/data.json.bak` or `.json.bak` as appropriate — do not bypass backup steps during automation unless intentional.

## Troubleshooting 404 / 500 map viewer errors (brief) 🔎
Common reasons for viewer errors:
- Generated map files are written to a `dist/` not mounted by the server (mismatch between generator `dist/` path and `control_room_api.py` static mounts).
- Incorrect `HAVEN_UI_DIR` overrides when map generation expects `Haven-UI/dist` but server mounts a different directory.
- Using a DB path mismatch where the web UI expects `haven_ui.db` under HAVEN_UI_DIR, but generator writes to `data/VH-Database.db`.

Recommendations:
- Run `scripts/check_paths.py` to print canonical paths used in your environment.
- Ensure `HAVEN_UI_DIR` is set when you run `control_room_api.py` if you're testing the web UI locally.

Map generation endpoints (web API):
- POST /api/generate_map: Queues map generation using Beta_VH_Map; prefer DB when available. The endpoint picks `HAVEN-UI/data/haven_ui.db` (if present) else `HAVEN-UI/data/data.json` else main DB.
- GET /api/map_status: Returns a JSON response indicating whether `VH-Map.html` was generated and its last-modified timestamp.

## Summary
- Standardize on `data/VH-Database.db` for production DB unless otherwise configured by `config.settings.DATABASE_PATH`.
- Use `database_path()` helper and `src.common.paths` helpers throughout the code to avoid path drift.
- When adding scripts or tests, prefer explicit `db_path` parameters and isolated test DBs for deterministic results.

If you want, I can add a short example showing `HavenDatabase(str(database_path()))` usage in the README and update more docs referencing the old `data/haven.db` string.
