# 🚀 Supabase Migration Guide

This guide explains how the stateful workflow demo has been migrated from SQLite to Supabase (PostgreSQL).

## 📋 Table of Contents

1. [What Changed](#what-changed)
2. [Why Supabase](#why-supabase)
3. [Setup Instructions](#setup-instructions)
4. [Database Schema](#database-schema)
5. [How It Works](#how-it-works)
6. [Querying Data](#querying-data)
7. [Key Differences](#key-differences)

---

## What Changed

### From SQLite to Supabase

```mermaid
graph LR
    A[SQLite<br/>Local File] -->|Migrated| B[Supabase<br/>Cloud PostgreSQL]
    
    C[SqliteSaver] -->|Replaced with| D[PostgresSaver]
    
    E[project_checkpoints.db] -->|Now stored in| F[Supabase Database]
    
    style A fill:#FFE4B5
    style B fill:#90EE90
    style C fill:#FFE4B5
    style D fill:#90EE90
    style E fill:#FFE4B5
    style F fill:#90EE90
```

### Code Changes

#### **1. Dependencies (pyproject.toml)**

**Before:**
```toml
dependencies = [
    "langgraph-checkpoint-sqlite>=2.0.0",
]
```

**After:**
```toml
dependencies = [
    "langgraph-checkpoint-postgres>=2.0.3",
    "psycopg>=3.1.0",
]
```

#### **2. Imports (main.py)**

**Before:**
```python
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
```

**After:**
```python
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
```

#### **3. Configuration**

**Before:**
```python
# SQLite - just a file path
db_path = "project_checkpoints.db"
conn = sqlite3.connect(db_path, check_same_thread=False)
checkpointer = SqliteSaver(conn)
```

**After:**
```python
# PostgreSQL - connection string from environment
DATABASE_URL = os.getenv("DATABASE_URL")
# Format: postgresql+psycopg://user:password@host:port/database

checkpointer = PostgresSaver.from_conn_string(
    DATABASE_URL,
    autocommit=True,
    prepare_threshold=0
)
```

---

## Why Supabase

### Benefits of Supabase over SQLite

| Feature | SQLite | Supabase |
|---------|--------|----------|
| **Storage** | Local file | Cloud database |
| **Scalability** | Single machine | Unlimited |
| **Concurrent Access** | Limited | Excellent |
| **Backup** | Manual | Automatic |
| **Multi-Machine** | ❌ No | ✅ Yes |
| **Production Ready** | ❌ No | ✅ Yes |
| **Collaboration** | ❌ No | ✅ Yes |
| **Query Tools** | Basic | Advanced (Supabase Studio) |
| **Cost** | Free | Free tier available |

### Use Cases

**Use SQLite when:**
- ✅ Development/prototyping
- ✅ Single-machine apps
- ✅ Offline-first apps
- ✅ Simple local storage

**Use Supabase when:**
- ✅ Production applications
- ✅ Multi-user systems
- ✅ Distributed systems
- ✅ Need real-time features
- ✅ Cloud-native apps
- ✅ Team collaboration

---

## Setup Instructions

### Step 1: Get Supabase Credentials

1. **Sign up for Supabase**: https://supabase.com
2. **Create a new project**
3. **Get your connection string**:
   - Go to Project Settings → Database
   - Copy the "Connection string" (with pooling)
   - Format: `postgresql://user:password@host:port/database`

### Step 2: Update .env File

Add the DATABASE_URL to your `.env` file:

```bash
# Supabase Database URL (PostgreSQL)
# Format: postgresql+psycopg://user:password@host:port/database
DATABASE_URL=postgresql+psycopg://postgres.[PROJECT-REF]:[PASSWORD]@aws-1-us-east-2.pooler.supabase.com:5432/postgres
```

**Important**: Change the prefix from `postgresql://` to `postgresql+psycopg://` for psycopg3.

### Step 3: Install Dependencies

```bash
# Install updated dependencies
uv sync

# Or with pip
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
# The PostgresSaver will automatically create tables on first run
python main.py
```

That's it! The application will:
1. Connect to Supabase
2. Create the checkpoint tables (if they don't exist)
3. Start saving state to the cloud database

---

## Database Schema

### Tables Created by PostgresSaver

The `PostgresSaver` automatically creates two tables in your Supabase database:

#### **1. checkpoints Table**

Stores complete state snapshots:

```sql
CREATE TABLE checkpoints (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    checkpoint_id TEXT NOT NULL,
    parent_checkpoint_id TEXT,
    type TEXT,
    checkpoint BYTEA,           -- Binary state data
    metadata BYTEA,             -- Timestamp, version info
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
);

CREATE INDEX idx_checkpoints_thread_id ON checkpoints(thread_id);
```

#### **2. checkpoint_writes Table**

Stores incremental updates:

```sql
CREATE TABLE checkpoint_writes (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    checkpoint_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    idx INTEGER NOT NULL,
    channel TEXT NOT NULL,      -- Node/field name
    type TEXT,
    value BYTEA,               -- Update value
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx)
);

CREATE INDEX idx_checkpoint_writes_thread_id ON checkpoint_writes(thread_id);
```

### Viewing Tables in Supabase Studio

1. Go to your Supabase project
2. Click "Table Editor" in the left sidebar
3. You'll see:
   - `checkpoints` table
   - `checkpoint_writes` table

---

## How It Works

### Data Flow with Supabase

```mermaid
sequenceDiagram
    participant App as Your App
    participant PG as PostgresSaver
    participant SB as Supabase Database
    
    Note over App,SB: Workflow Execution
    
    App->>PG: execute node (state)
    PG->>PG: Serialize state
    PG->>SB: INSERT INTO checkpoints
    PG->>SB: INSERT INTO checkpoint_writes
    SB-->>PG: Success
    PG-->>App: Continue
    
    Note over App,SB: Resume Later
    
    App->>PG: get_state(thread_id)
    PG->>SB: SELECT FROM checkpoints
    SB-->>PG: Latest checkpoint
    PG->>PG: Deserialize state
    PG-->>App: Return state
    App->>App: Continue from there
```

### Connection Pooling

Supabase uses **connection pooling** for better performance:

```python
# PostgresSaver uses a connection pool internally
checkpointer = PostgresSaver.from_conn_string(
    DATABASE_URL,
    autocommit=True,        # Commit after each operation
    prepare_threshold=0      # Disable prepared statements (better for pooling)
)
```

### Automatic Table Creation

Unlike SQLite where you had to create the database file, PostgresSaver **automatically creates tables** on first use:

```python
# No need to manually create tables!
checkpointer = PostgresSaver.from_conn_string(DATABASE_URL)

# Tables are created automatically when you first save a checkpoint
graph = workflow.compile(checkpointer=checkpointer)
result = graph.invoke(initial_state, config)  # ✅ Tables created here if needed
```

---

## Querying Data

### Option 1: Supabase Studio (Web UI)

1. Go to your Supabase project
2. Click "Table Editor"
3. Select `checkpoints` or `checkpoint_writes`
4. View, filter, and query your data visually

### Option 2: Python with psycopg

```python
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Connect to database
with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        # List all projects
        cur.execute("""
            SELECT DISTINCT thread_id, COUNT(*) as checkpoint_count
            FROM checkpoints
            GROUP BY thread_id
        """)
        
        for row in cur.fetchall():
            print(f"Project: {row[0]}, Checkpoints: {row[1]}")
```

### Option 3: LangGraph API (Recommended)

```python
from main import create_project_workflow

# Create graph with Supabase persistence
graph = create_project_workflow()

# Get current state
config = {"configurable": {"thread_id": "project-1"}}
state = graph.get_state(config)

print(f"Current stage: {state.values['current_stage']}")
print(f"Completed tasks: {len(state.values['completed_tasks'])}")

# Get history
history = list(graph.get_state_history(config))
print(f"Total checkpoints: {len(history)}")
```

### Option 4: SQL Queries in Supabase

Go to SQL Editor in Supabase and run queries:

```sql
-- View all projects
SELECT DISTINCT thread_id, COUNT(*) as checkpoints
FROM checkpoints
GROUP BY thread_id;

-- View checkpoint sizes
SELECT 
    thread_id,
    checkpoint_id,
    LENGTH(checkpoint) as size_bytes,
    metadata
FROM checkpoints
ORDER BY size_bytes DESC
LIMIT 10;

-- View recent activity
SELECT 
    thread_id,
    checkpoint_id,
    created_at
FROM checkpoints
ORDER BY created_at DESC
LIMIT 20;

-- View write channels
SELECT 
    channel,
    COUNT(*) as write_count
FROM checkpoint_writes
WHERE thread_id = 'project-1'
GROUP BY channel
ORDER BY write_count DESC;
```

---

## Key Differences

### 1. Storage Location

**SQLite:**
```
📁 project_checkpoints.db  (local file, ~500 KB)
```

**Supabase:**
```
☁️ Supabase Cloud Database (accessible from anywhere)
```

### 2. Connection String

**SQLite:**
```python
db_path = "project_checkpoints.db"
```

**Supabase:**
```python
DATABASE_URL = "postgresql+psycopg://user:password@host:port/database"
```

### 3. Concurrent Access

**SQLite:**
- ⚠️ Limited concurrent writes
- ⚠️ Database locked during writes
- ⚠️ Not suitable for multiple processes

**Supabase:**
- ✅ Unlimited concurrent reads
- ✅ Excellent concurrent write performance
- ✅ Perfect for distributed systems

### 4. Backup & Recovery

**SQLite:**
- Manual file backups
- Copy `.db` file

**Supabase:**
- Automatic daily backups
- Point-in-time recovery
- One-click restore

### 5. Monitoring

**SQLite:**
- No built-in monitoring
- Need external tools

**Supabase:**
- Built-in monitoring dashboard
- Query performance analytics
- Real-time connection monitoring
- Usage metrics

---

## Migration Checklist

- [x] Update `pyproject.toml` dependencies
- [x] Replace `SqliteSaver` with `PostgresSaver`
- [x] Add `DATABASE_URL` to `.env`
- [x] Update imports
- [x] Test connection
- [ ] Update query scripts (if any)
- [ ] Update documentation
- [ ] Deploy to production

---

## Troubleshooting

### Connection Timeout

**Problem:** `Connection terminated due to connection timeout`

**Solution:**
- Check your internet connection
- Verify Supabase project is active
- Check connection string format (must include `postgresql+psycopg://`)

### Table Already Exists

**Problem:** `relation "checkpoints" already exists`

**Solution:**
- This is normal! The tables were created on first run
- You can safely ignore this warning

### SSL Required

**Problem:** `SSL connection required`

**Solution:**
Add `?sslmode=require` to your DATABASE_URL:
```
DATABASE_URL=postgresql+psycopg://...?sslmode=require
```

---

## 🎯 Summary

### What You Get with Supabase

✅ **Cloud Storage** - Access from anywhere
✅ **Automatic Backups** - Never lose data
✅ **Scalability** - Handle any load
✅ **Collaboration** - Multiple users/machines
✅ **Real-time Features** - Subscriptions, webhooks
✅ **Built-in Tools** - Query editor, monitoring
✅ **Production Ready** - Enterprise-grade reliability

### Migration is Complete!

Your stateful workflow now uses:
- ☁️ Supabase PostgreSQL database
- 🔄 Cloud-based persistence
- 📊 Advanced monitoring
- 🚀 Production-ready infrastructure

Run `python main.py` and your checkpoints will be saved to Supabase! 🎉
