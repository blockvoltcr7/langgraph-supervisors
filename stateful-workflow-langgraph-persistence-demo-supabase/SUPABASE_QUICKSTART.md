# ⚡ Supabase Quick Start

Get up and running with the Supabase-powered stateful workflow in 5 minutes!

## 🚀 Quick Setup

### 1. Clone/Navigate to Project
```bash
cd /Users/samisabir-idrissi/dev/langgraph/supervisor-examples/stateful-workflow-langgraph-persistence-demo-supabase
```

### 2. Set Up Environment
```bash
# Copy example env file (if it exists)
cp .env.example .env

# Or create .env file with these variables:
cat > .env << 'EOF'
# OpenAI API Key
OPENAI_API_KEY=your_openai_key_here

# Supabase Database URL
DATABASE_URL=postgresql+psycopg://user:password@host:port/database

# Optional: LangSmith Tracing
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_key_here
LANGCHAIN_PROJECT=stateful-workflow-supabase
EOF
```

### 3. Install Dependencies
```bash
# With uv (recommended)
uv sync

# Or with pip
pip install -e .
```

### 4. Run the Demo!
```bash
python main.py
```

That's it! The application will:
1. ✅ Connect to Supabase
2. ✅ Create tables automatically (first run only)
3. ✅ Save checkpoints to the cloud
4. ✅ Show you the workflow in action

---

## 🔑 Getting Your Supabase Database URL

### Step-by-Step:

1. **Go to Supabase**: https://supabase.com
2. **Sign up** (free tier available)
3. **Create a new project**
   - Choose a name
   - Set a database password
   - Select a region (choose closest to you)
4. **Get your connection string**:
   - Click on your project
   - Go to **Project Settings** (gear icon)
   - Go to **Database** section
   - Find "Connection string"
   - Select **"URI"** tab
   - Copy the connection string
   - Replace `[YOUR-PASSWORD]` with your actual password

### Format the URL for psycopg3:

**Supabase gives you:**
```
postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres
```

**Change it to (add `+psycopg` after `postgresql`):**
```
postgresql+psycopg://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres
```

**For pooled connections (recommended for production):**
```
postgresql+psycopg://postgres.[PROJECT-REF]:[PASSWORD]@aws-1-us-east-2.pooler.supabase.com:5432/postgres
```

### Example:
```bash
# In your .env file
DATABASE_URL=postgresql+psycopg://postgres.abcdefghijk:MySecretPassword123@aws-1-us-east-2.pooler.supabase.com:5432/postgres
```

---

## 📊 View Your Data

### Option 1: Supabase Studio (Web UI)

1. Go to your Supabase project dashboard
2. Click **"Table Editor"** in the left sidebar
3. You'll see:
   - `checkpoints` - Complete state snapshots
   - `checkpoint_writes` - Incremental updates

Click on any table to browse the data!

### Option 2: Python Script

```bash
# View project state
python query_with_langgraph.py

# Quick database stats
python quick_queries_supabase.py
```

### Option 3: SQL Editor in Supabase

1. Go to **"SQL Editor"** in Supabase
2. Run queries:

```sql
-- See all projects
SELECT DISTINCT thread_id, COUNT(*) 
FROM checkpoints 
GROUP BY thread_id;

-- View latest checkpoints
SELECT * FROM checkpoints 
ORDER BY checkpoint_id DESC 
LIMIT 10;
```

---

## 🔍 What Gets Stored?

### In `checkpoints` Table:
- Complete project state at each step
- All messages (conversation history)
- Task lists (completed & pending)
- Work outputs (plans, results, reports)
- Metadata (timestamps, session info)

### In `checkpoint_writes` Table:
- Individual field updates
- Node outputs
- Incremental changes

---

## 💡 Common Use Cases

### 1. Resume After Days/Weeks

```python
from main import create_project_workflow

graph = create_project_workflow()
config = {"configurable": {"thread_id": "my-project"}}

# Day 1: Start project
result1 = graph.invoke(initial_state, config)

# Day 2: Resume (anywhere in the world!)
result2 = graph.invoke(None, config)  # Auto-resumes!
```

### 2. Multiple Projects

```python
# Project 1
config1 = {"configurable": {"thread_id": "project-alpha"}}
result1 = graph.invoke(state1, config1)

# Project 2
config2 = {"configurable": {"thread_id": "project-beta"}}
result2 = graph.invoke(state2, config2)

# Each project has its own state in the cloud!
```

### 3. Team Collaboration

```python
# Team member 1 (Machine A)
graph = create_project_workflow()
config = {"configurable": {"thread_id": "team-project"}}
result = graph.invoke(initial_state, config)

# Team member 2 (Machine B) - different location!
graph = create_project_workflow()  # Same DATABASE_URL in .env
config = {"configurable": {"thread_id": "team-project"}}
state = graph.get_state(config)  # Gets the same state!
```

---

## 🛠️ Testing the Connection

Create `test_supabase_connection.py`:

```python
#!/usr/bin/env python3
"""Test Supabase connection."""

import os
from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("🔍 Testing Supabase Connection...")
print(f"URL: {DATABASE_URL[:30]}...")

try:
    # Try to create checkpointer
    checkpointer = PostgresSaver.from_conn_string(
        DATABASE_URL,
        autocommit=True,
        prepare_threshold=0
    )
    
    print("✅ Connection successful!")
    print("✅ PostgresSaver created")
    print("✅ Tables will be created on first use")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Check DATABASE_URL format: postgresql+psycopg://...")
    print("2. Verify Supabase project is active")
    print("3. Check username/password are correct")
    print("4. Try with pooler URL: ...pooler.supabase.com...")
```

Run it:
```bash
python test_supabase_connection.py
```

---

## 📚 Next Steps

1. ✅ **Read the full guide**: `SUPABASE_MIGRATION_GUIDE.md`
2. ✅ **Understand the concepts**: `HOW_IT_WORKS.md`
3. ✅ **Learn to query**: `DATABASE_QUERIES_GUIDE.md`
4. ✅ **See examples**: `PRACTICAL_EXAMPLES.md`

---

## 🆘 Troubleshooting

### "ValueError: DATABASE_URL not found"
- Make sure `.env` file exists
- Check `DATABASE_URL` is set in `.env`
- Run `python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('DATABASE_URL'))"`

### "Connection timeout"
- Check internet connection
- Verify Supabase project is active (not paused)
- Try using the pooler URL: `...pooler.supabase.com...`

### "SSL connection required"
- Add `?sslmode=require` to end of DATABASE_URL

### "Wrong password"
- Double-check password in Supabase project settings
- Make sure you replaced `[YOUR-PASSWORD]` with actual password

---

## 🎉 You're Ready!

Your stateful workflow is now powered by Supabase!

Benefits:
- ☁️ **Cloud storage** - Access from anywhere
- 🔄 **Automatic backups** - Never lose data
- 👥 **Team collaboration** - Multiple users
- 📈 **Scalable** - Handle any load
- 🔒 **Secure** - Enterprise-grade security

Happy coding! 🚀
