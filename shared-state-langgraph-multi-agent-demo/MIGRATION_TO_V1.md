# Migration to LangGraph v1 / LangChain v1

This project has been upgraded to use **LangGraph v1** and **LangChain v1**.

## 🔄 Key Changes

### 1. Dependencies Updated

**Before (v0.x):**
```toml
"langgraph>=0.2.58"
"langchain-openai>=0.3.0"
"langchain-core>=0.3.64"
"langchain-community>=0.3.0"
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

research_agent = create_react_agent(
    model,
    tools=[web_search],
    prompt="You are a Research Agent..."
)
```

**After: `create_agent` (LangChain v1)**
```python
from langchain.agents import create_agent

research_agent = create_agent(
    model=model,
    tools=[web_search],
    system_prompt="You are a Research Agent..."
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
# Run the shared state demo
python main.py

# Or use LangGraph Studio
uv run langgraph dev
```

## ✅ What Still Works

- ✅ Shared state pattern (unchanged)
- ✅ Multi-agent collaboration (unchanged)
- ✅ Tool definitions (`@tool` decorator)
- ✅ State management with `TypedDict`
- ✅ Graph building with `StateGraph`
- ✅ Message handling with `add_messages`
- ✅ Supervisor routing logic
- ✅ Web search integration (Tavily)

## 🎯 Architecture (Unchanged)

```
User Query
    ↓
Supervisor (routes based on shared state progress)
    ↓
┌─────────────┬──────────────┬─────────────┐
│   Research  │   Analysis   │   Report    │
│   Agent     │   Agent      │   Agent     │
└─────────────┴──────────────┴─────────────┘
     ↓              ↓              ↓
Populates      Reads research  Reads analysis
web_results    Writes analysis Writes summary
```

## 🔑 Shared State Pattern

The core pattern remains the same:

1. **Research Agent** → Adds `web_results` to state
2. **Analysis Agent** → Reads `web_results`, adds `analysis` to state
3. **Report Agent** → Reads `analysis`, adds `final_report` to state
4. **Supervisor** → Sees all completed, returns result

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

## 📚 References

- [LangGraph v1 Release Notes](https://github.com/langchain-ai/langgraph/releases)
- [LangChain v1 Migration Guide](https://python.langchain.com/docs/versions/v1/)
- [create_agent Documentation](https://python.langchain.com/docs/how_to/agent_executor/)
- [Shared State Pattern](https://langchain-ai.github.io/langgraph/how-tos/pass-private-state/)

## 🔧 Troubleshooting

### Issue: `create_react_agent` not found
**Solution**: Update imports to use `create_agent` from `langchain.agents`

### Issue: `prompt` parameter not recognized
**Solution**: Use `system_prompt` instead of `prompt`

### Issue: Model parameter error
**Solution**: Pass `ChatOpenAI` instance with keyword argument: `model=model`

---

**Migration completed successfully!** ✅
