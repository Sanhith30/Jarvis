"""
Jarvis Local Assistant - FULL VERSION
All features working locally without LiveKit
"""

import speech_recognition as sr
import pyttsx3
import os
import webbrowser
import pyautogui
import subprocess
import requests
from dotenv import load_dotenv
from datetime import datetime
from fuzzywuzzy import process
import asyncio
import sys

load_dotenv()

# Initialize text-to-speech
try:
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 180)
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
            speak("Sorry, I didn't catch that.")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

# ==================== GOOGLE SEARCH ====================
def google_search(query):
    """Search Google"""
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    search_engine_id = os.getenv("SEARCH_ENGINE_ID")
    
    if not api_key or not search_engine_id:
        speak("Google API keys not configured. Opening browser search.")
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": api_key, "cx": search_engine_id, "q": query, "num": 3}
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            results = data.get("items", [])
            if results:
                speak(f"Found {len(results)} results for {query}")
                for i, item in enumerate(results[:3], 1):
                    print(f"{i}. {item.get('title')}")
                    print(f"   {item.get('link')}")
            else:
                speak("No results found")
        else:
            webbrowser.open(f"https://www.google.com/search?q={query}")
    except Exception as e:
        webbrowser.open(f"https://www.google.com/search?q={query}")

# ==================== WEATHER ====================
def get_weather(city=None):
    """Get weather information"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    if not api_key:
        speak("Weather API key not configured")
        return
    
    if not city:
        try:
            ip_info = requests.get("https://ipapi.co/json/").json()
            city = ip_info.get("city", "Delhi")
        except:
            city = "Delhi"
    
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            weather = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            
            speak(f"Weather in {city}: {weather}, Temperature {temp} degrees celsius, Humidity {humidity} percent")
        else:
            speak(f"Couldn't get weather for {city}")
    except Exception as e:
        speak("Error getting weather information")

# ==================== SCREENSHOT ====================
def take_screenshot():
    """Take a screenshot"""
    try:
        save_dir = "screenshots"
        os.makedirs(save_dir, exist_ok=True)
        filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        path = os.path.join(save_dir, filename)
        
        img = pyautogui.screenshot()
        img.save(path)
        
        speak("Screenshot saved")
        print(f"Saved to: {path}")
        return path
    except Exception as e:
        speak("Couldn't take screenshot")
        return None

# ==================== OPEN/CLOSE APPS ====================
def open_application(app_name):
    """Open an application"""
    apps = {
        "chrome": "chrome",
        "browser": "chrome",
        "notepad": "notepad",
        "calculator": "calc",
        "paint": "mspaint",
        "explorer": "explorer",
        "cmd": "cmd",
        "command prompt": "cmd",
        "powershell": "powershell",
        "word": "winword",
        "excel": "excel",
        "powerpoint": "powerpnt"
    }
    
    for key, value in apps.items():
        if key in app_name:
            try:
                os.system(f"start {value}")
                speak(f"Opening {key}")
                return True
            except:
                speak(f"Couldn't open {key}")
                return False
    
    speak(f"I don't know how to open {app_name}")
    return False

def close_application(app_name):
    """Close an application"""
    apps = {
        "chrome": "chrome.exe",
        "notepad": "notepad.exe",
        "calculator": "calculator.exe",
        "paint": "mspaint.exe"
    }
    
    for key, value in apps.items():
        if key in app_name:
            try:
                os.system(f"taskkill /f /im {value}")
                speak(f"Closing {key}")
                return True
            except:
                speak(f"Couldn't close {key}")
                return False
    
    speak(f"I don't know how to close {app_name}")
    return False

# ==================== FILE OPERATIONS ====================
def play_file(filename):
    """Search and open a file"""
    speak(f"Searching for {filename}")
    
    # Search in common directories
    search_dirs = [
        os.path.expanduser("~\\Desktop"),
        os.path.expanduser("~\\Documents"),
        os.path.expanduser("~\\Downloads"),
        os.path.expanduser("~\\Music"),
        os.path.expanduser("~\\Videos"),
    ]
    
    found_files = []
    for directory in search_dirs:
        if os.path.exists(directory):
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if filename.lower() in file.lower():
                        found_files.append(os.path.join(root, file))
    
    if found_files:
        # Use fuzzy matching to find best match
        file_names = [os.path.basename(f) for f in found_files]
        best_match, score = process.extractOne(filename, file_names)
        
        if score > 60:
            for f in found_files:
                if os.path.basename(f) == best_match:
                    try:
                        os.startfile(f)
                        speak(f"Opening {best_match}")
                        return True
                    except Exception as e:
                        speak("Couldn't open the file")
                        return False
    
    speak(f"Couldn't find {filename}")
    return False

# ==================== MOUSE & KEYBOARD CONTROL ====================
def move_mouse(direction, distance=100):
    """Move mouse cursor"""
    try:
        x, y = pyautogui.position()
        if direction == "left":
            pyautogui.moveTo(x - distance, y)
        elif direction == "right":
            pyautogui.moveTo(x + distance, y)
        elif direction == "up":
            pyautogui.moveTo(x, y - distance)
        elif direction == "down":
            pyautogui.moveTo(x, y + distance)
        speak(f"Moved mouse {direction}")
    except Exception as e:
        speak("Couldn't move mouse")

def click_mouse(button="left"):
    """Click mouse"""
    try:
        if button == "left":
            pyautogui.click()
        elif button == "right":
            pyautogui.rightClick()
        elif button == "double":
            pyautogui.doubleClick()
        speak(f"{button} click done")
    except Exception as e:
        speak("Couldn't click mouse")

def scroll_mouse(direction, amount=3):
    """Scroll mouse"""
    try:
        if direction == "up":
            pyautogui.scroll(amount * 100)
        elif direction == "down":
            pyautogui.scroll(-amount * 100)
        speak(f"Scrolled {direction}")
    except Exception as e:
        speak("Couldn't scroll")

def type_text(text):
    """Type text"""
    try:
        pyautogui.write(text, interval=0.05)
        speak("Text typed")
    except Exception as e:
        speak("Couldn't type text")

def press_key(key):
    """Press a key"""
    try:
        pyautogui.press(key)
        speak(f"Pressed {key}")
    except Exception as e:
        speak(f"Couldn't press {key}")

def control_volume(action):
    """Control system volume"""
    try:
        if action == "up":
            pyautogui.press("volumeup")
            speak("Volume increased")
        elif action == "down":
            pyautogui.press("volumedown")
            speak("Volume decreased")
        elif action == "mute":
            pyautogui.press("volumemute")
            speak("Volume muted")
    except Exception as e:
        speak("Couldn't control volume")

# ==================== COMMAND PROCESSOR ====================
def process_command(query):
    """Process voice commands"""
    
    if not query:
        return True
    
    # Greetings
    if any(word in query for word in ["hello", "hi", "hey jarvis"]):
        speak("Hello! How can I help you?")
    
    # Time and date
    elif "time" in query:
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        speak(f"The time is {time_str}")
    
    elif "date" in query:
        now = datetime.now()
        date_str = now.strftime("%B %d, %Y")
        speak(f"Today is {date_str}")
    
    # Google search
    elif "search" in query or "google" in query:
        speak("What should I search for?")
        search_query = listen()
        if search_query:
            google_search(search_query)
    
    # Weather
    elif "weather" in query:
        if "in" in query:
            city = query.split("in")[-1].strip()
            get_weather(city)
        else:
            speak("Which city?")
            city = listen()
            if city:
                get_weather(city)
    
    # Screenshot
    elif "screenshot" in query or "capture screen" in query:
        take_screenshot()
    
    # Open applications
    elif "open" in query:
        app_name = query.replace("open", "").strip()
        open_application(app_name)
    
    # Close applications
    elif "close" in query:
        app_name = query.replace("close", "").strip()
        close_application(app_name)
    
    # Play file
    elif "play" in query or "open file" in query:
        filename = query.replace("play", "").replace("open file", "").strip()
        if filename:
            play_file(filename)
        else:
            speak("Which file?")
            filename = listen()
            if filename:
                play_file(filename)
    
    # Mouse control
    elif "move mouse" in query or "move cursor" in query:
        if "left" in query:
            move_mouse("left")
        elif "right" in query:
            move_mouse("right")
        elif "up" in query:
            move_mouse("up")
        elif "down" in query:
            move_mouse("down")
    
    elif "click" in query:
        if "right" in query:
            click_mouse("right")
        elif "double" in query:
            click_mouse("double")
        else:
            click_mouse("left")
    
    elif "scroll" in query:
        if "up" in query:
            scroll_mouse("up")
        elif "down" in query:
            scroll_mouse("down")
    
    # Type text
    elif "type" in query:
        speak("What should I type?")
        text = listen()
        if text:
            type_text(text)
    
    # Press key
    elif "press" in query:
        key = query.replace("press", "").strip()
        if key:
            press_key(key)
    
    # Volume control
    elif "volume" in query:
        if "up" in query or "increase" in query:
            control_volume("up")
        elif "down" in query or "decrease" in query:
            control_volume("down")
        elif "mute" in query:
            control_volume("mute")
    
    # Exit
    elif "exit" in query or "quit" in query or "stop" in query or "bye" in query:
        speak("Goodbye! Have a great day!")
        return False
    
    # Help
    elif "help" in query:
        show_help()
    
    # Unknown command
    else:
        speak("I'm not sure how to help with that.")
    
    return True

def show_help():
    """Show available commands"""
    print("\n" + "="*70)
    print("🤖 JARVIS - Your Personal Desktop Assistant (FULL VERSION)")
    print("="*70)
    print("\n📋 Available Commands:")
    print("\n🗣️  Basic:")
    print("  • 'Hello/Hi' - Greet Jarvis")
    print("  • 'What time is it?' - Get current time")
    print("  • 'What's the date?' - Get current date")
    print("  • 'Help' - Show this help")
    
    print("\n🔍 Search & Info:")
    print("  • 'Search for [topic]' - Google search")
    print("  • 'What's the weather?' - Get weather")
    print("  • 'Weather in [city]' - Get weather for specific city")
    
    print("\n💻 Applications:")
    print("  • 'Open Chrome/Notepad/Calculator' - Open apps")
    print("  • 'Close Chrome/Notepad' - Close apps")
    print("  • 'Play [filename]' - Open a file")
    
    print("\n📸 System:")
    print("  • 'Take a screenshot' - Capture screen")
    print("  • 'Volume up/down/mute' - Control volume")
    
    print("\n🖱️  Mouse & Keyboard:")
    print("  • 'Move mouse left/right/up/down' - Move cursor")
    print("  • 'Click' - Left click")
    print("  • 'Right click' - Right click")
    print("  • 'Double click' - Double click")
    print("  • 'Scroll up/down' - Scroll")
    print("  • 'Type [text]' - Type text")
    print("  • 'Press [key]' - Press a key")
    
    print("\n🚪 Exit:")
    print("  • 'Exit/Quit/Stop/Bye' - Close Jarvis")
    
    print("\n💡 Tips:")
    print("  • Speak clearly after the listening prompt")
    print("  • Wait for Jarvis to finish speaking")
    print("  • Press Ctrl+C to force quit")
    print("="*70 + "\n")

def main():
    """Main function"""
    
    show_help()
    speak("Jarvis is online. All systems ready. How can I help you?")
    
    while True:
        try:
            query = listen()
            
            if query:
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
