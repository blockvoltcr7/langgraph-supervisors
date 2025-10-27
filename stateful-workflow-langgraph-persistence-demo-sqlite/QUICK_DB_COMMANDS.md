# ⚡ Quick Database Commands

Fastest ways to query the SQLite database.

## 🚀 One-Liners

### Command Line (SQLite)
```bash
# Open database
sqlite3 project_checkpoints.db

# Quick overview
sqlite3 project_checkpoints.db "SELECT thread_id, COUNT(*) FROM checkpoints GROUP BY thread_id;"

# Database size
sqlite3 project_checkpoints.db "SELECT COUNT(*) as checkpoints, (SELECT COUNT(*) FROM writes) as writes;"

# Largest checkpoints
sqlite3 project_checkpoints.db "SELECT substr(checkpoint_id, 1, 8) as id, LENGTH(checkpoint) as size FROM checkpoints ORDER BY size DESC LIMIT 5;"
```

### Python Scripts
```bash
# Simple overview
python simple_inspector.py

# Detailed state
python state_viewer.py

# Interactive exploration
python interactive_query.py

# Full inspection with LangGraph
python query_with_langgraph.py
```

## 📊 What You'll See

**Current Database:**
- 14 checkpoints
- 104 writes  
- 572 KB total size
- 1 project: "project-1"

**Project State:**
- Stage: complete ✅
- 10 tasks completed
- 12 messages exchanged
- Full project plan, execution results, and final report

## 🔍 Explore Further

Check out the full guide: **[DATABASE_QUERIES_GUIDE.md](./DATABASE_QUERIES_GUIDE.md)**

It includes:
- Step-by-step instructions
- SQL query examples
- Python scripts
- Interactive tools
- Data format explanations
