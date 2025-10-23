# 🚀 Quick Start Guide

## Step 1: Set Up Environment

### Option A: Automated Setup (Recommended)

```bash
./setup_env.sh
```

This will:
- Create `.env` from `.env.example`
- Prompt for your OpenAI API key
- Optionally configure LangSmith tracing

### Option B: Manual Setup

```bash
# Copy the example
cp .env.example .env

# Edit .env and add your keys
nano .env  # or use your preferred editor
```

Required in `.env`:
```env
OPENAI_API_KEY=sk-your-actual-key-here
```

Optional (for tracing):
```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your-langsmith-key
```

## Step 2: Activate Virtual Environment

```bash
source .venv/bin/activate
```

## Step 3: Run the Demo

```bash
python main.py
```

You should see:
```
✅ LangSmith tracing enabled (or disabled)
Using model: OpenAI GPT-4o-mini

================================================================================
HIERARCHICAL TEAMS PATTERN DEMO
================================================================================

Example 1: Communication Task
...
```

## Step 4: Use with Agent Chat UI

### Start the server:
```bash
langgraph dev
```

### Connect at:
**https://agentchat.vercel.app**

Fill in:
- **Deployment URL:** `http://localhost:2024`
- **Assistant / Graph ID:** `hierarchical`
- **LangSmith API Key:** (from your `.env`)

## 🧪 Test Queries

Try these in the Agent Chat UI:

### Simple Communication:
```
Send an email to john@example.com about the project update
```

### Simple Scheduling:
```
Schedule a team meeting for tomorrow at 2pm
```

### Cross-Team Coordination:
```
Schedule a design review for Tuesday at 3pm, book the main conference room, and send an email to the design team with a Slack notification in #design
```

## 🐛 Troubleshooting

### "OPENAI_API_KEY not found"

**Solution:**
1. Make sure `.env` file exists in the project directory
2. Check that `OPENAI_API_KEY=` has a valid key (starts with `sk-`)
3. Run `./setup_env.sh` to reconfigure

### "Invalid API key"

**Solution:**
1. Get a new API key from https://platform.openai.com/api-keys
2. Update `.env` file with the new key
3. Make sure there are no extra spaces or quotes around the key

### "Module not found"

**Solution:**
```bash
source .venv/bin/activate
uv sync
```

## 📚 Next Steps

- Read the full [README.md](README.md)
- View traces in [LangSmith](https://smith.langchain.com)
- Customize agents in `main.py`
- Add more teams and agents
