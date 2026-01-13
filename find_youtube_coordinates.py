"""
Helper script to find the exact coordinates for YouTube first video on YOUR screen
Run this to get the perfect click position for your display
"""
import pyautogui
import time
import webbrowser

print("🎯 YOUTUBE COORDINATE FINDER")
print("="*60)
print("\nThis script will help you find the exact position to click")
print("the first video on YouTube for your screen resolution.\n")

# Get screen size
screen_width, screen_height = pyautogui.size()
print(f"📺 Your Screen Resolution: {screen_width} x {screen_height}")

# Open YouTube search
print("\n🌐 Opening YouTube search for 'test song'...")
webbrowser.open("https://www.youtube.com/results?search_query=test+song")

print("\n⏳ Waiting 10 seconds for page to load...")
print("   (Make sure YouTube is fully loaded)")
time.sleep(10)

print("\n" + "="*60)
print("🖱️  INSTRUCTIONS:")
print("="*60)
print("1. Move your mouse over the FIRST VIDEO THUMBNAIL")
print("2. Position it in the CENTER of the first video")
print("3. Wait there for 3 seconds")
print("4. The script will capture the coordinates")
print("\n⏰ You have 10 seconds to position your mouse...")
print("   Starting in 3...")
time.sleep(1)
print("   2...")
time.sleep(1)
print("   1...")
time.sleep(1)
print("\n🎯 Position your mouse NOW over the first video!")
print("   (Waiting 10 seconds...)")

time.sleep(10)

# Get mouse position
x, y = pyautogui.position()

print("\n" + "="*60)
print("✅ COORDINATES CAPTURED!")
print("="*60)
print(f"\n📍 First Video Position: X={x}, Y={y}")
print(f"\n💡 Add this to your jarvis_ultimate.py:")
print(f"   click_attempts = [")
print(f"       ({x}, {y}),  # Your custom position")
print(f"       ({x-50}, {y-30}),  # Slightly left and up")
print(f"       ({x+50}, {y+30}),  # Slightly right and down")
print(f"       ({x}, {y+50}),  # Below")
print(f"   ]")

print("\n" + "="*60)
print("🧪 TESTING THE CLICK...")
print("="*60)
print(f"\nMoving mouse to ({x}, {y})...")
pyautogui.moveTo(x, y, duration=1)
time.sleep(1)

print("Clicking...")
pyautogui.click(x, y)

print("\n✅ Click executed!")
print("   Did the video start playing? (Check YouTube)")

print("\n" + "="*60)
print("📝 NEXT STEPS:")
print("="*60)
print("1. If video played: Use the coordinates shown above")
print("2. If video didn't play: Run this script again")
print("3. Update jarvis_ultimate.py with your coordinates")
print("\n🎉 Done! You can close this window.")

input("\nPress Enter to exit...")
