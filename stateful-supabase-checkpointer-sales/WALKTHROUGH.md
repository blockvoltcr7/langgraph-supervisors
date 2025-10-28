# 🎓 Complete Walkthrough - How to Send Messages

**3 ways to interact with the sales qualification system**

---

## 🚀 Method 1: Interactive Chat (EASIEST)

### Run the Chat Interface
```bash
python chat.py
```

### What Happens:
```
👤 Enter your username (e.g., @john_doe): @sarah

💬 CHAT WITH @sarah
────────────────────────────────────────────────────────────────────────────────

🆕 Starting new conversation

💡 Commands:
   - Type your message to chat
   - 'quit' or 'exit' to end

────────────────────────────────────────────────────────────────────────────────

👤 You: Hi, I'm interested in the program

🚀 Starting new conversation for @sarah
👤 User: Hi, I'm interested in the program
────────────────────────────────────────────────────────────────────────────────

🤖 AI (qualifier): Can you afford to invest $300 in this program?
📊 Stage: qualifying

👤 You: Yes, I can afford it

💬 Continuing conversation for @sarah
👤 User: Yes, I can afford it
────────────────────────────────────────────────────────────────────────────────

🤖 AI (qualifier): Excellent! You're qualified for our program...
📊 Stage: closing

🤖 AI (closer): 🎉 Perfect! Here's your payment link:
https://buy.stripe.com/test_@sarah_300
📊 Stage: complete

👤 You: quit

👋 Goodbye! Your conversation is saved in Supabase.
```

---

## 💻 Method 2: Use Python Functions Directly

### In Python Script or REPL:

```python
from main import start_new_conversation, continue_conversation

# Start a new conversation
start_new_conversation("@john_doe", "Hi, I want to join")

# Continue the conversation
continue_conversation("@john_doe", "Yes, I can afford $300")

# Send another message
continue_conversation("@john_doe", "Send me the payment link")
```

### Example Output:
```python
>>> from main import start_new_conversation

>>> start_new_conversation("@john", "Hi there!")

🚀 Starting new conversation for @john
👤 User: Hi there!
────────────────────────────────────────────────────────────────────────────────

🤖 AI (qualifier): Can you afford to invest $300 in this program?
📊 Stage: qualifying
```

---

## 🎬 Method 3: Run the Full Demo

### Run All Examples:
```bash
python main.py
```

This runs 3 complete scenarios:
1. **Qualified User** (@sarah_coach) - Gets Stripe link
2. **Disqualified User** (@broke_user) - Can't afford
3. **Multi-Session** (@fitness_pro) - Conversation over days

---

## 📊 Check Status & History

### Get User Status:
```python
from main import get_conversation_status

get_conversation_status("@john_doe")
```

**Output:**
```
📊 Status for @john_doe
════════════════════════════════════════════════════════════════════════════════
Qualified: True
Can Afford: True
Current Stage: complete
Stripe Link Sent: True
Stripe Link: https://buy.stripe.com/test_@john_doe_300
Started: 2025-01-27T01:00:00
Last Updated: 2025-01-27T01:05:00
Total Messages: 6
```

### View Conversation History:
```python
from main import view_conversation_history

view_conversation_history("@john_doe")
```

**Output:**
```
📜 Conversation History for @john_doe
════════════════════════════════════════════════════════════════════════════════

1. 👤 User:
   Hi, I want to join

2. 🤖 AI:
   Can you afford to invest $300 in this program?

3. 👤 User:
   Yes, I can afford $300

4. 🤖 AI:
   Excellent! You're qualified...

5. 🤖 AI:
   🎉 Perfect! Here's your payment link: https://...
```

---

## 🔄 Multi-Session Example

### Day 1 (Monday):
```bash
python chat.py
# Username: @sarah
# You: Hi, I'm interested
# AI: Can you afford $300?
# You: quit
```

### Day 3 (Wednesday):
```bash
python chat.py
# Username: @sarah
# ✅ Continuing existing conversation
# You: Yes, I can afford it
# AI: Here's your Stripe link!
```

**The conversation continues from where you left off!** 🎉

---

## 🛠️ Advanced: Build Your Own Integration

### Example: Instagram DM Bot

```python
from main import continue_conversation

def handle_instagram_dm(instagram_handle, message_text):
    """
    Handle incoming Instagram DM
    """
    username = f"@{instagram_handle}"
    
    # Send to sales qualification system
    continue_conversation(username, message_text)
    
    # Get the AI response from state
    from main import graph
    config = {"configurable": {"thread_id": username}}
    state = graph.get_state(config)
    
    # Get last AI message
    messages = state.values.get("messages", [])
    ai_response = messages[-1].content if messages else "Hi!"
    
    # Send back to Instagram
    send_instagram_dm(instagram_handle, ai_response)
    
    return ai_response

# When user DMs you on Instagram:
handle_instagram_dm("sarah_coach", "Hi, I want to join")
```

### Example: WhatsApp Bot

```python
from main import continue_conversation

def handle_whatsapp_message(phone_number, message_text):
    """
    Handle incoming WhatsApp message
    """
    username = phone_number  # Use phone as ID
    
    # Process through sales system
    continue_conversation(username, message_text)
    
    # Get response and send back
    # ... (similar to Instagram example)
```

---

## 📝 Quick Reference

### Start New Conversation:
```python
start_new_conversation(username, initial_message)
```

### Continue Conversation:
```python
continue_conversation(username, message)
```

### Check Status:
```python
get_conversation_status(username)
```

### View History:
```python
view_conversation_history(username)
```

### Interactive Chat:
```bash
python chat.py
```

### Run Full Demo:
```bash
python main.py
```

---

## 🎯 Entry Points Summary

| Method | Command | Use Case |
|--------|---------|----------|
| **Interactive Chat** | `python chat.py` | Testing, demos, manual conversations |
| **Python Functions** | `from main import ...` | Building integrations (Instagram, WhatsApp) |
| **Full Demo** | `python main.py` | See all examples at once |

---

## 💡 Pro Tips

### 1. **Each Username = Separate Conversation**
```python
start_new_conversation("@user1", "Hi")  # Conversation 1
start_new_conversation("@user2", "Hi")  # Conversation 2 (separate)
```

### 2. **Conversations Never Expire**
- Close your terminal
- Restart your computer
- Come back weeks later
- **Conversation continues!**

### 3. **Check Before Sending**
```python
# Check if user already qualified
status = get_conversation_status("@user")
if status and status.get("qualification"):
    print("User already qualified!")
```

### 4. **Multi-Channel Same User**
```python
# User starts on Instagram
continue_conversation("@sarah", "Hi")  # Instagram

# Continues on WhatsApp (same username)
continue_conversation("@sarah", "Yes")  # WhatsApp

# Same conversation! ✅
```

---

## 🎉 You're Ready!

**Easiest way to start:**
```bash
python chat.py
```

**For integrations:**
```python
from main import continue_conversation
continue_conversation("@username", "message")
```

**That's it!** 🚀
