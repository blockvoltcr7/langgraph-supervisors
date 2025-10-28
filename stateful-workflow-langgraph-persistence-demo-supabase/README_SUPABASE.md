# 🚀 Stateful Workflow with Supabase Persistence

Production-ready stateful workflow demo using **Supabase (PostgreSQL)** instead of SQLite for cloud-based persistence.

## ✨ What's New

This project demonstrates the **same stateful workflow pattern** as the SQLite version, but with:

- ☁️ **Cloud Storage** - State saved to Supabase (PostgreSQL)
- 🌍 **Access Anywhere** - Resume workflows from any machine
- 👥 **Team Collaboration** - Multiple users can access same project
- 📊 **Advanced Monitoring** - Supabase Studio dashboard
- 🔒 **Production Ready** - Enterprise-grade database
- 📈 **Scalable** - Handle unlimited projects and checkpoints

---

## 🎯 Quick Start

### 1. Install Dependencies
```bash
uv sync
# Or: pip install -e .
```

### 2. Configure Environment

Edit `.env` file:
```bash
# OpenAI API Key
OPENAI_API_KEY=your_openai_key_here

# Supabase Database URL (PostgreSQL)
DATABASE_URL=postgresql+psycopg://user:password@host:port/database

# Optional: LangSmith Tracing
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_key_here
```

### 3. Test Connection
```bash
python test_supabase_connection.py
```

### 4. Run Demo
```bash
python main.py
```

---

## 📚 Documentation

- **[SUPABASE_QUICKSTART.md](./SUPABASE_QUICKSTART.md)** - Get started in 5 minutes
- **[SUPABASE_MIGRATION_GUIDE.md](./SUPABASE_MIGRATION_GUIDE.md)** - Complete migration guide from SQLite
- **[HOW_IT_WORKS.md](./HOW_IT_WORKS.md)** - Conceptual understanding
- **[PRACTICAL_EXAMPLES.md](./PRACTICAL_EXAMPLES.md)** - Code examples

---

## 🔑 Get Your Supabase URL

1. Go to https://supabase.com
2. Create a new project (free tier available)
3. Get connection string:
   - Project Settings → Database
   - Copy "Connection string" (URI format)
   - **Important**: Change `postgresql://` to `postgresql+psycopg://`

Example:
```
postgresql+psycopg://postgres.[PROJECT-REF]:[PASSWORD]@aws-1-us-east-2.pooler.supabase.com:5432/postgres
```

---

## 📊 View Your Data

### Option 1: Supabase Studio (Web UI)
1. Go to your Supabase project
2. Click **"Table Editor"**
3. View `checkpoints` and `checkpoint_writes` tables

### Option 2: Python Scripts
```bash
# Complete project state
python query_with_langgraph.py

# Quick database stats
python quick_queries_supabase.py
```

### Option 3: SQL Editor in Supabase
```sql
-- View all projects
SELECT DISTINCT thread_id, COUNT(*) 
FROM checkpoints 
GROUP BY thread_id;
```

---

## 🏗️ Architecture

### Database Tables

LangGraph's `PostgresSaver` automatically creates two tables:

#### **checkpoints**
- Complete state snapshots
- Saved after every node execution
- Contains: messages, tasks, outputs, metadata

#### **checkpoint_writes**
- Incremental updates
- Individual field changes
- Node outputs

### Data Flow

```
Your App → PostgresSaver → Supabase Database (Cloud)
                              ↓
                         Global Access
                        (Any machine/user)
```

---

## 💡 Use Cases

### 1. Multi-Day Projects
```python
# Day 1 - Start planning
result = graph.invoke(initial_state, {"configurable": {"thread_id": "project-1"}})

# Day 2 - Resume execution (from different machine!)
result = graph.invoke(None, {"configurable": {"thread_id": "project-1"}})
```

### 2. Team Collaboration
```python
# Team member A starts the project
config = {"configurable": {"thread_id": "team-project"}}
result = graph.invoke(initial_state, config)

# Team member B continues (different location!)
config = {"configurable": {"thread_id": "team-project"}}
state = graph.get_state(config)  # Gets same state!
```

### 3. Fault Tolerance
```python
try:
    result = graph.invoke(initial_state, config)
except Exception:
    # State is saved! Resume later
    result = graph.invoke(None, config)
```

---

## 🔍 What Changed from SQLite

| Aspect | SQLite Version | Supabase Version |
|--------|---------------|------------------|
| Storage | Local file | Cloud database |
| Persistence | `SqliteSaver` | `PostgresSaver` |
| Connection | File path | Connection string |
| Tables | Manual creation | Auto-created |
| Access | Single machine | Global |
| Backup | Manual file copy | Automatic |
| Monitoring | None | Supabase Studio |
| Production | ❌ No | ✅ Yes |

---

## 🛠️ Development Tools

### Test Connection
```bash
python test_supabase_connection.py
```

### Query Database
```bash
# Using LangGraph API (recommended)
python query_with_langgraph.py

# Using SQL
python quick_queries_supabase.py
```

### Run Demo
```bash
python main.py
```

---

## 🚨 Troubleshooting

### "DATABASE_URL not found"
- Check `.env` file exists
- Verify `DATABASE_URL` is set

### "Connection timeout"
- Check internet connection
- Verify Supabase project is active

### "Wrong format"
- Must use: `postgresql+psycopg://...`
- Not: `postgresql://...`

See [SUPABASE_MIGRATION_GUIDE.md](./SUPABASE_MIGRATION_GUIDE.md) for more troubleshooting.

---

## 📦 Dependencies

- `langgraph>=1.0.1` - LangGraph v1
- `langgraph-checkpoint-postgres>=2.0.3` - PostgreSQL checkpointer
- `psycopg>=3.1.0` - PostgreSQL adapter
- `langchain>=1.0.0` - LangChain v1
- `langchain-openai>=1.0.1` - OpenAI integration

---

## 🎓 Learn More

### Understanding the Pattern
1. Read [HOW_IT_WORKS.md](./HOW_IT_WORKS.md) - Understand checkpointing
2. Read [SUPABASE_MIGRATION_GUIDE.md](./SUPABASE_MIGRATION_GUIDE.md) - See what changed
3. Try [PRACTICAL_EXAMPLES.md](./PRACTICAL_EXAMPLES.md) - Run examples

### Supabase Resources
- **Supabase Docs**: https://supabase.com/docs
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **PostgresSaver API**: https://langchain-ai.github.io/langgraph/reference/checkpoints/

---

## 🎉 Benefits of Supabase

✅ **Free Tier** - Get started for free
✅ **No Setup** - Just a connection string
✅ **Auto Backups** - Daily backups included
✅ **Built-in Tools** - Query editor, monitoring
✅ **Scalable** - Grows with your app
✅ **Global Access** - Work from anywhere
✅ **Team Ready** - Multiple users supported
✅ **Production Grade** - Enterprise reliability

---

## 📝 Example Usage

```python
from main import create_project_workflow

# Create workflow with Supabase persistence
graph = create_project_workflow()

# Initial state
initial_state = {
    "project_name": "AI Agent Platform",
    "project_description": "Build a multi-agent system...",
    "current_stage": "start",
    "planning_complete": False,
    "execution_complete": False,
    "review_complete": False,
    # ... other fields
}

# Run workflow (state saved to Supabase)
config = {"configurable": {"thread_id": "my-project"}}
result = graph.invoke(initial_state, config)

# Resume later (from anywhere!)
result = graph.invoke(None, config)
```

---

## 🤝 Contributing

This is a demo project showcasing the migration from SQLite to Supabase for LangGraph persistence.

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph)
- Powered by [Supabase](https://supabase.com)
- Uses [LangChain](https://github.com/langchain-ai/langchain)

---

**Ready to build production-ready stateful workflows? Start with [SUPABASE_QUICKSTART.md](./SUPABASE_QUICKSTART.md)!** 🚀
