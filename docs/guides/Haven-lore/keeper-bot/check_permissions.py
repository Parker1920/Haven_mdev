"""
Quick diagnostic script to check bot permissions and generate proper invite URL
"""
import os
from dotenv import load_dotenv

# Load environment
load_dotenv('.env')

bot_token = os.getenv('BOT_TOKEN')
guild_id = os.getenv('GUILD_ID')

if not bot_token:
    print("❌ BOT_TOKEN not found in .env file")
    exit(1)

# Extract bot's application ID from token
try:
    # Discord bot tokens have the format: base64(bot_id).random.random
    import base64
    bot_id = bot_token.split('.')[0]
    # Decode the base64 bot ID
    decoded = base64.b64decode(bot_id + '==')  # Add padding
    application_id = decoded.decode('utf-8')
    print(f"✅ Bot Application ID: {application_id}")
except Exception as e:
    print(f"⚠️  Could not extract bot ID: {e}")
    print("Please get your Application ID from the Discord Developer Portal")
    application_id = "YOUR_APPLICATION_ID"

print(f"✅ Guild ID: {guild_id}")
print()
print("=" * 70)
print("BOT INVITE URL (Copy this URL and open in your browser)")
print("=" * 70)

# Create invite URL with proper permissions and scopes
permissions = 274878294016  # Send Messages, Embed Links, Attach Files, Read Message History, Use Slash Commands, Manage Threads

invite_url = f"https://discord.com/api/oauth2/authorize?client_id={application_id}&permissions={permissions}&scope=bot%20applications.commands"

print(invite_url)
print()
print("=" * 70)
print()
print("INSTRUCTIONS:")
print("1. Copy the URL above")
print("2. Open it in your web browser")
print("3. Select your Discord server")
print("4. Click 'Authorize'")
print("5. This will re-invite the bot with correct permissions for slash commands")
print()
print("If the bot is already in your server, Discord will update its permissions.")
