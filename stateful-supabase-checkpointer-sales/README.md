# 🚀 Sales Qualification with LangGraph + Supabase

**Direct Python Implementation** - No FastAPI, just LangGraph with Supabase persistence.

---

## 🎯 What This Is

A sales qualification workflow where:

1. **Qualifier Agent** asks if user can afford $300
2. **If qualified** → routes to Closer Agent
3. **Closer Agent** sends Stripe payment link
4. **All state persists in Supabase** - conversations survive restarts

### Key Feature: **Multi-Session Conversations**

Run the script today, close it, run it again tomorrow - **conversation continues from where you left off!**

---

## ⚡ Quick Start

### 1. Install Dependencies
```bash
uv sync
```

### 2. Configure `.env`
```bash
OPENAI_API_KEY=your_key_here
DATABASE_URL=postgresql+psycopg://user:password@host:port/database
```

### 3. Run the Demo
```bash
python sales_qualification.py
```

### 4. Or Use Interactive Chat
```bash
python interactive_sales.py
```

---

## 📊 Example Output

```
🚀 Starting new conversation for @sarah_coach
👤 User: Hi, I'm interested in your program
────────────────────────────────────────────────────────────────────────────────

🤖 AI (qualifier): Can you afford to invest $300 in this program?
📊 Stage: qualifying

────────────────────────────────────────────────────────────────────────────────
👤 User: Yes, I can afford $300

🤖 AI (qualifier): Excellent! You're qualified for our program...
📊 Stage: closing

🤖 AI (closer): 🎉 Perfect! Here's your payment link:
https://buy.stripe.com/test_@sarah_coach_300
📊 Stage: complete
```

---

## 🔄 Multi-Session Example

### Session 1 (Monday):
```bash
python sales_qualification.py
# Conversation starts
# State saved to Supabase ✅
# Exit program
```

### Session 2 (Wednesday):
```bash
python sales_qualification.py
# Loads state from Supabase ✅
# Continues from where you left off!
```

---

## 💡 Files

- **`sales_qualification.py`** - Main workflow with demo
- **`interactive_sales.py`** - Interactive CLI chat
- **`.env`** - Configuration (DATABASE_URL, OPENAI_API_KEY)

---

## 🎓 How It Works

### State Schema:
```python
class SalesState(TypedDict):
    messages: list              # Conversation history
    user_id: str                # @username
    qualification: bool         # Qualified?
    can_afford: bool            # Can afford $300?
    current_stage: str          # qualifying | closing | complete
    stripe_link_sent: bool      # Link sent?
    stripe_link: str            # Payment URL
```

### Workflow:
```
START → Qualifier Agent
           ↓
    (Can afford $300?)
           ↓
    Yes → Closer Agent → Stripe Link → END
           ↓
    No → Disqualified → END
```

### Persistence:
- Every step saves to Supabase
- Use `thread_id` (username) to resume
- Works across sessions, devices, days

---

## 🧪 Test Scenarios

The demo (`sales_qualification.py`) shows:

1. **Qualified User** - Gets Stripe link
2. **Disqualified User** - Can't afford $300
3. **Multi-Session** - Conversation over multiple days

---

## 🎯 Use Cases

### 1. **Instagram DM Bot**
```python
# When user DMs
user_id = f"@{instagram_handle}"
continue_conversation(user_id, dm_content)
```

### 2. **WhatsApp Bot**
```python
# When user messages
user_id = phone_number
continue_conversation(user_id, whatsapp_message)
```

### 3. **CLI Tool**
```bash
python interactive_sales.py
# Chat directly in terminal
```

---

## 🔧 Customization

### Change Qualification Amount:
```python
def qualifier_agent(state: SalesState):
    # Change from $300 to $500
    system_prompt = """Ask if they can afford $500"""
```

### Add More Agents:
```python
workflow.add_node("upsell", upsell_agent)
workflow.add_node("support", support_agent)
```

### Real Stripe Integration:
```python
import stripe

def closer_agent(state: SalesState):
    session = stripe.checkout.Session.create(...)
    return {"stripe_link": session.url}
```

---

## 📊 Database Tables

Supabase automatically creates:

- **`checkpoints`** - Complete state snapshots
- **`checkpoint_writes`** - Incremental updates

View in Supabase Studio: https://app.supabase.com

---

## 🎉 Summary

You now have:

✅ Sales qualification workflow  
✅ LangGraph with Qualifier + Closer agents  
✅ Supabase persistent state  
✅ Multi-session conversations  
✅ Interactive CLI  
✅ No FastAPI needed  

**Run `python sales_qualification.py` to see it in action!** 🚀
