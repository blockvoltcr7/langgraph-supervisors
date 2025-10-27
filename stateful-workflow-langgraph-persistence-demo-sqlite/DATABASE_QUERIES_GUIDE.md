# 🔍 Database Queries Guide

Complete guide to connect to the SQLite database and run queries to inspect the stored state.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Method 1: Command Line SQLite](#method-1-command-line-sqlite)
3. [Method 2: Python Scripts](#method-2-python-scripts)
4. [Method 3: LangGraph API](#method-3-langgraph-api)
5. [Common Queries](#common-queries)
6. [Understanding the Data](#understanding-the-data)

---

## Quick Start

### The Easiest Way - Command Line:
```bash
# Open the database
sqlite3 project_checkpoints.db

# List tables
.tables

# View all projects
SELECT DISTINCT thread_id, COUNT(*) as checkpoints FROM checkpoints GROUP BY thread_id;

# Exit
.quit
```

### The Best Way - Python Script:
```bash
# Run the comprehensive query script
python query_with_langgraph.py
```

---

## Method 1: Command Line SQLite

### Connect to Database
```bash
cd /Users/samisabir-idrissi/dev/langgraph/supervisor-examples/stateful-workflow-langgraph-persistence-demo
sqlite3 project_checkpoints.db
```

### Basic Commands
```sql
-- List all tables
.tables

-- See table structure
.schema checkpoints
.schema writes

-- List all projects
SELECT DISTINCT thread_id, COUNT(*) as checkpoints 
FROM checkpoints 
GROUP BY thread_id;

-- View checkpoint sizes
SELECT checkpoint_id, length(checkpoint) as size_bytes 
FROM checkpoints 
WHERE thread_id = 'project-1' 
ORDER BY checkpoint_id;

-- Count total records
SELECT 
    (SELECT COUNT(*) FROM checkpoints) as total_checkpoints,
    (SELECT COUNT(*) FROM writes) as total_writes;
```

### Advanced Queries
```sql
-- View write channels (what gets updated)
SELECT DISTINCT channel, COUNT(*) as write_count 
FROM writes 
WHERE thread_id = 'project-1' 
GROUP BY channel 
ORDER BY write_count DESC;

-- Find largest checkpoints
SELECT checkpoint_id, length(checkpoint) as size 
FROM checkpoints 
ORDER BY size DESC 
LIMIT 5;

-- Timeline of checkpoints
SELECT 
    checkpoint_id,
    length(checkpoint) as size,
    substr(checkpoint_id, 1, 8) as short_id
FROM checkpoints 
WHERE thread_id = 'project-1' 
ORDER BY checkpoint_id;
```

---

## Method 2: Python Scripts

### Script 1: Simple Database Inspector
Create `simple_inspector.py`:

```python
#!/usr/bin/env python3
"""
Simple database inspector - no dependencies needed.
"""

import sqlite3
import json

def inspect_database():
    """Inspect the SQLite database."""
    conn = sqlite3.connect("project_checkpoints.db")
    cursor = conn.cursor()
    
    print("🔍 Database Inspector")
    print("=" * 40)
    
    # Basic stats
    cursor.execute("SELECT COUNT(*) FROM checkpoints")
    checkpoints = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM writes")
    writes = cursor.fetchone()[0]
    
    print(f"\n📊 Database Stats:")
    print(f"   Checkpoints: {checkpoints}")
    print(f"   Writes: {writes}")
    
    # Projects
    cursor.execute("""
        SELECT DISTINCT thread_id, COUNT(*) as count
        FROM checkpoints
        GROUP BY thread_id
    """)
    
    print(f"\n📁 Projects:")
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} checkpoints")
    
    # Checkpoint details
    cursor.execute("""
        SELECT checkpoint_id, length(checkpoint) as size
        FROM checkpoints
        WHERE thread_id = 'project-1'
        ORDER BY checkpoint_id
    """)
    
    print(f"\n📈 Checkpoint Sizes:")
    for i, row in enumerate(cursor.fetchall()):
        print(f"   {i+1:2d}. {row[0][:8]}...: {row[1]:6,} bytes")
    
    # Write channels
    cursor.execute("""
        SELECT channel, COUNT(*) as count
        FROM writes
        WHERE thread_id = 'project-1'
        GROUP BY channel
        ORDER BY count DESC
    """)
    
    print(f"\n📝 Write Channels:")
    for row in cursor.fetchall():
        print(f"   {row[0]:20s}: {row[1]:3d} writes")
    
    conn.close()

if __name__ == "__main__":
    inspect_database()
```

Run it:
```bash
python simple_inspector.py
```

### Script 2: Detailed State Viewer
Create `state_viewer.py`:

```python
#!/usr/bin/env python3
"""
View detailed state using LangGraph API.
"""

from main import create_project_workflow

def view_project_state(thread_id="project-1"):
    """View complete project state."""
    graph = create_project_workflow()
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"🎯 Project State: {thread_id}")
    print("=" * 50)
    
    # Get current state
    state = graph.get_state(config)
    
    if not state.values:
        print("❌ No state found for this project")
        return
    
    values = state.values
    
    print(f"\n📋 Project Info:")
    print(f"   Name: {values.get('project_name', 'N/A')}")
    print(f"   Description: {values.get('project_description', 'N/A')[:100]}...")
    
    print(f"\n🎯 Stage Status:")
    print(f"   Current Stage: {values.get('current_stage', 'unknown')}")
    print(f"   Planning Complete: {values.get('planning_complete', False)}")
    print(f"   Execution Complete: {values.get('execution_complete', False)}")
    print(f"   Review Complete: {values.get('review_complete', False)}")
    
    print(f"\n✅ Task Progress:")
    completed = values.get('completed_tasks', [])
    pending = values.get('pending_tasks', [])
    print(f"   Completed: {len(completed)} tasks")
    print(f"   Pending: {len(pending)} tasks")
    
    if completed:
        print(f"   Completed Tasks:")
        for i, task in enumerate(completed[:5]):
            print(f"     {i+1}. {task[:80]}...")
        if len(completed) > 5:
            print(f"     ... and {len(completed) - 5} more")
    
    if pending:
        print(f"   Pending Tasks:")
        for i, task in enumerate(pending[:5]):
            print(f"     {i+1}. {task[:80]}...")
        if len(pending) > 5:
            print(f"     ... and {len(pending) - 5} more")
    
    print(f"\n📝 Work Outputs:")
    if values.get('project_plan'):
        plan = values['project_plan']
        print(f"   Project Plan: {len(plan)} characters")
        print(f"   Preview: {plan[:150]}...")
    
    if values.get('execution_results'):
        results = values['execution_results']
        print(f"   Execution Results: {len(results)} items")
        for i, result in enumerate(results[:3]):
            print(f"     {i+1}. {result[:80]}...")
    
    if values.get('final_report'):
        report = values['final_report']
        print(f"   Final Report: {len(report)} characters")
        print(f"   Preview: {report[:150]}...")
    
    print(f"\n💬 Messages:")
    messages = values.get('messages', [])
    print(f"   Total Messages: {len(messages)}")
    for i, msg in enumerate(messages[:3]):
        msg_type = msg.__class__.__name__
        content = str(msg.content)[:100] if hasattr(msg, 'content') else str(msg)[:100]
        print(f"     {i+1}. [{msg_type}] {content}...")
    
    print(f"\n📊 Metadata:")
    print(f"   Started At: {values.get('started_at', 'N/A')}")
    print(f"   Last Updated: {values.get('last_updated', 'N/A')}")
    print(f"   Session Count: {values.get('session_count', 'N/A')}")

def view_project_history(thread_id="project-1"):
    """View project checkpoint history."""
    graph = create_project_workflow()
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"\n📜 Project History: {thread_id}")
    print("=" * 50)
    
    history = list(graph.get_state_history(config))
    
    for i, checkpoint in enumerate(history):
        values = checkpoint.values
        print(f"\nCheckpoint {i+1}:")
        print(f"   Stage: {values.get('current_stage', 'unknown')}")
        print(f"   Planning: {values.get('planning_complete', False)}")
        print(f"   Execution: {values.get('execution_complete', False)}")
        print(f"   Review: {values.get('review_complete', False)}")
        print(f"   Completed: {len(values.get('completed_tasks', []))}")
        print(f"   Pending: {len(values.get('pending_tasks', []))}")
        print(f"   Messages: {len(values.get('messages', []))}")

if __name__ == "__main__":
    view_project_state()
    view_project_history()
```

Run it:
```bash
python state_viewer.py
```

---

## Method 3: LangGraph API

### Direct Python Console
```python
# Open Python console
python

# Import and create graph
from main import create_project_workflow

# Create graph with persistence
graph = create_project_workflow()

# Configuration
config = {"configurable": {"thread_id": "project-1"}}

# Get current state
state = graph.get_state(config)
print(state.values["current_stage"])

# Get history
history = list(graph.get_state_history(config))
print(f"Total checkpoints: {len(history)}")

# View specific checkpoint
if history:
    latest = history[0]
    print(f"Latest stage: {latest.values['current_stage']}")
    print(f"Completed tasks: {len(latest.values['completed_tasks'])}")
```

### Interactive Query Script
Create `interactive_query.py`:

```python
#!/usr/bin/env python3
"""
Interactive database query tool.
"""

from main import create_project_workflow

def interactive_query():
    """Interactive query interface."""
    graph = create_project_workflow()
    
    print("🔍 Interactive Database Query")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. List projects")
        print("2. View project state")
        print("3. View project history")
        print("4. Time-travel to checkpoint")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            # List projects
            import sqlite3
            conn = sqlite3.connect("project_checkpoints.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT thread_id, COUNT(*) as count
                FROM checkpoints
                GROUP BY thread_id
            """)
            print("\nProjects:")
            for row in cursor.fetchall():
                print(f"  {row[0]}: {row[1]} checkpoints")
            conn.close()
        
        elif choice == "2":
            # View project state
            thread_id = input("Enter thread ID (default: project-1): ").strip() or "project-1"
            config = {"configurable": {"thread_id": thread_id}}
            
            state = graph.get_state(config)
            if state.values:
                print(f"\nCurrent Stage: {state.values['current_stage']}")
                print(f"Planning Complete: {state.values['planning_complete']}")
                print(f"Execution Complete: {state.values['execution_complete']}")
                print(f"Review Complete: {state.values['review_complete']}")
                print(f"Completed Tasks: {len(state.values['completed_tasks'])}")
                print(f"Pending Tasks: {len(state.values['pending_tasks'])}")
            else:
                print("No state found for this project")
        
        elif choice == "3":
            # View project history
            thread_id = input("Enter thread ID (default: project-1): ").strip() or "project-1"
            config = {"configurable": {"thread_id": thread_id}}
            
            history = list(graph.get_state_history(config))
            print(f"\nFound {len(history)} checkpoints:")
            
            for i, checkpoint in enumerate(history):
                values = checkpoint.values
                print(f"  {i+1}. Stage: {values['current_stage']}, "
                      f"Completed: {len(values['completed_tasks'])}")
        
        elif choice == "4":
            # Time-travel
            thread_id = input("Enter thread ID (default: project-1): ").strip() or "project-1"
            config = {"configurable": {"thread_id": thread_id}}
            
            history = list(graph.get_state_history(config))
            if not history:
                print("No checkpoints found")
                continue
            
            print(f"\nAvailable checkpoints: {len(history)}")
            checkpoint_num = input(f"Enter checkpoint number (1-{len(history)}): ").strip()
            
            try:
                idx = int(checkpoint_num) - 1
                if 0 <= idx < len(history):
                    old_checkpoint = history[idx]
                    graph.update_state(config, old_checkpoint.values)
                    print(f"✅ Time-traveled to checkpoint {checkpoint_num}")
                    print(f"   Stage: {old_checkpoint.values['current_stage']}")
                    print(f"   Completed Tasks: {len(old_checkpoint.values['completed_tasks'])}")
                else:
                    print("Invalid checkpoint number")
            except ValueError:
                print("Please enter a valid number")
        
        elif choice == "5":
            print("Goodbye! 👋")
            break
        
        else:
            print("Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    interactive_query()
```

Run it:
```bash
python interactive_query.py
```

---

## Common Queries

### SQL Queries (Command Line)

```sql
-- 1. Database overview
SELECT 
    (SELECT COUNT(*) FROM checkpoints) as checkpoints,
    (SELECT COUNT(*) FROM writes) as writes,
    (SELECT SUM(LENGTH(checkpoint)) FROM checkpoints) as total_bytes;

-- 2. All projects
SELECT thread_id, COUNT(*) as checkpoints 
FROM checkpoints 
GROUP BY thread_id;

-- 3. Project timeline
SELECT 
    ROW_NUMBER() OVER (ORDER BY checkpoint_id) as step,
    substr(checkpoint_id, 1, 8) as id,
    LENGTH(checkpoint) as size_bytes
FROM checkpoints 
WHERE thread_id = 'project-1';

-- 4. Most active channels
SELECT channel, COUNT(*) as writes 
FROM writes 
WHERE thread_id = 'project-1' 
GROUP BY channel 
ORDER BY writes DESC;

-- 5. Largest checkpoints
SELECT 
    substr(checkpoint_id, 1, 8) as id,
    LENGTH(checkpoint) as size_bytes
FROM checkpoints 
ORDER BY size_bytes DESC 
LIMIT 5;
```

### Python Queries

```python
# 1. Get all projects
import sqlite3
conn = sqlite3.connect("project_checkpoints.db")
cursor = conn.cursor()
cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
projects = [row[0] for row in cursor.fetchall()]
print("Projects:", projects)

# 2. Get checkpoint count for each project
cursor.execute("""
    SELECT thread_id, COUNT(*) as count 
    FROM checkpoints 
    GROUP BY thread_id
""")
for project, count in cursor.fetchall():
    print(f"{project}: {count} checkpoints")

# 3. Get latest state for a project
from main import create_project_workflow
graph = create_project_workflow()
config = {"configurable": {"thread_id": "project-1"}}
state = graph.get_state(config)
print("Current stage:", state.values["current_stage"])

# 4. Get project history
history = list(graph.get_state_history(config))
print(f"Total checkpoints: {len(history)}")
for i, checkpoint in enumerate(history[-5:]):  # Last 5
    print(f"{i+1}. Stage: {checkpoint.values['current_stage']}")
```

---

## Understanding the Data

### What You'll See

#### **Checkpoints Table**
- `thread_id`: Project identifier (e.g., "project-1")
- `checkpoint_id`: Unique ID for each state snapshot
- `checkpoint`: Complete state (binary format)
- `metadata`: Timestamp and version info

#### **Writes Table**
- `thread_id`: Project identifier
- `checkpoint_id`: Which checkpoint this write belongs to
- `channel`: What was updated (e.g., "messages", "current_stage")
- `value`: The new value (binary format)

#### **State Structure**
Each checkpoint contains:
```python
{
    "messages": [HumanMessage, AIMessage, ...],  # Conversation
    "project_name": "AI Agent Platform",         # Project info
    "project_description": "...",
    "planning_complete": True,                   # Stage flags
    "execution_complete": True,
    "review_complete": True,
    "project_plan": "...",                       # Work outputs
    "execution_results": [...],
    "final_report": "...",
    "current_stage": "complete",                 # Workflow state
    "completed_tasks": [...],
    "pending_tasks": [...],
    "started_at": "2025-10-27T00:14:24.562907", # Metadata
    "last_updated": "2025-10-27T00:15:31.961882",
    "session_count": 1
}
```

### What the Numbers Mean

- **14 checkpoints**: Project went through 14 state changes
- **104 writes**: Individual field updates across all checkpoints
- **572 KB database**: Total size of all stored data
- **63 KB largest checkpoint**: Final state with all data

---

## 🚀 Quick Start Commands

```bash
# 1. Quick overview (command line)
sqlite3 project_checkpoints.db "SELECT thread_id, COUNT(*) FROM checkpoints GROUP BY thread_id;"

# 2. Detailed view (Python)
python query_with_langgraph.py

# 3. Interactive exploration
python interactive_query.py

# 4. Simple stats
python simple_inspector.py

# 5. Current state only
python state_viewer.py
```

---

## 💡 Tips

1. **Use LangGraph API** for readable data (handles decompression)
2. **Use SQLite directly** for raw database stats
3. **Thread ID is key** - same ID = same project
4. **Checkpoints are immutable** - new ones only added
5. **Database grows** as project progresses
6. **Backup the .db file** - it contains everything!

---

## 🔧 Troubleshooting

### "no such table" error
```bash
# Check if database exists
ls -la project_checkpoints.db

# Check tables
sqlite3 project_checkpoints.db ".tables"
```

### "database is locked" error
```bash
# Make sure no other process is using it
lsof project_checkpoints.db

# Or copy and query the copy
cp project_checkpoints.db copy.db
sqlite3 copy.db
```

### Can't read checkpoint data
- Use the LangGraph API methods (they handle decompression)
- Don't try to read the binary blob directly with SQL

---

Happy querying! 🎉
