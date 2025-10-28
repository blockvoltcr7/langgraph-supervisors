# Migration to LangGraph v1 / LangChain v1

This project has been upgraded to use **LangGraph v1** and **LangChain v1**.

## 🔄 Key Changes

### 1. Dependencies Updated

**Before (v0.x):**
```toml
"langgraph>=0.2.58"
"langchain>=0.3.0"
"langchain-openai>=0.3.0"
"langchain-core>=0.3.64"
```

**After (v1.x):**
```toml
"langgraph>=1.0.1"                       # LangGraph v1
"langchain>=1.0.0"                       # LangChain v1 with create_agent
"langchain-core>=1.0.0,<2.0.0"           # Core components
"langchain-openai>=1.0.1"                # OpenAI integration
```

### 2. Agent Creation API Changed

**Before: `create_react_agent` (deprecated)**
```python
from langgraph.prebuilt import create_react_agent

flight_agent = create_react_agent(
    model,  # or "openai:gpt-4o-mini"
    tools=[book_flight, search_flights],
    prompt="You are a flight booking specialist..."
)
```

**After: `create_agent` (LangChain v1)**
```python
from langchain.agents import create_agent

flight_agent = create_agent(
    model=model,  # Must be ChatOpenAI instance
    tools=[book_flight, search_flights],
    system_prompt="You are a flight booking specialist..."
)
```

### 3. Parameter Changes

| Old Parameter | New Parameter | Notes |
|--------------|---------------|-------|
| `prompt` | `system_prompt` | Renamed for clarity |
| `model` (string) | `model` (ChatOpenAI) | Must be model instance |
| `name` | `name` | Same (optional) |

## 📦 Installation

```bash
# Install dependencies
uv sync

# Or with pip
pip install -e .
```

## 🚀 Running the Examples

Both scripts work the same way after migration:

```bash
# Prebuilt supervisor (easy way)
python prebuilt_supervisor.py

# Manual supervisor (full control)
python manual_supervisor.py
```

## ✅ What Still Works

- ✅ `create_supervisor` from `langgraph-supervisor` (unchanged)
- ✅ All tool definitions (unchanged)
- ✅ State management with `TypedDict` (unchanged)
- ✅ Graph building with `StateGraph` (unchanged)
- ✅ Message handling with `add_messages` (unchanged)

## 🎯 Benefits of v1

1. **Stability**: Production-ready APIs with long-term support
2. **Performance**: Optimized runtime and execution
3. **Compatibility**: Works seamlessly with LangChain v1 ecosystem
4. **Future-proof**: Built for long-term use

## 📚 References

- [LangGraph v1 Release Notes](https://github.com/langchain-ai/langgraph/releases)
- [LangChain v1 Migration Guide](https://python.langchain.com/docs/versions/v1/)
- [create_agent Documentation](https://python.langchain.com/docs/how_to/agent_executor/)

## 🔧 Troubleshooting

### Issue: `create_react_agent` not found
**Solution**: Update imports to use `create_agent` from `langchain.agents`

### Issue: `prompt` parameter not recognized
**Solution**: Use `system_prompt` instead of `prompt`

### Issue: Model string not working
**Solution**: Pass `ChatOpenAI` instance instead of string like `"openai:gpt-4o-mini"`

---

**Migration completed successfully!** ✅
