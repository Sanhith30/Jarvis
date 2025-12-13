#!/usr/bin/env python
"""
Direct test of memory system — simulates what Jarvis should do
when user asks "Do you remember?" or similar questions.
"""
import asyncio
from memory.jarvis_memory import get_recent_conversations

async def main():
    print("=" * 60)
    print("MEMORY SYSTEM TEST - Simulating Jarvis Response")
    print("=" * 60)
    print()
    
    # Simulate user asking for past conversation
    user_input = "Do you remember? What did I say before?"
    print(f"User: {user_input}")
    print()
    
    # Check if memory keywords are present
    memory_keywords = ["remember", "what did", "conversation", "previous", "history", "memory", "old conversations"]
    has_memory_keyword = any(kw in user_input for kw in memory_keywords)
    
    if has_memory_keyword:
        print("✓ Memory retrieval keyword detected!")
        print("✓ Calling get_recent_conversations()...")
        print()
        
        # Call the memory retrieval tool
        result = await get_recent_conversations(10)
        
        # Jarvis would then respond with this:
        print("Jarvis Response:")
        print("-" * 60)
        print(f"Sir, do you remember? Yes, I remember everything. Your previous conversations:\n\n{result}")
        print("-" * 60)
    else:
        print("✗ No memory keyword found")

if __name__ == "__main__":
    asyncio.run(main())
