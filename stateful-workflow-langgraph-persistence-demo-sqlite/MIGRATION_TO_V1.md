# Migration to LangGraph v1 / LangChain v1

This project has been upgraded to use **LangGraph v1** and **LangChain v1**.

## 🔄 Key Changes

### 1. Dependencies Updated

**Before (v0.x):**
```toml
"langgraph>=0.2.58"
"langgraph-checkpoint-sqlite>=2.0.0"
"langchain-openai>=0.3.0"
"langchain-core>=0.3.64"
"langgraph-cli[inmem]>=0.1.0"
```

**After (v1.x):**
```toml
"langgraph>=1.0.1"                       # LangGraph v1
"langgraph-checkpoint-sqlite>=2.0.0"     # SQLite persistence (unchanged)
"langchain>=1.0.0"                       # LangChain v1
"langchain-core>=1.0.0,<2.0.0"           # Core components
"langchain-openai>=1.0.1"                # OpenAI integration
"langgraph-cli[inmem]>=0.4.4"            # LangGraph Studio support
```

### 2. API Compatibility

**Good News**: This project was already using compatible APIs!

✅ **Already Compatible:**
- `StateGraph` from `langgraph.graph` (unchanged)
- `SqliteSaver` from `langgraph.checkpoint.sqlite` (unchanged)
- `ChatOpenAI` from `langchain_openai` (unchanged)
- `add_messages` from `langgraph.graph.message` (unchanged)

✅ **No Breaking Changes:**
- No `create_react_agent` usage
- No deprecated imports
- All persistence patterns work the same

⚠️ **One Fix Applied:**
- Fixed `create_project_workflow()` to handle config dict parameter from LangGraph Studio
- Added check for `isinstance(db_path, dict)` to use default database path

## 📦 Installation

```bash
# Install dependencies
uv sync

# Or with pip
pip install -e .
```

## ✅ What Works (Unchanged)

### 1. **Persistence Pattern**
```python
# SQLite checkpointer for state persistence
checkpointer = SqliteSaver.from_conn_string(":memory:")

# Compile with persistence
workflow = StateGraph(ProjectState)
# ... build graph ...
app = workflow.compile(checkpointer=checkpointer)
```

### 2. **State Management**
```python
class ProjectState(TypedDict):
    messages: Annotated[list, add_messages]
    project_name: str
    current_stage: Literal["planning", "execution", "review", "complete"]
    tasks: list[dict]
    completed_tasks: list[dict]
    review_notes: str
```

### 3. **Workflow Features**
- ✅ Checkpointing at every step
- ✅ Resume from any checkpoint
- ✅ Time-travel to previous states
- ✅ Cross-session persistence
- ✅ Interruption handling

## 🚀 Running the Demo

The demo works exactly the same after upgrade:

```bash
# Run the stateful workflow demo
python main.py

# Or use LangGraph Studio
uv run langgraph dev
```

## 🎨 LangGraph Studio

The project is configured for LangGraph Studio:

```bash
# Start the server
uv run langgraph dev

# Access Studio
https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

**Features in Studio:**
- Visual workflow representation
- Interactive testing with persistence
- State inspection at each checkpoint
- Resume workflows from Studio UI

## 🏗️ Architecture (Unchanged)

```
User Input
    ↓
Planning Node
    ↓ (checkpoint saved)
Execution Node (can loop multiple times)
    ↓ (checkpoint saved)
Review Node
    ↓ (checkpoint saved)
Complete
```

### Persistence Flow:
1. **Planning** → Save initial plan to SQLite
2. **Execution** → Save each task completion
3. **Review** → Save review notes
4. **Complete** → Final state saved

## 🎓 Benefits of v1

1. **Stability**: Production-ready APIs with long-term support
2. **Performance**: Optimized execution and checkpointing
3. **Compatibility**: Seamless integration with LangChain v1 ecosystem
4. **Enhanced Studio**: Better visualization and debugging
5. **Future-proof**: Built for long-term maintenance

## 📚 Key Features Demonstrated

### 1. **Multi-Session Workflows**
```python
# Start a project
thread_id = "project-1"
config = {"configurable": {"thread_id": thread_id}}

# Run some steps...
result = app.invoke(initial_state, config)

# Later, resume from where left off
resumed_result = app.invoke(None, config)
```

### 2. **Time Travel**
```python
# Get checkpoint history
history = list(app.get_state_history(config))

# Resume from an earlier checkpoint
earlier_state = history[3]
app.resume(earlier_state)
```

### 3. **Interruption Handling**
```python
# Interrupt before specific nodes
app = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["execution"]
)
```

## 🔧 Configuration

### Environment Variables (`.env`):
```bash
OPENAI_API_KEY=your_openai_key_here
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_key_here
LANGCHAIN_PROJECT=langgraph-supervisor-demo
```

### Database:
- **Default**: In-memory SQLite (`:memory:`)
- **Persistent**: File-based SQLite (`project_checkpoints.db`)
- **Custom**: Any SQLite connection string

## 📖 References

- [LangGraph v1 Release Notes](https://github.com/langchain-ai/langgraph/releases)
- [LangChain v1 Migration Guide](https://python.langchain.com/docs/versions/v1/)
- [Persistence Documentation](https://langchain-ai.github.io/langgraph/how-tos/persistence/)
- [Checkpointing Guide](https://langchain-ai.github.io/langgraph/how-tos/checkpoints/)

---

**Migration completed successfully!** ✅

*Note: This project was already well-structured and compatible, making the upgrade seamless.*
