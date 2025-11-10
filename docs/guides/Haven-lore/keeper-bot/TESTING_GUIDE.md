# The Keeper Bot - Phase 5 Testing Guide

## Haven Master Database Integration Testing

This guide provides comprehensive testing procedures for all 19 slash commands in The Keeper Discord bot, with special focus on the new Haven VH-Database.db integration.

---

## Prerequisites

### 1. Environment Setup
- [ ] Copy `.env.example` to `.env`
- [ ] Set `USE_HAVEN_DATABASE=true`
- [ ] Set `HAVEN_DB_PATH` to your VH-Database.db location
- [ ] Configure Discord bot token and guild ID
- [ ] Set up channel IDs (discovery, archive, investigation, lore)

### 2. Database Verification
- [ ] Verify VH-Database.db exists at configured path
- [ ] Verify database has `discoveries` table with correct schema
- [ ] Verify at least one star system exists in systems table
- [ ] Verify at least one planet/moon exists for testing

### 3. Bot Startup
- [ ] Start bot: `python src/main.py`
- [ ] Verify no errors in console
- [ ] Check for "Loaded Haven systems from database" message
- [ ] Confirm slash commands are synced to Discord guild

---

## Critical Integration Tests (Priority 1)

These commands directly interact with the Haven Master database and must be tested first.

### Test 1: `/discovery-report` (Enhanced Version)
**File:** `src/cogs/enhanced_discovery.py` (line 310)

**Purpose:** Report discoveries with Haven star system integration

**Test Steps:**
1. Run `/discovery-report` in Discord
2. **Verify:** System selector dropdown appears
3. **Verify:** Dropdown contains systems from VH-Database.db
4. Select a system from dropdown
5. **Verify:** Location selector shows planets/moons from that system
6. Select a location (planet or moon)
7. **Verify:** Discovery type selector appears with all types
8. Select discovery type
9. **Verify:** Modal form appears with appropriate fields
10. Fill out modal with test data:
    - Name: "Test Ancient Ruins"
    - Description: "Large stone structures with alien inscriptions"
    - Coordinates: "-45.123, 67.890"
    - Condition: "Well Preserved"
    - Time Period: "Ancient"
    - Evidence URL: (optional)
11. Submit modal
12. **Verify:** Success message appears
13. **Verify:** Discovery posted to archive channel
14. **Check Database:** Open VH-Database.db in DB Browser
    - Query: `SELECT * FROM discoveries ORDER BY id DESC LIMIT 1`
    - **Verify:** Discovery exists with correct:
      - `discovery_type`
      - `system_id` (resolved from system name)
      - `planet_id` or `moon_id` (resolved from location)
      - `location_type` (planet/moon)
      - `description`, `coordinates`, `condition`, `time_period`
      - `discovered_by` (Discord username)
      - `discord_user_id` and `discord_guild_id`
15. **Check Control Room:**
    - Open Master Control Room
    - Navigate to System Entry Wizard
    - Find the system you used for testing
    - Click "🔍 Discoveries" button on the planet/moon
    - **Verify:** Your test discovery appears in the window
16. **Check Keeper Database:**
    - Query keeper.db: `SELECT * FROM discoveries ORDER BY id DESC LIMIT 1`
    - **Verify:** Same discovery exists (dual-write successful)

**Expected Result:** ✅ Discovery saved to both databases and visible in Control Room

**Fallback Test:**
- Rename VH-Database.db temporarily
- Run `/discovery-report` again
- **Verify:** Bot falls back to standalone mode
- **Verify:** Command still works without Haven integration
- Restore VH-Database.db

---

### Test 2: `/haven-export`
**File:** `src/cogs/enhanced_discovery.py` (line 490)

**Purpose:** Export discoveries in Haven-compatible format

**Test Steps:**
1. Run `/haven-export` (without parameters)
2. **Verify:** Bot shows export statistics
3. **Verify:** Shows total discoveries count
4. **Verify:** Shows systems covered
5. **Verify:** Backup file created in `data/backups/`
6. Open backup JSON file
7. **Verify:** Contains `haven_exports` array
8. **Verify:** Each discovery has Haven-compatible structure:
   - `system_name`
   - `location_type` (planet/moon/space)
   - `location_name`
   - `discovery_type`
   - `coordinates` (or null)
9. Run `/haven-export system_name:Euclid-System-Test`
10. **Verify:** Export filtered to only that system
11. **Verify:** Backup file created
12. **Verify:** Filtered backup only contains discoveries from specified system

**Expected Result:** ✅ Exports create proper Haven-compatible backup files

---

### Test 3: `/pattern-analysis`
**File:** `src/cogs/pattern_recognition.py` (line 543)

**Purpose:** Analyze discoveries for patterns using Haven regional data

**Test Steps:**
1. Create 3+ discoveries in same system using `/discovery-report`
2. Note the ID of one discovery from success message
3. Run `/pattern-analysis discovery_id:<ID>`
4. **Verify:** Analysis completes successfully
5. **Verify:** Shows pattern detection results
6. **Verify:** If pattern found, shows confidence score
7. **Verify:** If threshold met, investigation thread created
8. **Check Database:** Query keeper.db patterns table
9. **Verify:** Pattern record created if applicable
10. **Verify:** Pattern uses Haven system data for regional coherence

**Expected Result:** ✅ Pattern analysis uses Haven data correctly

---

## Secondary Integration Tests (Priority 2)

Commands that should work seamlessly with Haven integration but don't directly write to VH-Database.

### Test 4: `/search-discoveries`
**File:** `src/cogs/discovery_system.py` (line 309)

**Test Steps:**
1. Run `/search-discoveries query:ruins`
2. **Verify:** Results show discoveries with "ruins" in description/type
3. Run `/search-discoveries discovery_type:ruins`
4. **Verify:** Results filtered to ruins only
5. Run `/search-discoveries user:@YourUsername`
6. **Verify:** Results show only your discoveries
7. **Verify:** Results show location from Haven system if available

**Expected Result:** ✅ Search finds discoveries from both databases

---

### Test 5: `/advanced-search`
**File:** `src/cogs/archive_system.py` (line 266)

**Test Steps:**
1. Run `/advanced-search`
2. Fill modal with:
   - Search Terms: "ancient"
   - Location: System name from Haven database
3. **Verify:** Results filtered to that Haven system
4. **Verify:** Pagination works for 10+ results
5. **Verify:** Location shows Haven system name correctly

**Expected Result:** ✅ Advanced search integrates Haven locations

---

## Standalone Commands (Priority 3)

Commands that don't interact with Haven integration but should continue working normally.

### Test 6: `/quick-discovery`
**File:** `src/cogs/discovery_system.py` (line 265)

**Test Steps:**
1. Run `/quick-discovery discovery_type:Bones description:"Fossil remains" location:"Planet Zeta"`
2. **Verify:** Discovery created quickly
3. **Verify:** Posted to archive channel
4. **Verify:** Saved to keeper.db

**Expected Result:** ✅ Quick discovery works in standalone mode

---

### Test 7: `/pattern-manager`
**File:** `src/cogs/archive_system.py` (line 384)

**Test Steps:**
1. Run `/pattern-manager`
2. **Verify:** Pattern selector shows detected patterns
3. Select a pattern
4. **Verify:** Pattern details display
5. Click "List Discoveries" button
6. **Verify:** Related discoveries shown
7. **Verify:** Includes discoveries from Haven-integrated submissions

**Expected Result:** ✅ Pattern manager shows all discoveries

---

### Test 8: Admin Commands

#### `/setup-channels`
**File:** `src/cogs/admin_tools.py` (line 160)

**Test Steps:**
1. Run `/setup-channels` (admin only)
2. Fill modal with channel mentions or IDs
3. **Verify:** Channels configured successfully
4. **Verify:** Config saved to database

**Expected Result:** ✅ Channel setup works

---

#### `/server-stats`
**File:** `src/cogs/admin_tools.py` (line 233)

**Test Steps:**
1. Run `/server-stats` (admin only)
2. **Verify:** Shows total discoveries (including Haven-integrated ones)
3. **Verify:** Shows pattern count
4. Click "Detailed Stats"
5. **Verify:** Expanded statistics include Haven discoveries

**Expected Result:** ✅ Stats include all discoveries

---

#### `/keeper-config`
**File:** `src/cogs/admin_tools.py` (line 446)

**Test Steps:**
1. Run `/keeper-config pattern_threshold:5`
2. **Verify:** Threshold updated
3. Run `/keeper-config auto_pattern:True`
4. **Verify:** Auto-pattern enabled
5. Run `/keeper-config` (no params)
6. **Verify:** Current config displayed

**Expected Result:** ✅ Config management works

---

### Test 9: Community Features

#### `/mystery-tier`
**File:** `src/cogs/community_features.py` (line 490)

**Test Steps:**
1. Run `/mystery-tier`
2. **Verify:** Shows current tier
3. **Verify:** Progress includes Haven-integrated discoveries
4. Click "View Requirements"
5. **Verify:** Tier requirements displayed

**Expected Result:** ✅ Tier system counts all discoveries

---

#### `/leaderboards`
**File:** `src/cogs/community_features.py` (line 667)

**Test Steps:**
1. Run `/leaderboards`
2. **Verify:** Discoveries leaderboard includes Haven submissions
3. Use selector to switch categories
4. **Verify:** All categories work
5. **Verify:** Rankings accurate

**Expected Result:** ✅ Leaderboards include all discovery sources

---

#### `/community-challenge`
**File:** `src/cogs/community_features.py` (line 581)

**Test Steps:**
1. Run `/community-challenge`
2. **Verify:** Active challenge displayed
3. Click "Submit Entry"
4. **Verify:** Modal accepts Haven-integrated discoveries
5. Click "View Leaderboard"
6. **Verify:** Challenge rankings work

**Expected Result:** ✅ Challenges accept all discovery types

---

#### `/create-challenge`
**File:** `src/cogs/community_features.py` (line 656)

**Test Steps:**
1. Run `/create-challenge` (admin only)
2. Fill modal with challenge details
3. **Verify:** Challenge created
4. **Verify:** Can be completed with Haven discoveries

**Expected Result:** ✅ Challenge creation works

---

#### Story Commands

##### `/keeper-story`
**File:** `src/cogs/community_features.py` (line 719)

**Test Steps:**
1. Run `/keeper-story`
2. **Verify:** Personalized story displays
3. **Verify:** References recent discoveries (including Haven ones)

**Expected Result:** ✅ Story integrates user's Haven discoveries

---

##### `/story-intro`
**File:** `src/cogs/community_features.py` (line 773)

**Test Steps:**
1. Run `/story-intro`
2. **Verify:** Act I introduction displays
3. **Verify:** Story embed formatted correctly

**Expected Result:** ✅ Story intro works

---

##### `/story-progress`
**File:** `src/cogs/community_features.py` (line 808)

**Test Steps:**
1. Run `/story-progress`
2. **Verify:** Shows community progression
3. **Verify:** Milestones reference discovery counts
4. Click "Read Act Intro"
5. **Verify:** Act intro displayed

**Expected Result:** ✅ Story progression tracks all discoveries

---

### Test 10: View Patterns

#### `/view-patterns`
**File:** `src/cogs/pattern_recognition.py` (line 591)

**Test Steps:**
1. Run `/view-patterns`
2. **Verify:** All patterns displayed grouped by tier
3. Run `/view-patterns tier:2`
4. **Verify:** Only tier 2 patterns shown
5. **Verify:** Patterns include Haven-integrated discoveries

**Expected Result:** ✅ Pattern viewing works across all sources

---

## Database Integrity Checks

After completing all tests, verify database integrity:

### VH-Database.db Checks
```sql
-- Check discoveries table exists
SELECT name FROM sqlite_master WHERE type='table' AND name='discoveries';

-- Verify discoveries have proper foreign keys
SELECT COUNT(*) FROM discoveries WHERE system_id IS NOT NULL;
SELECT COUNT(*) FROM discoveries WHERE planet_id IS NOT NULL;
SELECT COUNT(*) FROM discoveries WHERE moon_id IS NOT NULL;

-- Check discovery types
SELECT discovery_type, COUNT(*) FROM discoveries GROUP BY discovery_type;

-- Verify location resolution
SELECT
    d.id,
    d.discovery_name,
    s.name as system_name,
    p.name as planet_name,
    m.name as moon_name
FROM discoveries d
LEFT JOIN systems s ON d.system_id = s.id
LEFT JOIN planets p ON d.planet_id = p.id
LEFT JOIN moons m ON d.moon_id = m.id
ORDER BY d.id DESC
LIMIT 10;
```

### Keeper.db Checks
```sql
-- Verify discoveries synced
SELECT COUNT(*) FROM discoveries;

-- Check patterns created
SELECT COUNT(*) FROM patterns;

-- Verify guild data
SELECT * FROM server_config;
```

---

## Control Room UI Testing

### Discoveries Window Testing

1. **From System Entry Wizard:**
   - [ ] Open System Entry Wizard
   - [ ] Load an existing system that has discoveries
   - [ ] Click "🔍 Discoveries" on a planet card
   - [ ] **Verify:** DiscoveriesWindow opens
   - [ ] **Verify:** Shows discoveries for that planet only
   - [ ] Click "🔍" on a moon row
   - [ ] **Verify:** Shows discoveries for that moon only

2. **Filter Testing:**
   - [ ] Open discoveries window
   - [ ] Use filter dropdown to select "Ruins"
   - [ ] **Verify:** Only ruins-type discoveries shown
   - [ ] Try each filter type (Fossils, Logs, Tech, etc.)
   - [ ] **Verify:** Each filter works correctly
   - [ ] Select "All"
   - [ ] **Verify:** All discoveries shown again

3. **Display Testing:**
   - [ ] **Verify:** Discovery cards show:
     - Type icon and name
     - Mystery tier badge (if applicable)
     - Timestamp
     - Description
     - Condition, Era, Coordinates (if provided)
     - Significance analysis (if provided)
     - Discoverer name
   - [ ] **Verify:** Cards use themed styling (purple/cyan)
   - [ ] **Verify:** Scrolling works for 10+ discoveries
   - [ ] Click "Refresh" button
   - [ ] **Verify:** Latest discoveries loaded

4. **Error Handling:**
   - [ ] Open discoveries window when no discoveries exist
   - [ ] **Verify:** Shows "No discoveries yet" message
   - [ ] Try opening without database mode enabled
   - [ ] **Verify:** Shows warning message about database requirement

---

## Performance Testing

### Load Testing
1. Create 100+ discoveries via bot
2. Run `/search-discoveries`
3. **Verify:** Results return within 2 seconds
4. Run `/advanced-search` with no filters
5. **Verify:** Pagination handles large result sets
6. Open discoveries window for system with 50+ discoveries
7. **Verify:** Window loads smoothly
8. **Verify:** Scrolling is responsive

### Database Query Performance
1. Run EXPLAIN QUERY PLAN on critical queries
2. **Verify:** Proper indexes used
3. **Verify:** No table scans on large tables

---

## Failure Recovery Testing

### Test Database Unavailability
1. Stop bot
2. Rename VH-Database.db to VH-Database.db.bak
3. Start bot
4. **Verify:** Bot logs warning about database not found
5. **Verify:** Bot falls back to JSON mode or standalone
6. Run `/discovery-report`
7. **Verify:** Enhanced discovery falls back to basic mode
8. Restore VH-Database.db
9. Restart bot
10. **Verify:** Database integration restored

### Test Partial Data
1. Create discovery with missing optional fields
2. **Verify:** Discovery saves successfully
3. **Verify:** Control Room displays discovery correctly with missing fields
4. **Verify:** No errors or crashes

### Test Invalid Foreign Keys
1. Attempt to create discovery for non-existent system
2. **Verify:** Graceful error handling
3. **Verify:** Discovery either rejected or saved without foreign key

---

## Regression Testing Checklist

After any code changes, verify:

- [ ] All 19 slash commands still respond
- [ ] Discovery submission works (both enhanced and basic)
- [ ] Database writes succeed
- [ ] Control Room discoveries window opens
- [ ] Filters work in discoveries window
- [ ] Pattern detection functions
- [ ] Search commands return results
- [ ] Admin commands require permissions
- [ ] Community features work
- [ ] Story commands display
- [ ] No console errors or warnings
- [ ] Bot stays online for 24+ hours

---

## Success Criteria

Phase 5 is complete when:

✅ All 19 slash commands tested and working
✅ Enhanced `/discovery-report` reads from VH-Database.db
✅ Enhanced `/discovery-report` writes to VH-Database.db
✅ Discoveries appear in Control Room UI
✅ Filter and search functions work across both databases
✅ Pattern analysis uses Haven data
✅ Dual-write to keeper.db and VH-Database.db verified
✅ Fallback to standalone mode works
✅ No critical errors or crashes
✅ Documentation complete

---

## Common Issues and Solutions

### Issue: Bot can't find VH-Database.db
**Solution:** Check HAVEN_DB_PATH in .env, use absolute path

### Issue: Discoveries not showing in Control Room
**Solution:** Verify database backend enabled in Control Room settings

### Issue: Foreign key constraint failed
**Solution:** Ensure system/planet/moon exists before creating discovery

### Issue: Slash commands not appearing in Discord
**Solution:** Run sync diagnostic script, check bot permissions

### Issue: Discovery submitted but not in database
**Solution:** Check write_discovery_to_database() return value, verify exceptions logged

---

## Testing Log Template

```
Test Date: ___________
Tester: ___________
Bot Version: ___________
Database Version: ___________

Command Tested: ___________
Result: ✅ Pass / ❌ Fail
Notes: ___________

Issues Found: ___________
Screenshots: ___________
```

---

## Next Steps After Testing

1. Document any bugs found
2. Create GitHub issues for failures
3. Update bot documentation
4. Train users on new features
5. Monitor production logs
6. Schedule periodic regression tests

---

**Testing Guide Version:** 1.0
**Last Updated:** 2025-01-10
**Author:** Haven Development Team
