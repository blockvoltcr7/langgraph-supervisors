# Migration to LangGraph v1 / LangChain v1

This project has been upgraded to use **LangGraph v1** and **LangChain v1**.

## 🔄 Key Changes

### 1. Dependencies Updated

**Before (v0.x):**
```toml
"langgraph>=0.2.62"
"langchain-openai>=0.2.14"
"langchain-core>=0.3.28"
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

tech_agent = create_react_agent(
    model,
    tools=[check_system_status, create_bug_ticket],
    prompt="You are a Technical Support Specialist..."
)
```

**After: `create_agent` (LangChain v1)**
```python
from langchain.agents import create_agent

tech_agent = create_agent(
    model=model,
    tools=[check_system_status, create_bug_ticket],
    system_prompt="You are a Technical Support Specialist..."
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
# Run the subgraph demo
python main.py

# Or use LangGraph Studio
uv run langgraph dev
```

## ✅ What Still Works

- ✅ Subgraph pattern (unchanged)
- ✅ State isolation between teams (unchanged)
- ✅ Tool definitions (`@tool` decorator)
- ✅ State schemas with `MessagesState`
- ✅ Graph building with `StateGraph`
- ✅ Message handling with `add_messages`
- ✅ Coordinator routing logic
- ✅ Team-specific tools and context

## 🎯 Architecture (Unchanged)

```
Customer Request
    ↓
Coordinator (routes based on request type)
    ↓
┌─────────────────┬─────────────────┐
│  Tech Support   │  Billing Team   │
│   Subgraph      │   Subgraph      │
└─────────────────┴─────────────────┘
     ↓                   ↓
Private State       Private State
(ticket_created,    (refund_processed,
 issue_resolved)     subscription_updated)
```

## 🔑 Subgraph Pattern Benefits

The core pattern remains the same:

1. **Tech Support Team** → Isolated state with technical tools
2. **Billing Team** → Isolated state with billing tools
3. **Coordinator** → Routes to appropriate team based on request
4. **State Isolation** → Each team has private conversation history

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

### 1. **Subgraph Pattern**
```python
# Each team is a separate subgraph
tech_subgraph = create_tech_support_subgraph()
billing_subgraph = create_billing_subgraph()

# Coordinator routes to subgraphs
workflow.add_node("tech_team", tech_subgraph)
workflow.add_node("billing_team", billing_subgraph)
```

### 2. **State Isolation**
```python
class TechSupportState(MessagesState):
    ticket_created: bool = False
    issue_resolved: bool = False

class BillingState(MessagesState):
    refund_processed: bool = False
    subscription_updated: bool = False
```

### 3. **Specialized Tools**
- **Tech Support**: `check_system_status`, `create_bug_ticket`, `search_knowledge_base`
- **Billing**: `lookup_invoice`, `process_refund`, `update_subscription`

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
- [Subgraph Pattern](https://langchain-ai.github.io/langgraph/how-tos/subgraph/)

---

**Migration completed successfully!** ✅
