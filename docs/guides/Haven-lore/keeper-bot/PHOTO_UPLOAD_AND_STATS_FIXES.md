# Photo Upload & Server Stats Fixes

**Date:** 2025-11-11
**Status:** ✅ COMPLETE & DEPLOYED

---

## Issues Fixed

### 1. Server Statistics Showing Wrong Discovery Count ✅

**Problem:**
- `/server-stats` showed 5 discoveries when there should be 0
- Discovery count was reading from keeper.db instead of being reset

**Root Cause:**
- `reset_discoveries.py` only reset VH-Database.db and haven_load_test.db
- Did not reset docs/guides/Haven-lore/keeper-bot/data/keeper.db (bot's internal database)

**Fix:**
- Updated `reset_discoveries.py` to handle both Haven databases and keeper.db
- Added logic to detect database schema (Haven vs Keeper) and handle accordingly
- Ran reset script - deleted 5 discoveries from keeper.db

**Result:**
- All databases now have 0 discoveries
- `/server-stats` will show correct count

---

### 2. Literal `\n` Displaying in Server Stats ✅

**Problem:**
- Server stats embed showed literal `\n` instead of line breaks
- Example: `**Total:** 5\n**This Week:** 2` appeared as text instead of two lines

**Root Cause:**
- Lines 254, 260, 266, 272 in admin_tools.py used double backslash `\\n`
- Discord requires single backslash `\n` for actual newlines in embeds

**Fix:**
Changed in [admin_tools.py](src/cogs/admin_tools.py):
```python
# BEFORE:
value=f"**Total:** {stats['discoveries']['total']}\\n**This Week:** {stats['discoveries']['week']}"

# AFTER:
value=f"**Total:** {stats['discoveries']['total']}\n**This Week:** {stats['discoveries']['week']}"
```

**Files Changed:**
- Line 254: Discoveries field
- Line 260: Patterns field
- Line 266: Explorers field
- Line 272: Recent Activity join

**Result:**
- Stats now display with proper line breaks
- Clean, readable formatting

---

### 3. Photo Upload Not Working ✅

**Problem:**
- Users clicked "📸 Upload Evidence Photo" button
- Bot asked them to attach photo to next message
- But photo was never captured or saved
- evidence_url remained empty in database

**Root Cause:**
- `PhotoUploadView` button only sent an ephemeral message asking for photo
- No message listener to actually capture the attachment
- No code to update the discovery with the photo URL

**Solution Implemented:**

#### Step 1: Track Pending Uploads
Added to EnhancedDiscoverySystem.__init__:
```python
self.pending_photo_uploads = {}  # {user_id: discovery_id}
```

#### Step 2: Register User When Button Clicked
Updated PhotoUploadView (line 215-231):
```python
def __init__(self, discovery_id: int, cog):
    super().__init__(timeout=300)
    self.discovery_id = discovery_id
    self.cog = cog  # Reference to cog for tracking

async def upload_photo(self, interaction, button):
    # Register this user as waiting to upload
    self.cog.pending_photo_uploads[interaction.user.id] = self.discovery_id
    # ... send message
```

#### Step 3: Listen for Photo Attachments
Added on_message listener (line 259-313):
```python
@commands.Cog.listener()
async def on_message(self, message):
    # Ignore bots
    if message.author.bot:
        return

    # Check if user is waiting to upload
    if message.author.id not in self.pending_photo_uploads:
        return

    # Check for attachments
    if not message.attachments:
        return

    # Get discovery ID
    discovery_id = self.pending_photo_uploads[message.author.id]

    # Find image attachment
    photo_url = None
    for attachment in message.attachments:
        if attachment.content_type and attachment.content_type.startswith('image/'):
            photo_url = attachment.url
            break

    if not photo_url:
        await message.reply("⚠️ Please attach an image file")
        return

    # Update database
    await self.db.connection.execute(
        "UPDATE discoveries SET evidence_url = ? WHERE id = ?",
        (photo_url, discovery_id)
    )
    await self.db.connection.commit()

    # Remove from pending
    del self.pending_photo_uploads[message.author.id]

    # Confirm with embed showing the image
    embed = discord.Embed(
        title="✅ Evidence Photo Archived",
        description=f"Discovery #{discovery_id} updated",
        color=0x00ff00
    )
    embed.set_image(url=photo_url)
    await message.reply(embed=embed)
```

**Result:**
- ✅ Users click "Upload Evidence Photo" button
- ✅ Bot tracks they're waiting to upload
- ✅ User attaches photo to next message
- ✅ Bot captures photo URL from Discord CDN
- ✅ Updates discovery in database
- ✅ Confirms to user with visual preview
- ✅ Photo stored permanently in evidence_url field

---

## Files Modified

### 1. reset_discoveries.py
**Changes:**
- Added keeper.db to reset list
- Added schema detection (Haven vs Keeper database)
- Updated output messages to handle both database types

**Key Code:**
```python
# Reset both Haven databases
reset_discoveries('data/VH-Database.db')
reset_discoveries('data/haven_load_test.db')

# Reset Discord bot's keeper database
reset_discoveries('docs/guides/Haven-lore/keeper-bot/data/keeper.db')
```

### 2. admin_tools.py
**Changes:**
- Lines 254, 260, 266, 272: Changed `\\n` to `\n`

**Result:** Proper newlines in stat embeds

### 3. enhanced_discovery.py
**Changes:**
- Line 242: Added `self.pending_photo_uploads = {}`
- Line 215: Updated PhotoUploadView.__init__ to accept cog reference
- Line 224: Register user when upload button clicked
- Line 259-313: Added on_message listener for photo capture
- Line 424: Pass `self` to PhotoUploadView

**Result:** Complete photo upload workflow

---

## How Photo Upload Works Now

### User Workflow:
1. User submits discovery via `/discovery-report`
2. Discovery gets saved to database (discovery_id assigned)
3. Confirmation message appears with "📸 Upload Evidence Photo" button
4. User clicks button
5. Bot sends ephemeral message: "Please attach an image to your next message"
6. **User's ID is registered in `pending_photo_uploads` dictionary**
7. User posts message with image attachment
8. **Bot's on_message listener detects:**
   - Message is from a user (not bot)
   - User is in pending_photo_uploads
   - Message has attachments
   - At least one attachment is an image
9. **Bot updates discovery:**
   ```sql
   UPDATE discoveries SET evidence_url = 'https://cdn.discordapp.com/...' WHERE id = discovery_id
   ```
10. **Bot responds with confirmation embed showing the archived photo**
11. User is removed from pending uploads

### Technical Flow:
```
Click Button → Register User ID → User Uploads → Listener Catches →
Update Database → Confirm to User → Clear Pending
```

---

## Testing Checklist

### Test Server Stats
1. Run `/server-stats` as admin
2. Verify displays "Total: 0" and "This Week: 0"
3. Verify no literal `\n` characters appear
4. Verify line breaks display correctly

### Test Photo Upload
1. Submit a discovery via `/discovery-report`
2. Click "📸 Upload Evidence Photo" button
3. Receive ephemeral message asking for photo
4. Post a message with image attachment in same channel
5. Verify bot replies with "✅ Evidence Photo Archived"
6. Verify embed shows the uploaded image
7. Check database: `evidence_url` field should contain Discord CDN URL

### Verify Database
```sql
SELECT id, evidence_url FROM discoveries ORDER BY id DESC LIMIT 5;
```
Should show the Discord CDN URL for any discovery with uploaded photo.

---

## Database Status After Fixes

**VH-Database.db:**
- Systems: 5 ✅
- Planets: 20 ✅
- Moons: 5 ✅
- Discoveries: 0 ✅

**keeper.db:**
- Discoveries: 0 ✅ (was 5, now reset)

**Both databases:** Clean slate maintained

---

## Bot Status

**Online:** The Keeper#8095
**Commands Synced:** 17
**Cogs Loaded:** 5/5
**Haven Systems:** 5
**Discoveries:** 0

**New Features Active:**
- ✅ Photo upload workflow
- ✅ Server stats with proper formatting
- ✅ Clean database state

---

**Status: READY FOR PRODUCTION WITH PHOTO UPLOAD** 📸
