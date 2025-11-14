# Railway Deployment - Visual Architecture & Diagrams

## Current State vs Post-Deployment

### CURRENT (Local Development Only)

```
Your Computer
└── Haven_mdev/
    ├── src/
    │   ├── control_room.py ──────────┐
    │   ├── Beta_VH_Map.py            │ GUI/Scripts
    │   └── system_entry_wizard.py ───┤ (Run locally)
    │                                 │
    │   └── generate_ios_pwa.py ──────┘
    │
    ├── keeper-bot/
    │   └── src/
    │       └── main.py ──────────── Discord Bot
    │                               (Must run manually)
    │
    └── data/
        └── haven.db ───────────── SQLite
                                  (Local only)

Problems:
❌ Bot offline when computer sleeps
❌ Data not backed up
❌ Hard to share/collaborate
❌ Can't access from elsewhere
❌ Manual startup
```

### POST-DEPLOYMENT (Railway Cloud)

```
Your Computer              Railway Cloud                Discord Servers
│                         │                            │
└─ Git Push ──────────────→ Automatic Build ──────────→ Bot connects
                          │                            │
                          ├─ Service 1: Discord Bot   │
                          │  (Always Online)          ├─ Responds to
                          │  ├─ Cogs                  │  commands
                          │  ├─ Database queries      │
                          │  └─ Pattern detection     │
                          │                            │
                          ├─ Service 2: API (Optional)│
                          │  ├─ /api/generate-map    ├─ Available
                          │  ├─ /api/export-pwa      │  via HTTP
                          │  └─ /api/data            │
                          │                            │
                          └─ PostgreSQL Database
                             (Managed Backup)

Benefits:
✅ Bot online 24/7
✅ Automatic backups
✅ Easy to scale
✅ API accessible anywhere
✅ Git push = auto-deploy
✅ Managed infrastructure
```

---

## Data Flow Diagrams

### Option 1: Discord Bot Only

```
┌─────────────────────────────────────────────────────────┐
│                    RAILWAY                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────┐              │
│  │   Discord Bot Service                │              │
│  │   (keeper-bot/src/main.py)           │              │
│  │                                      │              │
│  │  ┌──────────────────────────────┐    │              │
│  │  │ Cogs:                        │    │              │
│  │  │ • Enhanced Discovery         │    │              │
│  │  │ • Pattern Recognition        │    │              │
│  │  │ • Archive System             │    │              │
│  │  │ • Community Features         │    │              │
│  │  └──────────────────────────────┘    │              │
│  │            ▲                          │              │
│  │            │ Discord API             │              │
│  │            ▼                          │              │
│  │  ┌──────────────────────────────┐    │              │
│  │  │ Personality Engine            │    │              │
│  │  │ • Pattern Analysis            │    │              │
│  │  │ • Message Generation          │    │              │
│  │  └──────────────────────────────┘    │              │
│  └──────────────┬───────────────────────┘              │
│                 │ SQL Queries                          │
│                 ▼                                      │
│  ┌──────────────────────────────────────┐              │
│  │   PostgreSQL Database                │              │
│  │   ├─ Systems                         │              │
│  │   ├─ Discoveries                     │              │
│  │   ├─ Users                           │              │
│  │   ├─ Guild Settings                  │              │
│  │   └─ Archives                        │              │
│  └──────────────────────────────────────┘              │
│                                                         │
└─────────────────────────────────────────────────────────┘

Discord Servers (Your Guilds)
     │◄────── Bot sends messages ─────┤
     │◄────── Responds to commands ────┤
```

### Option 2: Bot + API Service

```
┌────────────────────────────────────────────────────────────────┐
│                         RAILWAY                                │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌────────────────────────┐        ┌────────────────────────┐ │
│  │  Service 1:            │        │  Service 2:            │ │
│  │  Discord Bot           │        │  Map/Export API        │ │
│  │                        │        │                        │ │
│  │  ┌──────────────────┐  │        │  ┌──────────────────┐  │ │
│  │  │ main.py          │  │        │  │ api_server.py    │  │ │
│  │  │ • Cogs           │  │        │  │ • Flask Routes   │  │ │
│  │  │ • Commands       │  │        │  │ • /api/generate- │  │ │
│  │  │ • Personality    │  │        │  │   map            │  │ │
│  │  └──────────────────┘  │        │  │ • /api/export-   │  │ │
│  │         ▲               │        │  │   pwa            │  │ │
│  │         │               │        │  │ • /api/data      │  │ │
│  │  Discord API            │        │  │ • /health        │  │ │
│  │         │               │        │  └──────────────────┘  │ │
│  └─────────┼───────────────┘        └──────────┬──────────────┘ │
│            │                                   │                │
│            └───────────────────┬────────────────┘                │
│                                │                                │
│                          ┌──────▼──────┐                       │
│                          │ PostgreSQL   │                       │
│                          │ Database     │                       │
│                          │             │                        │
│                          │ • Systems   │                        │
│                          │ • Discovery │                        │
│                          │ • Archives  │                        │
│                          └─────────────┘                        │
│                                                                │
└────────────────────────────────────────────────────────────────┘

Discord Servers           Web Browsers / Apps
     │                          │
     ├─ Bot Messages            ├─ GET /health
     ├─ Commands                ├─ POST /api/generate-map
     └─ Interactions            ├─ POST /api/export-pwa
                                └─ GET /api/data
```

---

## Build & Deployment Flow

### Local Development

```
┌─────────────────────────────────────┐
│     Your Computer                   │
│                                     │
│  1. Make code changes               │
│     keeper-bot/src/main.py          │
│     + Edit features                 │
│                                     │
│  2. Test locally                    │
│     $ python keeper-bot/src/main.py │
│     ↓                               │
│     "The Keeper awakens..." ✅       │
│                                     │
│  3. Commit to Git                   │
│     $ git add .                     │
│     $ git commit -m "feat: ..."     │
│     $ git push origin main          │
└────────────────┬────────────────────┘
                 │
                 │ GitHub receives push
                 ▼
        ┌───────────────────┐
        │ GitHub Repository │
        │ Haven_mdev/main   │
        └────────┬──────────┘
                 │
                 │ Webhook notification
                 ▼
```

### Automatic Railway Deployment

```
┌──────────────────────────────────────────────────┐
│            Railway Dashboard                     │
│                                                  │
│  1. Webhook received ─ "New push detected"       │
│     ↓                                            │
│  2. Clone repository                            │
│     ↓                                            │
│  3. Detect buildpack                            │
│     └─ Found: Procfile                          │
│        Action: python keeper-bot/src/main.py    │
│     ↓                                            │
│  4. Install dependencies                        │
│     └─ Read: requirements.txt                   │
│        Action: pip install -r requirements.txt  │
│     ↓                                            │
│  5. Load environment variables                  │
│     ├─ DISCORD_BOT_TOKEN (from Variables)       │
│     ├─ DATABASE_URL (from PostgreSQL add-on)    │
│     └─ PORT (auto-injected: 5000)               │
│     ↓                                            │
│  6. Start application                           │
│     └─ Execute: python keeper-bot/src/main.py   │
│        Output: "The Keeper awakens..."           │
│     ↓                                            │
│  7. Verify health                               │
│     └─ Check logs for errors                    │
│        ✅ Running successfully                   │
│                                                  │
│  8. Route traffic                               │
│     ├─ Discord API → Bot                        │
│     └─ HTTP requests → API (if enabled)         │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## File Structure Evolution

### BEFORE (Current)

```
Haven_mdev/
├── config/
│   ├── requirements.txt ❌ WRONG LOCATION
│   └── ...
│
├── keeper-bot/
│   ├── requirements.txt ❌ WRONG LOCATION
│   └── src/
│       └── main.py
│
└── src/
    ├── control_room.py
    └── ...

Problems:
❌ Railway doesn't know what to run (no Procfile)
❌ Multiple requirements files
❌ GUI mixed with server code
❌ No clear entry point
```

### AFTER (Fixed for Railway)

```
Haven_mdev/
├── Procfile ✅ CRITICAL - Tells Railway what to run
├── requirements.txt ✅ CRITICAL - Consolidated dependencies
├── .env.example ✅ Documents environment variables
│
├── Dockerfile ✅ Container definition (optional but recommended)
├── docker-compose.yml ✅ Local testing (optional but recommended)
│
├── config/
│   ├── settings.py (MODIFIED - PostgreSQL support)
│   └── ...
│
├── keeper-bot/
│   ├── src/
│   │   └── main.py (MODIFIED - Fixed imports)
│   └── ...
│
├── src/
│   ├── api_server.py ✅ NEW - API wrapper (optional)
│   ├── control_room.py (unchanged - local only)
│   └── ...
│
└── scripts/
    └── migrate_to_postgres.py ✅ NEW - DB migration (optional)

Benefits:
✅ Clear entry point (Procfile)
✅ Single source of dependencies
✅ Railway can auto-detect and deploy
✅ Environment variables documented
✅ Separated concerns (GUI vs. service)
```

---

## Deployment States & Transitions

```
┌─────────────┐
│   INITIAL   │
│   ERROR     │
│             │
│ Pailpack    │
│ error       │
│ (no Procfile)
└──────┬──────┘
       │
       │ Create 3 critical files:
       │ • Procfile
       │ • requirements.txt
       │ • .env.example
       ▼
┌──────────────────┐
│   DETECTABLE     │
│                  │
│ Railway finds    │
│ entry point      │
│ (Procfile)       │
└──────┬───────────┘
       │
       │ Build starts
       ▼
┌──────────────────┐
│   BUILDING       │
│                  │
│ Installing       │
│ dependencies     │
│ from            │
│ requirements.txt │
└──────┬───────────┘
       │
       │ Run setup
       ▼
┌──────────────────┐
│   SETTING UP     │
│                  │
│ Loading env      │
│ variables        │
│ Creating dirs    │
│ etc.            │
└──────┬───────────┘
       │
       │ Start bot
       ▼
┌──────────────────┐
│   RUNNING ✅      │
│                  │
│ Bot online       │
│ Connected        │
│ to Discord       │
│ Ready for use    │
└──────────────────┘
```

---

## Network & Access Diagram

### Components & Their Network Access

```
┌─────────────────────────────────────────────────────────────┐
│                      INTERNET                               │
└────┬──────────────────┬────────────────────────┬────────────┘
     │                  │                        │
     │                  │                        │
┌────▼─────┐      ┌─────▼──────┐         ┌──────▼─────┐
│ Discord   │      │ Your App   │         │  GitHub    │
│ API       │      │  (browser) │         │ Repository │
│ Servers   │      │            │         │            │
└────┬─────┘      └─────┬──────┘         └──────┬─────┘
     │                  │                        │
     │ Messages         │ HTTPS                  │ Git
     │ Commands         │ GET /api/*             │ Webhooks
     │ Embeds           │ POST /api/*            │
     │                  │                        │
     │                  │                        │
     └────────────┬──────────────────────────────┘
                  │
                  │
     ┌────────────▼──────────────────────┐
     │      RAILWAY (Cloud)              │
     │                                   │
     │  ┌──────────────────┐            │
     │  │ Discord Bot      │────────────►│ Receive webhooks
     │  │ • Listens to API │             │ from GitHub
     │  │ • Sends messages │────────────►│ Auto-redeploy
     │  │ • Queries DB     │             │
     │  └────────┬─────────┘             │
     │           │ SQL                   │
     │           │ Queries               │
     │  ┌────────▼──────────┐            │
     │  │ PostgreSQL        │            │
     │  │ • Systems         │            │
     │  │ • Discoveries     │            │
     │  │ • Archives        │            │
     │  └───────────────────┘            │
     │                                   │
     │  ┌──────────────────┐             │
     │  │ API Service      │─────────────►│ HTTP Responses
     │  │ (optional)       │             │ to clients
     │  │ • /api/data      │             │
     │  │ • /api/map       │             │
     │  └──────────────────┘             │
     │                                   │
     └───────────────────────────────────┘
```

---

## Scaling Diagram (Future)

### Phase 1: Current (Single Service)

```
┌─────────────────┐
│  Discord Bot    │
│  (main.py)      │
│  ───────────    │
│  • Processes    │
│  • Archives     │
│  • Responds     │
└────────┬────────┘
         │
    ┌────▼────┐
    │ Database │
    └──────────┘
```

### Phase 2: Recommended (Two Services)

```
┌─────────────────┐        ┌──────────────┐
│  Discord Bot    │        │  API Server  │
│  (main.py)      │        │ (Flask/FastAPI)
│  ───────────    │        │  ────────────
│  • Processes    │        │  • Map gen
│  • Archives     │        │  • PWA export
│  • Responds     │        │  • Data serve
└────────┬────────┘        └──────┬───────┘
         │                        │
         └────────────┬───────────┘
                      │
                  ┌───▼────┐
                  │Database │
                  └─────────┘
```

### Phase 3: Enterprise (Multiple Services + Monitoring)

```
┌──────────────────┐    ┌──────────────┐    ┌──────────────┐
│   Discord Bot    │    │  API Server  │    │ Web Dashboard│
│   (main.py)      │    │  (Flask)     │    │  (React)     │
└────────┬─────────┘    └──────┬───────┘    └──────┬───────┘
         │                     │                   │
         └──────────────┬──────────────┬──────────┘
                        │              │
                   ┌────▼──────────────▼──┐
                   │  PostgreSQL          │
                   │  (with backups)      │
                   └──────────────────────┘
                        │
                        │ (optional)
                   ┌────▼──────────┐
                   │ Monitoring    │
                   │ • Datadog     │
                   │ • Sentry      │
                   │ • Logs        │
                   └───────────────┘
```

---

## Timeline Visualization

```
NOW              5 min           10 min          15 min          20 min
│                │                │                │                │
├─ Current     ├─ Create        ├─ Test         ├─ Push to      ├─ GitHub
│  state       │  Procfile      │  locally       │  GitHub         │ webhook
│  (error)     │  requirements  │               │               │ triggered
│              │  .env example  │               │               │
│              │                │               │               │
│              │                └─ Works! ✅     │               │
│              │                               │               │
└──────────────└───────────────────────────────┴─────────────────┴────────►
                            PART A: Critical Files (User works)


        20 min             25 min             30 min            35 min
        │                  │                  │                 │
        ├─ Go to Railway  ├─ Connect         ├─ Add            ├─ Set
        │  dashboard       │  GitHub           │  PostgreSQL     │  token
        │                  │  repository       │  add-on         │
        │                  │                  │                 │
        │                  │                  │                 ├─ Deploy
        │                  │                  │                 │  starts!
        │                  │                  │                 │
        └──────────────────┴──────────────────┴─────────────────┴────────►
                        PART B: Railway Setup (User configures)


             35 min          40 min           45 min          50 min
             │               │                │               │
             ├─ Build       ├─ Run           ├─ Bot          ├─ Monitor
             │  starts       │  application   │  comes         │  logs
             │  (reads       │  (execute      │  online ✅     │
             │  Procfile)    │  main.py)      │               │
             │               │                │               │
             │               └─ "Keeper      │               │
             │                  awakens"      │               │
             │                  appears       │               │
             │                  in logs       │               │
             │                               │               │
             └───────────────────────────────┴───────────────┴────────►
                     PART C: Automatic Deployment (Railway works)


Status Summary:
├─ 00-15 min: YOU create files
├─ 15-20 min: YOU push to GitHub
├─ 20-35 min: YOU configure Railway
└─ 35-50 min: RAILWAY auto-deploys ✅
             DONE! Bot is live! 🎉
```

---

## Decision Matrix

| Want | Time | Complexity | Tools | Cost |
|------|------|-----------|-------|------|
| **Just the bot** | 15 min | ⭐ | Procfile, req.txt | $5/mo |
| **+ Docker locally** | 30 min | ⭐⭐ | + Dockerfile | $5/mo |
| **+ API service** | 60 min | ⭐⭐ | + Flask | $12/mo |
| **+ Full prod** | 120 min | ⭐⭐⭐ | + migration | $15/mo |

Pick your path! ✅

---

## Failure Mode Analysis

| If This Fails | Root Cause | Solution |
|---------------|-----------|----------|
| Procfile not detected | Not at project root | Move file to `Haven_mdev/Procfile` |
| ModuleNotFoundError | Import paths broken | Add sys.path setup to main.py |
| DISCORD_BOT_TOKEN not found | Not set as variable | Go Railway → Variables → Add it |
| DATABASE_URL not found | PostgreSQL not added | Go Railway → Add Service → PostgreSQL |
| "Build plan error" | Procfile doesn't match structure | Verify `web: python keeper-bot/src/main.py` |
| Bot offline | Code crashed | Check Railway Logs tab |
| Database connection fails | PostgreSQL not ready | Wait 30 seconds, Railway may still initializing |

All fixable! Check `RAILWAY_DEPLOYMENT_PLAN.md` for detailed solutions.

---

This covers the complete architecture and flow. You now have both the "why" and the "how"! 🚀
