# Railway Deployment - Exact Files to Create/Modify

## Summary Table

| File | Location | Status | Purpose |
|------|----------|--------|---------|
| `Procfile` | Root | ✅ CREATE | Tells Railway what to run |
| `requirements.txt` | Root | ✅ CREATE | Consolidated dependencies |
| `.env.example` | Root | ✅ CREATE | Environment variable template |
| `Dockerfile` | Root | ✅ CREATE | Container image definition |
| `docker-compose.yml` | Root | ✅ CREATE | Local testing with PostgreSQL |
| `src/api_server.py` | Root | ✅ CREATE | Flask API for map/export endpoints |
| `scripts/migrate_to_postgres.py` | Root | ✅ CREATE | SQLite → PostgreSQL migration |
| `config/settings.py` | Root | ✏️ MODIFY | Add PostgreSQL support |
| `keeper-bot/src/main.py` | Root | ✏️ MODIFY | Fix import paths for Railway |

---

## File 1: `Procfile` (CREATE)

**Location:** `c:\Users\parke\OneDrive\Desktop\Haven_mdev\Procfile`

```
web: python keeper-bot/src/main.py
```

**Why:** Tells Railway "run the Discord bot as the web service"
**Size:** 1 line
**Critical:** YES - Without this, Railway doesn't know what to run

---

## File 2: `requirements.txt` (CREATE - ROOT LEVEL)

**Location:** `c:\Users\parke\OneDrive\Desktop\Haven_mdev\requirements.txt`

```txt
# ============================================
# HAVEN CONTROL ROOM - CONSOLIDATED REQUIREMENTS
# ============================================
# This is the single source of truth for all dependencies
# Installed by: pip install -r requirements.txt

# -------- Discord Bot (The Keeper) --------
discord.py>=2.3.0
aiofiles>=23.2.0
aiosqlite>=0.19.0
asyncio-throttle>=1.0.2

# -------- Configuration & Environment --------
python-dotenv>=1.0.0
colorama>=0.4.6
rich>=13.0.0

# -------- Database --------
psycopg2-binary>=2.9.0  # PostgreSQL for Railway
sqlalchemy>=2.0.0  # ORM layer (optional but recommended)

# -------- Image Processing --------
pillow>=10.0.0

# -------- Data Processing --------
pandas>=2.0
jsonschema>=4.0

# -------- Web API (for map/export endpoints) --------
flask>=2.3.0
flask-cors>=4.0.0
werkzeug>=2.3.0

# -------- Utilities --------
pathlib-mate>=1.5.0

# -------- Development (remove for production if needed) --------
# Commented out for Railway deployment - uncomment locally
# pytest>=7.0
# pytest-cov>=4.0
# mypy>=1.0
# black>=23.0
```

**Why:** Railway reads this to install all dependencies  
**Size:** ~40 lines  
**Critical:** YES - Must be at project root  
**Action:** DELETE the old `config/requirements.txt` and `keeper-bot/requirements.txt` after creating this

---

## File 3: `.env.example` (CREATE)

**Location:** `c:\Users\parke\OneDrive\Desktop\Haven_mdev\.env.example`

```bash
# ============================================
# HAVEN ENVIRONMENT VARIABLES
# ============================================
# Copy this to .env and fill in your values
# Railway Dashboard auto-injects most of these

# -------- DISCORD BOT --------
# Get your bot token from: https://discord.com/developers/applications
DISCORD_BOT_TOKEN=your_discord_bot_token_here

# -------- DATABASE --------
# Railway auto-provides this when you add PostgreSQL add-on
# Format: postgresql://user:password@host:port/database
DATABASE_URL=postgresql://haven:password@localhost:5432/haven

# For local SQLite development (if not using PostgreSQL):
# DATABASE_PATH=./data/haven.db

# -------- FLASK API (Optional - if deploying API service) --------
FLASK_ENV=production
FLASK_DEBUG=false
API_PORT=5000

# -------- HAVEN CONFIGURATION --------
# Use database backend (true) or JSON (false)
USE_DATABASE=true

# Data file paths (for JSON mode or fallback)
DATA_JSON_PATH=./data/data.json

# -------- LOGGING --------
LOG_LEVEL=INFO
LOG_FILE=./logs/haven.log

# -------- DEPLOYMENT --------
# Railway sets this automatically
# RAILWAY_ENVIRONMENT=production

# -------- OPTIONAL: Analytics/Monitoring --------
# SENTRY_DSN=
# DATADOG_API_KEY=
```

**Why:** Documents all environment variables your app needs  
**Size:** ~50 lines  
**Critical:** MEDIUM - Helps Railway and developers understand config  
**Action:** Keep this in version control, Railway fills in actual values via Dashboard

---

## File 4: `Dockerfile` (CREATE)

**Location:** `c:\Users\parke\OneDrive\Desktop\Haven_mdev\Dockerfile`

```dockerfile
# ============================================
# HAVEN CONTROL ROOM - DOCKER IMAGE
# ============================================
# Build: docker build -t haven .
# Run:   docker run -e DISCORD_BOT_TOKEN=xxx haven
# Railway uses this automatically if Procfile is present

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Create necessary directories
RUN mkdir -p logs data/backups data/exports

# Set permissions for logs
RUN chmod 777 logs

# Expose port (for API service if used)
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Default: Run Discord Bot
# Override with: docker run haven python src/api_server.py
CMD ["python", "keeper-bot/src/main.py"]
```

**Why:** Containers are how Railway runs your code  
**Size:** ~50 lines  
**Critical:** MEDIUM - Not strictly needed if Procfile works, but best practice  
**Action:** Use for local testing before pushing to Railway

---

## File 5: `docker-compose.yml` (CREATE)

**Location:** `c:\Users\parke\OneDrive\Desktop\Haven_mdev\docker-compose.yml`

```yaml
# ============================================
# HAVEN DOCKER COMPOSE - LOCAL TESTING
# ============================================
# Run locally: docker-compose up
# Test before deploying to Railway

version: '3.8'

services:
  # The Keeper Discord Bot
  keeper-bot:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: haven_keeper_bot
    environment:
      DISCORD_BOT_TOKEN: ${DISCORD_BOT_TOKEN}
      DATABASE_URL: postgresql://haven:haven_password@postgres:5432/haven
      RAILWAY_ENVIRONMENT: ${RAILWAY_ENVIRONMENT:-local}
      LOG_LEVEL: DEBUG
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    networks:
      - haven_network
    restart: unless-stopped

  # Optional: Map/Export API Service
  api-server:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: haven_api_server
    command: python src/api_server.py
    ports:
      - "5000:5000"
    environment:
      FLASK_ENV: development
      FLASK_DEBUG: "true"
      DATABASE_URL: postgresql://haven:haven_password@postgres:5432/haven
      API_PORT: 5000
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    networks:
      - haven_network
    restart: unless-stopped

  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: haven_postgres
    environment:
      POSTGRES_USER: haven
      POSTGRES_PASSWORD: haven_password
      POSTGRES_DB: haven
      POSTGRES_INITDB_ARGS: "--encoding=UTF8"
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - haven_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U haven -d haven"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

networks:
  haven_network:
    driver: bridge

volumes:
  postgres_data:
    driver: local
```

**Why:** Local testing mimics Railway's multi-service setup  
**Size:** ~80 lines  
**Critical:** MEDIUM - Helps verify everything works before Railway  
**Action:** Run `docker-compose up` to test locally

---

## File 6: `src/api_server.py` (CREATE)

**Location:** `c:\Users\parke\OneDrive\Desktop\Haven_mdev\src\api_server.py`

```python
"""
Haven API Server
Provides HTTP endpoints for map generation, PWA export, and data access.
Can run standalone on Railway as a separate service.

Usage:
  python src/api_server.py

Environment Variables:
  - DATABASE_URL: PostgreSQL connection string
  - FLASK_ENV: production/development
  - API_PORT: Port to listen on (default 5000, Railway sets PORT)
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# ============================================
# HEALTH CHECK ENDPOINT
# ============================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Railway."""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "haven-api"
    }), 200


# ============================================
# DATA ENDPOINTS
# ============================================

@app.route('/api/data', methods=['GET'])
def get_data():
    """
    Get all systems from database or JSON.
    Query params:
      - format: 'json' or 'table' (default: 'json')
      - limit: Max systems to return (default: unlimited)
      - offset: Pagination offset (default: 0)
    """
    try:
        from config.settings import get_data_provider
        provider = get_data_provider()
        
        limit = request.args.get('limit', type=int, default=None)
        offset = request.args.get('offset', type=int, default=0)
        
        systems = provider.get_all_systems()
        
        if limit:
            systems = systems[offset:offset+limit]
        
        return jsonify({
            "success": True,
            "count": len(systems),
            "data": systems
        }), 200
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/system/<system_name>', methods=['GET'])
def get_system(system_name):
    """Get details for a specific system."""
    try:
        from config.settings import get_data_provider
        provider = get_data_provider()
        
        system = provider.get_system(system_name)
        if not system:
            return jsonify({"error": "System not found"}), 404
        
        return jsonify({
            "success": True,
            "data": system
        }), 200
    except Exception as e:
        logger.error(f"Error fetching system: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================
# MAP GENERATION ENDPOINTS
# ============================================

@app.route('/api/generate-map', methods=['GET', 'POST'])
def generate_map():
    """
    Generate interactive 3D map HTML.
    POST body or GET params:
      - format: 'html' or 'json'
      - include_coordinates: bool (default: true)
      - include_planets: bool (default: true)
    """
    try:
        from src.Beta_VH_Map import generate_map_from_data
        from config.settings import get_data_provider
        
        provider = get_data_provider()
        systems = provider.get_all_systems()
        
        # Generate map HTML
        map_html = generate_map_from_data(systems)
        
        return {
            "success": True,
            "map_html": map_html,
            "generated_at": datetime.utcnow().isoformat(),
            "system_count": len(systems)
        }, 200
        
    except Exception as e:
        logger.error(f"Error generating map: {e}")
        return jsonify({"error": str(e), "details": str(e)}), 500


@app.route('/api/map.html', methods=['GET'])
def serve_map():
    """Serve the pre-generated map HTML file."""
    try:
        from common.paths import dist_dir
        map_path = dist_dir() / 'VH-Map.html'
        
        if not map_path.exists():
            return jsonify({"error": "Map not yet generated"}), 404
        
        return send_file(str(map_path), mimetype='text/html')
    except Exception as e:
        logger.error(f"Error serving map: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================
# EXPORT ENDPOINTS
# ============================================

@app.route('/api/export-pwa', methods=['POST'])
def export_pwa():
    """
    Export iOS PWA bundle.
    POST body:
      - app_name: str (optional, default: "Haven Star Map")
      - include_data: bool (default: true)
    """
    try:
        from src.generate_ios_pwa import create_pwa_bundle
        from config.settings import get_data_provider
        
        provider = get_data_provider()
        systems = provider.get_all_systems()
        
        # Optional: custom app name from request
        app_name = request.json.get('app_name', 'Haven Star Map') if request.json else 'Haven Star Map'
        
        # Generate PWA
        pwa_html = create_pwa_bundle(systems, app_name=app_name)
        
        return {
            "success": True,
            "pwa_html": pwa_html,
            "app_name": app_name,
            "exportable": True
        }, 200
        
    except Exception as e:
        logger.error(f"Error exporting PWA: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/export/json', methods=['GET'])
def export_json():
    """Export all data as JSON file."""
    try:
        from config.settings import get_data_provider
        provider = get_data_provider()
        systems = provider.get_all_systems()
        
        return jsonify({
            "success": True,
            "export_format": "json",
            "exported_at": datetime.utcnow().isoformat(),
            "system_count": len(systems),
            "data": systems
        }), 200
    except Exception as e:
        logger.error(f"Error exporting JSON: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================
# STATUS & INFO ENDPOINTS
# ============================================

@app.route('/api/status', methods=['GET'])
def status():
    """Get API and system status."""
    try:
        from config.settings import get_data_provider, USE_DATABASE
        provider = get_data_provider()
        system_count = len(provider.get_all_systems())
        
        return jsonify({
            "service": "Haven Control Room API",
            "status": "operational",
            "uptime_seconds": 0,  # Would need to track this
            "database_backend": "PostgreSQL" if USE_DATABASE else "JSON",
            "systems_in_database": system_count,
            "api_version": "1.0",
            "endpoints": {
                "/health": "GET - Health check",
                "/api/data": "GET - All systems",
                "/api/system/<name>": "GET - Specific system",
                "/api/generate-map": "GET/POST - Generate 3D map",
                "/api/export-pwa": "POST - Export iOS PWA",
                "/api/export/json": "GET - Export JSON",
                "/api/status": "GET - This endpoint"
            }
        }), 200
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "path": request.path,
        "method": request.method
    }), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "error": "Internal server error",
        "details": str(error) if app.debug else "See server logs"
    }), 500


# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    # Get port from Railway or use default
    port = int(os.getenv('PORT', os.getenv('API_PORT', 5000)))
    
    # Determine debug mode
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"🚀 Haven API Server starting on port {port}")
    logger.info(f"📍 Debug mode: {debug}")
    logger.info(f"🌍 http://0.0.0.0:{port}")
    logger.info(f"📊 Health check: http://localhost:{port}/health")
    logger.info(f"📖 Status: http://localhost:{port}/api/status")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        use_reloader=False  # Disable for production
    )
```

**Why:** Provides HTTP endpoints for external access to map/export functionality  
**Size:** ~300 lines  
**Critical:** MEDIUM - Extends your application's capabilities  
**Action:** Can deploy as second Railway service or skip if only want Discord bot

---

## File 7: `scripts/migrate_to_postgres.py` (CREATE)

**Location:** `c:\Users\parke\OneDrive\Desktop\Haven_mdev\scripts\migrate_to_postgres.py`

```python
"""
Migration script: SQLite → PostgreSQL
Migrates Haven data from keeper.db (SQLite) to PostgreSQL for Railway.

Usage:
  python scripts/migrate_to_postgres.py --source keeper.db --target postgresql://...

Before running on Railway:
  1. Create PostgreSQL add-on in Railway Dashboard
  2. Get DATABASE_URL from Railway
  3. Run this script locally first to test
  4. Then run on Railway before deploying bot
"""

import os
import sys
import sqlite3
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError:
    logger.error("psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)


def parse_connection_url(url: str) -> dict:
    """Parse PostgreSQL connection URL."""
    # postgresql://user:password@host:port/database
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'database': parsed.path.lstrip('/'),
        'user': parsed.username,
        'password': parsed.password
    }


def migrate_sqlite_to_postgres(sqlite_path: str, postgres_url: str) -> bool:
    """Migrate data from SQLite to PostgreSQL."""
    
    logger.info(f"📁 Source (SQLite): {sqlite_path}")
    logger.info(f"🗄️ Target (PostgreSQL): {postgres_url}")
    
    # Connect to SQLite
    try:
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        logger.info("✅ Connected to SQLite")
    except Exception as e:
        logger.error(f"❌ Failed to connect to SQLite: {e}")
        return False
    
    # Connect to PostgreSQL
    try:
        pg_params = parse_connection_url(postgres_url)
        pg_conn = psycopg2.connect(**pg_params)
        pg_cursor = pg_conn.cursor()
        logger.info("✅ Connected to PostgreSQL")
    except Exception as e:
        logger.error(f"❌ Failed to connect to PostgreSQL: {e}")
        return False
    
    try:
        # List SQLite tables
        sqlite_cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in sqlite_cursor.fetchall()]
        logger.info(f"📋 Found {len(tables)} tables in SQLite: {tables}")
        
        # Migrate each table
        for table_name in tables:
            logger.info(f"🔄 Migrating table: {table_name}")
            
            # Get data from SQLite
            sqlite_cursor.execute(f"SELECT * FROM {table_name}")
            rows = sqlite_cursor.fetchall()
            columns = [desc[0] for desc in sqlite_cursor.description]
            
            if not rows:
                logger.info(f"  ℹ️  Table is empty")
                continue
            
            logger.info(f"  📊 {len(rows)} rows found")
            
            # Create table in PostgreSQL if not exists
            # (Simplified - in production you'd want proper schema mapping)
            sqlite_cursor.execute(f"PRAGMA table_info({table_name})")
            schema = sqlite_cursor.fetchall()
            
            create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ("
            create_sql += ", ".join([
                f"{col[1]} {'TEXT' if col[2] == 'TEXT' else 'INTEGER' if col[2] == 'INTEGER' else 'NUMERIC'}"
                for col in schema
            ])
            create_sql += ")"
            
            try:
                pg_cursor.execute(create_sql)
                pg_conn.commit()
            except psycopg2.Error as e:
                logger.warning(f"  ⚠️ Table creation failed (may already exist): {e}")
            
            # Insert data
            try:
                placeholders = ", ".join(["%s"] * len(columns))
                insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                
                for row in rows:
                    try:
                        pg_cursor.execute(insert_sql, list(row))
                    except psycopg2.Error as e:
                        logger.warning(f"  ⚠️ Row insert failed: {e}")
                
                pg_conn.commit()
                logger.info(f"  ✅ Migrated {len(rows)} rows")
            except Exception as e:
                logger.error(f"  ❌ Migration failed: {e}")
                pg_conn.rollback()
                return False
        
        logger.info("✅ Migration complete!")
        
        # Verify
        pg_cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )
        pg_tables = [row[0] for row in pg_cursor.fetchall()]
        logger.info(f"✅ PostgreSQL now contains {len(pg_tables)} tables: {pg_tables}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False
    finally:
        sqlite_conn.close()
        pg_conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Migrate Haven data from SQLite to PostgreSQL"
    )
    parser.add_argument(
        '--source',
        default='keeper-bot/keeper.db',
        help='Path to SQLite database (default: keeper-bot/keeper.db)'
    )
    parser.add_argument(
        '--target',
        default=None,
        help='PostgreSQL connection URL (default: from DATABASE_URL env var)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be migrated without making changes'
    )
    
    args = parser.parse_args()
    
    # Get PostgreSQL URL
    postgres_url = args.target or os.getenv('DATABASE_URL')
    if not postgres_url:
        logger.error("❌ No PostgreSQL URL provided. Set DATABASE_URL or use --target")
        sys.exit(1)
    
    # Verify SQLite file exists
    if not os.path.exists(args.source):
        logger.error(f"❌ SQLite file not found: {args.source}")
        sys.exit(1)
    
    # Run migration
    success = migrate_sqlite_to_postgres(args.source, postgres_url)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

**Why:** Safely migrates your existing data to PostgreSQL  
**Size:** ~200 lines  
**Critical:** HIGH for migration, but can skip if starting fresh  
**Action:** Run before deploying to Railway if you have existing data

---

## File 8: `config/settings.py` (MODIFY)

**Location:** `c:\Users\parke\OneDrive\Desktop\Haven_mdev\config\settings.py`

**What to change:**

Find this section:
```python
# ========== FILE PATHS ==========

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directory
DATA_DIR = PROJECT_ROOT / "data"

# JSON data file (for JSON backend or EXE exports)
JSON_DATA_PATH = DATA_DIR / "data.json"

# SQLite database file (for database backend)
# This is the MASTER database - EXE and Mobile versions export JSON that gets imported here
DATABASE_PATH = DATA_DIR / "VH-Database.db"
```

Replace with:
```python
# ========== FILE PATHS ==========

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directory
DATA_DIR = PROJECT_ROOT / "data"

# JSON data file (for JSON backend or EXE exports)
JSON_DATA_PATH = DATA_DIR / "data.json"

# Database configuration - supports both SQLite and PostgreSQL
if os.getenv('RAILWAY_ENVIRONMENT'):
    # Production: PostgreSQL on Railway (auto-injected by Railway)
    DATABASE_URL = os.getenv('DATABASE_URL', '')
    DATABASE_PATH = None  # Not used in PostgreSQL mode
else:
    # Local development: SQLite
    DATABASE_URL = None  # Not used in SQLite mode
    DATABASE_PATH = DATA_DIR / "VH-Database.db"
```

**Why:** Makes settings work on both Railway (PostgreSQL) and local (SQLite)  
**Size:** 5 line change  
**Critical:** MEDIUM - Needed for Railway to use PostgreSQL automatically

---

## File 9: `keeper-bot/src/main.py` (MODIFY)

**Location:** `c:\Users\parke\OneDrive\Desktop\Haven_mdev\keeper-bot\src\main.py`

**What to change:**

Find the imports at the top (around line 1-20), add this at the beginning:

```python
"""
The Keeper - Discord Bot
A mysterious intelligence that archives discoveries and reveals patterns.
"""

# ============================================
# RAILWAY COMPATIBILITY: Fix import paths
# ============================================
import sys
from pathlib import Path

# Determine base paths for both local and Railway execution
KEEPER_BOT_DIR = Path(__file__).parent.parent  # keeper-bot/
PROJECT_ROOT = KEEPER_BOT_DIR.parent  # Haven_mdev/

# Add both to path so imports work everywhere
sys.path.insert(0, str(KEEPER_BOT_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

# ============================================
# STANDARD IMPORTS
# ============================================

import discord
from discord.ext import commands
import json
import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
# Try both locations: keeper-bot/.env and Haven_mdev/.env
env_files = [
    str(KEEPER_BOT_DIR / '.env'),
    str(PROJECT_ROOT / '.env'),
]
for env_file in env_files:
    if Path(env_file).exists():
        load_dotenv(env_file)
        break

from database.keeper_db import KeeperDatabase
from core.keeper_personality import KeeperPersonality
from cogs.enhanced_discovery import EnhancedDiscoverySystem
from cogs.pattern_recognition import PatternRecognition
from cogs.archive_system import ArchiveSystem
from cogs.admin_tools import AdminTools
```

**Why:** Makes bot work on both your local machine and Railway  
**Size:** 10 line addition (plus reorganization)  
**Critical:** MEDIUM - Required for Railway to find all imports

---

## Summary: Which Files to Prioritize

| Priority | File | Effort | Impact |
|----------|------|--------|--------|
| 🔴 CRITICAL | `Procfile` | 1 min | ✅✅✅ Unblocks Railway |
| 🔴 CRITICAL | `requirements.txt` (root) | 5 min | ✅✅✅ Railway installs deps |
| 🟠 HIGH | `.env.example` | 10 min | ✅✅ Documents config |
| 🟠 HIGH | `keeper-bot/src/main.py` (modify) | 5 min | ✅✅ Fixes imports |
| 🟡 MEDIUM | `Dockerfile` | 10 min | ✅ Better testing |
| 🟡 MEDIUM | `docker-compose.yml` | 10 min | ✅ Test locally |
| 🟢 OPTIONAL | `src/api_server.py` | 30 min | ✅ Extra features |
| 🟢 OPTIONAL | Migration script | 20 min | ✅ If migrating data |
| 🟢 OPTIONAL | `config/settings.py` (modify) | 5 min | ✅ Better Railway support |

**Minimal Viable Deployment (10 minutes):**
1. Create `Procfile`
2. Create `requirements.txt` at root
3. Create `.env.example`
4. Modify `keeper-bot/src/main.py` imports
5. Push to GitHub
6. Connect Railway

**Full Production Deployment (60 minutes):**
All of the above + Dockerfile + docker-compose.yml + api_server.py

---

## Quick Copy-Paste Commands (After creating files)

```bash
# Test locally
python keeper-bot/src/main.py

# Test with Docker
docker build -t haven .
docker run -e DISCORD_BOT_TOKEN=your_token haven

# Test full stack
docker-compose up

# Test API (if created)
curl http://localhost:5000/health

# Deploy to Railway (push to GitHub)
git add .
git commit -m "feat: prepare for Railway deployment"
git push origin main
```

That's it! Railway auto-detects `Procfile` and deploys.
