"""
Verify Haven Master Database Integration
Quick verification script to check all integration points before testing
"""

import os
import sys
import sqlite3
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def check_env_file():
    """Check if .env file exists and has required configuration"""
    print("=" * 60)
    print("1. Checking .env Configuration")
    print("=" * 60)

    env_path = Path(__file__).parent / ".env"
    env_example_path = Path(__file__).parent / ".env.example"

    if not env_path.exists():
        print("❌ .env file not found")
        print(f"   Expected at: {env_path}")
        if env_example_path.exists():
            print(f"   Copy from: {env_example_path}")
        return False

    print(f"✅ .env file found at: {env_path}")

    # Read and check key settings
    with open(env_path, 'r') as f:
        env_content = f.read()

    required_vars = [
        'BOT_TOKEN',
        'GUILD_ID',
        'USE_HAVEN_DATABASE',
        'HAVEN_DB_PATH'
    ]

    missing_vars = []
    for var in required_vars:
        if var not in env_content or f"{var}=your_" in env_content or f"{var}=" in env_content and env_content.split(f"{var}=")[1].split('\n')[0].strip() == '':
            missing_vars.append(var)

    if missing_vars:
        print(f"⚠️  Missing or not configured: {', '.join(missing_vars)}")
        return False

    print("✅ All required environment variables configured")

    # Check USE_HAVEN_DATABASE setting
    if 'USE_HAVEN_DATABASE=true' in env_content:
        print("✅ USE_HAVEN_DATABASE=true (Database mode enabled)")
    else:
        print("⚠️  USE_HAVEN_DATABASE not set to 'true'")
        print("   Bot will fall back to JSON mode")

    return True

def check_haven_database():
    """Check if VH-Database.db exists and has required schema"""
    print("\n" + "=" * 60)
    print("2. Checking Haven VH-Database.db")
    print("=" * 60)

    # Try to find database from .env
    env_path = Path(__file__).parent / ".env"
    db_path = None

    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('HAVEN_DB_PATH='):
                    db_path = line.split('=')[1].strip()
                    break

    if not db_path:
        print("❌ HAVEN_DB_PATH not found in .env")
        return False

    db_path = Path(db_path)
    if not db_path.exists():
        print(f"❌ VH-Database.db not found at: {db_path}")
        return False

    print(f"✅ VH-Database.db found at: {db_path}")

    # Check schema
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check required tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        required_tables = ['systems', 'planets', 'moons', 'discoveries']
        missing_tables = [t for t in required_tables if t not in tables]

        if missing_tables:
            print(f"❌ Missing required tables: {', '.join(missing_tables)}")
            conn.close()
            return False

        print("✅ All required tables exist: systems, planets, moons, discoveries")

        # Check discoveries table schema
        cursor.execute("PRAGMA table_info(discoveries)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}

        required_columns = [
            'id', 'discovery_type', 'system_id', 'planet_id', 'moon_id',
            'location_type', 'description', 'discovered_by', 'discord_user_id',
            'submission_timestamp'
        ]

        missing_columns = [c for c in required_columns if c not in columns]

        if missing_columns:
            print(f"❌ Discoveries table missing columns: {', '.join(missing_columns)}")
            conn.close()
            return False

        print("✅ Discoveries table has correct schema")

        # Check if we have test data
        cursor.execute("SELECT COUNT(*) FROM systems")
        system_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM planets")
        planet_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM moons")
        moon_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM discoveries")
        discovery_count = cursor.fetchone()[0]

        print(f"📊 Database Statistics:")
        print(f"   - Systems: {system_count}")
        print(f"   - Planets: {planet_count}")
        print(f"   - Moons: {moon_count}")
        print(f"   - Discoveries: {discovery_count}")

        if system_count == 0:
            print("⚠️  No systems in database - add at least one for testing")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def check_bot_files():
    """Check if bot files have the integration code"""
    print("\n" + "=" * 60)
    print("3. Checking Bot Integration Files")
    print("=" * 60)

    bot_root = Path(__file__).parent

    # Check haven_integration.py
    haven_int_path = bot_root / "src" / "core" / "haven_integration.py"
    if not haven_int_path.exists():
        print(f"❌ haven_integration.py not found at: {haven_int_path}")
        return False

    print(f"✅ haven_integration.py found")

    with open(haven_int_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for database integration
    if 'def _load_from_database' not in content:
        print("❌ _load_from_database method not found in haven_integration.py")
        return False

    if 'def write_discovery_to_database' not in content:
        print("❌ write_discovery_to_database method not found")
        return False

    print("✅ Database integration methods present")

    # Check enhanced_discovery.py
    enh_disc_path = bot_root / "src" / "cogs" / "enhanced_discovery.py"
    if not enh_disc_path.exists():
        print(f"❌ enhanced_discovery.py not found at: {enh_disc_path}")
        return False

    print(f"✅ enhanced_discovery.py found")

    with open(enh_disc_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for VH-Database write
    if 'write_discovery_to_database' not in content:
        print("❌ VH-Database write call not found in enhanced_discovery.py")
        return False

    print("✅ Dual-write to VH-Database implemented")

    return True

def check_control_room_integration():
    """Check if Control Room has discoveries viewer"""
    print("\n" + "=" * 60)
    print("4. Checking Control Room Integration")
    print("=" * 60)

    # Navigate up to Haven_mdev root
    control_room_root = Path(__file__).parent.parent.parent.parent.parent

    # Check discoveries_window.py
    disc_window_path = control_room_root / "src" / "discoveries_window.py"
    if not disc_window_path.exists():
        print(f"❌ discoveries_window.py not found at: {disc_window_path}")
        return False

    print(f"✅ discoveries_window.py found")

    # Check system_entry_wizard.py integration
    wizard_path = control_room_root / "src" / "system_entry_wizard.py"
    if not wizard_path.exists():
        print(f"❌ system_entry_wizard.py not found at: {wizard_path}")
        return False

    with open(wizard_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'from discoveries_window import DiscoveriesWindow' not in content:
        print("❌ DiscoveriesWindow import not found in system_entry_wizard.py")
        return False

    if 'def view_planet_discoveries' not in content:
        print("❌ view_planet_discoveries method not found")
        return False

    if 'def view_moon_discoveries' not in content:
        print("❌ view_moon_discoveries method not found")
        return False

    if '🔍 Discoveries' not in content:
        print("❌ Discoveries button not found in UI")
        return False

    print("✅ Discoveries window integrated into Control Room")
    print("✅ View methods implemented")
    print("✅ UI buttons added")

    return True

def check_database_common():
    """Check if common/database.py has discovery methods"""
    print("\n" + "=" * 60)
    print("5. Checking Common Database Module")
    print("=" * 60)

    control_room_root = Path(__file__).parent.parent.parent.parent.parent
    db_common_path = control_room_root / "src" / "common" / "database.py"

    if not db_common_path.exists():
        print(f"❌ common/database.py not found at: {db_common_path}")
        return False

    print(f"✅ common/database.py found")

    with open(db_common_path, 'r', encoding='utf-8') as f:
        content = f.read()

    required_methods = [
        'def add_discovery',
        'def get_discoveries',
        'def get_discovery_by_id',
        'def update_discovery',
        'def delete_discovery',
        'def get_discovery_count'
    ]

    missing_methods = [m for m in required_methods if m not in content]

    if missing_methods:
        print(f"❌ Missing methods: {', '.join([m.replace('def ', '') for m in missing_methods])}")
        return False

    print("✅ All discovery CRUD methods present")

    return True

def main():
    """Run all verification checks"""
    print("\n" + "=" * 60)
    print("HAVEN MASTER DATABASE INTEGRATION VERIFICATION")
    print("=" * 60)
    print()

    results = {
        'Environment Configuration': check_env_file(),
        'Haven VH-Database.db': check_haven_database(),
        'Bot Integration Files': check_bot_files(),
        'Control Room Integration': check_control_room_integration(),
        'Common Database Module': check_database_common()
    }

    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    all_passed = True
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check_name}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 All checks passed! Ready for Phase 5 testing.")
        print("\nNext steps:")
        print("1. Start Discord bot: python src/main.py")
        print("2. Follow TESTING_GUIDE.md for comprehensive testing")
        print("3. Start with Priority 1 tests (/discovery-report, /haven-export)")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix issues before testing.")
        print("\nRefer to:")
        print("- .env.example for configuration")
        print("- TESTING_GUIDE.md for requirements")
        return 1

if __name__ == "__main__":
    sys.exit(main())
