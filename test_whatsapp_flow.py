"""
Test script to verify WhatsApp interactive flow
"""

def test_whatsapp_command_parsing():
    """Test the WhatsApp command parsing logic"""
    
    print("🧪 TESTING WHATSAPP COMMAND FLOW")
    print("="*60)
    
    # Test Case 1: Interactive mode (no message or contact in query)
    query1 = "open whatsapp and send message"
    print(f"\n📝 Test 1: '{query1}'")
    
    message = None
    contact = None
    
    if "message" in query1 and "to" in query1:
        print("   → Has 'message' and 'to' in query")
        parts = query1.split("message")
        if len(parts) > 1:
            msg_part = parts[1].strip()
            if "to" in msg_part:
                msg_parts = msg_part.split("to")
                message = msg_parts[0].strip()
                contact = msg_parts[1].strip()
    else:
        print("   → Interactive mode detected")
        print("   → Would ask: 'What message should I send?'")
        message = "I'm running late"  # Simulated user input
        print(f"   → User says: '{message}'")
        print("   → Would ask: 'Who should I send it to?'")
        contact = "+919876543210"  # Simulated user input
        print(f"   → User says: '{contact}'")
    
    if message and contact:
        print(f"   ✅ SUCCESS: Would send '{message}' to {contact}")
    else:
        print(f"   ❌ FAILED: message={message}, contact={contact}")
    
    # Test Case 2: Full command with message and contact
    query2 = "open whatsapp and send message hello how are you to mom"
    print(f"\n📝 Test 2: '{query2}'")
    
    message = None
    contact = None
    
    if "message" in query2 and "to" in query2:
        print("   → Has 'message' and 'to' in query")
        parts = query2.split("message")
        if len(parts) > 1:
            msg_part = parts[1].strip()
            if "to" in msg_part:
                msg_parts = msg_part.split("to")
                message = msg_parts[0].strip()
                contact = msg_parts[1].strip()
                print(f"   → Extracted message: '{message}'")
                print(f"   → Extracted contact: '{contact}'")
    
    if message and contact:
        print(f"   ✅ SUCCESS: Would send '{message}' to {contact}")
    else:
        print(f"   ❌ FAILED: message={message}, contact={contact}")
    
    # Test Case 3: Message in query, but no contact
    query3 = "open whatsapp and send message I'm coming"
    print(f"\n📝 Test 3: '{query3}'")
    
    message = None
    contact = None
    
    if "message" in query3 and "to" in query3:
        print("   → Has 'message' and 'to' in query")
        parts = query3.split("message")
        if len(parts) > 1:
            msg_part = parts[1].strip()
            if "to" in msg_part:
                msg_parts = msg_part.split("to")
                message = msg_parts[0].strip()
                contact = msg_parts[1].strip()
            else:
                message = msg_part
                print(f"   → Extracted message: '{message}'")
                print("   → Would ask: 'Who should I send this to?'")
                contact = "john"  # Simulated user input
                print(f"   → User says: '{contact}'")
    else:
        print("   → Interactive mode")
    
    if message and contact:
        print(f"   ✅ SUCCESS: Would send '{message}' to {contact}")
    else:
        print(f"   ❌ FAILED: message={message}, contact={contact}")
    
    print("\n" + "="*60)
    print("✅ All test cases completed!")
    print("\n📋 Expected Flow for 'open whatsapp and send message':")
    print("1. Jarvis: 'Opening WhatsApp. Please tell me the message and contact.'")
    print("2. Jarvis: 'What message should I send?'")
    print("3. User: 'I'm running late'")
    print("4. Jarvis: 'Who should I send it to?'")
    print("5. User: '+919876543210'")
    print("6. Jarvis: 'Sending I'm running late to +919876543210 on WhatsApp'")
    print("7. [Sends message]")

if __name__ == "__main__":
    test_whatsapp_command_parsing()
