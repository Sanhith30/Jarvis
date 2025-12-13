"""
Jarvis Local Assistant - Works directly with your microphone
No LiveKit required - runs as a local desktop assistant
"""

import speech_recognition as sr
import pyttsx3
import os
import webbrowser
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Initialize text-to-speech
try:
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 180)  # Speed of speech
except Exception as e:
    print(f"TTS Engine Error: {e}")
    engine = None

def speak(text):
    """Make Jarvis speak"""
    print(f"Jarvis: {text}")
    if engine:
        engine.say(text)
        engine.runAndWait()

def listen():
    """Listen to microphone and convert to text"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n🎤 Listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            print("🔄 Recognizing...")
            
            query = r.recognize_google(audio, language='en-US')
            print(f"You said: {query}")
            return query.lower()
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that. Could you repeat?")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

def process_command(query):
    """Process voice commands"""
    
    if not query:
        return True
    
    # Greetings
    if any(word in query for word in ["hello", "hi", "hey"]):
        speak("Hello! How can I help you?")
    
    # Time and date
    elif "time" in query or "date" in query:
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        date_str = now.strftime("%B %d, %Y")
        speak(f"The time is {time_str} and today is {date_str}")
    
    # Google search
    elif "search" in query or "google" in query:
        speak("What should I search for?")
        search_query = listen()
        if search_query:
            speak(f"Searching for {search_query}")
            webbrowser.open(f"https://www.google.com/search?q={search_query}")
    
    # Weather
    elif "weather" in query:
        speak("Which city?")
        city = listen()
        if city:
            speak(f"Getting weather for {city}")
            # Implement weather API call here
    
    # Open applications
    elif "open" in query:
        if "chrome" in query or "browser" in query:
            speak("Opening Chrome")
            os.system("start chrome")
        elif "notepad" in query:
            speak("Opening Notepad")
            os.system("start notepad")
        elif "calculator" in query:
            speak("Opening Calculator")
            os.system("start calc")
        else:
            speak("Which application should I open?")
    
    # Screenshot
    elif "screenshot" in query or "capture" in query:
        speak("Taking screenshot")
        try:
            import pyautogui
            screenshot = pyautogui.screenshot()
            screenshot.save("screenshots/screenshot.png")
            speak("Screenshot saved")
        except Exception as e:
            speak("Sorry, couldn't take screenshot")
    
    # Volume control
    elif "volume" in query:
        if "up" in query or "increase" in query:
            speak("Increasing volume")
            os.system("nircmd changesysvolume 2000")
        elif "down" in query or "decrease" in query:
            speak("Decreasing volume")
            os.system("nircmd changesysvolume -2000")
        elif "mute" in query:
            speak("Muting")
            os.system("nircmd mutesysvolume 1")
    
    # Type text
    elif "type" in query:
        speak("What should I type?")
        text = listen()
        if text:
            try:
                import pyautogui
                pyautogui.write(text)
                speak("Done")
            except Exception as e:
                speak("Sorry, couldn't type that")
    
    # Exit
    elif "exit" in query or "quit" in query or "stop" in query or "bye" in query:
        speak("Goodbye! Have a great day!")
        return False
    
    # Unknown command
    else:
        speak("I'm not sure how to help with that. Try saying 'help' for available commands.")
    
    return True

def show_help():
    """Show available commands"""
    print("\n" + "="*60)
    print("🤖 JARVIS - Your Personal Desktop Assistant")
    print("="*60)
    print("\nAvailable Commands:")
    print("  • 'Hello' - Greet Jarvis")
    print("  • 'What time is it?' - Get current time")
    print("  • 'Search for [topic]' - Google search")
    print("  • 'What's the weather?' - Get weather")
    print("  • 'Open Chrome/Notepad/Calculator' - Open apps")
    print("  • 'Take a screenshot' - Capture screen")
    print("  • 'Volume up/down/mute' - Control volume")
    print("  • 'Type [text]' - Type text")
    print("  • 'Exit/Quit/Stop' - Close Jarvis")
    print("\nTips:")
    print("  • Speak clearly and wait for the beep")
    print("  • Say 'Jarvis' to wake up the assistant")
    print("  • Press Ctrl+C to force quit")
    print("="*60 + "\n")

def main():
    """Main function - runs the local assistant"""
    
    show_help()
    speak("Jarvis is online. How can I help you?")
    
    while True:
        try:
            # Listen for wake word or command
            query = listen()
            
            if query:
                # Process the command
                should_continue = process_command(query)
                
                if not should_continue:
                    break
            
        except KeyboardInterrupt:
            speak("Shutting down. Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue

if __name__ == "__main__":
    main()
