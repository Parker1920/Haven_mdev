# Haven Control Room - Railway Deployment Plan

**Date:** November 11, 2025  
**Project:** Haven_mdev (Star Mapping + Discord Bot + Map Generator + iOS PWA)  
**Target:** https://railway.app (Pailpack buildpack error fix)

---

## Executive Summary

Your Haven project has **multiple deployable components**:
1. **Control Room GUI** (Desktop, CustomTkinter) - ❌ NOT suitable for Railway (requires GUI/display)
2. **Map Generator** (Beta_VH_Map.py) - ✅ Can be web service with API
3. **Discord Bot** (The Keeper) - ✅ BEST fit for Railway
4. **iOS PWA Exporter** - ✅ Can be static/API service
5. **Database** (SQLite/PostgreSQL) - ✅ PostgreSQL for Railway

**Error you're getting:** "error creating build plan with Pailpack" = Railway can't detect how to run your project.

---

## The Problem: Why It Failed

**Railway needs to know:**
- ✅ What language/framework?
- ✅ What's the entry point?
- ✅ What dependencies?
- ✅ What process to run?

**Your repo has:**
- ❌ Multiple entry points (`control_room.py`, `Beta_VH_Map.py`, `keeper-bot/src/main.py`)
- ❌ Desktop GUI code mixed with server code
- ❌ No `Procfile` (tells Railway what to run)
- ❌ No clear Docker configuration
- ❌ Requirements split across multiple files

---

## Solution: Restructured Deployment Architecture

I recommend deploying **two independent services** on Railway:

### **Service 1: The Keeper Discord Bot** (Primary)
- **Language:** Python 3.11+
- **Entrypoint:** `keeper-bot/src/main.py`
- **Dependencies:** discord.py, aiosqlite, python-dotenv
- **Runtime:** Always-on async bot
- **Database:** PostgreSQL or SQLite (attached volume)

### **Service 2: Map/Export API Service** (Optional)
- **Language:** Python + Flask/FastAPI
- **Entrypoint:** API server exposing:
  - `/api/generate-map` → generates HTML map
  - `/api/export-pwa` → builds iOS PWA
  - `/api/data` → serves JSON data
- **Database:** Shared PostgreSQL with Keeper Bot

### **What CANNOT Deploy to Railway**
- ❌ `control_room.py` (GUI requires display server)
- ❌ `.bat` / `.command` launcher scripts
- ❌ User-interactive TUI wizards

---

## Step-by-Step Implementation Plan

### **Phase 1: Prepare Keeper Bot for Railway** (Est. 30 min)

#### 1.1 Create Procfile
```bash
# File: Procfile
web: python keeper-bot/src/main.py
```
This tells Railway: "Run the Discord bot as the main process"

#### 1.2 Consolidate Requirements
Create `/requirements.txt` at project root with all dependencies:
```txt
# Core Discord Bot
discord.py>=2.3.0
aiofiles>=23.2.0
aiosqlite>=0.19.0
python-dotenv>=1.0.0
pillow>=10.0.0
asyncio-throttle>=1.0.2
colorama>=0.4.6
rich>=13.0.0

# Map Generation (if including API)
flask>=2.3.0
flask-cors>=4.0.0
pandas>=2.0
jsonschema>=4.0

# Database
psycopg2-binary>=2.9.0  # For PostgreSQL

# Shared utilities
pathlib-mate>=1.5.0
```

#### 1.3 Environment Variables Setup
Create `.env.example` at project root:
```bash
# Railway will inject these at runtime
DISCORD_BOT_TOKEN=your_token_here
DATABASE_URL=postgresql://user:pass@host/dbname
FLASK_ENV=production
ENABLE_MAP_API=true
```

#### 1.4 Fix import paths in Keeper Bot
Update `keeper-bot/src/main.py` to handle both local and Railway paths:
```python
import sys
from pathlib import Path

# Handle both relative (local dev) and absolute (Railway) imports
KEEPER_ROOT = Path(__file__).parent.parent
PROJECT_ROOT = KEEPER_ROOT.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(KEEPER_ROOT))

# Then import as normal
from database.keeper_db import KeeperDatabase
...
```

#### 1.5 Database Migration for Railway
**Currently:** SQLite (`keeper.db`)  
**For Railway:** PostgreSQL (managed, persistent)

Update `config/settings.py`:
```python
import os

if os.getenv('RAILWAY_ENVIRONMENT'):
    # Production: Use PostgreSQL on Railway
    DATABASE_URL = os.getenv('DATABASE_URL', '')
    USE_DATABASE = True
else:
    # Local dev: Use SQLite
    DATABASE_PATH = DATA_DIR / "VH-Database.db"
    USE_DATABASE = True
```

Create migration script `scripts/migrate_to_postgres.py`:
```python
# Migrates SQLite → PostgreSQL
# Run once before deploying
```

---

### **Phase 2: Create Map/Export API** (Est. 1 hour)

Create `/src/api_server.py`:
```python
from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Import Haven modules
from src.Beta_VH_Map import generate_map_html
from src.generate_ios_pwa import create_pwa_bundle

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/api/generate-map', methods=['POST'])
def generate_map():
    """Generate interactive 3D map from data"""
    try:
        data = request.json
        html_output = generate_map_html(data)
        return {'map_html': html_output}, 200
    except Exception as e:
        return {'error': str(e)}, 400

@app.route('/api/export-pwa', methods=['POST'])
def export_pwa():
    """Export iOS PWA bundle"""
    try:
        data = request.json
        pwa_html = create_pwa_bundle(data)
        return {'pwa_html': pwa_html}, 200
    except Exception as e:
        return {'error': str(e)}, 400

@app.route('/api/data', methods=['GET'])
def get_data():
    """Serve current Haven data"""
    # Load from database or JSON
    from config.settings import get_data_provider
    provider = get_data_provider()
    return provider.get_all_systems()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

Create alternative `Procfile.api`:
```
web: python src/api_server.py
```

---

### **Phase 3: Docker Configuration** (Est. 20 min)

Create `/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Ensure logs directory exists
RUN mkdir -p logs

# Default: run Discord Bot
# Can override with: docker run ... python src/api_server.py
CMD ["python", "keeper-bot/src/main.py"]
```

Create `/docker-compose.yml` for local testing:
```yaml
version: '3.8'

services:
  keeper-bot:
    build: .
    environment:
      DISCORD_BOT_TOKEN: ${DISCORD_BOT_TOKEN}
      DATABASE_URL: postgresql://haven:password@postgres:5432/haven
    depends_on:
      - postgres

  api-server:
    build: .
    command: python src/api_server.py
    ports:
      - "5000:5000"
    environment:
      DATABASE_URL: postgresql://haven:password@postgres:5432/haven
    depends_on:
      - postgres

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: haven
      POSTGRES_PASSWORD: password
      POSTGRES_DB: haven
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

### **Phase 4: Deploy to Railway** (Est. 10 min)

#### 4.1 Push to GitHub
```bash
git add .
git commit -m "feat: prepare for Railway deployment"
git push origin main
```

#### 4.2 Connect Railway to GitHub
1. Go to https://railway.app/dashboard
2. Create NEW project → "Deploy from GitHub"
3. Select `Haven_mdev` repository
4. Railway auto-detects Python, reads `Procfile`

#### 4.3 Configure Environment Variables in Railway
- Go to Service → Settings → Variables
- Add:
  - `DISCORD_BOT_TOKEN` = your Discord bot token
  - `DATABASE_URL` = PostgreSQL connection string (Railway provides this)
  - `FLASK_ENV` = production

#### 4.4 Add PostgreSQL Add-on
- Project → Add Service → "New Database" → PostgreSQL
- Railway automatically injects `DATABASE_URL`

#### 4.5 Verify & Deploy
- Push to main branch
- Railway auto-deploys from your Procfile

---

## File Structure (After Implementation)

```
Haven_mdev/
├── Procfile                      # ← Railway entry point (CRITICAL)
├── Dockerfile                    # ← For Docker builds
├── docker-compose.yml            # ← Local testing
├── requirements.txt              # ← Consolidated (CRITICAL)
├── README.md
│
├── config/
│   ├── settings.py              # ← Update for PostgreSQL
│   ├── requirements.txt          # ← DELETE (merge to root)
│   └── ...
│
├── keeper-bot/
│   ├── src/
│   │   ├── main.py              # ← Discord Bot entrypoint
│   │   ├── database/
│   │   │   └── keeper_db.py      # ← Supports PostgreSQL
│   │   └── cogs/
│   ├── requirements.txt          # ← DELETE (merge to root)
│   ├── .env.example
│   └── ...
│
├── src/
│   ├── api_server.py            # ← NEW: Flask API
│   ├── Beta_VH_Map.py           # ← Refactor for API use
│   ├── generate_ios_pwa.py      # ← Refactor for API use
│   ├── control_room.py          # ← Keep (desktop only)
│   └── ...
│
├── data/
│   ├── data.json
│   └── haven.db                 # ← Will migrate to PostgreSQL
│
└── scripts/
    ├── migrate_to_postgres.py   # ← NEW: DB migration
    └── ...
```

---

## Deployment Checklist

- [ ] **Phase 1: Keeper Bot**
  - [ ] Create `Procfile` at root
  - [ ] Create consolidated `/requirements.txt`
  - [ ] Create `.env.example`
  - [ ] Fix import paths in `keeper-bot/src/main.py`
  - [ ] Test locally: `python keeper-bot/src/main.py`

- [ ] **Phase 2: API Service** (Optional but recommended)
  - [ ] Create `/src/api_server.py`
  - [ ] Test locally: `python src/api_server.py`
  - [ ] Test endpoints: `curl http://localhost:5000/health`

- [ ] **Phase 3: Containerization**
  - [ ] Create `Dockerfile`
  - [ ] Test locally: `docker build -t haven . && docker run haven`

- [ ] **Phase 4: Database Migration**
  - [ ] Create PostgreSQL migration script
  - [ ] Test locally with docker-compose
  - [ ] Run migration before Railway deployment

- [ ] **Phase 5: Railway Setup**
  - [ ] Connect GitHub repository
  - [ ] Create PostgreSQL add-on
  - [ ] Set environment variables
  - [ ] Verify Procfile is detected
  - [ ] Deploy

- [ ] **Post-Deployment**
  - [ ] Verify Discord Bot connects
  - [ ] Check logs: Railway Dashboard → Logs
  - [ ] Test API endpoints (if deployed)
  - [ ] Verify database persistence

---

## Expected Outcomes

✅ **Discord Bot** runs 24/7 on Railway  
✅ **Map Generator** available via HTTP API  
✅ **iOS PWA Export** available via API  
✅ **PostgreSQL Database** persists data across restarts  
✅ **Zero local dependencies** for deployment  
✅ **Automatic redeploys** on git push  

---

## Why This Fixes "Pailpack Error"

| Issue | Solution |
|-------|----------|
| No build plan | Added `Procfile` → explicit entry point |
| Multiple entry points | Created separate services with clear purposes |
| Mixed dependencies | Consolidated `/requirements.txt` at root |
| GUI code confuses builder | Separated CLI/API code from desktop code |
| No database config | Added PostgreSQL with Railway add-on |
| Env variable mess | Created `.env.example` + Railway Variables UI |

---

## Next Steps

1. **Tell me which components you want to deploy:**
   - [ ] Just Discord Bot?
   - [ ] Bot + Map API?
   - [ ] Everything?

2. **I can then:**
   - Generate the exact files needed
   - Provide step-by-step implementation code
   - Create the migration scripts
   - Test locally first before Railway push

3. **Questions to clarify:**
   - Do you want the **map generator as an API** or just accessible via Discord?
   - Should the **iOS PWA export** be available on Railway?
   - Do you have the **Discord Bot Token** ready for Railway?

---

## References

- [Railway Python Deployment](https://docs.railway.app/guides/python)
- [Procfile Format](https://devcenter.heroku.com/articles/procfile)
- [Discord.py on Railway](https://docs.railway.app/guides/discord-bot)
- [PostgreSQL on Railway](https://docs.railway.app/databases/postgresql)
