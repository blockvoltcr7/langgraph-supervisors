# ⚡ Quick Start - Sales Qualification with LangGraph + Supabase

**Get started in 3 steps!**

---

## 🚀 Run the Demo

### 1. Install Dependencies
```bash
uv sync
```

### 2. Run Main Demo
```bash
python main.py
```

This will run 3 example scenarios:
- ✅ Qualified user (gets Stripe link)
- ❌ Disqualified user (can't afford)
- 🔄 Multi-session conversation

### 3. Or Try Interactive Chat
```bash
python interactive_sales.py
```

Chat with the AI directly in your terminal!

---

## 📁 Key Files

- **`main.py`** - Sales qualification workflow (run this!)
- **`interactive_sales.py`** - Interactive CLI chat
- **`.env`** - Configuration (DATABASE_URL, OPENAI_API_KEY)

---

## 🎯 What It Does

```
User: "Hi, I'm interested"
  ↓
AI: "Can you afford $300?"
  ↓
User: "Yes"
  ↓
AI: "Here's your Stripe link!"
  ↓
[Saved to Supabase ✅]
```

---

## 💡 Multi-Session Magic

Run the script, exit, run again tomorrow - **conversation continues!**

```bash
# Day 1
python main.py
# Exit

# Day 3
python main.py
# Loads from Supabase - continues conversation!
```

---

## 🔧 Helper Scripts

```bash
# Check Supabase connection
python test_supabase_connection.py

# Create/verify tables
python check_and_create_tables.py

# Query database
python query_with_langgraph.py
```

---

## 📚 Learn More

- **README.md** - Full documentation
- **main.py** - Complete implementation with examples

---

**That's it! Run `python main.py` to see it in action!** 🎉
