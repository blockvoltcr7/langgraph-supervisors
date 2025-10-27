# 🔄 Stateful Workflows with Persistence

A production-ready implementation of **persistent stateful workflows** using LangGraph's checkpointing system. This pattern enables long-running tasks, resume capability, and time-travel debugging.

## 🎯 What You'll Learn

This is the **most important pattern for production systems**:

**Workflows don't just run once—they persist, resume, and recover.**

### Key Concepts:

1. **Checkpointing** - Automatic state saving at every step
2. **Thread-based Persistence** - Each workflow has a unique thread ID
3. **Resume Capability** - Continue from where you left off
4. **Time Travel** - Go back to any previous checkpoint
5. **Multi-Session** - Work across days, weeks, or months

## 📐 Architecture

```
Day 1: Start Project
    ↓
┌─────────────────────────────────┐
│  Planning Stage                 │  ← Checkpoint 1
│  • Create project plan          │
│  • Break down tasks             │
└─────────────────────────────────┘
    ↓ [State saved to SQLite]
    
Day 2: Resume & Execute
    ↓
┌─────────────────────────────────┐
│  Execution Stage                │  ← Checkpoint 2
│  • Complete tasks 1-3           │
│  • Report progress              │
└─────────────────────────────────┘
    ↓ [State saved to SQLite]
    
Day 3: Resume & Execute More
    ↓
┌─────────────────────────────────┐
│  Execution Stage (continued)    │  ← Checkpoint 3
│  • Complete tasks 4-6           │
│  • Report progress              │
└─────────────────────────────────┘
    ↓ [State saved to SQLite]
    
Day 4: Resume & Finalize
    ↓
┌─────────────────────────────────┐
│  Review Stage                   │  ← Checkpoint 4
│  • Review all work              │
│  • Create final report          │
└─────────────────────────────────┘
    ↓ [State saved to SQLite]
    ✅ Complete!
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
uv sync
```

### 2. Set Up API Keys

```bash
cp .env.example .env
```

Edit `.env` and add:
```env
OPENAI_API_KEY=sk-your-key-here
```

### 3. Run Demo (Day 1)

```bash
source .venv/bin/activate
python main.py
```

**What happens:**
- Creates `project_checkpoints.db` (SQLite database)
- Runs planning → execution → review stages
- Saves state at each step
- Shows how to resume later

### 4. Resume Later (Day 2+)

```bash
python -c "from main import resume_project, create_project_workflow; resume_project(create_project_workflow(), 'project-1')"
```

**What happens:**
- Loads state from database
- Continues from last checkpoint
- No data loss!

## 💾 How Persistence Works

### The Checkpointer

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# Create checkpointer (persists to SQLite)
checkpointer = SqliteSaver.from_conn_string("project_checkpoints.db")

# Compile graph with checkpointer
graph = workflow.compile(checkpointer=checkpointer)
```

### Thread IDs

Each workflow instance has a unique thread ID:

```python
config = {"configurable": {"thread_id": "project-1"}}
graph.invoke(initial_state, config)
```

**Same thread ID = Same workflow instance**

### Automatic Checkpointing

State is saved automatically after every node:

```
Node 1 executes → Checkpoint saved
Node 2 executes → Checkpoint saved  
Node 3 executes → Checkpoint saved
...
```

## 🎯 Use Case: Multi-Day Project Management

### State Schema

```python
class ProjectState(TypedDict):
    # Project info
    project_name: str
    project_description: str
    
    # Stage completion flags (persisted!)
    planning_complete: bool
    execution_complete: bool
    review_complete: bool
    
    # Stage outputs (persisted!)
    project_plan: str
    execution_results: list[str]
    final_report: str
    
    # Workflow tracking
    current_stage: Literal["planning", "execution", "review", "complete"]
    completed_tasks: list[str]
    pending_tasks: list[str]
    
    # Metadata
    started_at: str
    last_updated: str
```

### Workflow Stages

**Stage 1: Planning**
```python
def planning_stage(state):
    # Create project plan
    # Break down into tasks
    return {
        "project_plan": plan,
        "pending_tasks": tasks,
        "planning_complete": True,
        "current_stage": "execution"
    }
```

**Stage 2: Execution** (can run multiple times)
```python
def execution_stage(state):
    # Complete 2-3 tasks
    # Update progress
    return {
        "completed_tasks": completed,
        "pending_tasks": remaining,
        "execution_complete": all_done,
        "current_stage": "review" if all_done else "execution"
    }
```

**Stage 3: Review**
```python
def review_stage(state):
    # Review all work
    # Create final report
    return {
        "final_report": report,
        "review_complete": True,
        "current_stage": "complete"
    }
```

## 🔍 Key Features

### 1. **Resume from Any Point** ✅

```python
# Day 1: Start project
start_new_project(graph, "AI Platform", description, "project-1")

# Day 2: Resume (continues from last checkpoint)
resume_project(graph, "project-1")

# Day 3: Resume again
resume_project(graph, "project-1")
```

### 2. **Time Travel** ⏰

```python
# Get all checkpoints
checkpoints = list(graph.get_state_history(config))

# Go back to checkpoint 2
old_state = checkpoints[2]
graph.update_state(config, old_state.values)
```

### 3. **Multi-Session Support** 🔄

```python
# Session 1 (Monday)
config = start_new_project(..., "project-1")
# State saved to DB

# Session 2 (Tuesday) - Different Python process!
config = {"configurable": {"thread_id": "project-1"}}
resume_project(graph, "project-1")
# Loads state from DB
```

### 4. **Crash Recovery** 💪

```python
# Process crashes during execution
# ...

# Restart and resume
resume_project(graph, "project-1")
# Continues from last successful checkpoint
```

### 5. **Parallel Workflows** 🚀

```python
# Multiple independent projects
start_new_project(..., "project-1")
start_new_project(..., "project-2") 
start_new_project(..., "project-3")

# Each has its own thread and state
```

## 📊 State Flow Example

### Initial State (Day 1)
```python
{
    "project_name": "AI Platform",
    "planning_complete": False,  # Not done yet
    "execution_complete": False,
    "review_complete": False,
    "current_stage": "planning",
    "pending_tasks": [],
    "completed_tasks": []
}
```

### After Planning (Day 1)
```python
{
    "project_name": "AI Platform",
    "planning_complete": True,  # ✅ Done!
    "execution_complete": False,
    "review_complete": False,
    "project_plan": "[detailed plan]",
    "current_stage": "execution",
    "pending_tasks": ["Task 1", "Task 2", "Task 3"],
    "completed_tasks": []
}
# ← Checkpoint saved to SQLite
```

### After First Execution (Day 2)
```python
{
    "project_name": "AI Platform",
    "planning_complete": True,
    "execution_complete": False,  # Still working
    "review_complete": False,
    "project_plan": "[detailed plan]",
    "current_stage": "execution",
    "pending_tasks": [],  # All done!
    "completed_tasks": ["Task 1", "Task 2", "Task 3"]
}
# ← Checkpoint saved to SQLite
```

### After Review (Day 3)
```python
{
    "project_name": "AI Platform",
    "planning_complete": True,
    "execution_complete": True,
    "review_complete": True,  # ✅ All done!
    "final_report": "[comprehensive report]",
    "current_stage": "complete"
}
# ← Final checkpoint saved to SQLite
```

## 🛠️ Production Patterns

### 1. **Database Persistence**

```python
# Development: SQLite
checkpointer = SqliteSaver.from_conn_string("checkpoints.db")

# Production: PostgreSQL
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:pass@localhost/db"
)
```

### 2. **Error Handling**

```python
def safe_execution_stage(state):
    try:
        result = execute_tasks(state)
        return result
    except Exception as e:
        # State is still saved!
        return {
            "error": str(e),
            "current_stage": "execution",  # Retry
            "last_error_at": datetime.now().isoformat()
        }
```

### 3. **Progress Tracking**

```python
def get_progress(graph, thread_id):
    state = graph.get_state({"configurable": {"thread_id": thread_id}})
    
    total_tasks = len(state.values["pending_tasks"]) + len(state.values["completed_tasks"])
    completed = len(state.values["completed_tasks"])
    
    return {
        "progress": f"{completed}/{total_tasks}",
        "percentage": (completed / total_tasks * 100) if total_tasks > 0 else 0,
        "current_stage": state.values["current_stage"]
    }
```

### 4. **Cleanup Old Checkpoints**

```python
import sqlite3
from datetime import datetime, timedelta

def cleanup_old_checkpoints(db_path, days=30):
    """Remove checkpoints older than N days"""
    cutoff = datetime.now() - timedelta(days=days)
    
    conn = sqlite3.connect(db_path)
    conn.execute(
        "DELETE FROM checkpoints WHERE created_at < ?",
        (cutoff.isoformat(),)
    )
    conn.commit()
    conn.close()
```

## 🎓 Learning Value

This pattern teaches:

1. **Checkpointing** - How LangGraph saves state automatically
2. **Thread Management** - Using thread IDs for workflow instances
3. **SQLite Integration** - Persistent storage with SqliteSaver
4. **Resume Logic** - Loading and continuing from checkpoints
5. **Time Travel** - Accessing historical states
6. **Production Patterns** - Error handling, cleanup, monitoring

## 🔍 Comparison with Previous Patterns

| Aspect | Flat Supervisor | Shared State | **Persistence** |
|--------|----------------|--------------|------------------|
| State | In-memory | In-memory | **Persisted to DB** |
| Resume | ❌ No | ❌ No | **✅ Yes** |
| Multi-session | ❌ No | ❌ No | **✅ Yes** |
| Crash recovery | ❌ No | ❌ No | **✅ Yes** |
| Time travel | ❌ No | ❌ No | **✅ Yes** |
| Best for | Simple tasks | Complex workflows | **Long-running tasks** |

## 💎 Why This Pattern is Critical

### Real-World Scenarios:

✅ **Multi-day projects** - Work spanning days or weeks
✅ **Human-in-the-loop** - Wait for human approval
✅ **External dependencies** - Wait for API responses
✅ **Batch processing** - Process thousands of items
✅ **Scheduled workflows** - Cron-like execution

### Without Persistence:
- ❌ Restart from scratch after crash
- ❌ Lose all progress
- ❌ Can't pause and resume
- ❌ No audit trail

### With Persistence:
- ✅ Resume from last checkpoint
- ✅ Never lose progress
- ✅ Pause and resume anytime
- ✅ Complete audit trail
- ✅ Time-travel debugging

## 🚀 Next Steps

### Extend the System:

1. **Add Human-in-the-Loop**
   ```python
   from langgraph.types import interrupt
   
   def approval_stage(state):
       # Pause for human approval
       response = interrupt({"question": "Approve?"})
       return {"approved": response}
   ```

2. **Add Scheduled Execution**
   ```python
   import schedule
   
   schedule.every().day.at("09:00").do(
       lambda: resume_project(graph, "daily-report")
   )
   ```

3. **Add Monitoring**
   ```python
   def monitor_workflows(db_path):
       # Query checkpoint database
       # Alert on stuck workflows
       # Track completion rates
   ```

4. **Add Parallel Execution**
   ```python
   from concurrent.futures import ThreadPoolExecutor
   
   with ThreadPoolExecutor() as executor:
       futures = [
           executor.submit(resume_project, graph, f"project-{i}")
           for i in range(10)
       ]
   ```

## 📚 Resources

- [LangGraph Persistence Docs](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [Checkpointers Reference](https://langchain-ai.github.io/langgraph/reference/checkpoints/)
- [SQLite Saver](https://langchain-ai.github.io/langgraph/reference/checkpoints/#sqlitesaver)
- [Time Travel Guide](https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/time-travel/)

---

**Built with LangGraph** 🦜🔗

**Pattern:** Stateful Workflows with Persistence
**Complexity:** Advanced
**Production-Ready:** ✅
**Critical for:** Long-running tasks, multi-session workflows, crash recovery