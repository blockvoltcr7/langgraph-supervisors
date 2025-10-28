# Migration to LangGraph v1 / LangChain v1

This project has been upgraded to use **LangGraph v1** and **LangChain v1**.

## 🔄 Key Changes

### 1. Dependencies Updated

**Before (v0.x):**
```toml
"langgraph>=0.2.58"
"langchain-openai>=0.3.0"
"langchain-core>=0.3.64"
"langgraph-cli[inmem]>=0.1.0"
```

**After (v1.x):**
```toml
"langgraph>=1.0.1"                       # LangGraph v1
"langchain>=1.0.0"                       # LangChain v1 with create_agent
"langchain-core>=1.0.0,<2.0.0"           # Core components
"langchain-openai>=1.0.1"                # OpenAI integration
"langgraph-cli[inmem]>=0.4.4"            # LangGraph Studio support
```

### 2. Agent Creation API Changed

**Before: `create_react_agent` (deprecated)**
```python
from langgraph.prebuilt import create_react_agent

email_agent = create_react_agent(
    model,
    tools=[send_email],
    prompt="You are an email assistant..."
)
```

**After: `create_agent` (LangChain v1)**
```python
from langchain.agents import create_agent

email_agent = create_agent(
    model=model,
    tools=[send_email],
    system_prompt="You are an email assistant..."
)
```

### 3. Parameter Changes

| Old Parameter | New Parameter | Notes |
|--------------|---------------|-------|
| `prompt` | `system_prompt` | Renamed for clarity |
| `model` (positional) | `model=` (keyword) | Must use keyword argument |

## 📦 Installation

```bash
# Install dependencies
uv sync

# Or with pip
pip install -e .
```

## 🚀 Running the Demo

The demo works the same way after migration:

```bash
# Run the hierarchical teams demo
python main.py

# Or use LangGraph Studio
uv run langgraph dev
```

## ✅ What Still Works

- ✅ Hierarchical supervisor pattern (unchanged)
- ✅ Multi-level routing (unchanged)
- ✅ Tool definitions (`@tool` decorator)
- ✅ State management with `MessagesState`
- ✅ Graph building with `StateGraph`
- ✅ Message handling
- ✅ Team coordination logic
- ✅ Agent specialization

## 🎯 Architecture (Unchanged)

```
                Top Supervisor
                /            \
    Communication Team    Scheduling Team
    Supervisor            Supervisor
    /        \            /          \
Email      Slack      Calendar    Meeting
Agent      Agent      Agent       Agent
```

## 🔑 Hierarchical Pattern Benefits

The core pattern remains the same:

1. **Top Supervisor** → Routes to team supervisors
2. **Team Supervisors** → Route to specialized agents
3. **Worker Agents** → Execute specific tasks
4. **Multi-Level Routing** → Efficient task delegation

## 🎨 LangGraph Studio

The project is configured for LangGraph Studio:

```bash
# Start the server
uv run langgraph dev

# Access Studio
https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

## 🎓 Benefits of v1

1. **Stability**: Production-ready APIs with long-term support
2. **Performance**: Optimized execution and runtime
3. **Compatibility**: Seamless integration with LangChain v1 ecosystem
4. **Consistency**: Unified API across LangGraph and LangChain
5. **Future-proof**: Built for long-term maintenance

## 📚 Key Features Demonstrated

### 1. **Hierarchical Routing**
```python
# Top supervisor routes to team supervisors
top_supervisor → communication_team or scheduling_team

# Team supervisors route to worker agents
communication_team → email_agent or slack_agent
scheduling_team → calendar_agent or meeting_agent
```

### 2. **Specialized Agents**

**Communication Team:**
- **Email Agent**: Compose and send professional emails
- **Slack Agent**: Send messages to Slack channels

**Scheduling Team:**
- **Calendar Agent**: Create calendar events
- **Meeting Agent**: Book meeting rooms

### 3. **Multi-Level State Management**
```python
class HierarchicalState(MessagesState):
    next_team: Literal["communication", "scheduling", "FINISH", "__start__"]
    next_agent: Literal["email", "slack", "calendar", "meeting", "FINISH", "__start__"]
```

## 🔧 Troubleshooting

### Issue: `create_react_agent` not found
**Solution**: Update imports to use `create_agent` from `langchain.agents`

### Issue: `prompt` parameter not recognized
**Solution**: Use `system_prompt` instead of `prompt`

### Issue: Model parameter error
**Solution**: Pass `ChatOpenAI` instance with keyword argument: `model=model`

## 📖 References

- [LangGraph v1 Release Notes](https://github.com/langchain-ai/langgraph/releases)
- [LangChain v1 Migration Guide](https://python.langchain.com/docs/versions/v1/)
- [create_agent Documentation](https://python.langchain.com/docs/how_to/agent_executor/)
- [Hierarchical Teams Pattern](https://langchain-ai.github.io/langgraph/how-tos/hierarchical-teams/)

---

**Migration completed successfully!** ✅
