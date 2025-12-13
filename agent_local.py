"""
JARVIS LOCAL AGENT - Complete Local Version
Same structure as agent.py but works without LiveKit
All features included with local voice recognition
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

# Import all Jarvis modules
from Jarvis_prompts import behavior_prompts, Reply_prompts
from memory.jarvis_memory import load_memory_sync, save_memory_sync

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Memory interceptor flag
ENABLE_MEMORY_INTERCEPTOR = True

# ==================== TTS ENGINE ====================
def speak(text):
    """Jarvis speaks - Creates new engine each time to avoid hanging"""
    print(f"\n🤖 Jarvis: {text}")
    
    try:
        # Create fresh engine for each speech to avoid hanging
        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 180)
        engine.setProperty('volume', 1.0)
        
        engine.say(text)
        engine.runAndWait()
        
        # Stop and delete engine
        engine.stop()
        del engine
        
    except Exception as e:
        logger.error(f"❌ Speech error: {e}")
        logger.warning("⚠️ Continuing in text-only mode")

def listen():
    """Listen to microphone"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n🎤 Listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            print("🔄 Recognizing...")
            
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

# ==================== ASSISTANT CLASS ====================
class LocalAssistant:
    """Local Jarvis Assistant with all tools"""
    
    def __init__(self):
        self.instructions = behavior_prompts
        self.memory = load_memory_sync()
        logger.info("✅ Local Assistant initialized")
    
    # ==================== GOOGLE SEARCH ====================
    async def google_search(self, query: str) -> str:
        """Search Google"""
        logger.info(f"🔍 Searching: {query}")
        api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        search_engine_id = os.getenv("SEARCH_ENGINE_ID")
        
        if not api_key or not search_engine_id:
            speak("Opening browser search")
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return "Browser search opened"
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {"key": api_key, "cx": search_engine_id, "q": query, "num": 3}
        
        try:
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                results = data.get("items", [])
                if results:
                    result_text = f"Found {len(results)} results:\n"
                    for i, item in enumerate(results[:3], 1):
                        result_text += f"{i}. {item.get('title')}\n"
                    speak(result_text)
                    return result_text
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return "Browser search opened"
        except Exception as e:
            logger.error(f"Search error: {e}")
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return "Browser search opened"
    
    # ==================== WEATHER ====================
    async def get_weather(self, city: str = "") -> str:
        """Get weather information"""
        logger.info(f"🌤️ Getting weather for: {city}")
        api_key = os.getenv("OPENWEATHER_API_KEY")
        
        if not api_key:
            speak("Weather API not configured")
            return "Weather API not configured"
        
        if not city:
            try:
                ip_info = requests.get("https://ipapi.co/json/", timeout=3).json()
                city = ip_info.get("city", "Delhi")
            except:
                city = "Delhi"
        
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": api_key, "units": "metric"}
        
        try:
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                weather = data["weather"][0]["description"]
                temp = data["main"]["temp"]
                humidity = data["main"]["humidity"]
                
                result = f"Weather in {city}: {weather}, {temp}°C, Humidity {humidity}%"
                speak(result)
                return result
        except Exception as e:
            logger.error(f"Weather error: {e}")
            speak("Couldn't get weather")
            return "Weather error"
    
    # ==================== SCREENSHOT ====================
    async def screenshot_tool(self) -> str:
        """Take screenshot"""
        logger.info("📸 Taking screenshot")
        try:
            save_dir = "screenshots"
            os.makedirs(save_dir, exist_ok=True)
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            path = os.path.join(save_dir, filename)
            
            img = pyautogui.screenshot()
            img.save(path)
            
            result = f"Screenshot saved: {path}"
            speak("Screenshot saved")
            logger.info(f"✅ {result}")
            return result
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            speak("Couldn't take screenshot")
            return "Screenshot failed"
    
    # ==================== OPEN/CLOSE APPS ====================
    async def open_app(self, app_name: str) -> str:
        """Open application"""
        logger.info(f"🚀 Opening: {app_name}")
        apps = {
            "chrome": "chrome", "browser": "chrome",
            "notepad": "notepad", "calculator": "calc",
            "paint": "mspaint", "explorer": "explorer",
            "cmd": "cmd", "powershell": "powershell"
        }
        
        for key, value in apps.items():
            if key in app_name.lower():
                try:
                    os.system(f"start {value}")
                    speak(f"Opening {key}")
                    return f"Opened {key}"
                except Exception as e:
                    logger.error(f"Open error: {e}")
                    speak(f"Couldn't open {key}")
                    return f"Failed to open {key}"
        
        speak(f"Don't know how to open {app_name}")
        return f"Unknown app: {app_name}"
    
    async def close_app(self, app_name: str) -> str:
        """Close application"""
        logger.info(f"🛑 Closing: {app_name}")
        apps = {
            "chrome": "chrome.exe",
            "notepad": "notepad.exe",
            "calculator": "calculator.exe"
        }
        
        for key, value in apps.items():
            if key in app_name.lower():
                try:
                    os.system(f"taskkill /f /im {value}")
                    speak(f"Closing {key}")
                    return f"Closed {key}"
                except Exception as e:
                    logger.error(f"Close error: {e}")
                    return f"Failed to close {key}"
        
        return f"Unknown app: {app_name}"
    
    # ==================== FILE OPERATIONS ====================
    async def play_file(self, filename: str) -> str:
        """Search and open file"""
        logger.info(f"📁 Searching file: {filename}")
        speak(f"Searching for {filename}")
        
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
            file_names = [os.path.basename(f) for f in found_files]
            best_match, score = process.extractOne(filename, file_names)
            
            if score > 60:
                for f in found_files:
                    if os.path.basename(f) == best_match:
                        try:
                            os.startfile(f)
                            speak(f"Opening {best_match}")
                            return f"Opened {best_match}"
                        except Exception as e:
                            logger.error(f"File open error: {e}")
                            return "Couldn't open file"
        
        speak(f"Couldn't find {filename}")
        return f"File not found: {filename}"
    
    # ==================== MOUSE & KEYBOARD ====================
    async def move_cursor(self, direction: str, distance: int = 100) -> str:
        """Move mouse cursor"""
        try:
            x, y = pyautogui.position()
            if direction == "left": pyautogui.moveTo(x - distance, y)
            elif direction == "right": pyautogui.moveTo(x + distance, y)
            elif direction == "up": pyautogui.moveTo(x, y - distance)
            elif direction == "down": pyautogui.moveTo(x, y + distance)
            speak(f"Moved mouse {direction}")
            return f"Moved {direction}"
        except Exception as e:
            return f"Move error: {e}"
    
    async def mouse_click(self, button: str = "left") -> str:
        """Click mouse"""
        try:
            if button == "left": pyautogui.click()
            elif button == "right": pyautogui.rightClick()
            elif button == "double": pyautogui.doubleClick()
            speak(f"{button} click")
            return f"{button} click done"
        except Exception as e:
            return f"Click error: {e}"
    
    async def scroll_cursor(self, direction: str, amount: int = 3) -> str:
        """Scroll mouse"""
        try:
            if direction == "up": pyautogui.scroll(amount * 100)
            elif direction == "down": pyautogui.scroll(-amount * 100)
            speak(f"Scrolled {direction}")
            return f"Scrolled {direction}"
        except Exception as e:
            return f"Scroll error: {e}"
    
    async def type_text(self, text: str) -> str:
        """Type text"""
        try:
            pyautogui.write(text, interval=0.05)
            speak("Text typed")
            return "Text typed"
        except Exception as e:
            return f"Type error: {e}"
    
    async def press_key(self, key: str) -> str:
        """Press key"""
        try:
            pyautogui.press(key)
            speak(f"Pressed {key}")
            return f"Pressed {key}"
        except Exception as e:
            return f"Key error: {e}"
    
    async def control_volume(self, action: str) -> str:
        """Control volume"""
        try:
            if action == "up": pyautogui.press("volumeup")
            elif action == "down": pyautogui.press("volumedown")
            elif action == "mute": pyautogui.press("volumemute")
            speak(f"Volume {action}")
            return f"Volume {action}"
        except Exception as e:
            return f"Volume error: {e}"
    
    # ==================== MEMORY ====================
    async def get_recent_conversations(self, limit: int = 5) -> str:
        """Get recent conversations"""
        try:
            memory = load_memory_sync()
            conversations = memory.get("conversation", [])
            
            if not conversations:
                return "No conversations remembered yet"
            
            recent = conversations[-limit:]
            result = "Previous conversations:\n"
            for entry in recent:
                speaker = entry.get("speaker", "unknown")
                text = entry.get("text", "")
                result += f"- {speaker}: {text}\n"
            
            speak("Here are recent conversations")
            return result
        except Exception as e:
            logger.error(f"Memory error: {e}")
            return "Memory error"
    
    async def save_conversation(self, speaker: str, text: str):
        """Save conversation to memory"""
        try:
            memory = load_memory_sync()
            if "conversation" not in memory:
                memory["conversation"] = []
            
            entry = {
                "speaker": speaker,
                "text": text,
                "timestamp": datetime.now().isoformat()
            }
            memory["conversation"].append(entry)
            save_memory_sync(memory)
        except Exception as e:
            logger.error(f"Save memory error: {e}")

# ==================== COMMAND PROCESSOR ====================
async def process_command(assistant: LocalAssistant, query: str) -> bool:
    """Process voice commands"""
    
    if not query:
        return True
    
    # Save user input to memory
    await assistant.save_conversation("user", query)
    
    # Greetings
    if any(word in query for word in ["hello", "hi", "hey jarvis"]):
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
        
        response = f"{greeting} sir! I am Jarvis, your personal AI assistant. How can I help you?"
        speak(response)
        await assistant.save_conversation("jarvis", response)
    
    # Time
    elif "time" in query:
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        response = f"The time is {time_str}"
        speak(response)
        await assistant.save_conversation("jarvis", response)
    
    # Date
    elif "date" in query:
        now = datetime.now()
        date_str = now.strftime("%B %d, %Y")
        response = f"Today is {date_str}"
        speak(response)
        await assistant.save_conversation("jarvis", response)
    
    # Memory retrieval
    elif any(word in query for word in ["remember", "previous", "past conversation", "memory"]):
        result = await assistant.get_recent_conversations()
        speak(result)
        await assistant.save_conversation("jarvis", result)
    
    # Google search
    elif "search" in query or "google" in query:
        speak("What should I search for?")
        search_query = listen()
        if search_query:
            await assistant.google_search(search_query)
    
    # Weather
    elif "weather" in query:
        if "in" in query:
            city = query.split("in")[-1].strip()
            await assistant.get_weather(city)
        else:
            await assistant.get_weather()
    
    # Screenshot
    elif "screenshot" in query or "capture" in query:
        await assistant.screenshot_tool()
    
    # Open app
    elif "open" in query:
        app_name = query.replace("open", "").strip()
        await assistant.open_app(app_name)
    
    # Close app
    elif "close" in query:
        app_name = query.replace("close", "").strip()
        await assistant.close_app(app_name)
    
    # Play file
    elif "play" in query or "open file" in query:
        filename = query.replace("play", "").replace("open file", "").strip()
        if filename:
            await assistant.play_file(filename)
    
    # Mouse control
    elif "move mouse" in query or "move cursor" in query:
        if "left" in query: await assistant.move_cursor("left")
        elif "right" in query: await assistant.move_cursor("right")
        elif "up" in query: await assistant.move_cursor("up")
        elif "down" in query: await assistant.move_cursor("down")
    
    elif "click" in query:
        if "right" in query: await assistant.mouse_click("right")
        elif "double" in query: await assistant.mouse_click("double")
        else: await assistant.mouse_click("left")
    
    elif "scroll" in query:
        if "up" in query: await assistant.scroll_cursor("up")
        elif "down" in query: await assistant.scroll_cursor("down")
    
    # Type text
    elif "type" in query:
        speak("What should I type?")
        text = listen()
        if text:
            await assistant.type_text(text)
    
    # Press key
    elif "press" in query:
        key = query.replace("press", "").strip()
        if key:
            await assistant.press_key(key)
    
    # Volume
    elif "volume" in query:
        if "up" in query or "increase" in query:
            await assistant.control_volume("up")
        elif "down" in query or "decrease" in query:
            await assistant.control_volume("down")
        elif "mute" in query:
            await assistant.control_volume("mute")
    
    # Exit
    elif "exit" in query or "quit" in query or "stop" in query or "bye" in query:
        speak("Goodbye sir! Have a great day!")
        return False
    
    # Unknown
    else:
        speak("I'm not sure how to help with that sir")
    
    return True

# ==================== MAIN ENTRYPOINT ====================
async def entrypoint():
    """Main entry point - mirrors agent.py structure"""
    max_retries = 5
    retry_count = 0
    base_wait_time = 3
    
    while retry_count < max_retries:
        try:
            print(f"\n🚀 Starting local agent session (attempt {retry_count + 1}/{max_retries})...")
            
            # Initialize assistant
            assistant = LocalAssistant()
            
            print("✅ Connected to local microphone, waiting for audio input...")
            
            # Inject memory context if enabled
            if ENABLE_MEMORY_INTERCEPTOR:
                try:
                    print("🧠 Fetching memory context...")
                    memory_context = await assistant.get_recent_conversations(limit=5)
                    if "No conversations" not in memory_context:
                        print("✅ Memory context loaded")
                    else:
                        print("ℹ️ No previous conversations")
                except Exception as e:
                    print(f"⚠️ Memory injection skipped: {e}")
            
            # Initial greeting
            now = datetime.now()
            hour = now.hour
            if hour < 12: greeting = "Good morning"
            elif hour < 17: greeting = "Good afternoon"
            elif hour < 21: greeting = "Good evening"
            else: greeting = "Good night"
            
            speak(f"{greeting} sir! Jarvis is online. All systems ready. How can I help you?")
            
            # Main loop
            while True:
                query = listen()
                
                if query:
                    should_continue = await process_command(assistant, query)
                    
                    if not should_continue:
                        break
            
            print("✅ Session completed successfully")
            break
            
        except KeyboardInterrupt:
            print("\n⛔ Agent stopped by user")
            break
        except Exception as e:
            print(f"❌ Session error (attempt {retry_count + 1}/{max_retries}): {e}")
            retry_count += 1
            
            if retry_count < max_retries:
                wait_time = base_wait_time * retry_count
                print(f"⏳ Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
            else:
                print("❌ Max retries exceeded. Shutting down.")
                raise

if __name__ == "__main__":
    # Try to start GUI
    try:
        gui_path = os.path.join(os.path.dirname(__file__), "jarvis_gui.py")
        if os.path.exists(gui_path):
            subprocess.Popen([sys.executable, gui_path], stdout=None, stderr=None, stdin=None, close_fds=True)
        else:
            print("jarvis_gui.py not found; GUI will not be started.")
    except Exception as e:
        print("Failed to start GUI subprocess:", e)
    
    # Run the agent
    asyncio.run(entrypoint())
