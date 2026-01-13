"""
JARVIS ENHANCED LOCAL AGENT
- Opens ANY app on your laptop
- Natural conversation with personality
- Types in opened apps
- Always speaks responses
- Full conversational AI
"""

from dotenv import load_dotenv
import subprocess, os, sys, asyncio
import logging
import speech_recognition as sr
import pyttsx3
from datetime import datetime
import pyautogui
import requests
from fuzzywuzzy import process
import webbrowser
import time
import winreg
import psutil

# Import Jarvis modules
from Jarvis_prompts import behavior_prompts, Reply_prompts
from memory.jarvis_memory import load_memory_sync, save_memory_sync

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== ENHANCED TTS ENGINE ====================
def speak(text):
    """Enhanced Jarvis speech - Always works"""
    print(f"\n🤖 Jarvis: {text}")
    
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            # Create completely fresh engine
            engine = pyttsx3.init()
            
            # Get and set voice
            voices = engine.getProperty('voices')
            if voices and len(voices) > 0:
                # Try to find a good voice
                for voice in voices:
                    if 'david' in voice.name.lower() or 'mark' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
                else:
                    engine.setProperty('voice', voices[0].id)
            
            # Set properties
            engine.setProperty('rate', 190)  # Slightly faster
            engine.setProperty('volume', 1.0)
            
            # Speak
            engine.say(text)
            engine.runAndWait()
            
            # Cleanup
            try:
                engine.stop()
            except:
                pass
            
            del engine
            return True
            
        except Exception as e:
            logger.error(f"Speech attempt {attempt + 1} failed: {e}")
            if attempt < max_attempts - 1:
                time.sleep(0.5)
            continue
    
    logger.warning("⚠️ All speech attempts failed - continuing in text mode")
    return False

def listen():
    """Enhanced listening with better error handling"""
    r = sr.Recognizer()
    
    # Adjust for ambient noise once
    with sr.Microphone() as source:
        print("\n🎤 Listening...")
        r.pause_threshold = 1
        r.energy_threshold = 300
        r.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            # Listen with timeout
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            print("🔄 Recognizing...")
            
            # Recognize speech
            query = r.recognize_google(audio, language='en-US')
            print(f"👤 You: {query}")
            return query.lower()
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except Exception as e:
            logger.error(f"Listen error: {e}")
            return None

# ==================== APP DISCOVERY & MANAGEMENT ====================
def find_all_apps():
    """Find all installed applications on Windows"""
    apps = {}
    
    # Common app locations
    common_paths = [
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        r"C:\Windows\System32",
        os.path.expanduser("~\\AppData\\Local"),
        os.path.expanduser("~\\AppData\\Roaming")
    ]
    
    # Registry locations for installed programs
    registry_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    
    # Get from registry
    try:
        for reg_path in registry_paths:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey = winreg.OpenKey(key, subkey_name)
                        try:
                            name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            try:
                                path = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                if path and os.path.exists(path):
                                    apps[name.lower()] = path
                            except:
                                pass
                        except:
                            pass
                        winreg.CloseKey(subkey)
                    except:
                        continue
                winreg.CloseKey(key)
            except:
                continue
    except:
        pass
    
    # Add common Windows apps
    windows_apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "paint": "mspaint.exe",
        "wordpad": "wordpad.exe",
        "cmd": "cmd.exe",
        "powershell": "powershell.exe",
        "explorer": "explorer.exe",
        "chrome": "chrome.exe",
        "firefox": "firefox.exe",
        "edge": "msedge.exe",
        "word": "winword.exe",
        "excel": "excel.exe",
        "powerpoint": "powerpnt.exe",
        "outlook": "outlook.exe",
        "teams": "teams.exe",
        "zoom": "zoom.exe",
        "discord": "discord.exe",
        "spotify": "spotify.exe",
        "vlc": "vlc.exe",
        "steam": "steam.exe"
    }
    
    for name, exe in windows_apps.items():
        apps[name] = exe
    
    return apps

def open_any_app(app_name):
    """Open any application by name"""
    app_name = app_name.lower().strip()
    
    # Get all available apps
    apps = find_all_apps()
    
    # Direct match
    if app_name in apps:
        try:
            if apps[app_name].endswith('.exe'):
                os.system(f'start "" "{apps[app_name]}"')
            else:
                os.startfile(apps[app_name])
            return f"Opening {app_name}"
        except Exception as e:
            logger.error(f"Failed to open {app_name}: {e}")
    
    # Fuzzy match
    app_names = list(apps.keys())
    matches = process.extract(app_name, app_names, limit=3)
    
    for match, score in matches:
        if score > 60:  # Good enough match
            try:
                if apps[match].endswith('.exe'):
                    os.system(f'start "" "{apps[match]}"')
                else:
                    os.startfile(apps[match])
                return f"Opening {match} (matched {app_name})"
            except Exception as e:
                continue
    
    # Try direct command
    try:
        os.system(f"start {app_name}")
        return f"Attempting to open {app_name}"
    except:
        pass
    
    return f"Couldn't find {app_name}. Try being more specific."

# ==================== ENHANCED ASSISTANT CLASS ====================
class EnhancedAssistant:
    """Enhanced Jarvis with personality and conversation"""
    
    def __init__(self):
        self.memory = load_memory_sync()
        self.conversation_context = []
        logger.info("✅ Enhanced Assistant initialized")
    
    async def save_conversation(self, speaker: str, text: str):
        """Save conversation to memory"""
        try:
            if "conversation" not in self.memory:
                self.memory["conversation"] = []
            
            entry = {
                "speaker": speaker,
                "text": text,
                "timestamp": datetime.now().isoformat()
            }
            self.memory["conversation"].append(entry)
            self.conversation_context.append(entry)
            
            # Keep only last 10 in context
            if len(self.conversation_context) > 10:
                self.conversation_context = self.conversation_context[-10:]
            
            save_memory_sync(self.memory)
        except Exception as e:
            logger.error(f"Save memory error: {e}")
    
    async def get_recent_conversations(self, limit: int = 5) -> str:
        """Get recent conversations"""
        try:
            conversations = self.memory.get("conversation", [])
            if not conversations:
                return "No conversations remembered yet"
            
            recent = conversations[-limit:]
            result = "Previous conversations:\n"
            for entry in recent:
                speaker = entry.get("speaker", "unknown")
                text = entry.get("text", "")
                result += f"- {speaker}: {text}\n"
            
            return result
        except Exception as e:
            return "Memory error"
    
    async def google_search(self, query: str) -> str:
        """Enhanced Google search"""
        logger.info(f"🔍 Searching: {query}")
        api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        search_engine_id = os.getenv("SEARCH_ENGINE_ID")
        
        if api_key and search_engine_id:
            try:
                url = "https://www.googleapis.com/customsearch/v1"
                params = {"key": api_key, "cx": search_engine_id, "q": query, "num": 3}
                response = requests.get(url, params=params, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("items", [])
                    if results:
                        result_text = f"Found {len(results)} results for {query}:\n"
                        for i, item in enumerate(results[:2], 1):
                            result_text += f"{i}. {item.get('title')}\n"
                        return result_text
            except Exception as e:
                logger.error(f"API search failed: {e}")
        
        # Fallback to browser
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Opened browser search for {query}"
    
    async def get_weather(self, city: str = "") -> str:
        """Get weather with personality"""
        api_key = os.getenv("OPENWEATHER_API_KEY")
        
        if not api_key:
            return "Weather API not configured, sir. But I can tell you it's perfect weather for coding!"
        
        if not city:
            try:
                ip_info = requests.get("https://ipapi.co/json/", timeout=3).json()
                city = ip_info.get("city", "your location")
            except:
                city = "your location"
        
        try:
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {"q": city, "appid": api_key, "units": "metric"}
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                weather = data["weather"][0]["description"]
                temp = data["main"]["temp"]
                
                return f"Weather in {city}: {weather}, {temp}°C. Perfect for staying productive, sir!"
        except:
            pass
        
        return f"Couldn't get weather for {city}, but I'm sure it's lovely outside!"
    
    async def take_screenshot(self) -> str:
        """Take screenshot with personality"""
        try:
            save_dir = "screenshots"
            os.makedirs(save_dir, exist_ok=True)
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            path = os.path.join(save_dir, filename)
            
            img = pyautogui.screenshot()
            img.save(path)
            
            return f"Screenshot captured and saved, sir. Saved to {filename}"
        except Exception as e:
            return "Screenshot failed, sir. Perhaps the screen is camera-shy today."
    
    async def type_text_smart(self, text: str) -> str:
        """Smart typing that waits for active window"""
        try:
            # Wait a moment for user to click where they want to type
            await asyncio.sleep(1)
            
            # Type with natural intervals
            for char in text:
                pyautogui.write(char)
                await asyncio.sleep(0.02)  # Natural typing speed
            
            return f"Typed: {text}"
        except Exception as e:
            return f"Typing failed: {e}"

# ==================== ENHANCED COMMAND PROCESSOR ====================
async def process_enhanced_command(assistant: EnhancedAssistant, query: str) -> bool:
    """Enhanced command processing with personality"""
    
    if not query:
        return True
    
    # Save user input
    await assistant.save_conversation("user", query)
    
    # Greetings with personality
    if any(word in query for word in ["hello", "hi", "hey", "jarvis"]):
        now = datetime.now()
        hour = now.hour
        
        if hour < 12:
            greeting = "Good morning"
        elif hour < 17:
            greeting = "Good afternoon"
        elif hour < 21:
            greeting = "Good evening"
        else:
            greeting = "Good night"
        
        responses = [
            f"{greeting} sir! Jarvis at your service. How may I assist you today?",
            f"{greeting} sir! All systems online and ready. What can I do for you?",
            f"{greeting} sir! I'm here and ready to help. What's on your agenda?"
        ]
        
        import random
        response = random.choice(responses)
        speak(response)
        await assistant.save_conversation("jarvis", response)
    
    # Time with personality
    elif "time" in query:
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        response = f"The time is {time_str}, sir. Time flies when you're being productive!"
        speak(response)
        await assistant.save_conversation("jarvis", response)
    
    # Date with personality
    elif "date" in query:
        now = datetime.now()
        date_str = now.strftime("%B %d, %Y")
        response = f"Today is {date_str}, sir. Another day, another opportunity for greatness!"
        speak(response)
        await assistant.save_conversation("jarvis", response)
    
    # Memory retrieval
    elif any(word in query for word in ["remember", "previous", "past", "memory", "history"]):
        result = await assistant.get_recent_conversations()
        speak("Here's what I remember from our recent conversations, sir.")
        speak(result)
        await assistant.save_conversation("jarvis", result)
    
    # Enhanced search
    elif "search" in query or "google" in query:
        if "for" in query:
            search_term = query.split("for", 1)[1].strip()
        else:
            speak("What would you like me to search for, sir?")
            search_term = listen()
        
        if search_term:
            speak(f"Searching for {search_term}")
            result = await assistant.google_search(search_term)
            speak(result)
    
    # Weather
    elif "weather" in query:
        if "in" in query:
            city = query.split("in")[-1].strip()
        else:
            city = ""
        result = await assistant.get_weather(city)
        speak(result)
    
    # Screenshot
    elif "screenshot" in query or "capture" in query:
        result = await assistant.take_screenshot()
        speak(result)
    
    # Enhanced app opening - ANY APP
    elif "open" in query:
        app_name = query.replace("open", "").strip()
        if app_name:
            speak(f"Opening {app_name}")
            result = open_any_app(app_name)
            speak(result)
        else:
            speak("Which application would you like me to open, sir?")
    
    # Type text in active window
    elif "type" in query:
        if "type" in query and len(query.split()) > 1:
            text_to_type = query.replace("type", "", 1).strip()
            if text_to_type:
                speak(f"Typing: {text_to_type}")
                await assistant.type_text_smart(text_to_type)
                speak("Text typed successfully, sir.")
            else:
                speak("What would you like me to type, sir?")
                text = listen()
                if text:
                    await assistant.type_text_smart(text)
                    speak("Done, sir.")
        else:
            speak("What should I type, sir?")
            text = listen()
            if text:
                await assistant.type_text_smart(text)
                speak("Typed successfully, sir.")
    
    # Mouse control
    elif "click" in query:
        try:
            pyautogui.click()
            speak("Clicked, sir.")
        except:
            speak("Click failed, sir.")
    
    # Volume control
    elif "volume" in query:
        try:
            if "up" in query or "increase" in query:
                pyautogui.press("volumeup")
                speak("Volume increased, sir.")
            elif "down" in query or "decrease" in query:
                pyautogui.press("volumedown")
                speak("Volume decreased, sir.")
            elif "mute" in query:
                pyautogui.press("volumemute")
                speak("Volume muted, sir.")
        except:
            speak("Volume control failed, sir.")
    
    # Conversational responses
    elif any(word in query for word in ["how are you", "what's up", "how do you feel"]):
        responses = [
            "I'm functioning at optimal capacity, sir. Ready to assist with whatever you need!",
            "All systems running smoothly, sir. How can I help make your day more productive?",
            "I'm doing excellent, sir. My circuits are humming with efficiency!"
        ]
        import random
        response = random.choice(responses)
        speak(response)
        await assistant.save_conversation("jarvis", response)
    
    elif any(word in query for word in ["thank you", "thanks", "good job"]):
        responses = [
            "You're very welcome, sir. It's my pleasure to assist you.",
            "Always happy to help, sir. That's what I'm here for!",
            "My pleasure, sir. Anything else you need?"
        ]
        import random
        response = random.choice(responses)
        speak(response)
        await assistant.save_conversation("jarvis", response)
    
    # Exit
    elif any(word in query for word in ["exit", "quit", "stop", "bye", "goodbye"]):
        speak("Goodbye sir! It's been a pleasure assisting you today. Until next time!")
        return False
    
    # Unknown command - conversational response
    else:
        responses = [
            "I'm not quite sure how to help with that, sir. Could you rephrase or try a different command?",
            "That's an interesting request, sir. Could you be more specific about what you'd like me to do?",
            "I didn't quite catch that command, sir. Feel free to try again or ask for help."
        ]
        import random
        response = random.choice(responses)
        speak(response)
        await assistant.save_conversation("jarvis", response)
    
    return True

# ==================== MAIN ENTRYPOINT ====================
async def main():
    """Enhanced main function"""
    print("\n" + "="*70)
    print("🤖 JARVIS ENHANCED - Your Personal AI Assistant")
    print("="*70)
    print("\n🎯 Features:")
    print("  • Opens ANY app on your laptop")
    print("  • Natural conversation with personality")
    print("  • Types in opened applications")
    print("  • Always speaks responses")
    print("  • Remembers conversations")
    print("  • Smart search and weather")
    print("="*70)
    
    try:
        # Test speech first
        speak("Initializing Jarvis Enhanced. Please wait.")
        
        # Initialize assistant
        assistant = EnhancedAssistant()
        
        # Greeting
        now = datetime.now()
        hour = now.hour
        if hour < 12: greeting = "Good morning"
        elif hour < 17: greeting = "Good afternoon"
        elif hour < 21: greeting = "Good evening"
        else: greeting = "Good night"
        
        speak(f"{greeting} sir! Jarvis Enhanced is online. All systems ready. How can I assist you today?")
        
        # Main loop
        while True:
            query = listen()
            
            if query:
                should_continue = await process_enhanced_command(assistant, query)
                if not should_continue:
                    break
    
    except KeyboardInterrupt:
        speak("Shutting down. Goodbye sir!")
    except Exception as e:
        logger.error(f"Main error: {e}")
        speak("An error occurred, but I'm still here to help, sir.")

if __name__ == "__main__":
    # Start GUI if available
    try:
        gui_path = os.path.join(os.path.dirname(__file__), "jarvis_gui.py")
        if os.path.exists(gui_path):
            subprocess.Popen([sys.executable, gui_path])
    except:
        pass
    
    # Run enhanced Jarvis
    asyncio.run(main())