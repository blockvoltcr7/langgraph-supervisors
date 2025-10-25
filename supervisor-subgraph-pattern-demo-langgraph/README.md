# 🎯 Customer Support System with Subgraphs

A practical demonstration of **LangGraph subgraphs** using a real-world customer support system. This example shows how to build modular, isolated agent teams with their own memory and state.

## 🏗️ Architecture

```
                    Coordinator
                    /          \
            Tech Support    Billing Team
            Subgraph        Subgraph
            /    |    \     /    |    \
        Status  KB  Ticket Invoice Refund Sub
```

### Key Components:

1. **Coordinator** (Parent Graph) - Routes customer requests to appropriate teams
2. **Tech Support Subgraph** - Handles technical issues with isolated memory
3. **Billing Subgraph** - Manages billing/payment issues with isolated memory

## ✨ What Makes This Different from Supervisor Pattern?

| Feature | Hierarchical Supervisor | Subgraphs (This Example) |
|---------|------------------------|--------------------------|
| **Memory** | Shared across all agents | Isolated per subgraph |
| **State** | Single shared state | Different state schemas per team |
| **Modularity** | Tightly coupled | Fully modular & reusable |
| **Routing** | LLM-driven supervisors | Can be code-defined or LLM-driven |
| **Privacy** | All agents see all messages | Teams only see their own context |

## 🎯 Key Features

- ✅ **Isolated State Schemas** - Each team has different state structure (tickets vs refunds)
- ✅ **Modular Components** - Subgraphs are reusable across projects
- ✅ **State Transformation** - Parent coordinates without seeing team internals
- ✅ **Real-world Tools** - System status, bug tickets, invoices, refunds
- ✅ **LangSmith Tracing** - Full observability across parent and subgraphs
- ✅ **Clean Separation** - Teams don't interfere with each other's state

## 🚀 Quick Start

### 1. Install Dependencies

```bash
uv sync
```

### 2. Set Up Environment

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```env
OPENAI_API_KEY=your_key_here
```

### 3. Run the Demo

```bash
source .venv/bin/activate
python main.py
```

### 4. Run Tests (Optional)

```bash
# Run full test suite (17 test cases)
python test_scenarios.py

# Run quick test (3 scenarios)
python test_scenarios.py --quick
```

See [TEST_CASES.md](TEST_CASES.md) for all test scenarios and expected results.

**Having issues?** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common problems and solutions.

## 💬 Example Scenarios

### Technical Support Request:
```
"The API is returning 500 errors. Can you check if the service is down?"
```

**Flow:**
1. Coordinator → Routes to Tech Support subgraph
2. Tech Support → Checks system status
3. Tech Support → Searches knowledge base
4. Tech Support → Creates bug ticket if needed
5. Returns result to coordinator

**Key Point:** Billing team never sees this conversation!

### Billing Request:
```
"I need a refund for invoice INV-003. I was charged twice by mistake."
```

**Flow:**
1. Coordinator → Routes to Billing subgraph
2. Billing → Looks up invoice history
3. Billing → Processes refund
4. Returns result to coordinator

**Key Point:** Tech team never sees this conversation!

## 🔍 Understanding Subgraphs

### What's a Subgraph?

A subgraph is a **complete graph** that becomes a **node** in a parent graph:

```python
# Create subgraph
tech_subgraph = create_tech_support_subgraph()

# Use it as a node in parent graph
parent.add_node("tech_team", tech_subgraph)
```

### Isolated State Schemas

Each subgraph has its own state structure:

```python
# Subgraph compiles with its own state schema
subgraph = builder.compile()
```

This means:
- Tech team tracks `ticket_created` and `issue_resolved`
- Billing team tracks `refund_processed` and `subscription_updated`
- Teams don't interfere with each other's state
- Parent graph only sees shared `messages` key

### Different State Schemas

```python
# Tech team state
class TechSupportState(MessagesState):
    ticket_created: bool
    issue_resolved: bool

# Billing team state  
class BillingState(MessagesState):
    refund_processed: bool
    subscription_updated: bool

# Parent state (simpler)
class CoordinatorState(MessagesState):
    assigned_team: str
```

## 🛠️ Tools by Team

### Technical Support Tools:
- `check_system_status()` - Check if services are operational
- `create_bug_ticket()` - Create tickets for unresolved issues
- `search_knowledge_base()` - Search technical documentation

### Billing Tools:
- `lookup_invoice()` - View customer invoice history
- `process_refund()` - Process refund requests
- `update_subscription()` - Change subscription plans

## 📊 When to Use Subgraphs

### ✅ Use Subgraphs When:
- Teams need **isolated memory** (privacy/security)
- Different teams have **different state requirements**
- You want **modular, reusable** components
- Multiple teams are developing independently
- You need clear **separation of concerns**

### ❌ Use Supervisor Pattern When:
- All agents should **share conversation history**
- You need **dynamic, LLM-driven routing** at every level
- Simpler state management is sufficient
- You want maximum flexibility in coordination

## 🎨 Customization Ideas

### Add More Teams:
```python
# Add a Sales team subgraph
sales_subgraph = create_sales_subgraph()
parent.add_node("sales_team", sales_subgraph)
```

### Add Real APIs:
Replace stubbed tools with:
- Jira/Linear API for bug tickets
- Stripe API for billing
- StatusPage API for system status
- Zendesk API for ticket management

### Add Human-in-the-Loop:
```python
from langgraph.types import interrupt

def process_refund_with_approval(invoice_id, amount):
    approved = interrupt(f"Approve ${amount} refund?")
    if approved:
        return process_refund(invoice_id, amount)
```

## 🔄 Comparison with Hierarchical Pattern

Your `hierarchical-team-pattern-langgraph` example uses:
- **Supervisor nodes** that make routing decisions
- **Shared state** across all levels
- **LLM-driven routing** at each level

This subgraph example uses:
- **Subgraphs as nodes** with isolated memory
- **Different state schemas** per team
- **Coordinator routing** at top level only

**You can combine both!** Use supervisors within subgraphs for complex team coordination.

## 📚 Learn More

- [LangGraph Subgraphs Documentation](https://langchain-ai.github.io/langgraph/how-tos/subgraph/)
- [Multi-Agent Patterns](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)
- [Supervisor Pattern Tutorial](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/)

## 🎓 Key Takeaways

1. **Subgraphs = Modularity** - Build reusable components
2. **Isolated Memory = Privacy** - Teams don't see each other's context
3. **Different States = Flexibility** - Each team tracks what matters to them
4. **State Transformation = Clean Interfaces** - Parent doesn't need team details

---

**Built with LangGraph** 🦜🔗