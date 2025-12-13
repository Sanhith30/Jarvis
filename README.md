# How to Run Jarvis Voice Assistant

## Prerequisites
All dependencies are now installed! ✅

## Running the Project

### Start the Agent
```cmd
python agent.py dev
```

This will:
- Start the LiveKit agent in development mode
- Automatically launch the GUI window
- Connect to your LiveKit server using credentials from `.env`

### What Happens Next
1. The agent connects to LiveKit using your configured credentials
2. A GUI window opens showing the assistant status
3. The agent waits for voice input through LiveKit's audio connection
4. You can interact with Jarvis through voice commands

## Voice Commands You Can Use

### Search & Information
- "Search Google for [topic]"
- "What's the weather in [city]?"
- "What's the current date and time?"

### Computer Control
- "Open [app name]" (e.g., "Open Chrome")
- "Close [app name]"
- "Open [folder name]"
- "Play [file name]"
- "Take a screenshot"

### Mouse & Keyboard
- "Move cursor to [x], [y]"
- "Click the mouse"
- "Type [text]"
- "Press [key]"
- "Press [hotkey combination]"
- "Increase/decrease volume"
- "Scroll up/down"

### Memory
- Jarvis automatically remembers your conversations
- It will recall context from previous interactions

## Troubleshooting

### Connection Issues
- Verify your LiveKit credentials in `.env` are correct
- Make sure your LiveKit server is running
- Check your internet connection

### No Audio
- Ensure your microphone is connected and working
- Check Windows audio settings
- Verify LiveKit audio permissions

### GUI Not Opening
- The GUI should open automatically
- If not, you can run it separately: `python jarvis_gui.py`

## Stopping the Agent
Press `Ctrl+C` in the terminal to stop Jarvis

## Notes
- The agent uses Google's "Charon" voice
- It auto-retries up to 5 times on connection failures
- Memory is saved in `memory/memory.json`
- Screenshots are saved in `screenshots/` folder

