# Migration to LangGraph v1 and LangChain v1

This document outlines the changes made to migrate the agentic RAG demo to use LangGraph v1 and LangChain v1.

## Changes Made

### 1. Dependencies Updated (`pyproject.toml`)

**Added:**
- `langchain>=1.0.0` - Required for the new `create_agent` API

**Updated:**
- Changed exact version pins to `>=` for more flexibility
- All packages now use LangGraph v1 and LangChain v1 compatible versions

### 2. Import Changes (`main.py`)

**Before:**
```python
from langgraph.prebuilt import create_react_agent
```

**After:**
```python
from langchain.agents import create_agent
```

### 3. API Changes

#### Agent Creation

**Before (deprecated):**
```python
agent = create_react_agent(
    model,
    tools=[retrieve_langgraph_docs],
    prompt="You are a helpful assistant..."
)
```

**After (LangChain v1):**
```python
agent = create_agent(
    model=model,  # Now explicitly named parameter
    tools=[retrieve_langgraph_docs],
    system_prompt="You are a helpful assistant..."  # Renamed from 'prompt'
)
```

### 4. Key Differences

| Feature | create_react_agent (deprecated) | create_agent (v1) |
|---------|--------------------------------|-------------------|
| Package | `langgraph.prebuilt` | `langchain.agents` |
| Model parameter | Positional | Named (`model=`) |
| Prompt parameter | `prompt` | `system_prompt` |
| Middleware support | ❌ No | ✅ Yes |
| Built on | LangGraph | LangGraph (same runtime) |

## Benefits of Migration

1. **Future-proof**: Using the officially supported API going forward
2. **Middleware support**: Can add pre/post-model hooks, human-in-the-loop, etc.
3. **Better integration**: Seamless with LangChain v1 ecosystem
4. **Same runtime**: Still runs on LangGraph with all its features (checkpointing, streaming, etc.)

## What Stayed the Same

- Graph structure and execution model (unchanged)
- State management with `StateGraph`
- Checkpointing with `MemorySaver`
- Streaming and human-in-the-loop capabilities
- Tool definitions and usage

## Installation

To install the updated dependencies:

```bash
# Using pip
pip install -e .

# Using uv (recommended)
uv pip install -e .
```

## Running the Demo

The demo runs exactly the same way:

```bash
python main.py
```

## References

- [LangGraph v1 Release Notes](https://docs.langchain.com/oss/python/releases/langgraph-v1)
- [LangChain v1 Release Notes](https://docs.langchain.com/oss/python/releases/langchain-v1)
- [Migration Guide](https://docs.langchain.com/oss/python/migrate/langchain-v1#create-agent)
