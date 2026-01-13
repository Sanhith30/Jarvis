from dotenv import load_dotenv

import subprocess, os, sys, asyncio
import logging
import re

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    google,
    noise_cancellation,
)
from Jarvis_prompts import behavior_prompts, Reply_prompts
from Jarvis_screenshot import screenshot_tool
from Jarvis_google_search import google_search, get_current_datetime
from memory.jarvis_memory import load_memory, save_memory, get_recent_conversations, add_memory_entry
from memory_interceptor import MEMORY_KEYWORDS
from jarvis_get_whether import get_weather
from Jarvis_window_CTRL import open, close, folder_file
from Jarvis_file_opner import Play_file
from keyboard_mouse_CTRL import move_cursor_tool, mouse_click_tool, scroll_cursor_tool, type_text_tool, press_key_tool, swipe_gesture_tool, press_hotkey_tool, control_volume_tool

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Memory interceptor flag - set to True to enable client-side memory injection
ENABLE_MEMORY_INTERCEPTOR = True


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=behavior_prompts,
                         tools=[
                            google_search,
                            get_current_datetime,
                            get_weather,
                            open, # This is for opening apps
                            close, 
                            load_memory, save_memory,
                            get_recent_conversations, # For retrieving past conversations
                            add_memory_entry, # For adding entries to memory
                            folder_file, # This is for opening folders
                            Play_file,  # This is for running files like MP4, MP3, PDF, PPT, img, png etc.
                            screenshot_tool, # Tool for taking screenshots
                            move_cursor_tool, # This is for moving the cursor
                            mouse_click_tool, # This is for mouse clicking
                            scroll_cursor_tool, # This is for scrolling the cursor
                            type_text_tool, # This is for typing text
                            press_key_tool, # This is for pressing keys
                            press_hotkey_tool, # This is for pressing hotkeys
                            control_volume_tool, # This is for controlling volume
                            swipe_gesture_tool # This is for gesture swipe 
                            
                         ]
                         )


async def entrypoint(ctx: agents.JobContext):
    """Entry point for LiveKit agent session with improved error handling"""
    max_retries = 5  # Increased from 3
    retry_count = 0
    base_wait_time = 3  # Increased from 2
    
    while retry_count < max_retries:
        try:
            print(f"\n🚀 Starting agent session (attempt {retry_count + 1}/{max_retries})...")
            
            session = AgentSession(
                llm=google.beta.realtime.RealtimeModel(
                    voice="Charon"
                )
            )
            
            await session.start(
                room=ctx.room,
                agent=Assistant(),
                room_input_options=RoomInputOptions(
                    noise_cancellation=noise_cancellation.BVC(),
                    video_enabled=True 
                ),
            )

            await ctx.connect()
            print("✅ Connected to room, waiting for audio input...")

            # Generate reply with timeout handling
            try:
                # Try to inject memory context into the reply instructions
                instructions = Reply_prompts
                
                if ENABLE_MEMORY_INTERCEPTOR:
                    try:
                        print("🧠 Fetching memory context...")
                        # Fetch recent conversations to inject context
                        memory_context = await get_recent_conversations(limit=5)  # Reduced from 10
                        
                        # Only inject if there's actual memory, keep it brief
                        if "No conversations remembered yet" not in memory_context:
                            instructions = f"""{Reply_prompts}

[RECENT CONTEXT]
{memory_context}
[/CONTEXT]"""
                            print("✅ Memory context injected")
                        else:
                            instructions = Reply_prompts
                            print("ℹ️ No previous conversations to inject")
                    except Exception as e:
                        print(f"⚠️ Memory injection skipped: {e}")
                        instructions = Reply_prompts
                
                print("📡 Sending instructions to LLM (this may take a moment)...")
                await session.generate_reply(
                    instructions=instructions
                )
                print("✅ Session completed successfully")
                break  # Success - exit retry loop
                
            except Exception as e:
                error_msg = str(e).lower()
                print(f"⚠️ Reply generation error (attempt {retry_count + 1}/{max_retries}): {e}")
                
                # Check if it's a timeout/connection error worth retrying
                if any(keyword in error_msg for keyword in ["timed out", "timeout", "connection", "websocket", "closed"]):
                    if retry_count < max_retries - 1:
                        retry_count += 1
                        wait_time = base_wait_time * retry_count  # Exponential backoff
                        print(f"🔄 Connection issue detected. Retrying in {wait_time}s... ({retry_count}/{max_retries})")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        print("❌ Max retries exceeded after multiple timeouts")
                        raise
                else:
                    # Not a timeout - propagate error immediately
                    raise
            
        except KeyboardInterrupt:
            print("\n⛔ Agent stopped by user")
            break
        except Exception as e:
            print(f"❌ Session error (attempt {retry_count + 1}/{max_retries}): {e}")
            retry_count += 1
            
            if retry_count < max_retries:
                wait_time = base_wait_time * retry_count  # Exponential backoff
                print(f"⏳ Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
            else:
                print("❌ Max retries exceeded. Shutting down.")
                raise


if __name__ == "__main__":
    # Try to start the GUI alongside the agent (runs in a separate process)
    try:
        gui_path = os.path.join(os.path.dirname(__file__), "jarvis_gui.py")
        if os.path.exists(gui_path):
            # Start GUI as a detached subprocess so the agent can continue
            subprocess.Popen([sys.executable, gui_path], stdout=None, stderr=None, stdin=None, close_fds=True)
        else:
            print("jarvis_gui.py not found; GUI will not be started.")
    except Exception as e:
        print("Failed to start GUI subprocess:", e)

    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))