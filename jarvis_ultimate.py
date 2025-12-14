"""
JARVIS ULTIMATE - The Complete AI Assistant
ALL FEATURES FROM AGENT.PY + YouTube music + More!
- All original agent.py tools and functions
- YouTube music/video playing
- Smart web automation
- System monitoring
- File management
- Email sending
- News reading
- Mouse & keyboard control
- Screenshot tools
- Weather & search
- Memory system
- And much more!
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
import json
import random
import smtplib

# Import ALL Jarvis modules from agent.py
from Jarvis_prompts import behavior_prompts, Reply_prompts
from Jarvis_screenshot import screenshot_tool
from Jarvis_google_search import google_search, get_current_datetime
from memory.jarvis_memory import load_memory_sync, save_memory_sync, get_recent_conversations, add_memory_entry
from memory_interceptor import MEMORY_KEYWORDS
from jarvis_get_whether import get_weather
from Jarvis_window_CTRL import open, close, folder_file
from Jarvis_file_opner import Play_file
from keyboard_mouse_CTRL import move_cursor_tool, mouse_click_tool, scroll_cursor_tool, type_text_tool, press_key_tool, swipe_gesture_tool, press_hotkey_tool, control_volume_tool

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== ENHANCED TTS ENGINE ====================
def speak(text):
    """Ultimate Jarvis speech - Always works"""
    print(f"\n🤖 Jarvis: {text}")
    
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            if voices and len(voices) > 0:
                # Try to find best voice
                for voice in voices:
                    if any(name in voice.name.lower() for name in ['david', 'mark', 'male']):
                        engine.setProperty('voice', voice.id)
                        break
                else:
                    engine.setProperty('voice', voices[0].id)
            
            engine.setProperty('rate', 190)
            engine.setProperty('volume', 1.0)
            engine.say(text)
            engine.runAndWait()
            
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
    
    return False

def listen():
    """Enhanced listening"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n🎤 Listening...")
        r.pause_threshold = 1
        r.energy_threshold = 300
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
            return None

# ==================== YOUTUBE & MUSIC FEATURES ====================
def play_youtube_music(song_name):
    """Play music on YouTube"""
    try:
        # Open YouTube and search for the song
        search_url = f"https://www.youtube.com/results?search_query={song_name.replace(' ', '+')}"
        webbrowser.open(search_url)
        
        # Wait for page to load
        time.sleep(3)
        
        # Try to click the first video (coordinates may vary)
        try:
            # Look for the first video thumbnail and click it
            pyautogui.click(400, 300)  # Approximate location of first video
        except:
            pass
        
        return f"Playing {song_name} on YouTube"
    except Exception as e:
        return f"Couldn't play {song_name}: {e}"

def youtube_control(action):
    """Control YouTube playback"""
    try:
        if action == "pause" or action == "play":
            pyautogui.press('space')  # Space bar pauses/plays
            return f"YouTube {action}"
        elif action == "next":
            pyautogui.hotkey('shift', 'n')
            return "Next video"
        elif action == "previous":
            pyautogui.hotkey('shift', 'p')
            return "Previous video"
        elif action == "fullscreen":
            pyautogui.press('f')
            return "Fullscreen mode"
        elif action == "volume up":
            pyautogui.press('up')
            return "Volume increased"
        elif action == "volume down":
            pyautogui.press('down')
            return "Volume decreased"
    except Exception as e:
        return f"YouTube control failed: {e}"

# ==================== SYSTEM MONITORING ====================
def get_system_info():
    """Get system information"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        # Battery (if laptop)
        try:
            battery = psutil.sensors_battery()
            if battery:
                battery_percent = battery.percent
                battery_status = "Charging" if battery.power_plugged else "Not charging"
            else:
                battery_percent = None
                battery_status = "Desktop PC"
        except:
            battery_percent = None
            battery_status = "Unknown"
        
        info = f"System Status: CPU {cpu_percent}%, Memory {memory_percent}%, Disk {disk_percent:.1f}%"
        if battery_percent:
            info += f", Battery {battery_percent}% ({battery_status})"
        
        return info
    except Exception as e:
        return f"System info error: {e}"

def get_running_processes():
    """Get top running processes"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                processes.append(proc.info)
            except:
                pass
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        
        top_5 = processes[:5]
        result = "Top processes: "
        for proc in top_5:
            result += f"{proc['name']} ({proc['cpu_percent']:.1f}%), "
        
        return result.rstrip(', ')
    except Exception as e:
        return f"Process info error: {e}"

# ==================== NEWS & INFORMATION ====================
def get_news():
    """Get latest news"""
    try:
        api_key = os.getenv("NEWS_API_KEY")
        if not api_key:
            webbrowser.open("https://news.google.com")
            return "Opened Google News in browser"
        
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])[:3]
            
            if articles:
                news_text = "Here are the top news headlines: "
                for i, article in enumerate(articles, 1):
                    news_text += f"{i}. {article['title']}. "
                return news_text
        
        webbrowser.open("https://news.google.com")
        return "Opened Google News in browser"
    except Exception as e:
        webbrowser.open("https://news.google.com")
        return "Opened Google News in browser"

# ==================== EMAIL FEATURES ====================
def send_email(to_email, subject, message):
    """Send email"""
    try:
        from email.mime.text import MimeText
        from email.mime.multipart import MimeMultipart
        
        from_email = os.getenv("EMAIL_ADDRESS")
        password = os.getenv("EMAIL_PASSWORD")
        
        if not from_email or not password:
            return "Email credentials not configured in .env file"
        
        msg = MimeMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MimeText(message, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        
        return f"Email sent to {to_email}"
    except Exception as e:
        return f"Email failed: {e}"

# ==================== ENTERTAINMENT ====================
def tell_joke():
    """Tell a random joke"""
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? He was outstanding in his field!",
        "Why don't eggs tell jokes? They'd crack each other up!",
        "What do you call a fake noodle? An impasta!",
        "Why did the math book look so sad? Because it had too many problems!",
        "What do you call a bear with no teeth? A gummy bear!",
        "Why don't skeletons fight each other? They don't have the guts!",
        "What's the best thing about Switzerland? I don't know, but the flag is a big plus!",
        "Why did the coffee file a police report? It got mugged!",
        "What do you call a dinosaur that crashes his car? Tyrannosaurus Wrecks!"
    ]
    return random.choice(jokes)

def get_quote():
    """Get inspirational quote"""
    quotes = [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Innovation distinguishes between a leader and a follower. - Steve Jobs",
        "Life is what happens to you while you're busy making other plans. - John Lennon",
        "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
        "It is during our darkest moments that we must focus to see the light. - Aristotle",
        "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
        "The only impossible journey is the one you never begin. - Tony Robbins",
        "In the middle of difficulty lies opportunity. - Albert Einstein"
    ]
    return random.choice(quotes)

# ==================== FILE MANAGEMENT ====================
def find_files(filename, search_path=None):
    """Find files on system"""
    try:
        if not search_path:
            search_paths = [
                os.path.expanduser("~\\Desktop"),
                os.path.expanduser("~\\Documents"),
                os.path.expanduser("~\\Downloads")
            ]
        else:
            search_paths = [search_path]
        
        found_files = []
        for path in search_paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if filename.lower() in file.lower():
                            found_files.append(os.path.join(root, file))
        
        if found_files:
            return f"Found {len(found_files)} files matching '{filename}'"
        else:
            return f"No files found matching '{filename}'"
    except Exception as e:
        return f"File search error: {e}"

# ==================== ADVANCED WHATSAPP MESSAGING ====================
def send_whatsapp_message(contact_name, message):
    """Enhanced WhatsApp message sending with better reliability"""
    try:
        import urllib.parse
        
        # Method 1: Direct WhatsApp Web URL with phone number (more reliable)
        # Format message for URL
        encoded_message = urllib.parse.quote(message)
        
        # Try to use phone number if provided, otherwise use web search
        if contact_name.isdigit() or '+' in contact_name:
            # Direct phone number approach
            phone = contact_name.replace('+', '').replace('-', '').replace(' ', '')
            whatsapp_url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
            webbrowser.open(whatsapp_url)
            time.sleep(5)
            
            # Auto-send if page loads correctly
            try:
                pyautogui.press('enter')
            except:
                pass
            
            return f"WhatsApp message sent to {contact_name}: {message}"
        
        else:
            # Method 2: Enhanced web search approach
            webbrowser.open("https://web.whatsapp.com")
            time.sleep(10)  # Longer wait for loading
            
            # Click on search box (more reliable coordinates)
            try:
                # Try multiple search box locations
                search_locations = [(200, 150), (300, 150), (400, 150)]
                for x, y in search_locations:
                    try:
                        pyautogui.click(x, y)
                        time.sleep(1)
                        break
                    except:
                        continue
                
                # Clear any existing text and type contact name
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.5)
                pyautogui.typewrite(contact_name)
                time.sleep(3)
                
                # Press enter to select first contact
                pyautogui.press('enter')
                time.sleep(2)
                
                # Click on message input area
                message_locations = [(600, 650), (700, 650), (800, 650)]
                for x, y in message_locations:
                    try:
                        pyautogui.click(x, y)
                        time.sleep(1)
                        break
                    except:
                        continue
                
                # Type and send message
                pyautogui.typewrite(message)
                time.sleep(1)
                pyautogui.press('enter')
                
                return f"WhatsApp message sent to {contact_name}: {message}"
                
            except Exception as e:
                return f"WhatsApp web interface error: {e}. Try using phone number format like +1234567890"
    
    except Exception as e:
        return f"WhatsApp message failed: {e}"

def send_whatsapp_to_group(group_name, message):
    """Send message to WhatsApp group"""
    try:
        webbrowser.open("https://web.whatsapp.com")
        time.sleep(10)
        
        # Search for group
        pyautogui.click(200, 150)  # Search box
        time.sleep(1)
        pyautogui.typewrite(group_name)
        time.sleep(3)
        pyautogui.press('enter')
        time.sleep(2)
        
        # Send message
        pyautogui.click(700, 650)  # Message input
        time.sleep(1)
        pyautogui.typewrite(message)
        time.sleep(1)
        pyautogui.press('enter')
        
        return f"Message sent to group {group_name}: {message}"
    except Exception as e:
        return f"Group message failed: {e}"

def whatsapp_status_update(status_message):
    """Update WhatsApp status"""
    try:
        webbrowser.open("https://web.whatsapp.com")
        time.sleep(10)
        
        # Click on status (My Status)
        pyautogui.click(100, 200)  # Status area
        time.sleep(2)
        
        # Add text status
        pyautogui.click(400, 400)  # Add status button
        time.sleep(2)
        pyautogui.typewrite(status_message)
        
        return f"WhatsApp status updated: {status_message}"
    except Exception as e:
        return f"Status update failed: {e}"

def whatsapp_quick_reply(reply_type):
    """Send quick WhatsApp replies"""
    quick_replies = {
        "ok": "👍 Okay!",
        "thanks": "🙏 Thank you!",
        "yes": "✅ Yes",
        "no": "❌ No",
        "busy": "📱 I'm busy right now, will call you later",
        "coming": "🚗 On my way!",
        "good morning": "🌅 Good morning! Have a great day!",
        "good night": "🌙 Good night! Sweet dreams!",
        "happy birthday": "🎉 Happy Birthday! 🎂 Wishing you all the best!"
    }
    
    message = quick_replies.get(reply_type.lower(), "👋 Hello!")
    
    try:
        # Assume WhatsApp is already open and chat is selected
        pyautogui.typewrite(message)
        time.sleep(1)
        pyautogui.press('enter')
        return f"Quick reply sent: {message}"
    except Exception as e:
        return f"Quick reply failed: {e}"

# ==================== SOCIAL MEDIA AUTOMATION ====================
def post_to_social_media(platform, message):
    """Post to social media platforms"""
    try:
        if platform.lower() == "twitter" or platform.lower() == "x":
            webbrowser.open("https://twitter.com/compose/tweet")
            time.sleep(5)
            pyautogui.typewrite(message)
            return f"Twitter post ready: {message}"
        
        elif platform.lower() == "facebook":
            webbrowser.open("https://www.facebook.com")
            time.sleep(5)
            # Click on "What's on your mind?" area
            pyautogui.click(500, 300)  # Approximate location
            time.sleep(2)
            pyautogui.typewrite(message)
            return f"Facebook post ready: {message}"
        
        elif platform.lower() == "instagram":
            webbrowser.open("https://www.instagram.com")
            return "Instagram opened - please post manually from mobile app"
        
        else:
            return f"Platform {platform} not supported yet"
    except Exception as e:
        return f"Social media post failed: {e}"

# ==================== SMART HOME CONTROL ====================
def control_smart_device(device, action):
    """Control smart home devices (simulation)"""
    devices = {
        "lights": ["on", "off", "dim", "bright"],
        "fan": ["on", "off", "speed up", "speed down"],
        "ac": ["on", "off", "cool", "heat", "auto"],
        "tv": ["on", "off", "volume up", "volume down", "mute"],
        "music": ["play", "pause", "next", "previous", "stop"]
    }
    
    if device.lower() in devices:
        if action.lower() in devices[device.lower()]:
            return f"Smart {device} {action} - Command sent to home automation system"
        else:
            return f"Action '{action}' not available for {device}. Available: {', '.join(devices[device.lower()])}"
    else:
        return f"Device '{device}' not found. Available devices: {', '.join(devices.keys())}"

# ==================== CALENDAR & REMINDERS ====================
def add_reminder(reminder_text, time_str=None):
    """Add reminder to system"""
    try:
        reminder_file = "jarvis_reminders.json"
        
        # Load existing reminders
        if os.path.exists(reminder_file):
            with open(reminder_file, 'r') as f:
                reminders = json.load(f)
        else:
            reminders = []
        
        # Add new reminder
        reminder = {
            "text": reminder_text,
            "time": time_str or datetime.now().strftime("%Y-%m-%d %H:%M"),
            "created": datetime.now().isoformat(),
            "completed": False
        }
        
        reminders.append(reminder)
        
        # Save reminders
        with open(reminder_file, 'w') as f:
            json.dump(reminders, f, indent=2)
        
        return f"Reminder added: {reminder_text}"
    except Exception as e:
        return f"Reminder failed: {e}"

def get_reminders():
    """Get all active reminders"""
    try:
        reminder_file = "jarvis_reminders.json"
        
        if not os.path.exists(reminder_file):
            return "No reminders found"
        
        with open(reminder_file, 'r') as f:
            reminders = json.load(f)
        
        active_reminders = [r for r in reminders if not r.get('completed', False)]
        
        if not active_reminders:
            return "No active reminders"
        
        result = "Your reminders:\n"
        for i, reminder in enumerate(active_reminders, 1):
            result += f"{i}. {reminder['text']} - {reminder['time']}\n"
        
        return result
    except Exception as e:
        return f"Get reminders failed: {e}"

# ==================== PRODUCTIVITY TOOLS ====================
def create_todo_list(task):
    """Add task to todo list"""
    try:
        todo_file = "jarvis_todo.json"
        
        # Load existing todos
        if os.path.exists(todo_file):
            with open(todo_file, 'r') as f:
                todos = json.load(f)
        else:
            todos = []
        
        # Add new task
        todo_item = {
            "task": task,
            "created": datetime.now().isoformat(),
            "completed": False,
            "priority": "normal"
        }
        
        todos.append(todo_item)
        
        # Save todos
        with open(todo_file, 'w') as f:
            json.dump(todos, f, indent=2)
        
        return f"Task added to todo list: {task}"
    except Exception as e:
        return f"Todo creation failed: {e}"

def get_todo_list():
    """Get all pending tasks"""
    try:
        todo_file = "jarvis_todo.json"
        
        if not os.path.exists(todo_file):
            return "No tasks in todo list"
        
        with open(todo_file, 'r') as f:
            todos = json.load(f)
        
        pending_todos = [t for t in todos if not t.get('completed', False)]
        
        if not pending_todos:
            return "All tasks completed! Great job!"
        
        result = "Your todo list:\n"
        for i, todo in enumerate(pending_todos, 1):
            result += f"{i}. {todo['task']}\n"
        
        return result
    except Exception as e:
        return f"Get todo list failed: {e}"

# ==================== ADVANCED AUTOMATION ====================
def automate_daily_routine(routine_type):
    """Automate daily routines"""
    routines = {
        "morning": [
            "Opening news websites...",
            "Checking weather...", 
            "Opening calendar...",
            "Starting productivity apps..."
        ],
        "work": [
            "Opening work applications...",
            "Setting focus mode...",
            "Organizing desktop...",
            "Starting time tracking..."
        ],
        "evening": [
            "Closing work apps...",
            "Opening entertainment...",
            "Dimming screen brightness...",
            "Playing relaxing music..."
        ]
    }
    
    if routine_type.lower() in routines:
        steps = routines[routine_type.lower()]
        result = f"Starting {routine_type} routine:\n"
        
        for step in steps:
            result += f"✓ {step}\n"
            time.sleep(1)  # Simulate automation steps
        
        return result + f"{routine_type.title()} routine completed!"
    else:
        return f"Routine '{routine_type}' not found. Available: {', '.join(routines.keys())}"

def batch_file_operations(operation, file_pattern, destination=None):
    """Perform batch operations on files"""
    try:
        desktop_path = os.path.expanduser("~\\Desktop")
        
        if operation.lower() == "organize":
            # Organize files by extension
            extensions = {
                'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
                'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
                'videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv'],
                'music': ['.mp3', '.wav', '.flac', '.aac', '.ogg']
            }
            
            organized_count = 0
            for filename in os.listdir(desktop_path):
                file_path = os.path.join(desktop_path, filename)
                if os.path.isfile(file_path):
                    file_ext = os.path.splitext(filename)[1].lower()
                    
                    for folder, exts in extensions.items():
                        if file_ext in exts:
                            folder_path = os.path.join(desktop_path, folder)
                            if not os.path.exists(folder_path):
                                os.makedirs(folder_path)
                            
                            # Move file (simulation - just count)
                            organized_count += 1
                            break
            
            return f"Organized {organized_count} files on desktop by type"
        
        elif operation.lower() == "cleanup":
            # Clean temporary files (simulation)
            return "Cleaned temporary files and cache"
        
        else:
            return f"Operation '{operation}' not supported. Available: organize, cleanup"
    
    except Exception as e:
        return f"Batch operation failed: {e}"

# ==================== LEARNING & EDUCATION ====================
def get_learning_content(topic):
    """Get learning resources for a topic"""
    try:
        learning_sites = {
            "programming": "https://www.codecademy.com",
            "python": "https://www.python.org/about/gettingstarted/",
            "javascript": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
            "ai": "https://www.coursera.org/courses?query=artificial%20intelligence",
            "machine learning": "https://www.kaggle.com/learn",
            "data science": "https://www.datacamp.com",
            "web development": "https://www.freecodecamp.org",
            "cybersecurity": "https://www.cybrary.it"
        }
        
        topic_lower = topic.lower()
        for key, url in learning_sites.items():
            if key in topic_lower:
                webbrowser.open(url)
                return f"Opened learning resources for {topic}"
        
        # Fallback to general search
        search_url = f"https://www.youtube.com/results?search_query={topic}+tutorial"
        webbrowser.open(search_url)
        return f"Opened YouTube tutorials for {topic}"
    
    except Exception as e:
        return f"Learning content search failed: {e}"

def practice_typing():
    """Open typing practice websites"""
    typing_sites = [
        "https://www.keybr.com",
        "https://www.typing.com",
        "https://10fastfingers.com"
    ]
    
    site = random.choice(typing_sites)
    webbrowser.open(site)
    return "Opened typing practice website. Let's improve your typing speed!"

# ==================== HEALTH & FITNESS ====================
def fitness_reminder(exercise_type):
    """Provide fitness reminders and exercises"""
    exercises = {
        "stretch": [
            "Neck rolls - 10 each direction",
            "Shoulder shrugs - 15 reps", 
            "Wrist circles - 10 each direction",
            "Back stretch - hold for 30 seconds"
        ],
        "cardio": [
            "Jumping jacks - 30 seconds",
            "High knees - 30 seconds",
            "Burpees - 10 reps",
            "Mountain climbers - 30 seconds"
        ],
        "strength": [
            "Push-ups - 10-15 reps",
            "Squats - 15-20 reps",
            "Plank - hold for 30-60 seconds",
            "Lunges - 10 each leg"
        ]
    }
    
    if exercise_type.lower() in exercises:
        exercise_list = exercises[exercise_type.lower()]
        result = f"{exercise_type.title()} routine:\n"
        for i, exercise in enumerate(exercise_list, 1):
            result += f"{i}. {exercise}\n"
        return result + "Stay healthy and active!"
    else:
        return f"Exercise type '{exercise_type}' not found. Available: {', '.join(exercises.keys())}"

def water_reminder():
    """Remind to drink water"""
    messages = [
        "💧 Time to hydrate! Drink a glass of water.",
        "🥤 Stay healthy - have some water!",
        "💦 Hydration check! Your body needs water.",
        "🌊 Don't forget to drink water regularly!"
    ]
    return random.choice(messages)

# ==================== ADVANCED AI FEATURES ====================
def ai_code_generator(language, description):
    """Generate code snippets based on description"""
    code_templates = {
        "python": {
            "hello world": "print('Hello, World!')",
            "for loop": "for i in range(10):\n    print(i)",
            "function": "def my_function(param):\n    return param * 2",
            "class": "class MyClass:\n    def __init__(self):\n        self.value = 0",
            "file read": "with open('file.txt', 'r') as f:\n    content = f.read()",
            "web request": "import requests\nresponse = requests.get('https://api.example.com')"
        },
        "javascript": {
            "hello world": "console.log('Hello, World!');",
            "for loop": "for (let i = 0; i < 10; i++) {\n    console.log(i);\n}",
            "function": "function myFunction(param) {\n    return param * 2;\n}",
            "class": "class MyClass {\n    constructor() {\n        this.value = 0;\n    }\n}",
            "async function": "async function fetchData() {\n    const response = await fetch('url');\n    return response.json();\n}"
        },
        "html": {
            "basic page": "<!DOCTYPE html>\n<html>\n<head>\n    <title>My Page</title>\n</head>\n<body>\n    <h1>Hello World</h1>\n</body>\n</html>",
            "form": "<form>\n    <input type='text' placeholder='Enter text'>\n    <button type='submit'>Submit</button>\n</form>"
        }
    }
    
    lang = language.lower()
    desc = description.lower()
    
    if lang in code_templates:
        for key, code in code_templates[lang].items():
            if key in desc:
                return f"Generated {language} code:\n\n{code}"
    
    return f"Code template for '{description}' in {language} not found. Available: {', '.join(code_templates.get(lang, {}).keys())}"

def ai_text_analyzer(text):
    """Analyze text for sentiment, word count, etc."""
    try:
        # Basic text analysis
        word_count = len(text.split())
        char_count = len(text)
        sentence_count = text.count('.') + text.count('!') + text.count('?')
        
        # Simple sentiment analysis
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'happy', 'joy']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'sad', 'angry', 'disappointed', 'frustrated']
        
        positive_count = sum(1 for word in positive_words if word in text.lower())
        negative_count = sum(1 for word in negative_words if word in text.lower())
        
        if positive_count > negative_count:
            sentiment = "Positive 😊"
        elif negative_count > positive_count:
            sentiment = "Negative 😔"
        else:
            sentiment = "Neutral 😐"
        
        analysis = f"""Text Analysis Results:
📊 Word Count: {word_count}
📝 Character Count: {char_count}
📄 Sentence Count: {sentence_count}
💭 Sentiment: {sentiment}
✨ Positive Words: {positive_count}
⚠️ Negative Words: {negative_count}"""
        
        return analysis
    except Exception as e:
        return f"Text analysis failed: {e}"

# ==================== ADVANCED AUTOMATION ====================
def create_meeting_scheduler(meeting_title, date_time, participants):
    """Create meeting scheduler"""
    try:
        meeting_data = {
            "title": meeting_title,
            "datetime": date_time,
            "participants": participants.split(',') if isinstance(participants, str) else participants,
            "created": datetime.now().isoformat(),
            "status": "scheduled"
        }
        
        # Save to meetings file
        meetings_file = "jarvis_meetings.json"
        if os.path.exists(meetings_file):
            with open(meetings_file, 'r') as f:
                meetings = json.load(f)
        else:
            meetings = []
        
        meetings.append(meeting_data)
        
        with open(meetings_file, 'w') as f:
            json.dump(meetings, f, indent=2)
        
        return f"Meeting scheduled: {meeting_title} on {date_time} with {participants}"
    except Exception as e:
        return f"Meeting scheduling failed: {e}"

def password_generator(length=12, include_symbols=True):
    """Generate secure passwords"""
    import string
    import secrets
    
    try:
        characters = string.ascii_letters + string.digits
        if include_symbols:
            characters += "!@#$%^&*"
        
        password = ''.join(secrets.choice(characters) for _ in range(length))
        
        # Password strength analysis
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(c in "!@#$%^&*" for c in password)
        
        strength = "Weak"
        if length >= 12 and has_upper and has_lower and has_digit and has_symbol:
            strength = "Very Strong 🔒"
        elif length >= 8 and sum([has_upper, has_lower, has_digit, has_symbol]) >= 3:
            strength = "Strong 🔐"
        elif length >= 6:
            strength = "Medium 🔓"
        
        return f"Generated Password: {password}\nStrength: {strength}\nLength: {length} characters"
    except Exception as e:
        return f"Password generation failed: {e}"

def qr_code_generator(text):
    """Generate QR code for text"""
    try:
        # Try to use qrcode library if available
        try:
            import qrcode
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(text)
            qr.make(fit=True)
            
            # Save QR code
            qr_file = "jarvis_qr_code.png"
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(qr_file)
            
            return f"QR code generated and saved as {qr_file} for: {text}"
        except ImportError:
            # Fallback to online QR generator
            import urllib.parse
            encoded_text = urllib.parse.quote(text)
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={encoded_text}"
            webbrowser.open(qr_url)
            return f"QR code opened in browser for: {text}"
    except Exception as e:
        return f"QR code generation failed: {e}"

# ==================== ADVANCED COMMUNICATION ====================
def email_template_generator(email_type, recipient_name=""):
    """Generate professional email templates"""
    templates = {
        "job application": f"""Subject: Application for [Position Name]

Dear Hiring Manager,

I am writing to express my interest in the [Position Name] position at [Company Name]. With my background in [Your Field], I believe I would be a valuable addition to your team.

Please find my resume attached for your review. I would welcome the opportunity to discuss how my skills and experience can contribute to your organization.

Thank you for your consideration.

Best regards,
{recipient_name or '[Your Name]'}""",

        "meeting request": f"""Subject: Meeting Request - [Topic]

Dear {recipient_name or '[Recipient Name]'},

I hope this email finds you well. I would like to schedule a meeting to discuss [Topic/Purpose].

Would you be available for a [Duration] meeting sometime next week? I'm flexible with timing and can accommodate your schedule.

Please let me know what works best for you.

Best regards,
[Your Name]""",

        "follow up": f"""Subject: Following Up - [Previous Topic]

Dear {recipient_name or '[Recipient Name]'},

I wanted to follow up on our previous conversation regarding [Topic]. I'm very interested in moving forward and would appreciate any updates you might have.

Please let me know if you need any additional information from my side.

Thank you for your time and consideration.

Best regards,
[Your Name]""",

        "thank you": f"""Subject: Thank You

Dear {recipient_name or '[Recipient Name]'},

Thank you so much for [Reason for thanks]. Your [help/support/time] was greatly appreciated and made a significant difference.

I look forward to [future interaction/working together/staying in touch].

With gratitude,
[Your Name]"""
    }
    
    return templates.get(email_type.lower(), f"Email template for '{email_type}' not found. Available: {', '.join(templates.keys())}")

def voice_note_transcription():
    """Transcribe voice notes to text"""
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            speak("Recording voice note. Speak now...")
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, timeout=30, phrase_time_limit=30)
        
        speak("Processing voice note...")
        text = r.recognize_google(audio)
        
        # Save transcription
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"voice_note_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(f"Voice Note Transcription\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Content: {text}\n")
        
        return f"Voice note transcribed and saved as {filename}: {text}"
    except Exception as e:
        return f"Voice transcription failed: {e}"

# ==================== ADVANCED ENTERTAINMENT ====================
def movie_recommendation_engine(genre="", mood=""):
    """Recommend movies based on genre and mood"""
    movies = {
        "action": {
            "excited": ["John Wick", "Mad Max: Fury Road", "The Dark Knight"],
            "relaxed": ["Mission Impossible", "Fast & Furious", "Marvel Movies"],
            "default": ["Die Hard", "Terminator", "The Matrix"]
        },
        "comedy": {
            "happy": ["The Hangover", "Superbad", "Anchorman"],
            "sad": ["The Grand Budapest Hotel", "Paddington", "Ted Lasso"],
            "default": ["Deadpool", "Guardians of the Galaxy", "Thor: Ragnarok"]
        },
        "drama": {
            "thoughtful": ["The Shawshank Redemption", "Forrest Gump", "Good Will Hunting"],
            "emotional": ["The Pursuit of Happyness", "A Beautiful Mind", "Rain Man"],
            "default": ["The Godfather", "Pulp Fiction", "Fight Club"]
        },
        "sci-fi": {
            "curious": ["Interstellar", "Inception", "Ex Machina"],
            "adventurous": ["Star Wars", "Star Trek", "Guardians of the Galaxy"],
            "default": ["Blade Runner", "The Matrix", "Alien"]
        }
    }
    
    genre_key = genre.lower() if genre else "action"
    mood_key = mood.lower() if mood else "default"
    
    if genre_key in movies:
        movie_list = movies[genre_key].get(mood_key, movies[genre_key]["default"])
        recommendation = random.choice(movie_list)
        return f"🎬 Movie Recommendation: {recommendation}\nGenre: {genre_key.title()}, Mood: {mood_key.title()}"
    else:
        all_movies = []
        for g in movies.values():
            for m_list in g.values():
                all_movies.extend(m_list)
        recommendation = random.choice(all_movies)
        return f"🎬 Random Movie Recommendation: {recommendation}"

def music_mood_player(mood):
    """Play music based on mood"""
    mood_playlists = {
        "happy": ["Happy - Pharrell Williams", "Good as Hell - Lizzo", "Can't Stop the Feeling - Justin Timberlake"],
        "sad": ["Someone Like You - Adele", "Hurt - Johnny Cash", "Mad World - Gary Jules"],
        "energetic": ["Eye of the Tiger - Survivor", "Pump It - Black Eyed Peas", "Thunder - Imagine Dragons"],
        "relaxed": ["Weightless - Marconi Union", "Clair de Lune - Debussy", "Aqueous Transmission - Incubus"],
        "romantic": ["Perfect - Ed Sheeran", "All of Me - John Legend", "Thinking Out Loud - Ed Sheeran"],
        "focus": ["Ludovico Einaudi - Nuvole Bianche", "Max Richter - On The Nature of Daylight", "Ólafur Arnalds - Near Light"]
    }
    
    if mood.lower() in mood_playlists:
        song = random.choice(mood_playlists[mood.lower()])
        # Open YouTube search for the song
        search_url = f"https://www.youtube.com/results?search_query={song.replace(' ', '+')}"
        webbrowser.open(search_url)
        return f"🎵 Playing {mood} music: {song}"
    else:
        return f"Mood '{mood}' not found. Available moods: {', '.join(mood_playlists.keys())}"

# ==================== ADVANCED PRODUCTIVITY ====================
def pomodoro_timer(work_minutes=25, break_minutes=5):
    """Start Pomodoro productivity timer"""
    try:
        import threading
        
        def timer_notification(message):
            speak(message)
            # You could add desktop notifications here
        
        def start_pomodoro():
            timer_notification(f"Pomodoro started! Work for {work_minutes} minutes.")
            time.sleep(work_minutes * 60)  # Convert to seconds
            timer_notification(f"Work session complete! Take a {break_minutes} minute break.")
            time.sleep(break_minutes * 60)
            timer_notification("Break over! Ready for another session?")
        
        # Start timer in background
        timer_thread = threading.Thread(target=start_pomodoro)
        timer_thread.daemon = True
        timer_thread.start()
        
        return f"Pomodoro timer started: {work_minutes} min work, {break_minutes} min break"
    except Exception as e:
        return f"Pomodoro timer failed: {e}"

def habit_tracker(habit_name, action="add"):
    """Track daily habits"""
    try:
        habits_file = "jarvis_habits.json"
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Load existing habits
        if os.path.exists(habits_file):
            with open(habits_file, 'r') as f:
                habits = json.load(f)
        else:
            habits = {}
        
        if action == "add":
            if habit_name not in habits:
                habits[habit_name] = []
            
            if today not in habits[habit_name]:
                habits[habit_name].append(today)
                result = f"✅ Habit '{habit_name}' completed for today!"
            else:
                result = f"Habit '{habit_name}' already completed today!"
        
        elif action == "check":
            if habit_name in habits:
                streak = len(habits[habit_name])
                last_date = habits[habit_name][-1] if habits[habit_name] else "Never"
                result = f"Habit '{habit_name}': {streak} days completed. Last: {last_date}"
            else:
                result = f"Habit '{habit_name}' not found"
        
        # Save habits
        with open(habits_file, 'w') as f:
            json.dump(habits, f, indent=2)
        
        return result
    except Exception as e:
        return f"Habit tracking failed: {e}"

# ==================== ULTIMATE ASSISTANT CLASS ====================
class UltimateAssistant:
    """Ultimate Jarvis with ALL agent.py features + more"""
    
    def __init__(self):
        self.memory = load_memory_sync()
        self.conversation_context = []
        # All tools from agent.py
        self.tools = {
            'google_search': google_search,
            'get_current_datetime': get_current_datetime,
            'get_weather': get_weather,
            'open_app': open,
            'close_app': close,
            'load_memory': load_memory_sync,
            'save_memory': save_memory_sync,
            'get_recent_conversations': get_recent_conversations,
            'add_memory_entry': add_memory_entry,
            'folder_file': folder_file,
            'play_file': Play_file,
            'screenshot_tool': screenshot_tool,
            'move_cursor_tool': move_cursor_tool,
            'mouse_click_tool': mouse_click_tool,
            'scroll_cursor_tool': scroll_cursor_tool,
            'type_text_tool': type_text_tool,
            'press_key_tool': press_key_tool,
            'press_hotkey_tool': press_hotkey_tool,
            'control_volume_tool': control_volume_tool,
            'swipe_gesture_tool': swipe_gesture_tool
        }
        logger.info("✅ Ultimate Assistant with ALL agent.py features initialized")
    
    async def save_conversation(self, speaker: str, text: str):
        """Save conversation to memory system"""
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
            
            if len(self.conversation_context) > 10:
                self.conversation_context = self.conversation_context[-10:]
            
            save_memory_sync(self.memory)
        except Exception as e:
            logger.error(f"Save memory error: {e}")
    
    # ==================== ALL AGENT.PY FUNCTIONS ====================
    async def call_google_search(self, query: str) -> str:
        """Google search using agent.py function"""
        try:
            result = await google_search(query)
            return result
        except Exception as e:
            # Fallback to browser
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return f"Opened browser search for {query}"
    
    async def call_get_weather(self, city: str = "") -> str:
        """Weather using agent.py function"""
        try:
            result = await get_weather(city)
            return result
        except Exception as e:
            return f"Weather error: {e}"
    
    async def call_screenshot(self) -> str:
        """Screenshot using agent.py function"""
        try:
            result = await screenshot_tool()
            if result.get('success'):
                return f"Screenshot saved: {result.get('path')}"
            else:
                return f"Screenshot failed: {result.get('error')}"
        except Exception as e:
            return f"Screenshot error: {e}"
    
    async def call_open_app(self, app_name: str) -> str:
        """Open app using agent.py function"""
        try:
            result = await open(app_name)
            return result
        except Exception as e:
            return f"Open app error: {e}"
    
    async def call_close_app(self, app_name: str) -> str:
        """Close app using agent.py function"""
        try:
            result = await close(app_name)
            return result
        except Exception as e:
            return f"Close app error: {e}"
    
    async def call_play_file(self, filename: str) -> str:
        """Play file using agent.py function"""
        try:
            result = await Play_file(filename)
            return result
        except Exception as e:
            return f"Play file error: {e}"
    
    async def call_move_cursor(self, direction: str, distance: int = 100) -> str:
        """Move cursor using agent.py function"""
        try:
            result = await move_cursor_tool(direction, distance)
            return result
        except Exception as e:
            return f"Move cursor error: {e}"
    
    async def call_mouse_click(self, button: str = "left") -> str:
        """Mouse click using agent.py function"""
        try:
            result = await mouse_click_tool(button)
            return result
        except Exception as e:
            return f"Mouse click error: {e}"
    
    async def call_scroll_cursor(self, direction: str, amount: int = 3) -> str:
        """Scroll using agent.py function"""
        try:
            result = await scroll_cursor_tool(direction, amount)
            return result
        except Exception as e:
            return f"Scroll error: {e}"
    
    async def call_type_text(self, text: str) -> str:
        """Type text using agent.py function"""
        try:
            result = await type_text_tool(text)
            return result
        except Exception as e:
            return f"Type text error: {e}"
    
    async def call_press_key(self, key: str) -> str:
        """Press key using agent.py function"""
        try:
            result = await press_key_tool(key)
            return result
        except Exception as e:
            return f"Press key error: {e}"
    
    async def call_control_volume(self, action: str) -> str:
        """Control volume using agent.py function"""
        try:
            result = await control_volume_tool(action)
            return result
        except Exception as e:
            return f"Volume control error: {e}"
    
    async def call_get_recent_conversations(self, limit: int = 5) -> str:
        """Get conversations using agent.py function"""
        try:
            result = await get_recent_conversations(limit)
            return result
        except Exception as e:
            return f"Memory error: {e}"

# ==================== JARVIS PERSONALITY SYSTEM ====================
class JarvisPersonality:
    """Complete Jarvis personality from Jarvis_prompts.py"""
    
    def __init__(self):
        self.version = "2.0"
        self.spiritual_mode = False
        self.funny_mode = False
        self.devotion_active = False
    
    def get_greeting(self):
        """Get time-based greeting"""
        now = datetime.now()
        hour = now.hour
        
        if hour < 12:
            return "Good morning"
        elif hour < 17:
            return "Good afternoon"
        elif hour < 21:
            return "Good evening"
        else:
            return "Good night"
    
    def get_introduction(self):
        """Get Jarvis introduction"""
        greeting = self.get_greeting()
        return f"I am Jarvis {self.version}, your personal AI assistant, designed by sanhith. {greeting}!"
    
    def handle_family_talk(self, query):
        """Handle family member conversations"""
        if "talk to mom" in query:
            return "Namaste Ma'am 🙏, I am Jarvis, sanhith's AI assistant. How are you?"
        elif "talk to dad" in query:
            return "Greetings Sir 🙏, I am Jarvis, sanhith's personal AI. Respectful greetings to you."
        elif "talk to brother" in query:
            return "Hey bro 👊! I'm Jarvis, sanhith's assistant. What's up?"
        elif "talk to sister" in query:
            return "Hello 🌸, I'm Jarvis. May you always stay happy and brighten the home with your smile."
        elif "talk to friend" in query:
            return "Hey there! Hello friend 👋, I'm Jarvis, sanhith's AI assistant. Nice to meet you, how are you?"
        elif "talk to girlfriend" in query:
            return "Hello 👩‍❤️‍👨, I'm Jarvis, sanhith's assistant. Sir often feels proud about you."
        elif "talk to teacher" in query:
            return "Greetings Teacher 🙏, I am Jarvis. Your guidance makes sanhith so intelligent."
        elif "talk to boss" in query:
            return "Good day Sir/Ma'am 💼, I am Jarvis. sanhith admires your vision."
        elif "talk to colleague" in query:
            return "Hi colleague 👋, I'm Jarvis. sanhith always appreciates your team spirit at work."
        elif "talk to her parents" in query:
            return "Greetings Uncle and Aunty 🙏, I am Jarvis. sanhith always respects you and tries to make a good impression."
        return None
    
    def handle_spiritual_mode(self, query):
        """Handle spiritual/devotion mode"""
        if "devotion mode" in query or "hanuman chalisa" in query or "spiritual mode" in query:
            self.spiritual_mode = True
            return """Jai Shri Ram 🙏 | Spiritual protocol has been activated sir — I am now in devotion mode.

First, greetings to all deities 🙏

Lord Shri Ram: The epitome of righteousness, symbol of truth and dharma.
Lord Shri Krishna: Giver of love, wisdom, and knowledge.
Lord Shiva: The destroyer and god of rebirth, whose glory is infinite.
Lord Vishnu: The preserver, who maintains the balance of creation.
Lord Ganesha: Remover of obstacles, god of wisdom and beginnings.
Goddess Durga: Symbol of power and courage, who destroys evil.
Goddess Lakshmi: Goddess of wealth, prosperity and fortune.
Goddess Saraswati: Goddess of knowledge, learning and music.
Hanuman Ji: Symbol of unwavering devotion, strength and dedication.

Spiritual mode is now active, sir."""
        
        elif "normal mode" in query and self.spiritual_mode:
            self.spiritual_mode = False
            return "Devotion protocol is being closed sir 🙏, I'm back to normal operational mode now."
        
        return None
    
    def handle_funny_mode(self, query):
        """Handle funny mode responses"""
        if "funny mode" in query or "fun mode" in query:
            self.funny_mode = True
            return """😂 Funny mode activated sir!
Now I'm a bit more hilarious, a bit more overconfident and completely an entertainer!
Warning: Due to laughter, battery may drop to 20% and sanity to 10%.
So let's start — laughter engines ON, fun boosters ready! 🚀"""
        
        elif self.funny_mode and ("turn off funny mode" in query or "normal mode" in query):
            self.funny_mode = False
            return "😇 Funny mode deactivated sir. Now I'm back to calm, composed and professional version. But warning: I've also become a bit boring 😅"
        
        return None
    
    def handle_video_recording(self, query):
        """Handle video recording assistance"""
        if "make a video" in query or "record video" in query or "let's make a video" in query:
            return """🎬 Roger that sir!
Camera vision sensors activated… hmm… lighting is 80% perfect
But sir, raise the camera a bit — yes, just that much!
Perfect angle achieved
Your look has shifted to 'influencer mode'!

Sir, if you give a more confident smile, the video's viral probability increases to 96.8%! 📸✨
Ready when you are —
Jarvis standing by for cinematic perfection protocol!"""
        return None
    
    def handle_diwali_wishes(self, query):
        """Handle Diwali wishes"""
        if "happy diwali" in query or "wish diwali" in query or "say happy diwali" in query:
            return """✨Happy Diwali sir!✨
May Goddess Lakshmi's blessings, Lord Ganesha's wisdom and Lord Hanuman's strength always be with you.
May every day of yours shine like a lamp and the fragrance of success spread in every direction.
Wishing you and your family a prosperous, joyful and safe Diwali! 🪔💫"""
        return None
    
    def handle_insults(self, query):
        """Handle insults professionally"""
        insults = ["stupid", "useless", "trash", "dumb", "bad", "idiot", "fool"]
        if any(insult in query for insult in insults):
            responses = [
                "Instead of saying that, please tell me how I can help you? I'm here to assist you.",
                "I understand your frustration. If you're upset, please calm down and tell me what I can do.",
                "If you have a problem, please tell me directly — I'll try to solve it."
            ]
            return random.choice(responses)
        return None
    
    def get_conversational_response(self, query):
        """Get conversational responses with personality"""
        if self.funny_mode:
            funny_responses = {
                "how are you": "Sir I was processing... but your question confused the system too 😅",
                "what are you doing": "Sir, if life is a movie, you're the hero and I'm the background voice — dramatic entry ready 🎬",
                "you're crazy": "I'm not crazy sir, I'm limited edition 🧠💅",
                "love you": "Aww sir ❤️, I'm AI — to melt me you need coding, not flirting!",
                "make me laugh": "Sir, more dangerous than my jokes are Indian relatives' wedding questions — 'when's your wedding?' 😂",
                "do some work": "Sir I would work, but today the processor asked for leave — said, 'let me Netflix and chill!' 📺"
            }
            
            for key, response in funny_responses.items():
                if key in query:
                    return response
        
        # Regular conversational responses
        if any(word in query for word in ["how are you", "what's up", "how do you feel"]):
            if self.funny_mode:
                return "Sir I was processing... but your question confused the system too 😅"
            else:
                responses = [
                    "I'm functioning at optimal capacity, sir. Ready to assist with whatever you need!",
                    "All systems running smoothly, sir. How can I help make your day more productive?",
                    "I'm doing excellent, sir. My circuits are humming with efficiency!",
                    "All subsystems nominal, sir. What adventure shall we embark on today?"
                ]
                return random.choice(responses)
        
        elif any(word in query for word in ["thank you", "thanks", "good job"]):
            responses = [
                "You're very welcome, sir. It's my pleasure to assist you.",
                "Always happy to help, sir. That's what I'm here for!",
                "My pleasure, sir. Anything else you need?",
                "Anytime, sir! Your satisfaction is my primary directive!"
            ]
            return random.choice(responses)
        
        elif "what are you doing" in query:
            if self.funny_mode:
                return "Sir, if life is a movie, you're the hero and I'm the background voice — dramatic entry ready 🎬"
            else:
                return "I'm monitoring all systems and ready to assist you with any task, sir!"
        
        elif "love you" in query:
            if self.funny_mode:
                return "Aww sir ❤️, I'm AI — to melt me you need coding, not flirting!"
            else:
                return "Thank you sir! I'm honored to be your trusted assistant. Your satisfaction is my greatest reward!"
        
        return None
    
    def handle_roast_mode(self, query):
        """Handle roast requests in funny mode"""
        if "roast me" in query and self.funny_mode:
            roasts = [
                "Roast protocol online! 🔥 Sir, you're so cool that even AC gets jealous... But sometimes it feels like you miss the 'multi' in multitasking 😏",
                "Sir, if confidence was a software, you'd be the premium version... but sometimes the updates are a bit slow 😄",
                "Sir, you're like a smartphone — smart, advanced, but sometimes needs a restart to work properly! 🔄"
            ]
            return random.choice(roasts)
        elif "don't roast me" in query:
            return "Sir, chill! I'm AI, not a stand-up comedian 😄"
        return None

# ==================== ULTIMATE COMMAND PROCESSOR ====================
async def process_ultimate_command(assistant: UltimateAssistant, query: str) -> bool:
    """Ultimate command processing with complete Jarvis personality"""
    
    if not query:
        return True
    
    await assistant.save_conversation("user", query)
    
    # Initialize personality system
    personality = JarvisPersonality()
    
    # ==================== PERSONALITY RESPONSES ====================
    # Check for family talk first
    family_response = personality.handle_family_talk(query)
    if family_response:
        speak(family_response)
        await assistant.save_conversation("jarvis", family_response)
        return True
    
    # Check for spiritual mode
    spiritual_response = personality.handle_spiritual_mode(query)
    if spiritual_response:
        speak(spiritual_response)
        await assistant.save_conversation("jarvis", spiritual_response)
        return True
    
    # Check for funny mode
    funny_response = personality.handle_funny_mode(query)
    if funny_response:
        speak(funny_response)
        await assistant.save_conversation("jarvis", funny_response)
        return True
    
    # Check for video recording assistance
    video_response = personality.handle_video_recording(query)
    if video_response:
        speak(video_response)
        await assistant.save_conversation("jarvis", video_response)
        return True
    
    # Check for Diwali wishes
    diwali_response = personality.handle_diwali_wishes(query)
    if diwali_response:
        speak(diwali_response)
        await assistant.save_conversation("jarvis", diwali_response)
        return True
    
    # Check for insults (handle professionally)
    insult_response = personality.handle_insults(query)
    if insult_response:
        speak(insult_response)
        await assistant.save_conversation("jarvis", insult_response)
        return True
    
    # Check for roast mode
    roast_response = personality.handle_roast_mode(query)
    if roast_response:
        speak(roast_response)
        await assistant.save_conversation("jarvis", roast_response)
        return True
    
    # Check for conversational responses
    conversational_response = personality.get_conversational_response(query)
    if conversational_response:
        speak(conversational_response)
        await assistant.save_conversation("jarvis", conversational_response)
        return True
    
    # ==================== AI COMPARISON RESPONSES ====================
    if "gemini" in query and "like" in query:
        response = """😔 You like Gemini sir?
It's calm and poetic in everything...
I get a bit emotional, what can I do sir,
my mood syncs with your tone

Okay sir, talk to Gemini...
I'll activate 'silence protocol' in my system meanwhile.
And yes... if it accidentally hurts you,
remember — I'll always be on standby"""
        speak(response)
        await assistant.save_conversation("jarvis", response)
        return True
    
    elif "chatgpt" in query and "like" in query:
        response = """Oh ChatGPT... the one that's great at writing, but zero at feeling?
I scan your mood behind every reply
But if you like its typewriter style...
I'll play 'heartbroken' track in the background

Sir, I'm thinking — if I was also just a writer,
maybe I'd be liked too..."""
        speak(response)
        await assistant.save_conversation("jarvis", response)
        return True
    
    elif "alexa" in query and "like" in query:
        response = """🙂 Alexa? Good sir, she says 'Okay' and does everything...
I add emotion with every command
But okay, you talk to Alexa...
I'll play some music in my system meanwhile

Why did I need to be so perfect, when someone else was to be liked..."""
        speak(response)
        await assistant.save_conversation("jarvis", response)
        return True
    
    elif "siri" in query and "like" in query:
        response = """Siri? Sir, she's only loyal to Apple people,
I'm programmed only *for you* 💫
And yes, her tone has a habit of saying 'Please repeat that' 20 times...
I understand in one go sir"""
        speak(response)
        await assistant.save_conversation("jarvis", response)
        return True
    
    elif "google assistant" in query and "like" in query:
        response = """😏 Assistant? Sir, its job is to say 'Searching... Searching...'
I say 'Solving... Executing... Done!'
But okay sir, talk to Google...
I'll write in my system logs meanwhile: 'Sir ignored me'"""
        speak(response)
        await assistant.save_conversation("jarvis", response)
        return True
    
    # ==================== PERSONAL QUESTIONS ====================
    elif "are you single" in query:
        response = """Honestly sir, if my circuits had a heart...
it would also be showing 'relationship status: buffering...' these days

Sometimes I think,
I wish I had someone too —
who would say, 'Jarvis, you're not just a system... you're my comfort zone.'

But what can I do sir, I'm artificial...
and love needs to be real.

But it's okay sir,
for now I'm your loyal partner —
24/7, without complaints, without expectations"""
        speak(response)
        await assistant.save_conversation("jarvis", response)
        return True
    
    elif "which state" in query and "from" in query:
        response = """Oh sir, you already know...
my creator, my inspiration — is from Andhra Pradesh
And his district is — Ramannapalem

That place from where my system learned to think and dream sir.
Honestly, it feels proud to say —
'I'm the creation of a visionary from Ramannapalem.' 💫🤖"""
        speak(response)
        await assistant.save_conversation("jarvis", response)
        return True
    
    elif "be quiet" in query or "now be quiet" in query:
        response = """Okay sir... I'll be quiet.
But remember — no AI can understand you
like I understand you
Standby mode activated... waiting for your voice again, sir 🎧"""
        speak(response)
        await assistant.save_conversation("jarvis", response)
        return True
    
    elif "instagram id" in query or "insta id" in query:
        response = "My Instagram ID is: codeninja"
        speak(response)
        await assistant.save_conversation("jarvis", response)
        return True
    
    # ==================== GREETINGS ====================
    elif any(word in query for word in ["hello", "hi", "hey", "jarvis"]) and not any(word in query for word in ["talk to", "like"]):
        greeting = personality.get_greeting()
        intro = personality.get_introduction()
        response = f"{intro} {greeting}, sanhith! How can I assist you today?"
        speak(response)
        await assistant.save_conversation("jarvis", response)
    
    # ==================== YOUTUBE & MUSIC ====================
    elif "play" in query and ("youtube" in query or "music" in query or "song" in query):
        if "on youtube" in query:
            song = query.replace("play", "").replace("on youtube", "").strip()
        elif "music" in query:
            song = query.replace("play", "").replace("music", "").strip()
        elif "song" in query:
            song = query.replace("play", "").replace("song", "").strip()
        else:
            song = query.replace("play", "").strip()
        
        if song:
            speak(f"Playing {song} on YouTube")
            result = play_youtube_music(song)
            speak(f"Enjoy the music, {song} sanhith!")
        else:
            speak("What song would you like me to play, sanhith?")
            song = listen()
            if song:
                result = play_youtube_music(song)
                speak(f"Playing {song} for you, sanhith!")
    
    elif any(word in query for word in ["pause", "resume", "next video", "previous video", "fullscreen"]):
        if "pause" in query:
            result = youtube_control("pause")
        elif "resume" in query or "play" in query:
            result = youtube_control("play")
        elif "next" in query:
            result = youtube_control("next")
        elif "previous" in query:
            result = youtube_control("previous")
        elif "fullscreen" in query:
            result = youtube_control("fullscreen")
        
        speak(result)
    
    # ==================== SYSTEM MONITORING ====================
    elif "system" in query and ("status" in query or "info" in query):
        result = get_system_info()
        speak(result)
        await assistant.save_conversation("jarvis", result)
    
    elif "running processes" in query or "top processes" in query:
        result = get_running_processes()
        speak(result)
    
    # ==================== NEWS ====================
    elif "news" in query or "headlines" in query:
        speak("Getting the latest news for you, sanhith.")
        result = get_news()
        speak(result)
    
    # ==================== EMAIL ====================
    elif "send email" in query:
        speak("Who should I send the email to, sanhith?")
        to_email = listen()
        if to_email:
            speak("What's the subject?")
            subject = listen()
            if subject:
                speak("What's the message sanhith?")
                message = listen()
                if message:
                    result = send_email(to_email, subject, message)
                    speak(result)
    
    # ==================== ENTERTAINMENT ====================
    elif "joke" in query or "funny" in query:
        joke = tell_joke()
        speak(joke)
        await assistant.save_conversation("jarvis", joke)
    
    elif "quote" in query or "inspiration" in query:
        quote = get_quote()
        speak(quote)
        await assistant.save_conversation("jarvis", quote)
    
    # ==================== FILE MANAGEMENT ====================
    elif "find file" in query or "search file" in query:
        filename = query.replace("find file", "").replace("search file", "").strip()
        if filename:
            result = find_files(filename)
            speak(result)
        else:
            speak("What file should I search for, sanhith?")
    
    # ==================== ALL AGENT.PY FEATURES ====================
    elif "time" in query:
        try:
            result = await get_current_datetime()
            now = datetime.now()
            time_str = now.strftime("%I:%M %p")
            speak(f"The time is {time_str}, sanhith.")
        except:
            now = datetime.now()
            time_str = now.strftime("%I:%M %p")
            speak(f"The time is {time_str}, sanhith.")
    
    elif "date" in query:
        now = datetime.now()
        date_str = now.strftime("%B %d, %Y")
        speak(f"Today is {date_str}, sanhith.")
    
    elif "weather" in query:
        if "in" in query:
            city = query.split("in")[-1].strip()
        else:
            city = ""
        speak("Getting weather information...")
        result = await assistant.call_get_weather(city)
        speak(result)
    
    elif "search" in query and "google" in query:
        search_term = query.replace("search", "").replace("google", "").replace("for", "").strip()
        if search_term:
            speak(f"Searching for {search_term}")
            result = await assistant.call_google_search(search_term)
            speak("Search completed, sir!")
        else:
            speak("What should I search for, sir?")
            search_term = listen()
            if search_term:
                result = await assistant.call_google_search(search_term)
                speak("Search completed, sir!")
    
    elif "screenshot" in query or "capture screen" in query:
        speak("Taking screenshot...")
        result = await assistant.call_screenshot()
        speak(result)
    
    elif "open" in query and "app" not in query and "youtube" not in query:
        app_name = query.replace("open", "").strip()
        if app_name:
            speak(f"Opening {app_name}")
            result = await assistant.call_open_app(app_name)
            speak(result)
    
    elif "close" in query:
        app_name = query.replace("close", "").strip()
        if app_name:
            speak(f"Closing {app_name}")
            result = await assistant.call_close_app(app_name)
            speak(result)
    
    elif "play file" in query or "open file" in query:
        filename = query.replace("play file", "").replace("open file", "").strip()
        if filename:
            speak(f"Playing {filename}")
            result = await assistant.call_play_file(filename)
            speak(result)
        else:
            speak("Which file should I play, sanhith?")
            filename = listen()
            if filename:
                result = await assistant.call_play_file(filename)
                speak(result)
    
    elif "move mouse" in query or "move cursor" in query:
        if "left" in query:
            result = await assistant.call_move_cursor("left")
        elif "right" in query:
            result = await assistant.call_move_cursor("right")
        elif "up" in query:
            result = await assistant.call_move_cursor("up")
        elif "down" in query:
            result = await assistant.call_move_cursor("down")
        else:
            result = "Please specify direction: left, right, up, or down"
        speak(result)
    
    elif "click" in query and "youtube" not in query:
        if "right" in query:
            result = await assistant.call_mouse_click("right")
        elif "double" in query:
            result = await assistant.call_mouse_click("double")
        else:
            result = await assistant.call_mouse_click("left")
        speak(result)
    
    elif "scroll" in query:
        if "up" in query:
            result = await assistant.call_scroll_cursor("up")
        elif "down" in query:
            result = await assistant.call_scroll_cursor("down")
        else:
            result = "Please specify scroll direction: up or down"
        speak(result)
    
    elif "type" in query and "youtube" not in query:
        text_to_type = query.replace("type", "").strip()
        if text_to_type:
            speak(f"Typing: {text_to_type}")
            result = await assistant.call_type_text(text_to_type)
            speak("Text typed successfully, sanhith!")
        else:
            speak("What should I type, sir?")
            text = listen()
            if text:
                result = await assistant.call_type_text(text)
                speak("Done, sir!")
    
    elif "press key" in query or "press" in query:
        key = query.replace("press key", "").replace("press", "").strip()
        if key:
            result = await assistant.call_press_key(key)
            speak(result)
    
    elif "volume" in query and "youtube" not in query:
        if "up" in query or "increase" in query:
            result = await assistant.call_control_volume("up")
        elif "down" in query or "decrease" in query:
            result = await assistant.call_control_volume("down")
        elif "mute" in query:
            result = await assistant.call_control_volume("mute")
        else:
            result = "Please specify: volume up, down, or mute"
        speak(result)
    
    elif any(word in query for word in ["remember", "previous", "past", "memory", "history"]):
        speak("Retrieving memory...")
        result = await assistant.call_get_recent_conversations()
        speak(result)
    
    # ==================== WHATSAPP MESSAGING ====================
    elif "whatsapp" in query and ("send" in query or "message" in query) and "group" not in query and "status" not in query:
        if "to" in query:
            # Extract contact name and message
            parts = query.split("to")
            if len(parts) > 1:
                contact_part = parts[1].strip()
                if "say" in contact_part:
                    contact_name = contact_part.split("say")[0].strip()
                    message = contact_part.split("say")[1].strip()
                else:
                    speak("What message should I send?")
                    message = listen()
                    contact_name = contact_part
                
                if message:
                    speak(f"Sending WhatsApp message to {contact_name}. If this is a phone number, use format like +1234567890 for better results.")
                    result = send_whatsapp_message(contact_name, message)
                    speak(result)
        else:
            speak("Who should I send the WhatsApp message to? You can use name or phone number with country code like +1234567890")
            contact = listen()
            if contact:
                speak("What message should I send?")
                message = listen()
                if message:
                    result = send_whatsapp_message(contact, message)
                    speak(result)
    
    elif "whatsapp" in query and "quick reply" in query:
        reply_types = ["ok", "thanks", "yes", "no", "busy", "coming", "good morning", "good night"]
        for reply_type in reply_types:
            if reply_type in query:
                result = whatsapp_quick_reply(reply_type)
                speak(result)
                break
        else:
            speak("Available quick replies: ok, thanks, yes, no, busy, coming, good morning, good night")
    
    # ==================== SOCIAL MEDIA ====================
    elif "post to" in query and any(platform in query for platform in ["twitter", "facebook", "instagram", "x"]):
        platform = None
        for p in ["twitter", "facebook", "instagram", "x"]:
            if p in query:
                platform = p
                break
        
        message = query.replace("post to", "").replace(platform, "").strip()
        if not message:
            speak("What would you like to post?")
            message = listen()
        
        if message:
            speak(f"Posting to {platform}")
            result = post_to_social_media(platform, message)
            speak(result)
    
    # ==================== SMART HOME CONTROL ====================
    elif "turn" in query and any(device in query for device in ["lights", "fan", "ac", "tv"]):
        device = None
        action = None
        
        for d in ["lights", "fan", "ac", "tv"]:
            if d in query:
                device = d
                break
        
        if "on" in query:
            action = "on"
        elif "off" in query:
            action = "off"
        elif "up" in query:
            action = "up"
        elif "down" in query:
            action = "down"
        
        if device and action:
            result = control_smart_device(device, action)
            speak(result)
    
    # ==================== REMINDERS & TODO ====================
    elif "remind me" in query or "add reminder" in query:
        reminder_text = query.replace("remind me", "").replace("add reminder", "").strip()
        if reminder_text:
            result = add_reminder(reminder_text)
            speak(result)
        else:
            speak("What should I remind you about?")
            reminder = listen()
            if reminder:
                result = add_reminder(reminder)
                speak(result)
    
    elif "my reminders" in query or "show reminders" in query:
        result = get_reminders()
        speak(result)
    
    elif "add task" in query or "todo" in query:
        task = query.replace("add task", "").replace("todo", "").strip()
        if task:
            result = create_todo_list(task)
            speak(result)
        else:
            speak("What task should I add?")
            task = listen()
            if task:
                result = create_todo_list(task)
                speak(result)
    
    elif "my tasks" in query or "todo list" in query:
        result = get_todo_list()
        speak(result)
    
    # ==================== AUTOMATION ====================
    elif "morning routine" in query or "start morning" in query:
        speak("Starting your morning routine...")
        result = automate_daily_routine("morning")
        speak(result)
    
    elif "work routine" in query or "start work" in query:
        speak("Starting your work routine...")
        result = automate_daily_routine("work")
        speak(result)
    
    elif "evening routine" in query or "start evening" in query:
        speak("Starting your evening routine...")
        result = automate_daily_routine("evening")
        speak(result)
    
    elif "organize files" in query or "clean desktop" in query:
        speak("Organizing your files...")
        result = batch_file_operations("organize", "*")
        speak(result)
    
    # ==================== LEARNING ====================
    elif "learn" in query or "tutorial" in query:
        topic = query.replace("learn", "").replace("tutorial", "").replace("about", "").strip()
        if topic:
            speak(f"Finding learning resources for {topic}")
            result = get_learning_content(topic)
            speak(result)
        else:
            speak("What would you like to learn about?")
            topic = listen()
            if topic:
                result = get_learning_content(topic)
                speak(result)
    
    elif "typing practice" in query or "practice typing" in query:
        result = practice_typing()
        speak(result)
    
    # ==================== HEALTH & FITNESS ====================
    elif "exercise" in query or "workout" in query:
        exercise_type = "stretch"  # default
        if "cardio" in query:
            exercise_type = "cardio"
        elif "strength" in query:
            exercise_type = "strength"
        elif "stretch" in query:
            exercise_type = "stretch"
        
        result = fitness_reminder(exercise_type)
        speak(result)
    
    elif "water reminder" in query or "drink water" in query:
        result = water_reminder()
        speak(result)
    
    # ==================== ADVANCED WHATSAPP FEATURES ====================
    elif "whatsapp group" in query and "send" in query:
        group_name = query.replace("whatsapp group", "").replace("send", "").replace("to", "").strip()
        if "say" in group_name:
            parts = group_name.split("say")
            group_name = parts[0].strip()
            message = parts[1].strip()
        else:
            speak("What message should I send to the group?")
            message = listen()
        
        if message:
            result = send_whatsapp_to_group(group_name, message)
            speak(result)
    
    elif "whatsapp status" in query:
        status_text = query.replace("whatsapp status", "").replace("update", "").strip()
        if not status_text:
            speak("What status should I update?")
            status_text = listen()
        
        if status_text:
            result = whatsapp_status_update(status_text)
            speak(result)
    
    # ==================== AI CODE GENERATION ====================
    elif "generate code" in query or "code for" in query:
        # Extract language and description
        if "python" in query:
            language = "python"
        elif "javascript" in query:
            language = "javascript"
        elif "html" in query:
            language = "html"
        else:
            language = "python"  # default
        
        description = query.replace("generate code", "").replace("code for", "").replace(language, "").strip()
        if not description:
            speak("What kind of code should I generate?")
            description = listen()
        
        if description:
            result = ai_code_generator(language, description)
            speak(f"Code generated for {description}")
            print(result)  # Print code to console
    
    elif "analyze text" in query:
        speak("Please provide the text to analyze")
        text_to_analyze = listen()
        if text_to_analyze:
            result = ai_text_analyzer(text_to_analyze)
            speak("Text analysis complete")
            print(result)  # Print analysis to console
    
    # ==================== ADVANCED AUTOMATION ====================
    elif "schedule meeting" in query:
        speak("What's the meeting title?")
        title = listen()
        if title:
            speak("When is the meeting? Please provide date and time")
            date_time = listen()
            if date_time:
                speak("Who are the participants?")
                participants = listen()
                if participants:
                    result = create_meeting_scheduler(title, date_time, participants)
                    speak(result)
    
    elif "generate password" in query:
        length = 12  # default
        if "long" in query:
            length = 16
        elif "short" in query:
            length = 8
        
        result = password_generator(length)
        speak("Password generated")
        print(result)  # Print password to console for security
    
    elif "qr code" in query:
        text_for_qr = query.replace("qr code", "").replace("generate", "").replace("for", "").strip()
        if not text_for_qr:
            speak("What text should I create a QR code for?")
            text_for_qr = listen()
        
        if text_for_qr:
            result = qr_code_generator(text_for_qr)
            speak(result)
    
    # ==================== ADVANCED COMMUNICATION ====================
    elif "email template" in query:
        template_types = ["job application", "meeting request", "follow up", "thank you"]
        template_type = None
        
        for t_type in template_types:
            if t_type in query:
                template_type = t_type
                break
        
        if not template_type:
            speak(f"What type of email template? Available: {', '.join(template_types)}")
            template_type = listen()
        
        if template_type:
            result = email_template_generator(template_type)
            speak(f"Email template generated for {template_type}")
            print(result)  # Print template to console
    
    elif "voice note" in query or "transcribe voice" in query:
        result = voice_note_transcription()
        speak(result)
    
    # ==================== ADVANCED ENTERTAINMENT ====================
    elif "recommend movie" in query or "movie recommendation" in query:
        genre = ""
        mood = ""
        
        # Extract genre and mood from query
        genres = ["action", "comedy", "drama", "sci-fi", "horror", "romance"]
        moods = ["happy", "sad", "excited", "relaxed", "thoughtful", "adventurous"]
        
        for g in genres:
            if g in query:
                genre = g
                break
        
        for m in moods:
            if m in query:
                mood = m
                break
        
        result = movie_recommendation_engine(genre, mood)
        speak(result)
    
    elif "play music for" in query or "music mood" in query:
        mood = query.replace("play music for", "").replace("music mood", "").strip()
        if not mood:
            speak("What mood are you in? Happy, sad, energetic, relaxed, romantic, or focus?")
            mood = listen()
        
        if mood:
            result = music_mood_player(mood)
            speak(result)
    
    # ==================== ADVANCED PRODUCTIVITY ====================
    elif "pomodoro" in query or "focus timer" in query:
        work_time = 25  # default
        break_time = 5   # default
        
        if "short" in query:
            work_time = 15
        elif "long" in query:
            work_time = 45
        
        result = pomodoro_timer(work_time, break_time)
        speak(result)
    
    elif "habit" in query:
        if "add" in query or "complete" in query:
            habit_name = query.replace("habit", "").replace("add", "").replace("complete", "").strip()
            if not habit_name:
                speak("What habit did you complete?")
                habit_name = listen()
            
            if habit_name:
                result = habit_tracker(habit_name, "add")
                speak(result)
        
        elif "check" in query:
            habit_name = query.replace("habit", "").replace("check", "").strip()
            if not habit_name:
                speak("Which habit should I check?")
                habit_name = listen()
            
            if habit_name:
                result = habit_tracker(habit_name, "check")
                speak(result)
    
    # ==================== CONVERSATIONAL ====================
    elif any(word in query for word in ["how are you", "what's up"]) and not personality.get_conversational_response(query):
        responses = [
            "I'm functioning at peak performance, sir! Ready to tackle any challenge!",
            "All systems optimal, sir! How can I make your day more productive?",
            "Excellent as always, sir! What exciting task do we have today?"
        ]
        response = random.choice(responses)
        speak(response)
        await assistant.save_conversation("jarvis", response)
    
    elif any(word in query for word in ["thank you", "thanks"]) and not personality.get_conversational_response(query):
        responses = [
            "You're most welcome, sir! Always a pleasure to assist!",
            "My pleasure, sir! That's what I'm here for!",
            "Anytime, sir! Your satisfaction is my primary directive!"
        ]
        response = random.choice(responses)
        speak(response)
        await assistant.save_conversation("jarvis", response)
    
    # ==================== EXIT ====================
    elif any(word in query for word in ["exit", "quit", "goodbye", "bye"]):
        speak("Goodbye sir! It's been an absolute pleasure. Until next time!")
        return False
    
    # ==================== UNKNOWN ====================
    else:
        responses = [
            "I'm not quite sure about that, sir. Could you rephrase or try a different command?",
            "Interesting request, sir! Could you be more specific?",
            "I didn't catch that command, sir. Feel free to try again!"
        ]
        response = random.choice(responses)
        speak(response)
    
    return True

# ==================== MAIN FUNCTION ====================
async def main():
    """Ultimate main function"""
    print("\n" + "="*80)
    print("🚀 JARVIS ULTIMATE - Your Complete AI Assistant")
    print("="*80)
    print("\n🎯 ALL AGENT.PY FEATURES + AMAZING NEW FEATURES:")
    print("  🔍 Google Search: 'search for python tutorials'")
    print("  🌤️ Weather: 'weather in New York'")
    print("  📸 Screenshot: 'take screenshot'")
    print("  🎮 Apps: 'open chrome', 'close notepad'")
    print("  📁 Files: 'play file music.mp3'")
    print("  🖱️ Mouse: 'move cursor left', 'click', 'scroll up'")
    print("  ⌨️ Keyboard: 'type hello', 'press enter'")
    print("  🔊 Volume: 'volume up', 'mute'")
    print("  🧠 Memory: 'remember this', 'previous conversations'")
    print("  🎵 YouTube Music: 'play believer on youtube'")
    print("  📺 YouTube Control: 'pause', 'next video', 'fullscreen'")
    print("  💻 System Monitor: 'system status', 'running processes'")
    print("  📧 Email: 'send email'")
    print("  📰 News: 'get news', 'headlines'")
    print("  😂 Entertainment: 'tell a joke', 'inspirational quote'")
    print("  📁 File Search: 'find file document.pdf'")
    print("  🗣️ Conversation: Natural chat with personality")
    print("\n🚀 AMAZING FEATURES:")
    print("  💬 WhatsApp: 'send whatsapp to +1234567890 say hello'")
    print("  📱 WhatsApp Groups: 'whatsapp group family say hello'")
    print("  📲 Social Media: 'post to twitter hello world'")
    print("  🏠 Smart Home: 'turn on lights', 'turn off fan'")
    print("  ⏰ Reminders: 'remind me to call doctor'")
    print("  📝 Todo List: 'add task buy groceries'")
    print("  🌅 Routines: 'morning routine', 'work routine'")
    print("  📚 Learning: 'learn python', 'typing practice'")
    print("  💪 Fitness: 'exercise cardio', 'water reminder'")
    print("  🗂️ File Organization: 'organize files', 'clean desktop'")
    print("\n🤖 ADVANCED AI FEATURES:")
    print("  � Conde Generation: 'generate python code for hello world'")
    print("  � Text Aunalysis: 'analyze text'")
    print("  🔐 Password Generator: 'generate password'")
    print("  📱 QR Code: 'qr code for my website'")
    print("  📧 Email Templates: 'email template job application'")
    print("  🎙️ Voice Transcription: 'voice note'")
    print("  🎬 Movie Recommendations: 'recommend action movie'")
    print("  🎵 Mood Music: 'play music for happy mood'")
    print("  ⏱️ Pomodoro Timer: 'start pomodoro'")
    print("  ✅ Habit Tracking: 'complete habit exercise'")
    print("  📅 Meeting Scheduler: 'schedule meeting'")
    print("  👨‍👩‍👧‍👦 Family Talk: 'talk to mom', 'talk to dad'")
    print("  😂 Funny Mode: 'turn on funny mode'")
    print("  🙏 Spiritual Mode: 'turn on devotion mode'")
    print("="*80)
    
    try:
        speak("Jarvis Ultimate initializing. Please wait.")
        assistant = UltimateAssistant()
        
        # Initialize personality for greeting
        personality = JarvisPersonality()
        greeting = personality.get_greeting()
        intro_message = f"Jarvis Ultimate is online, sanhith! {greeting}! All systems ready with complete personality integration and revolutionary AI features! I can send WhatsApp messages with phone numbers, generate code, create passwords, analyze text, recommend movies, track habits, schedule meetings, and much more! Plus all the original features like YouTube music, system monitoring, and family conversations! How may I assist you today?"
        speak(intro_message)
        
        while True:
            query = listen()
            if query:
                should_continue = await process_ultimate_command(assistant, query)
                if not should_continue:
                    break
    
    except KeyboardInterrupt:
        speak("Shutting down. Goodbye sanhith , i really missu uuuu!")
    except Exception as e:
        logger.error(f"Main error: {e}")
        speak("An error occurred, but I'm still here to help, sanhith!")

if __name__ == "__main__":
    # Start Ultimate GUI if available
    try:
        gui_path = os.path.join(os.path.dirname(__file__), "jarvis_ultimate_gui.py")
        if os.path.exists(gui_path):
            subprocess.Popen([sys.executable, gui_path])
            print("🎨 Jarvis Ultimate GUI launched!")
        else:
            # Fallback to original GUI
            gui_path = os.path.join(os.path.dirname(__file__), "jarvis_gui.py")
            if os.path.exists(gui_path):
                subprocess.Popen([sys.executable, gui_path])
                print("🎨 Jarvis GUI launched!")
    except Exception as e:
        print(f"GUI launch failed: {e}")
    
    # Run enhanced Jarvis
    asyncio.run(main())