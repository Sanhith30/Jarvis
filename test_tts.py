"""
Test TTS (Text-to-Speech) to see if it's working
"""

import pyttsx3

print("Testing TTS Engine...")

try:
    # Initialize engine
    engine = pyttsx3.init('sapi5')
    print("✅ Engine initialized")
    
    # Get voices
    voices = engine.getProperty('voices')
    print(f"✅ Found {len(voices)} voices")
    
    # Set voice
    engine.setProperty('voice', voices[0].id)
    print(f"✅ Voice set to: {voices[0].name}")
    
    # Set rate
    engine.setProperty('rate', 180)
    print("✅ Rate set to 180")
    
    # Test speech
    print("\n🔊 Testing speech...")
    engine.say("Hello, I am Jarvis. This is a test.")
    engine.runAndWait()
    print("✅ Speech test completed")
    
    print("\n✅ TTS is working correctly!")
    
except Exception as e:
    print(f"\n❌ TTS Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure you have audio output device")
    print("2. Check Windows audio settings")
    print("3. Try: pip install --upgrade pyttsx3")
    print("4. Try: pip install pywin32")
