# Channel Configuration Centralization Fix

## Problem Identified

The bot had **INCONSISTENT channel configuration sources** causing pattern alerts to fail while Act transition alerts worked:

### Before Fix - Three Different Sources:

1. **Act Transition Alerts** (`enhanced_discovery.py` line 570):
   - Used `os.getenv('ARCHIVE_CHANNEL_ID')` - reads from **.env file**
   - ✅ **WORKED** - You got the Act II announcement

2. **Pattern Alerts** (`pattern_recognition.py` line 426):
   - Used `await self.db.get_server_config()` - reads from **DATABASE**
   - ❌ **FAILED** - No config in database (requires `/setup-channels` command)

3. **Discovery Archive Posts** (`enhanced_discovery.py` line 443):
   - Used `await self.db.get_server_config()` - reads from **DATABASE**
   - ❌ **FAILED** - Same database issue

## Root Cause

You have the channel IDs in your `.env` file, but the pattern alert code was **ONLY** checking the database (which is empty because you never ran `/setup-channels`). This created "dead code paths" where some notifications worked (reading from .env) while others failed (reading from database).

## Solution Implemented

Created **centralized channel configuration** (`src/core/channel_config.py`) with fallback logic:

```python
class ChannelConfig:
    async def get_archive_channel(self, guild):
        # 1. Try database first (from /setup-channels)
        # 2. Fallback to environment variable (.env file)
        # 3. Return None if neither exists
```

### Files Modified:

1. **NEW FILE**: `src/core/channel_config.py`
   - Centralized channel configuration manager
   - Prioritizes database, falls back to environment variables
   - Methods: `get_archive_channel()`, `get_investigation_channel()`, `get_community_channel()`

2. **pattern_recognition.py**:
   - Added `from core.channel_config import ChannelConfig`
   - Replaced database-only lookup with centralized config
   - Now uses `self.channel_config.get_archive_channel()`

3. **enhanced_discovery.py**:
   - Added `from core.channel_config import ChannelConfig`
   - Replaced BOTH database lookup AND direct env lookup
   - Both `post_to_archive_channel()` and `_announce_act_transition()` now use centralized config

## Result

**ALL notifications now work consistently:**
- ✅ Pattern alerts will now use your .env ARCHIVE_CHANNEL_ID
- ✅ Act transition alerts still work (using same centralized config)
- ✅ Discovery archive posts now work (using same centralized config)
- ✅ If you later run `/setup-channels`, database config will take priority
- ✅ No more "dead files" - single source of truth for channel configuration

## Testing the Fix

You already have 2 patterns detected (Pattern 1 and Pattern 2) from your 5 discoveries. To test:

1. Submit a 6th discovery of the same type (🦗 biological findings)
2. Pattern alert should now appear in your archive channel
3. Check terminal logs for: `"Pattern alert posted for pattern X"`

## Why This Matters

**Before**: Each notification type independently decided where to read channel IDs from → inconsistent behavior

**After**: All notifications use the same centralized helper → consistent behavior with smart fallback

**Benefit**: You don't need to run `/setup-channels` if you already have IDs in `.env`, but the option exists for users who prefer the database approach.
