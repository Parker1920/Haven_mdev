# Railway Deployment - Quick Visual Reference

## What Your Project Has vs What Railway Needs

```
YOUR PROJECT:                          RAILWAY NEEDS:
├─ GUI Desktop (control_room.py)       ✗ Can't run (no display)
├─ Map Generator (Beta_VH_Map.py)      ✓ Convert to API endpoint
├─ Discord Bot (keeper-bot/)           ✓✓ PERFECT FIT
├─ iOS PWA Exporter                    ✓ Include in API
├─ Database (SQLite locally)           ✓ Use PostgreSQL
└─ Multiple entry points               ✗ Need Procfile + clarity
```

---

## The Error You Got

```
❌ "error creating build plan with pailpack"

Translation: Railway looked at your repo and said:
"I see Python code, but where do I START? What am I supposed to run?"
```

---

## The Solution (Simple Version)

```
YOU NEED 3 FILES AT PROJECT ROOT:

1. Procfile
   web: python keeper-bot/src/main.py
   
2. requirements.txt
   (all dependencies consolidated here)
   
3. .env.example
   DISCORD_BOT_TOKEN=xxx
   DATABASE_URL=xxx
```

---

## Two-Service Architecture (What I Recommend)

```
┌──────────────────────────────────────────────────────────────┐
│                      RAILWAY PROJECT                         │
├──────────────────────────┬──────────────────────────────────┤
│                          │                                  │
│    SERVICE 1             │      SERVICE 2                   │
│  (Primary)               │    (Optional)                    │
│                          │                                  │
│  THE KEEPER BOT          │    MAP/EXPORT API                │
│  ────────────────        │    ─────────────────             │
│  • Discord.py            │    • Flask/FastAPI               │
│  • Always on             │    • Listens on port 5000        │
│  • Cogs system           │    • /api/generate-map           │
│  • Pattern detection     │    • /api/export-pwa             │
│                          │    • /api/data                   │
│  Procfile:               │    • /health                     │
│  web: python ...main.py  │                                  │
│                          │    Procfile.api:                 │
│                          │    web: python api_server.py     │
│                          │                                  │
└──────────────────────────┴──────────────────────────────────┘
                          │
                   ┌──────▼──────┐
                   │ PostgreSQL   │
                   │ (Railway     │
                   │  Managed)    │
                   └─────────────┘
```

---

## Implementation Timeline

| Phase | Task | Time | Complexity |
|-------|------|------|------------|
| 1 | Create `Procfile` + consolidated `requirements.txt` | 5 min | ⭐ |
| 2 | Fix Keeper Bot imports for Railway | 5 min | ⭐ |
| 3 | Create `.env.example` + env var mapping | 5 min | ⭐ |
| 4 | Create `/src/api_server.py` (optional) | 20 min | ⭐⭐ |
| 5 | Create `Dockerfile` for consistency | 10 min | ⭐⭐ |
| 6 | Test locally with docker-compose | 10 min | ⭐⭐ |
| 7 | Push to GitHub | 2 min | ⭐ |
| 8 | Connect Railway + deploy | 5 min | ⭐ |

**Total: ~60 minutes for full setup**

---

## File Creation Roadmap

```
MUST CREATE (Critical):
├── Procfile                      ✓
└── requirements.txt (at root)    ✓

SHOULD CREATE (High Value):
├── .env.example                  ✓
├── Dockerfile                    ✓
├── docker-compose.yml            ✓
└── src/api_server.py             ✓

OPTIONAL (Nice to Have):
├── .railway.toml                 (Railway config)
├── scripts/migrate_to_postgres.py (DB migration)
└── .dockerignore                 (Docker optimization)

DO NOT TOUCH:
├── src/control_room.py           (stays as-is, local only)
├── keeper-bot/src/main.py        (minimal fixes, mostly works)
└── src/Beta_VH_Map.py            (minor refactoring only)
```

---

## Environment Variables Mapping

```
Local Development:              Railway Cloud:
─────────────────              ──────────────

.env file:                      Railway Dashboard:
├─ DISCORD_BOT_TOKEN      →     Variables tab
├─ DATABASE_URL           →     Auto-injected from PostgreSQL add-on
├─ FLASK_ENV              →     Variables tab
└─ DEBUG=false            →     Variables tab
```

---

## Database Migration Strategy

```
Current:                    Post-Railway:
───────                     ─────────────

SQLite (keeper.db)   ────→   PostgreSQL
├─ Single file              ├─ Managed by Railway
├─ No backups               ├─ Auto-backups included
└─ Local only               └─ Multi-region redundancy
```

---

## Common Issues & Solutions

| Error | Cause | Fix |
|-------|-------|-----|
| `Procfile not found` | File at wrong location | Must be at PROJECT ROOT, not in subdirs |
| `No module named discord` | Missing requirements | Run `pip install -r requirements.txt` before deploy |
| `PORT 8080 not listening` | Didn't set `port=os.getenv('PORT')` | Railway injects PORT env var |
| `Database connection failed` | SQLite path hardcoded | Use `DATABASE_URL` env var instead |
| `ImportError: no module 'keeper'` | Relative imports broken | Add `sys.path.insert(0, str(Path(__file__).parent.parent))` |

---

## Success Criteria (After Deploy)

```
✅ Bot comes online in Discord ("The Keeper is online")
✅ No errors in Railway Logs tab
✅ `/health` endpoint returns 200 (if using API)
✅ Database persists across container restarts
✅ Automatic re-deploy on git push
✅ All environment variables loaded correctly
```

---

## Debug Checklist (If Deploy Fails)

1. **Check Railway Logs:**
   ```
   Project → Service → Logs (see live output)
   ```

2. **Verify Procfile format:**
   ```
   cat Procfile
   # Should output: web: python keeper-bot/src/main.py
   ```

3. **Test locally first:**
   ```bash
   python keeper-bot/src/main.py
   # Should show: "The Keeper awakens..."
   ```

4. **Verify environment variables:**
   ```
   Railway Dashboard → Variables tab
   # Must include DISCORD_BOT_TOKEN
   ```

5. **Check requirements.txt is complete:**
   ```bash
   pip install -r requirements.txt
   # Should complete without errors
   ```

---

## Next Action Items

Choose one:

**Option A: Minimal Deploy (Just Bot)**
- Create: `Procfile`, `requirements.txt`, `.env.example`
- Time: 15 minutes
- Result: Discord bot runs 24/7 on Railway

**Option B: Full Deploy (Bot + API)**
- Create: All of Option A + `Dockerfile`, `api_server.py`, `docker-compose.yml`
- Time: 60 minutes
- Result: Bot + Map/Export endpoints accessible

**Option C: Enterprise Deploy (With DB Migration)**
- Create: All of Option B + migration scripts + PostgreSQL setup
- Time: 120 minutes  
- Result: Production-ready with persistent database

---

## Command Reference (After Setup)

```bash
# Test locally
python keeper-bot/src/main.py

# Test with Docker
docker build -t haven .
docker run -e DISCORD_BOT_TOKEN=xxx haven

# Test full stack with docker-compose
docker-compose up

# Deploy to Railway
git push origin main
# (Railway auto-deploys from Procfile)
```

---

## Support Resources

- **Railway Docs:** https://docs.railway.app
- **Discord.py Docs:** https://discordpy.readthedocs.io
- **Flask API Guide:** https://flask.palletsprojects.com
- **PostgreSQL on Railway:** https://docs.railway.app/databases/postgresql
