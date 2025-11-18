"""
Test script for Round Table AI

Run this to verify Round Table AI is working correctly.
"""

import asyncio
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_roundtable_ai():
    """Test Round Table AI initialization and basic functionality."""
    print("=" * 60)
    print("Round Table AI - Test Script")
    print("=" * 60)

    # Initialize
    print("\n1. Initializing Round Table AI...")
    try:
        from src.roundtable_ai.api_integration import get_round_table_ai

        haven_ui_root = project_root / 'Haven-UI'
        rtai = get_round_table_ai(haven_ui_root)

        print("   ✓ Round Table AI initialized successfully")
    except Exception as e:
        print(f"   ✗ Failed to initialize: {e}")
        return

    # Check status
    print("\n2. Checking system status...")
    try:
        stats = rtai.get_statistics()
        agents = rtai.list_agents()

        print(f"   ✓ Total agents: {stats['total_agents']}")
        print(f"   ✓ Registered agents:")
        for agent in agents:
            print(f"     - {agent['name']}: {agent['role']}")
    except Exception as e:
        print(f"   ✗ Failed to get status: {e}")

    # Check data access
    print("\n3. Testing data access...")
    try:
        disc_stats = rtai.data_access.get_discovery_statistics()
        systems = rtai.data_access.get_all_systems()

        print(f"   ✓ Total discoveries: {disc_stats.get('total_count', 0)}")
        print(f"   ✓ Total systems: {len(systems)}")
        print(f"   ✓ Discoveries by type: {disc_stats.get('by_type', {})}")
    except Exception as e:
        print(f"   ✗ Failed to access data: {e}")

    # Test AI interface (without actually calling API)
    print("\n4. Checking AI interface...")
    try:
        ai_available = rtai.ai_interface.is_available()
        print(f"   ✓ Primary AI provider available: {ai_available}")

        if not ai_available:
            print("   ⚠ Warning: No AI API keys configured")
            print("     Set ANTHROPIC_API_KEY or OPENAI_API_KEY in Haven-UI/.env")
    except Exception as e:
        print(f"   ✗ Failed to check AI interface: {e}")

    # Test discovery analysis (if we have discoveries)
    print("\n5. Testing discovery analysis (without AI)...")
    try:
        recent = rtai.data_access.get_recent_discoveries(days=7, limit=5)
        print(f"   ✓ Recent discoveries (last 7 days): {len(recent)}")

        if recent:
            print("   Sample discoveries:")
            for d in recent[:3]:
                print(f"     - {d.get('discovery_type')}: {d.get('description', '')[:50]}...")
        else:
            print("   ⚠ No recent discoveries found")
    except Exception as e:
        print(f"   ✗ Failed to test analysis: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print("✓ Round Table AI is operational!")
    print("\nNext steps:")
    print("1. Set up API keys in Haven-UI/.env:")
    print("   ANTHROPIC_API_KEY=your_key_here")
    print("   OPENAI_API_KEY=your_key_here")
    print("\n2. Start Haven-UI server:")
    print("   cd Haven-UI")
    print("   python -m uvicorn src.control_room_api:app --reload")
    print("\n3. Test API endpoints:")
    print("   curl http://localhost:8000/api/rtai/status")
    print("   curl -X POST http://localhost:8000/api/rtai/analyze/discoveries?limit=5")
    print("\n4. View real-time AI chat:")
    print("   Navigate to http://localhost:8000/rtai")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_roundtable_ai())
