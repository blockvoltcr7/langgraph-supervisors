# 🚀 Stateful Workflows with Supabase Persistence

Production-ready stateful workflow demo using **Supabase (PostgreSQL)** for cloud-based persistence with LangGraph v1.

---

## ✨ What This Is

A complete example of **long-running, persistent workflows** that:

- ☁️ **Save state to Supabase** (cloud PostgreSQL database)
- 🌍 **Resume from anywhere** (any machine, any time)
- 👥 **Support collaboration** (multiple users, same project)
- 🔄 **Handle interruptions** (crash recovery, pause/resume)
- ⏮️ **Enable time-travel** (go back to any checkpoint)
- 📊 **Production-ready** (enterprise-grade infrastructure)

---

## 🎯 Use Case: Multi-Day Project Workflow

```
Day 1: Planning
  ↓ [State saved to Supabase]
  
Day 2: Execution (from different machine!)
  ↓ [State saved to Supabase]
  
Day 3: Review & Complete
  ↓ [State saved to Supabase]
```

Each step is saved to the cloud. Resume anytime, anywhere!

---

## ⚡ Quick Start

### 1. Install Dependencies
```bash
uv sync
# Or: pip install -e .
```

### 2. Configure Environment

Create/edit `.env`:
```bash
# OpenAI API Key
OPENAI_API_KEY=your_openai_key_here

# Supabase Database URL (PostgreSQL)
DATABASE_URL=postgresql+psycopg://user:password@host:port/database

# Optional: LangSmith Tracing
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_key_here
```

### 3. Create Database Tables
```bash
python check_and_create_tables.py
```

### 4. Run Demo
```bash
python main.py
```

---

## 📚 Complete Documentation

### **Start Here** 👇
- **[SUPABASE_QUICKSTART.md](./SUPABASE_QUICKSTART.md)** - Get started in 5 minutes

### **Learn More**
- **[SUPABASE_MIGRATION_GUIDE.md](./SUPABASE_MIGRATION_GUIDE.md)** - Complete guide with diagrams
- **[HOW_IT_WORKS.md](./HOW_IT_WORKS.md)** - Understand the concepts
- **[PRACTICAL_EXAMPLES.md](./PRACTICAL_EXAMPLES.md)** - Code examples

### **Reference**
- **[MIGRATION_COMPLETE.md](./MIGRATION_COMPLETE.md)** - What changed from SQLite
- **[SUMMARY.md](./SUMMARY.md)** - Quick reference

---

## 🔑 Get Your Supabase URL

1. Go to https://supabase.com (free tier available)
2. Create a new project
3. Get connection string:
   - Project Settings → Database
   - Copy "Connection string" (URI)
   - **Change** `postgresql://` to `postgresql+psycopg://`

Example:
```
postgresql+psycopg://postgres.[PROJECT-REF]:[PASSWORD]@aws-1-us-east-2.pooler.supabase.com:5432/postgres
```

---

## 📊 View Your Data

### Option 1: Supabase Studio (Web UI)
1. Go to https://app.supabase.com
2. Select your project
3. Click **"Table Editor"**
4. Browse `checkpoints` and `checkpoint_writes` tables

### Option 2: Python Scripts
```bash
# Complete project state
python query_with_langgraph.py

# Quick database stats
python quick_queries_supabase.py
```

### Option 3: Test Connection
```bash
python test_supabase_connection.py
```

---

## 🏗️ Architecture

### Database Tables (Auto-Created)

**`checkpoints`** - Complete state snapshots
- Saved after every node execution
- Contains: messages, tasks, outputs, metadata

**`checkpoint_writes`** - Incremental updates
- Individual field changes
- Node outputs

### Data Flow

```
Your App → PostgresSaver → Supabase (Cloud)
                              ↓
                         Global Access
                        (Any machine/user)
```

---

## 💡 Example Usage

```python
from main import create_project_workflow

# Create workflow with Supabase persistence
graph = create_project_workflow()

# Initial state
initial_state = {
    "project_name": "AI Agent Platform",
    "project_description": "Build a multi-agent system...",
    "current_stage": "start",
    # ... other fields
}

# Run workflow (state saved to Supabase)
config = {"configurable": {"thread_id": "my-project"}}
result = graph.invoke(initial_state, config)

# Resume later (from anywhere!)
result = graph.invoke(None, config)
```

---

## 🎓 Key Features

### 1. **Multi-Day Workflows**
Work on projects over days or weeks. State persists in the cloud.

### 2. **Team Collaboration**
Multiple team members can access the same project from different machines.

### 3. **Fault Tolerance**
If your app crashes, resume from the last checkpoint.

### 4. **Time Travel**
Go back to any previous state for debugging or changes.

### 5. **Production Ready**
Built on enterprise-grade Supabase infrastructure.

---

## 🛠️ Development Tools

### Check Tables
```bash
python check_and_create_tables.py
```

### Test Connection
```bash
python test_supabase_connection.py
```

### Query Database
```bash
python query_with_langgraph.py
python quick_queries_supabase.py
```

---

## 📦 Tech Stack

- **LangGraph v1** - Stateful workflow orchestration
- **Supabase** - Cloud PostgreSQL database
- **PostgresSaver** - LangGraph's PostgreSQL checkpointer
- **LangChain v1** - AI framework
- **OpenAI GPT-4o-mini** - Language model

---

## 🎯 Why Supabase?

| Feature | Benefit |
|---------|---------|
| ☁️ **Cloud Storage** | Access from anywhere |
| 📈 **Scalable** | Grows with your app |
| 💾 **Auto Backups** | Never lose data |
| 🔒 **Secure** | Enterprise-grade security |
| 👥 **Multi-User** | Team collaboration |
| 📊 **Monitoring** | Built-in dashboard |
| 🆓 **Free Tier** | Get started for free |

---

## 🚨 Troubleshooting

### "DATABASE_URL not found"
- Check `.env` file exists
- Verify `DATABASE_URL` is set

### "Connection timeout"
- Check internet connection
- Verify Supabase project is active

### "Tables don't exist"
- Run: `python check_and_create_tables.py`

See [SUPABASE_MIGRATION_GUIDE.md](./SUPABASE_MIGRATION_GUIDE.md) for more help.

---

## 📖 Learn the Pattern

### 1. **Quick Start** (5 minutes)
Read: [SUPABASE_QUICKSTART.md](./SUPABASE_QUICKSTART.md)

### 2. **Understand Concepts**
Read: [HOW_IT_WORKS.md](./HOW_IT_WORKS.md)

### 3. **See Examples**
Read: [PRACTICAL_EXAMPLES.md](./PRACTICAL_EXAMPLES.md)

### 4. **Deep Dive**
Read: [SUPABASE_MIGRATION_GUIDE.md](./SUPABASE_MIGRATION_GUIDE.md)

---

## 🎉 Benefits

### Before (No Persistence)
- ❌ Lose state on crash
- ❌ Can't pause/resume
- ❌ No audit trail
- ❌ Single session only

### After (Supabase Persistence)
- ✅ Crash recovery
- ✅ Pause/resume anytime
- ✅ Complete history
- ✅ Multi-session workflows
- ✅ Team collaboration
- ✅ Production-ready

---

## 📝 Project Structure

```
stateful-workflow-langgraph-persistence-demo-supabase/
├── main.py                          # Main workflow (Supabase)
├── pyproject.toml                   # Dependencies
├── .env                             # Configuration
│
├── README.md                        # This file
├── SUPABASE_QUICKSTART.md           # 5-minute setup
├── SUPABASE_MIGRATION_GUIDE.md      # Complete guide
├── HOW_IT_WORKS.md                  # Concepts
├── PRACTICAL_EXAMPLES.md            # Examples
│
├── test_supabase_connection.py      # Test connection
├── check_and_create_tables.py       # Setup tables
├── query_with_langgraph.py          # Query tool
└── quick_queries_supabase.py        # Quick queries
```

---

## 🤝 Contributing

This is a demo project showcasing Supabase persistence with LangGraph.

---

## 📄 License

MIT License

---

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph)
- Powered by [Supabase](https://supabase.com)
- Uses [LangChain](https://github.com/langchain-ai/langchain)

---

## 🚀 Get Started Now!

1. **Read**: [SUPABASE_QUICKSTART.md](./SUPABASE_QUICKSTART.md)
2. **Setup**: Get your Supabase URL
3. **Run**: `python main.py`
4. **Build**: Amazing stateful workflows!

**Your journey to production-ready workflows starts here!** 🎊
