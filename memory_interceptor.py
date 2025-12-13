"""
Memory Interceptor - Detects memory keywords and pre-fetches conversation context
before sending to LLM. This ensures Jarvis always has context about past conversations
when asked, bypassing unreliable LLM tool-calling behavior.
"""
import asyncio
from memory.jarvis_memory import get_recent_conversations

# Memory retrieval keywords in English
MEMORY_KEYWORDS = [
    "remember", "what did", "conversation", "previous", "history", "memory", 
    "old conversations", "do you remember", "recall", "past", "past conversation",
    "yesterday what", "what did i say", "remember", "recall", "past conversation",
    "tell me what", "my conversations", "previous talk"
]

def should_retrieve_memory(user_text: str) -> bool:
    """Check if user input contains memory-related keywords"""
    if not user_text or not isinstance(user_text, str):
        return False
    
    text_lower = user_text.lower().strip()
    return any(kw.lower() in text_lower for kw in MEMORY_KEYWORDS)

async def inject_memory_context(user_text: str, system_prompt: str = "") -> tuple[str, str]:
    """
    If user asked about memory, fetch recent conversations and inject into system prompt.
    Returns: (modified_system_prompt, user_text) tuple
    
    This ensures the LLM always has context about past conversations,
    even if it doesn't invoke the memory tool directly.
    """
    if not should_retrieve_memory(user_text):
        return system_prompt, user_text
    
    try:
        # Fetch recent conversations
        memory_context = await get_recent_conversations(limit=10)
        
        # Inject into system prompt
        enhanced_prompt = f"""{system_prompt}

[MEMORY CONTEXT INJECTED]
{memory_context}
[END MEMORY CONTEXT]

Respond that you remember the above past conversations.
"""
        return enhanced_prompt, user_text
        
    except Exception as e:
        print(f"⚠️ Memory injection error: {e}")
        # Fallback: return original prompt if injection fails
        return system_prompt, user_text

async def process_with_memory(user_input: str, base_instructions: str = "") -> dict:
    """
    Process user input with memory awareness.
    If memory keyword detected, fetch and return conversation context.
    
    Returns dict with keys:
    - has_memory_request: bool
    - context: str (memory summary or empty)
    - enhanced_instructions: str (modified instructions with context)
    """
    if not should_retrieve_memory(user_input):
        return {
            "has_memory_request": False,
            "context": "",
            "enhanced_instructions": base_instructions
        }
    
    try:
        context = await get_recent_conversations(limit=10)
        enhanced = f"{base_instructions}\n\n[MEMORY]\n{context}\n[/MEMORY]"
        
        return {
            "has_memory_request": True,
            "context": context,
            "enhanced_instructions": enhanced
        }
    except Exception as e:
        print(f"❌ Memory processing error: {e}")
        return {
            "has_memory_request": False,
            "context": "",
            "enhanced_instructions": base_instructions
        }


if __name__ == "__main__":
    # Quick test
    test_inputs = [
        "What did we talk about before?",
        "Do you remember?",
        "Open a file",
        "Tell me my previous conversations",
    ]
    
    async def test():
        for inp in test_inputs:
            result = should_retrieve_memory(inp)
            print(f"'{inp}' -> Memory request: {result}")
        
        # Test actual retrieval
        result = await process_with_memory("What happened before?", "Base instructions")
        print(f"\nMemory processing result:\n{result}")
    
    asyncio.run(test())
