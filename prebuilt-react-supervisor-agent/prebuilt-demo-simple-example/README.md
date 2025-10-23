# ⚡ Prebuilt vs Manual Supervisor Comparison

This demo shows **two ways** to build the same supervisor multi-agent system:

1. **Prebuilt** - Using `create_supervisor` (80 lines)
2. **Manual** - Building the graph yourself (200 lines)

## 🎯 What This Demonstrates

**Use Case:** Travel Booking Assistant
- Flight booking agent (search & book flights)
- Hotel booking agent (search & book hotels)
- Supervisor coordinates them

**Both implementations do the EXACT same thing!**

## 🚀 Quick Start

### 1. Install Dependencies

```bash
uv sync
```

### 2. Set Up API Key

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Run Prebuilt Version

```bash
source .venv/bin/activate
python prebuilt_supervisor.py
```

### 4. Run Manual Version

```bash
python manual_supervisor.py
```

**Compare the code!** Both do the same thing, but look at the difference in complexity.

## 🔍 Side-by-Side Comparison

### Prebuilt Version (`prebuilt_supervisor.py`)

```python
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor

# 1. Create agents
flight_agent = create_react_agent(
    model="openai:gpt-4o-mini",
    tools=[book_flight, search_flights],
    prompt="You are a flight booking specialist.",
    name="flight_assistant"  # Required!
)

hotel_agent = create_react_agent(
    model="openai:gpt-4o-mini",
    tools=[book_hotel, search_hotels],
    prompt="You are a hotel booking specialist.",
    name="hotel_assistant"  # Required!
)

# 2. Create supervisor (ONE LINE!)
supervisor = create_supervisor(
    agents=[flight_agent, hotel_agent],
    model=ChatOpenAI(model="gpt-4o-mini"),
    prompt="You are a travel coordinator..."
).compile()

# 3. Done! Use it:
supervisor.invoke({"messages": [...]})
```

**Lines of code:** ~80

---

### Manual Version (`manual_supervisor.py`)

```python
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent

# 1. Define state schema
class SupervisorState(TypedDict):
    messages: Annotated[list, add_messages]
    next_agent: Literal["flight", "hotel", "FINISH"]

# 2. Create agents (same)
flight_agent = create_react_agent(...)
hotel_agent = create_react_agent(...)

# 3. Wrap agents in nodes
def flight_agent_node(state):
    result = flight_agent.invoke(state)
    return {"messages": result["messages"]}

def hotel_agent_node(state):
    result = hotel_agent.invoke(state)
    return {"messages": result["messages"]}

# 4. Create supervisor node
def supervisor_node(state):
    # Custom routing logic
    messages = [SystemMessage(...)] + state["messages"]
    response = model.invoke(messages)
    
    # Parse response
    if "flight" in response.content:
        next_agent = "flight"
    elif "hotel" in response.content:
        next_agent = "hotel"
    else:
        next_agent = "FINISH"
    
    return {"messages": [response], "next_agent": next_agent}

# 5. Create routing function
def route_supervisor(state):
    next_agent = state.get("next_agent")
    if next_agent == "flight":
        return "flight"
    elif next_agent == "hotel":
        return "hotel"
    else:
        return "__end__"

# 6. Build graph
workflow = StateGraph(SupervisorState)
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("flight", flight_agent_node)
workflow.add_node("hotel", hotel_agent_node)

# 7. Add edges
workflow.add_edge(START, "supervisor")
workflow.add_conditional_edges(
    "supervisor",
    route_supervisor,
    {"flight": "flight", "hotel": "hotel", "__end__": END}
)
workflow.add_edge("flight", "supervisor")
workflow.add_edge("hotel", "supervisor")

# 8. Compile
supervisor = workflow.compile()
```

**Lines of code:** ~200

---

## 📊 Detailed Comparison

| Aspect | Prebuilt (`create_supervisor`) | Manual (Graph Building) |
|--------|-------------------------------|-------------------------|
| **Lines of Code** | ~80 | ~200 |
| **State Schema** | ✅ Automatic | ❌ Manual definition |
| **Supervisor Node** | ✅ Automatic | ❌ Manual implementation |
| **Routing Logic** | ✅ Automatic | ❌ Manual parsing |
| **Graph Construction** | ✅ Automatic | ❌ Manual edges |
| **Agent Wrapping** | ✅ Automatic | ❌ Manual nodes |
| **Error Handling** | ✅ Built-in | ❌ Your responsibility |
| **Best Practices** | ✅ Enforced | ❌ Your responsibility |
| **Customization** | ⚠️ Limited | ✅ Full control |
| **Learning Curve** | ✅ Easy | ❌ Steep |
| **Time to Build** | ⚡ 5 minutes | 🐌 30+ minutes |

## 💡 What `create_supervisor` Does For You

### 1. **State Management**
Automatically creates the state schema with:
- `messages` field with proper reducer
- `next_agent` field for routing
- Proper type hints

### 2. **Supervisor Node**
Automatically creates a supervisor that:
- Analyzes user requests
- Decides which agent to route to
- Handles multi-step workflows
- Knows when to finish

### 3. **Routing Logic**
Automatically implements:
- Conditional routing based on supervisor decisions
- Return paths from agents to supervisor
- Finish condition

### 4. **Graph Construction**
Automatically builds:
- All nodes (supervisor + agents)
- All edges (routing + returns)
- Entry and exit points

### 5. **Agent Integration**
Automatically:
- Wraps agents in nodes
- Handles message passing
- Manages state updates

## 🎯 When to Use Each Approach

### Use `create_supervisor` (Prebuilt) When:

✅ **Quick prototypes** - Need something working in minutes
✅ **Simple use cases** - Basic supervisor pattern is enough
✅ **Production apps** - Want battle-tested implementation
✅ **Team projects** - Easier for others to understand
✅ **Learning basics** - Focus on agents, not graph mechanics

### Use Manual Approach When:

✅ **Custom patterns** - Hierarchical teams, complex routing
✅ **Special state** - Need custom state fields
✅ **Learning deeply** - Want to understand internals
✅ **Advanced features** - Persistence, time-travel, etc.
✅ **Full control** - Need to customize every detail

## 🔥 Key Differences in Code

### Agent Names (IMPORTANT!)

**Prebuilt requires names:**
```python
flight_agent = create_react_agent(
    ...,
    name="flight_assistant"  # ← REQUIRED for create_supervisor
)
```

**Manual doesn't:**
```python
flight_agent = create_react_agent(...)
# No name needed, you control routing
```

### State Initialization

**Prebuilt:**
```python
# Simple! Just messages
supervisor.invoke({
    "messages": [{"role": "user", "content": "..."}]
})
```

**Manual:**
```python
# Need to provide next_agent
supervisor.invoke({
    "messages": [HumanMessage(content="...")],
    "next_agent": "flight"  # ← Required
})
```

### Customization

**Prebuilt:**
```python
# Limited to prompt customization
create_supervisor(
    agents=[...],
    prompt="Custom supervisor instructions"  # ← Only customization
)
```

**Manual:**
```python
# Full control over everything
def supervisor_node(state):
    # Your custom logic here!
    # Can do anything you want
    pass
```

## 📝 Example Output

### Query: "Book a flight from BOS to JFK on Dec 25th"

**Both versions produce:**
```
ai: I'll help you book that flight. Let me search for available options.
tool: 🔍 Found 5 flights from BOS to JFK: AA101, UA202, DL303, SW404, B6505
ai: I found several flights. I'll book AA101 for you.
tool: ✈️ Successfully booked flight from BOS to JFK on Dec 25th
ai: Done! Your flight from BOS to JFK on December 25th is booked.
```

### Query: "Book a flight from LAX to NYC and a hotel in Manhattan"

**Both versions handle multi-step:**
```
1. Supervisor → Routes to flight agent
2. Flight agent → Books flight
3. Supervisor → Routes to hotel agent  
4. Hotel agent → Books hotel
5. Supervisor → Finishes
```

## 🎓 Learning Value

### What You Learn from Prebuilt:
- ✅ How to use `create_react_agent`
- ✅ How to use `create_supervisor`
- ✅ Agent naming conventions
- ✅ Quick prototyping
- ✅ Production patterns

### What You Learn from Manual:
- ✅ State schema design
- ✅ Graph construction
- ✅ Routing logic
- ✅ Node wrapping
- ✅ Edge configuration
- ✅ Full LangGraph API

## 🚀 Next Steps

### Extend the Prebuilt Version:

1. **Add more agents:**
```python
car_rental_agent = create_react_agent(..., name="car_rental")

supervisor = create_supervisor(
    agents=[flight_agent, hotel_agent, car_rental_agent],
    ...
)
```

2. **Customize supervisor prompt:**
```python
create_supervisor(
    agents=[...],
    prompt="""
    You are a premium travel concierge.
    Always suggest the best options.
    Be proactive and helpful.
    """
)
```

### Extend the Manual Version:

1. **Add custom state fields:**
```python
class SupervisorState(TypedDict):
    messages: Annotated[list, add_messages]
    next_agent: Literal[...]
    booking_summary: dict  # ← Custom field
    total_cost: float      # ← Custom field
```

2. **Add persistence:**
```python
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string("travel.db")
graph = workflow.compile(checkpointer=checkpointer)
```

## 📚 Resources

- [LangGraph Supervisor Docs](https://github.com/langchain-ai/langgraph-supervisor-py)
- [create_react_agent](https://langchain-ai.github.io/langgraph/reference/prebuilt/#create_react_agent)
- [Multi-Agent Patterns](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)

## 🎯 Summary

**Prebuilt (`create_supervisor`):**
- ⚡ Fast to build (5 minutes)
- 📝 Less code (~80 lines)
- ✅ Best practices built-in
- ⚠️ Limited customization
- 🚀 Perfect for production

**Manual (Graph Building):**
- 🐌 Slower to build (30+ minutes)
- 📝 More code (~200 lines)
- 🎯 Full control
- 💡 Deep learning
- 🔧 Perfect for custom patterns

---

**Both are valid! Choose based on your needs:**
- Need it fast? → Use prebuilt
- Need custom features? → Use manual
- Learning? → Try both!

**You now understand BOTH approaches!** 🎉