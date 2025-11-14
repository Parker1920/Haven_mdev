"""
Migration script to add guild_id column to discoveries table.
Run this script to update existing databases.
"""

import asyncio
import aiosqlite
import os
import sys

async def migrate_database():
    """Add guild_id column to discoveries table if it doesn't exist."""
    
    db_path = "data/keeper.db"
    
    if not os.path.exists(db_path):
        print(f"✅ Database not found at {db_path} - no migration needed (fresh install)")
        return True
    
    print(f"🔍 Checking database at {db_path}...")
    
    try:
        async with aiosqlite.connect(db_path) as db:
            # Check if guild_id column already exists
            cursor = await db.execute("PRAGMA table_info(discoveries)")
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'guild_id' in column_names:
                print("✅ guild_id column already exists in discoveries table - no migration needed")
                return True
            
            print("🔧 Adding guild_id column to discoveries table...")
            
            # Add guild_id column (nullable since existing records won't have it)
            await db.execute("ALTER TABLE discoveries ADD COLUMN guild_id TEXT")
            await db.commit()
            
            print("✅ Successfully added guild_id column to discoveries table")
            
            # Count existing records
            cursor = await db.execute("SELECT COUNT(*) FROM discoveries")
            count = (await cursor.fetchone())[0]
            print(f"📊 {count} existing discovery records will have NULL guild_id (can be updated manually if needed)")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("THE KEEPER - Database Migration")
    print("Adding guild_id column to discoveries table")
    print("=" * 60)
    print()
    
    success = asyncio.run(migrate_database())
    
    print()
    if success:
        print("✅ Migration completed successfully!")
        print()
        print("Next steps:")
        print("1. Restart The Keeper bot")
        print("2. Bot will now track discoveries per guild")
        print("3. Existing discoveries will show as NULL guild_id")
        sys.exit(0)
    else:
        print("❌ Migration failed!")
        print()
        print("Please check the error above and try again.")
        print("You may need to backup your database and restore it.")
        sys.exit(1)
