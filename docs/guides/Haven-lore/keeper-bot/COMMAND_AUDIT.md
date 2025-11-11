# Discord Bot Command Audit & Permissions

**Generated:** 2025-11-11
**Bot:** The Keeper#8095

---

## Command Inventory (17 Total)

### Admin Tools (4 commands)
| Command | Description | Current Access | Should Be Admin-Only |
|---------|-------------|----------------|---------------------|
| `/setup-channels` | Configure The Keeper's channels | Everyone | ✅ YES |
| `/server-stats` | View server statistics and activity | Everyone | ❓ Optional (can be public) |
| `/keeper-config` | Configure The Keeper's settings | Everyone | ✅ YES |
| `/reload-haven` | Reload Haven star systems from database | Admin-only ✅ | ✅ YES (already protected) |

### Discovery System (3 commands)
| Command | Description | Current Access | Should Be Admin-Only |
|---------|-------------|----------------|---------------------|
| `/discovery-report` | Report a discovery (Haven-Enhanced) | Everyone | ❌ NO (user command) |
| `/haven-export` | Export discoveries for Haven integration | Everyone | ✅ YES |
| `/search-discoveries` | Search the Archive for discoveries | Everyone | ❌ NO (user command) |

**Note:** There are TWO `/discovery-report` commands:
- `discovery_system.py` - Legacy system (line 139)
- `enhanced_discovery.py` - Haven-Enhanced version (line 252) ✅ ACTIVE

**Recommendation:** Remove the legacy `discovery_system.py` cog to eliminate duplicate command.

### Archive & Pattern Recognition (4 commands)
| Command | Description | Current Access | Should Be Admin-Only |
|---------|-------------|----------------|---------------------|
| `/advanced-search` | Advanced search through archives | Everyone | ❌ NO (user command) |
| `/pattern-manager` | Manage and analyze detected patterns | Everyone | ✅ YES |
| `/pattern-analysis` | Manually trigger pattern analysis | Everyone | ✅ YES |
| `/view-patterns` | View detected patterns by mystery tier | Everyone | ❌ NO (user command) |

### Community Features (6 commands)
| Command | Description | Current Access | Should Be Admin-Only |
|---------|-------------|----------------|---------------------|
| `/mystery-tier` | View mystery tier progression | Everyone | ❌ NO (user command) |
| `/community-challenge` | View and participate in challenges | Everyone | ❌ NO (user command) |
| `/create-challenge` | Create a community challenge | Everyone | ✅ YES |
| `/leaderboards` | View community leaderboards | Everyone | ❌ NO (user command) |
| `/keeper-story` | Personalized story interaction | Everyone | ❌ NO (user command) |
| `/story-intro` | View Act I introduction | Everyone | ❌ NO (user command) |
| `/story-progress` | View community story progression | Everyone | ❌ NO (user command) |

---

## Commands That Need Admin Protection (9 total)

### Critical Admin-Only Commands
1. ✅ `/reload-haven` - Already protected with `@app_commands.default_permissions(administrator=True)`
2. ❌ `/setup-channels` - Needs admin protection
3. ❌ `/keeper-config` - Needs admin protection
4. ❌ `/haven-export` - Needs admin protection
5. ❌ `/create-challenge` - Needs admin protection
6. ❌ `/pattern-manager` - Needs admin protection
7. ❌ `/pattern-analysis` - Needs admin protection

### Optional Admin Commands (Recommend Public)
8. `/server-stats` - Can remain public (provides transparency)

---

## Duplicate/Legacy Commands to Remove

### Duplicate Discovery System
- **Issue:** Both `discovery_system.py` and `enhanced_discovery.py` register `/discovery-report`
- **Resolution:** Remove/disable `discovery_system.py` cog (legacy system)
- **Keep:** `enhanced_discovery.py` (has Haven database integration and location_name fix)

### Unused/Deprecated Commands
- `/quick-discovery` (discovery_system.py line 265) - Appears unused, may conflict with enhanced system

---

## Environment Configuration

**.env File Status:**
- ✅ `ADMIN_ROLE_ID=1436890437909610618` - Already configured
- ⚠️ `MODERATOR_ROLE_ID=` - Empty (optional to configure)

---

## Implementation Plan

### Phase 1: Add Admin Checks (Priority)
Add permission decorator to these commands:
```python
@app_commands.default_permissions(administrator=True)
```

**Commands to protect:**
1. `/setup-channels`
2. `/keeper-config`
3. `/haven-export`
4. `/create-challenge`
5. `/pattern-manager`
6. `/pattern-analysis`

### Phase 2: Add Runtime Role Checks
For additional security, add runtime checks using ADMIN_ROLE_ID from .env:
```python
async def check_admin(interaction: discord.Interaction) -> bool:
    admin_role_id = os.getenv('ADMIN_ROLE_ID')
    if admin_role_id:
        return any(role.id == int(admin_role_id) for role in interaction.user.roles)
    return interaction.user.guild_permissions.administrator
```

### Phase 3: Remove Legacy Code
1. Disable or remove `discovery_system.py` cog
2. Remove `/quick-discovery` if unused
3. Clean up any backup files (`.backup` extensions)

---

## Command Status Summary

| Status | Count | Commands |
|--------|-------|----------|
| ✅ Working & Correct Permissions | 1 | `/reload-haven` |
| ⚠️ Working but Need Admin Lock | 6 | `/setup-channels`, `/keeper-config`, `/haven-export`, `/create-challenge`, `/pattern-manager`, `/pattern-analysis` |
| ✅ Working & Public (Correct) | 9 | `/discovery-report`, `/search-discoveries`, `/advanced-search`, `/view-patterns`, `/mystery-tier`, `/community-challenge`, `/leaderboards`, `/keeper-story`, `/story-intro`, `/story-progress` |
| ⚠️ Optional Public | 1 | `/server-stats` |
| ❌ Duplicate/Legacy | 1+ | Legacy discovery_system.py commands |

---

## Recommended User Experience

### What Users Should See:
- ✅ Discovery submission commands
- ✅ Search and viewing commands
- ✅ Story and lore commands
- ✅ Leaderboards and progression
- ✅ Community challenges (view/participate)

### What Only Admins Should See:
- 🔒 Channel setup and configuration
- 🔒 Bot settings and behavior
- 🔒 Data export tools
- 🔒 Challenge creation
- 🔒 Pattern analysis tools
- 🔒 System reload commands
