# 🎓 Getting Started with Subgraphs

Welcome! This guide will help you understand and run the subgraph pattern example.

## 📚 What You'll Learn

1. **What are subgraphs** and how they differ from supervisor patterns
2. **When to use subgraphs** vs other multi-agent patterns
3. **How to implement** isolated memory for agent teams
4. **Practical example** with customer support system

## 🎯 The Big Idea

**Subgraphs = Graphs within Graphs**

Think of it like this:
- Your **parent graph** is like a company
- Each **subgraph** is like a department (Tech, Billing, Sales)
- Each department has its **own private workspace** (isolated memory)
- The company coordinator **routes work** to the right department

## 🏃 Quick Start (3 Steps)

### Step 1: Setup Environment

```bash
# Already done if you ran uv sync!
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-...
```

### Step 2: Test Your Setup

```bash
source .venv/bin/activate
python test_simple.py
```

You should see:
```
✅ ALL TESTS PASSED!
```

### Step 3: Run the Demo

```bash
python main.py
```

Watch as customer requests are routed to specialized teams!

## 📖 Understanding the Code

### The Architecture

```python
# 1. Create specialized subgraphs
tech_subgraph = create_tech_support_subgraph()
billing_subgraph = create_billing_subgraph()

# 2. Each subgraph has isolated memory
subgraph = builder.compile(checkpointer=True)  # 🔑 Key feature!

# 3. Compose into parent graph
parent.add_node("tech_team", tech_subgraph)
parent.add_node("billing_team", billing_subgraph)
```

### Key Concepts

#### 1. Isolated Memory
```python
# Tech team's conversation
tech_subgraph.invoke(
    {"messages": [...]},
    config={"thread_id": "tech-team"}  # Separate thread!
)

# Billing team's conversation  
billing_subgraph.invoke(
    {"messages": [...]},
    config={"thread_id": "billing-team"}  # Different thread!
)
```

**Result:** Teams don't see each other's conversations!

#### 2. Different State Schemas
```python
# Tech team tracks technical stuff
class TechSupportState(MessagesState):
    ticket_created: bool
    issue_resolved: bool

# Billing team tracks financial stuff
class BillingState(MessagesState):
    refund_processed: bool
    subscription_updated: bool
```

**Result:** Each team tracks what matters to them!

#### 3. Modular Components
```python
# Build once, use anywhere
tech_subgraph = create_tech_support_subgraph()

# Use in multiple parent graphs
customer_support_graph.add_node("tech", tech_subgraph)
internal_tools_graph.add_node("tech", tech_subgraph)
```

**Result:** Reusable, testable components!

## 🔍 Compare with Supervisor Pattern

### Your Hierarchical Supervisor Example:
```python
# All agents share state
class HierarchicalState(MessagesState):
    next_team: str
    next_agent: str

# Supervisors at every level
top_supervisor → team_supervisor → agent
```

**When to use:** All agents need shared context

### This Subgraph Example:
```python
# Each team has own state
class TechState(MessagesState): ...
class BillingState(MessagesState): ...

# Coordinator at top only
coordinator → subgraph (handles internally)
```

**When to use:** Teams need privacy/isolation

## 🎮 Try These Experiments

### Experiment 1: Add a New Team

```python
# In main.py, add a Sales subgraph
def create_sales_subgraph():
    """Sales team with CRM tools"""
    # ... your implementation
    return builder.compile(checkpointer=True)

# Add to coordinator
sales_subgraph = create_sales_subgraph()
parent.add_node("sales_team", sales_subgraph)
```

### Experiment 2: Add More Tools

```python
@tool
def escalate_to_human(issue: str) -> str:
    """Escalate complex issues to human support"""
    return f"Issue escalated: {issue}"

# Add to tech support tools
tech_agent = create_react_agent(
    model,
    tools=[check_system_status, create_bug_ticket, escalate_to_human],
    prompt="..."
)
```

### Experiment 3: Enable LangSmith Tracing

```bash
# In .env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_key_here
```

Then run `python main.py` and view traces at https://smith.langchain.com

## 📊 What Happens When You Run

```
Customer: "The API is down!"
    ↓
Coordinator: "This is a tech issue"
    ↓
Tech Subgraph (isolated memory):
    1. Check system status → "API operational"
    2. Search KB → "Check logs..."
    3. Create ticket → "BUG-1234 created"
    ↓
Response: "I've checked the API..."
```

**Meanwhile, billing team has no idea this happened!**

## 🐛 Troubleshooting

### "OPENAI_API_KEY not found"
```bash
cp .env.example .env
# Edit .env and add your key
```

### "Module not found"
```bash
uv sync
source .venv/bin/activate
```

### "Rate limit exceeded"
```python
# In main.py, add delays between examples
import time
time.sleep(5)  # Between examples
```

## 📚 Next Steps

### 1. Read the Docs
- [README.md](README.md) - Full architecture details
- [SUBGRAPHS_VS_SUPERVISOR.md](SUBGRAPHS_VS_SUPERVISOR.md) - Detailed comparison
- [QUICKSTART.md](QUICKSTART.md) - Quick reference

### 2. Explore the Code
- `main.py` - Full implementation
- `test_simple.py` - Setup verification

### 3. Compare Patterns
- Check `../hierarchical-team-pattern-langgraph` for supervisor pattern
- See how they differ in practice

### 4. Build Your Own
Start with this template and:
- Add your own teams (Sales, HR, DevOps)
- Integrate real APIs (Stripe, Jira, Slack)
- Add human-in-the-loop approvals
- Deploy with `langgraph dev`

## 💡 Key Takeaways

1. **Subgraphs = Modularity**
   - Build reusable components
   - Test teams independently
   - Develop in parallel

2. **Isolated Memory = Privacy**
   - Teams don't see each other's conversations
   - Perfect for multi-tenant systems
   - Better security and compliance

3. **Different States = Flexibility**
   - Each team tracks what matters
   - No state pollution
   - Cleaner code

4. **Combine Patterns = Power**
   - Use supervisors within subgraphs
   - Best of both worlds
   - Maximum flexibility

## 🎉 You're Ready!

You now understand:
- ✅ What subgraphs are
- ✅ How they differ from supervisors
- ✅ When to use each pattern
- ✅ How to implement them

**Go build something amazing!** 🚀

---

Questions? Check out:
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [LangChain Discord](https://discord.gg/langchain)
- [GitHub Issues](https://github.com/langchain-ai/langgraph/issues)
