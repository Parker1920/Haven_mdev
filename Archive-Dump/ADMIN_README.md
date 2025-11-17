Archive: Admin & Migration Tools
================================

This document explains how to use archived migration and import tools from the `Archive-Dump` when working with legacy JSON exports or performing one-time migrations.

Important: These tools are deprecated and **not** part of the active web-first runtime. They are safe to use locally for migration or auditing purposes but should be used with caution.

Common files
------------
- `Archive-Dump/src/migration/json_to_sqlite.py` — One-time JSON → SQLite migrator
- `Archive-Dump/src/migration/import_json.py` — JSON import for public EXE exports
- `Archive-Dump/src/migration/sync_data.py` — Bidirectional sync utility (JSON ↔ DB)

Recommended flow to migrate JSON → DB safely
------------------------------------------
1. Backup your active database:

```powershell
copy data\haven.db data\backups\haven.db.bak
```

2. Run the JSON → SQLite migrator locally with the same Python environment used by the server:

```powershell
py Archive-Dump\src\migration\json_to_sqlite.py --force --json data\data.json --db data\haven.db
```

3. Verify data and run tests locally.

Using sync tools
----------------
The archived `sync_data.py` allows checking and syncing between JSON and DB — but is a legacy tool. Use it for offline reconciliation only.

Admin token and API usage
-------------------------
Prefer the admin API endpoints for day-to-day admin tasks: use `HAVEN_ADMIN_TOKEN` for POST requests to `/api/settings`, `/api/db_upload`, `/api/data_sources/current`.

If you need help migrating data or running archived tools safely, see the comprehensive migration guide in `docs/scaling` and reach out to the team.
