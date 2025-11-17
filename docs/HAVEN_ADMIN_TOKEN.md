## HAVEN_ADMIN_TOKEN - Admin usage & security

Overview
--------
The Haven Control Room web API supports admin-only actions that can be enabled by setting the `HAVEN_ADMIN_TOKEN` environment variable for the server process.

How it works
------------
- The server reads the `HAVEN_ADMIN_TOKEN` environment variable on startup.
- The web API checks the `X-HAVEN-ADMIN` or `X-Haven-Admin` request header value and matches it against the token.
- If the token is not configured, admin-only actions are allowed (for development convenience). If you want production safety, set `HAVEN_ADMIN_TOKEN`.

Common admin actions
--------------------
- Save settings (POST /api/settings) — Requires the `X-HAVEN-ADMIN` header.
- Upload database (POST /api/db_upload) — Admin-only.
- Switch data source (POST /api/data_sources/current) — Admin-only.

How to set token (Windows PowerShell)
------------------------------------
```powershell
setx HAVEN_ADMIN_TOKEN "your-strong-secret" -m
# Restart the server/PowerShell before the value is available to the process
```

How to call admin endpoints
---------------------------
Add the header `X-HAVEN-ADMIN: your-strong-secret` to your POST requests. Example curl:
```bash
curl -X POST http://localhost:8000/api/settings \
  -H "Content-Type: application/json" \
  -H "X-HAVEN-ADMIN: your-strong-secret" \
  -d '{"theme": {"bg": "#ffffff", "text": "#111827"}}'
```

Security note
-------------
- Keep the token secret. Consider using a Vault or environment management system.
- Rotate the token periodically if used in production environments.
# HAVEN_ADMIN_TOKEN (Admin Access)

This project supports an admin token that protects potentially destructive operations, such as replacing the database file or changing the active data source.

How to use:
1. Copy `.env.example` to `.env` in the repo root.
2. Set `HAVEN_ADMIN_TOKEN` to a secret (random string) you control.

Example:

```
HAVEN_ADMIN_TOKEN=MyS3cr3tT0ken
```

3. When calling API endpoints that require admin permissions (e.g., `POST /api/data_sources/current`, `POST /api/db_upload`, `POST /api/settings`), provide the header `X-Haven-Admin` with the token value.

Example curl usage (replace host and token):

```
curl -X POST http://127.0.0.1:8000/api/data_sources/current \
  -H "X-Haven-Admin: MyS3cr3tT0ken" \
  -H "Content-Type: application/json" \
  -d '{"name": "testing"}'
```

Behavior:
- If `HAVEN_ADMIN_TOKEN` is not set in the environment, the server will log a warning and admin endpoints will be open (for convenience).
- If `HAVEN_ADMIN_TOKEN` is set, admin endpoints require the header and will return 403 when invalid.

Security note:
- Keep your token secret and do not commit your `.env` file into version control. Use the token only on trusted machines.
