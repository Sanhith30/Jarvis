"""
Generate a LiveKit token to connect to your Jarvis agent
"""

from livekit import api
import os
from dotenv import load_dotenv

load_dotenv()

# Get credentials from .env
api_key = os.getenv('LIVEKIT_API_KEY')
api_secret = os.getenv('LIVEKIT_API_SECRET')
livekit_url = os.getenv('LIVEKIT_URL')

if not api_key or not api_secret:
    print("❌ Error: LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set in .env file")
    exit(1)

# Create token
token = api.AccessToken(api_key, api_secret)

# Set identity and permissions
token.with_identity("user-" + str(os.urandom(4).hex()))
token.with_name("Jarvis User")
token.with_grants(api.VideoGrants(
    room_join=True,
    room="jarvis-room",
    can_publish=True,
    can_subscribe=True
))

jwt_token = token.to_jwt()

print("\n" + "="*70)
print("🎫 LIVEKIT TOKEN GENERATED")
print("="*70)
print(f"\n📍 LiveKit URL: {livekit_url}")
print(f"🏠 Room Name: jarvis-room")
print(f"\n🔑 Token:\n{jwt_token}")
print("\n" + "="*70)
print("\n📋 How to use:")
print("1. Keep your agent running: python agent.py dev")
print("2. Go to: https://meet.livekit.io")
print("3. Click 'Custom' or 'Settings'")
print(f"4. Enter URL: {livekit_url}")
print("5. Paste the token above")
print("6. Click 'Connect' and join the room")
print("7. Enable your microphone and start talking!")
print("="*70 + "\n")
