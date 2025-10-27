# 🚀 Quick Start Guide

## What This Demo Does

This is a **multi-day project management workflow** that demonstrates:

✅ **Checkpointing** - State saved automatically to SQLite  
✅ **Resume capability** - Continue from where you left off  
✅ **Time travel** - View all historical checkpoints  
✅ **Multi-session** - Work across different days/sessions  
✅ **Crash recovery** - Never lose progress  

## 📋 Prerequisites

- Python 3.12+
- OpenAI API key
- 5 minutes

## 🎯 Quick Demo (3 Steps)

### Step 1: Setup (30 seconds)

```bash
# Install dependencies
uv sync

# Configure API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Step 2: Run First Session (2 minutes)

```bash
source .venv/bin/activate
python main.py
```

**What happens:**
```
🚀 Starting new project: AI Agent Platform
📝 Thread ID: project-1

✓ PLANNING stage completed
  Next: execution

✓ EXECUTION stage completed  
  Next: execution

✓ EXECUTION stage completed
  Next: review

✓ REVIEW stage completed
  Next: complete

✅ Project workflow complete!
```

**Behind the scenes:**
- Creates `project_checkpoints.db` (SQLite database)
- Saves 6 checkpoints (one after each stage)
- All state persisted to disk

### Step 3: View History (30 seconds)

```bash
python -c "from main import get_project_history, create_project_workflow; get_project_history(create_project_workflow(), 'project-1')"
```

**Output:**
```
📜 Project History (Thread: project-1)

Checkpoint 1: Stage: complete
Checkpoint 2: Stage: review  
Checkpoint 3: Stage: execution
Checkpoint 4: Stage: execution
Checkpoint 5: Stage: planning
Checkpoint 6: Stage: unknown (initial)
```

## 🔄 Resume Capability Demo

### Scenario: Multi-Day Project

**Day 1: Start project**
```bash
python main.py
# Creates project, runs planning
# State saved to database
```

**Day 2: Resume (different session!)**
```bash
python -c "from main import resume_project, create_project_workflow; resume_project(create_project_workflow(), 'project-1')"
```

**What happens:**
- Loads state from database
- Continues from last checkpoint
- No data loss!

## 💡 Key Concepts Demonstrated

### 1. Automatic Checkpointing

```python
# Every node execution creates a checkpoint
Planning → Checkpoint 1 saved
Execution → Checkpoint 2 saved
Execution → Checkpoint 3 saved
Review → Checkpoint 4 saved
```

### 2. Thread-Based Persistence

```python
# Same thread_id = Same workflow instance
config = {"configurable": {"thread_id": "project-1"}}

# Different thread_id = Different workflow
config = {"configurable": {"thread_id": "project-2"}}
```

### 3. State Schema

```python
class ProjectState(TypedDict):
    # Completion flags (persisted!)
    planning_complete: bool
    execution_complete: bool
    review_complete: bool
    
    # Stage outputs (persisted!)
    project_plan: str
    execution_results: list[str]
    final_report: str
    
    # Workflow tracking
    current_stage: str
    completed_tasks: list[str]
    pending_tasks: list[str]
```

## 📊 What Gets Saved

### SQLite Database: `project_checkpoints.db`

**Size:** ~156 KB for one complete workflow

**Contents:**
- All state values at each checkpoint
- Message history
- Metadata (timestamps, config)
- Complete audit trail

**Tables:**
- `checkpoints` - State snapshots
- `writes` - Individual state updates

## 🎓 Learning Exercises

### Exercise 1: Multiple Projects

```bash
# Start 3 different projects
python -c "from main import start_new_project, create_project_workflow; \
  graph = create_project_workflow(); \
  start_new_project(graph, 'Project A', 'Build API', 'proj-a'); \
  start_new_project(graph, 'Project B', 'Build UI', 'proj-b'); \
  start_new_project(graph, 'Project C', 'Build DB', 'proj-c')"

# Each has independent state!
```

### Exercise 2: Crash Recovery

```bash
# Start a project
python main.py

# Simulate crash (Ctrl+C during execution)
# Then resume
python -c "from main import resume_project, create_project_workflow; \
  resume_project(create_project_workflow(), 'project-1')"

# Continues from last successful checkpoint!
```

### Exercise 3: Time Travel

```python
from main import create_project_workflow

graph = create_project_workflow()
config = {"configurable": {"thread_id": "project-1"}}

# Get all checkpoints
checkpoints = list(graph.get_state_history(config))

# Go back to checkpoint 3 (execution stage)
old_state = checkpoints[3]
print(f"Going back to: {old_state.values['current_stage']}")
print(f"Completed tasks: {old_state.values['completed_tasks']}")

# Can even update state to go back
graph.update_state(config, old_state.values)
```

## 🔍 Debugging Tips

### View Database Contents

```bash
sqlite3 project_checkpoints.db

# List all threads
SELECT DISTINCT thread_id FROM checkpoints;

# Count checkpoints per thread
SELECT thread_id, COUNT(*) FROM checkpoints GROUP BY thread_id;

# View latest checkpoint
SELECT * FROM checkpoints ORDER BY checkpoint_id DESC LIMIT 1;
```

### Check State

```python
from main import create_project_workflow

graph = create_project_workflow()
config = {"configurable": {"thread_id": "project-1"}}

# Get current state
state = graph.get_state(config)
print(f"Current stage: {state.values['current_stage']}")
print(f"Planning done: {state.values['planning_complete']}")
print(f"Execution done: {state.values['execution_complete']}")
print(f"Review done: {state.values['review_complete']}")
```

## 🚨 Common Issues

### Issue: "No project found"

**Cause:** Thread ID doesn't exist in database

**Solution:**
```bash
# List all threads
python -c "import sqlite3; \
  conn = sqlite3.connect('project_checkpoints.db'); \
  print(conn.execute('SELECT DISTINCT thread_id FROM checkpoints').fetchall())"
```

### Issue: Database locked

**Cause:** Multiple processes accessing database

**Solution:** Close other connections or use `check_same_thread=False`

## 📈 Production Patterns

### Pattern 1: Scheduled Workflows

```python
import schedule
from main import resume_project, create_project_workflow

def daily_task():
    graph = create_project_workflow()
    resume_project(graph, "daily-report")

schedule.every().day.at("09:00").do(daily_task)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Pattern 2: Progress Monitoring

```python
def get_progress(thread_id):
    graph = create_project_workflow()
    state = graph.get_state({"configurable": {"thread_id": thread_id}})
    
    total = len(state.values["pending_tasks"]) + len(state.values["completed_tasks"])
    done = len(state.values["completed_tasks"])
    
    return {
        "progress": f"{done}/{total}",
        "percentage": (done / total * 100) if total > 0 else 0,
        "stage": state.values["current_stage"]
    }
```

### Pattern 3: Error Recovery

```python
def safe_resume(thread_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            graph = create_project_workflow()
            resume_project(graph, thread_id)
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(5)
    return False
```

## 🎯 Next Steps

1. **Modify the workflow** - Add your own stages
2. **Add human-in-the-loop** - Pause for approvals
3. **Add parallel execution** - Run multiple tasks simultaneously
4. **Deploy to production** - Use PostgreSQL instead of SQLite

## 📚 Further Reading

- [Full README](README.md) - Complete documentation
- [LangGraph Persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [Checkpointers](https://langchain-ai.github.io/langgraph/reference/checkpoints/)

---

**You now understand stateful workflows with persistence!** 🎉

This is the foundation for building production-ready AI systems that:
- Never lose progress
- Can pause and resume
- Recover from crashes
- Work across multiple sessions
- Provide complete audit trails
