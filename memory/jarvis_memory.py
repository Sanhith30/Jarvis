import speech_recognition as sr
import pyttsx3
import json
import os
from datetime import datetime
from livekit.agents import function_tool

# --- Configuration ---
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory.json")

# ==============================================================================
# 1. Core Engine Components
# ==============================================================================

try:
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
except Exception as e:
    print(f"TTS Engine Error: {e}")
    engine = None

def speak(audio):
    """This function makes Jarvis speak and saves the conversation to memory"""
    print(f"Jarvis: {audio}")
    if engine:
        engine.say(audio)
        engine.runAndWait()
    append_conversation_sync("jarvis", audio)

def take_command():
    """Listens from microphone, converts to text and saves the conversation"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            print("Listening timed out.")
            return "None"

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-IN')
        print(f"User said: {query}\n")
        append_conversation_sync("user", query)
        return query.lower()
    except Exception:
        print("Sorry, I did not understand that.")
        return "None"

# ==============================================================================
# 2. Memory Management Functions
# ==============================================================================

def load_memory_sync():
    """Loads memory from JSON file"""
    if not os.path.exists(MEMORY_FILE):
        return {"facts": {}, "conversation": []}
    
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            if "facts" not in data: data["facts"] = {}
            if "conversation" not in data: data["conversation"] = []
            return data
        except json.JSONDecodeError:
            return {"facts": {}, "conversation": []}

def save_memory_sync(data: dict):
    """Saves memory to JSON file"""
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def append_conversation_sync(speaker: str, text: str):
    """Adds conversation to memory"""
    if not text or text == "None":
        return
        
    entry = {"speaker": speaker, "text": text, "ts": datetime.now().isoformat()}
    memory = load_memory_sync()
    memory["conversation"].append(entry)
    save_memory_sync(memory)

# ==============================================================================
# 3. Jarvis Action Functions
# ==============================================================================

def remember_something(memory):
    """Asks user for a fact and saves it to memory['facts']"""
    speak("Okay, what should I remember?")
    thing_to_remember = take_command()
    if thing_to_remember != "None":
        speak(f"Okay, what information should I remember about '{thing_to_remember}'?")
        info = take_command()
        if info != "None":
            memory['facts'][thing_to_remember] = info
            save_memory_sync(memory)
            speak("Okay, I have remembered this.")
        else:
            speak("Sorry, I didn't hear the information.")
    else:
        speak("Sorry, I didn't hear what to remember.")

def recall_something(memory, query):
    """Finds and tells information from memory['facts']"""
    found = False
    for key in memory['facts'].keys():
        if key in query:
            speak(f"I remember that {key}, {memory['facts'][key]}")
            found = True
            break
    if not found:
        speak("Sorry, I don't remember any facts about this.")

def recall_conversation(memory):
    """Reads and tells past conversation from memory['conversation']"""
    speak("Okay, here are our previous conversations.")
    recent_chats = memory['conversation'][-5:] # Last 5 conversations
    
    if not recent_chats:
        speak("Sorry, no conversations remembered yet.")
        return

    for entry in recent_chats:
        speaker = "You said" if entry.get("speaker") == "user" else "I said"
        text = entry.get("text", "")
        speak(f"{speaker}, {text}")

def forget_something(memory):
    """Asks which fact to forget from memory['facts']"""
    speak("Which fact should I forget?")
    key_to_forget = take_command()
    if key_to_forget in memory['facts']:
        del memory['facts'][key_to_forget]
        save_memory_sync(memory)
        speak(f"Okay, I have forgotten about '{key_to_forget}'.")
    elif key_to_forget != "None":
        speak(f"I don't remember any fact named '{key_to_forget}'.")
    else:
        speak("Sorry, I didn't hear you.")

# ==============================================================================
# 4. LiveKit Agent Tools - @function_tool decorated
# ==============================================================================

@function_tool
async def load_memory(limit: int = 10) -> str:
    """Loads all facts from memory"""
    try:
        memory = load_memory_sync()
        facts = memory.get("facts", {})
        
        if not facts:
            return "No facts remembered yet."
        
        facts_list = "\n".join([f"• {key}: {value}" for key, value in list(facts.items())[:limit]])
        return f"Remembered facts:\n{facts_list}"
    except Exception as e:
        return f"Error loading memory: {str(e)}"

@function_tool
async def save_memory(data: dict) -> str:
    """Saves new data to memory"""
    try:
        save_memory_sync(data)
        return "✓ Data saved successfully"
    except Exception as e:
        return f"❌ Error saving: {str(e)}"

@function_tool
async def get_recent_conversations(limit: int = 10) -> str:
    """Retrieves past conversations and provides summary"""
    try:
        memory = load_memory_sync()
        entries = memory.get("entries", [])
        
        if not entries:
            return "No conversations remembered yet."
        
        recent = entries[-limit:]
        summary_lines = []
        
        for entry in recent:
            speaker = "You" if entry.get("speaker") == "user" else "Jarvis"
            text = entry.get("text", "")
            summary_lines.append(f"- {speaker}: {text}")
        
        return "Previous conversations:\n" + "\n".join(summary_lines)
    except Exception as e:
        return f"Error retrieving conversations: {str(e)}"

@function_tool
async def add_memory_entry(speaker: str, text: str) -> str:
    """Adds new entry to conversation"""
    try:
        append_conversation_sync(speaker, text)
        return f"✓ Entry for '{speaker}' added"
    except Exception as e:
        return f"❌ Error adding entry: {str(e)}"

# ==============================================================================
# 4. Command Processing
# ==============================================================================

def process_command(query, memory):
    """Processes command and takes appropriate action"""
    
    if "remember" in query or "remember this" in query:
        remember_something(memory)
        return True

    elif "previous conversation" in query or "past conversation" in query or "what did we talk" in query:
        current_memory = load_memory_sync()
        recall_conversation(current_memory)
        return True

    elif "forget" in query or "forget this" in query:
        forget_something(memory)
        return True
    
    elif "what is" in query or "when is" in query or "tell me" in query or "who is" in query:
        recall_something(memory, query)
        return True

    elif "stop" in query or "exit" in query or "quit" in query:
        speak("Okay, shutting down the system. Goodbye!")
        return False # Return False to stop the loop

    # If no command matches
    # speak("I didn't understand that command.") # You can uncomment this if you want
    return True # Return True to continue the loop


# ==============================================================================
# 5. Main Program Execution
# ==============================================================================

if __name__ == "__main__":
    memory_data = load_memory_sync()
    speak("System is online, how can I help you?")
    
    # This loop is now very clean
    while True:
        query = take_command()

        if query == "None":
            continue

        # All logic is now inside the process_command function
        should_continue = process_command(query, memory_data)
        
        if not should_continue:
            break