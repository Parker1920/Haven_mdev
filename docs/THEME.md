Server-side Theme configuration
================================

Overview
--------
The Haven Control Room can persist a server-side theme that affects all users visiting the web UI. This is stored in `settings.json` as:

```json
{
  "theme": {
    "bg": "#f8fafc",
    "text": "#111827",
    "card": "#ffffff",
    "primary": "#06b6d4"
  }
}
```

How to change theme
-------------------
1. Visit the SPA `Settings` page and update colors using the color pickers, then click 'Save' (requires admin token if `HAVEN_ADMIN_TOKEN` is set).
2. Or POST directly to `POST /api/settings` with a JSON body. Example:

```bash
curl -X POST http://localhost:8000/api/settings \
  -H 'Content-Type: application/json' \
  -H 'X-HAVEN-ADMIN: yourtoken' \
  -d '{"theme": {"bg": "#0f172a", "text": "#e2e8f0"}}'
```

How the SPA uses theme
----------------------
On page load the SPA fetches `/api/settings` and applies the `theme` values as CSS variables:

- `--app-bg` : background color
- `--app-text`: text color
- `--app-card`: card background color
- `--app-primary`: primary accent color

These are applied to body and relevant components so the UI reflects the server-defined palette.

Backend persistence
-------------------
The server will create a `settings.json` at project root on startup if missing; this file persists server settings including theme.
