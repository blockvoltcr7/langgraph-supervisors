# LangGraph Supervisor Agent Demo

This project demonstrates a **proper LangGraph supervisor pattern** using `StateGraph` where a central supervisor agent coordinates specialized calendar and email agents through explicit graph orchestration.

## 🔄 Key Difference from LangChain-Only Implementations

Unlike the other example in this repo which uses LangChain agents with minimal LangGraph utilities, this implementation uses **true LangGraph concepts**:

- **`StateGraph`** for defining the multi-agent orchestration flow
- **Explicit nodes** for each agent (supervisor, calendar, email)
- **Directed edges** defining the flow between agents
- **`Command` objects** for handoffs between agents
- **Graph-based state management** rather than just agent tool calling

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Supervisor Agent                │
│  (Routes tasks using handoff tools)     │
└────────────┬────────────────────────────┘
             │
      ┌──────┴──────┐
      │             │
      ▼             ▼
┌──────────┐  ┌──────────┐
│ Calendar │  │  Email   │
│  Agent   │  │  Agent   │
└────┬─────┘  └────┬─────┘
     │             │
     ▼             ▼
┌─────────┐   ┌─────────┐
│Calendar │   │  Email  │
│  APIs   │   │  APIs   │
└─────────┘   └─────────┘
```

The flow is orchestrated through a `StateGraph`:
- **START** → **supervisor** → **calendar_agent**/**email_agent** → **supervisor** → **END**
- Agents communicate via **handoff tools** that return `Command` objects to navigate the graph
- State flows through the graph with message history preserved

## 📋 Prerequisites

- Python 3.12+
- OpenAI API key

## 🚀 Installation

### 1. Install dependencies

```bash
uv sync
```

### 2. Set up environment variables

Edit the `.env` file and add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Enable LangSmith tracing for debugging and observability
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=langgraph-supervisor-demo
```

**LangSmith Tracing (Optional):**
- Sign up at [smith.langchain.com](https://smith.langchain.com) to get your API key
- Set `LANGSMITH_TRACING=true` to enable tracing
- View detailed execution traces, debug issues, and monitor performance
- See the full conversation flow between supervisor and worker agents

## 🎯 Usage

### Run the demo

```bash
uv run python main.py
```

You'll see a menu:
```
🤖 LangGraph Supervisor Agent Demo
================================================================================

✅ Environment configured
✅ LangGraph supervisor system initialized

Choose a mode:
  1. Run Example 1 (Simple calendar request)
  2. Run Example 2 (Complex multi-domain request)
  3. Interactive mode
  4. Run all examples
```

### Example 1: Simple Calendar Request

**Input:** "Schedule a team standup for tomorrow at 9am"

**Flow:**
1. Supervisor analyzes request → detects calendar task
2. Supervisor calls `transfer_to_calendar_agent` tool
3. `Command` navigates graph to calendar agent node
4. Calendar agent parses time, calls calendar API
5. Calendar agent returns to supervisor via edge
6. Supervisor provides final response

### Example 2: Complex Multi-Domain Request

**Input:** "Schedule a meeting with the design team next Tuesday at 2pm for 1 hour, and send them an email reminder about reviewing the new mockups."

**Flow:**
1. Supervisor analyzes request → detects both calendar and email tasks
2. Supervisor calls `transfer_to_calendar_agent` first
3. Calendar agent completes task, returns to supervisor
4. Supervisor then calls `transfer_to_email_agent`
5. Email agent completes task, returns to supervisor
6. Supervisor provides final coordinated response

### Interactive Mode

Chat directly with the supervisor agent and see the graph orchestration in action.

## 🧠 How It Works

### 1. Handoff Tools

The supervisor uses special **handoff tools** that return `Command` objects:

```python
@tool(name, description=description)
def handoff_tool(state, tool_call_id) -> Command:
    return Command(
        goto=agent_name,  # Navigate to agent node
        update={**state, "messages": state["messages"] + [tool_message]},
        graph=Command.PARENT,  # Navigate in parent graph
    )
```

### 2. StateGraph Orchestration

```python
supervisor_graph = (
    StateGraph(MessagesState)
    .add_node(supervisor_agent, destinations=("calendar_agent", "email_agent", END))
    .add_node(calendar_agent)
    .add_node(email_agent)
    .add_edge(START, "supervisor")
    .add_edge("calendar_agent", "supervisor")  # Return to supervisor
    .add_edge("email_agent", "supervisor")     # Return to supervisor
    .compile()
)
```

### 3. Message Flow

All agent interactions are preserved in the message history, allowing:
- Context-aware handoffs
- Sequential task execution
- Coordinated final responses

## 🔍 Key LangGraph Concepts Demonstrated

- **`StateGraph`**: Core orchestration mechanism
- **`Command` objects**: Graph navigation and state updates
- **Node functions**: Agent implementations as graph nodes
- **Directed edges**: Explicit flow control
- **`MessagesState`**: Structured state management
- **Graph compilation**: Creating executable graphs

## 📚 Documentation References

This implementation is based on the [LangGraph Multi-Agent Supervisor tutorial](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/).

## 🤝 Comparison with LangChain-Only Approach

| Feature | LangChain Only | This LangGraph Implementation |
|---------|----------------|-------------------------------|
| **Architecture** | Agent tool calling | Graph-based state machine |
| **Flow Control** | Implicit via agent prompts | Explicit via StateGraph edges |
| **State Management** | Agent internal state | Structured MessagesState |
| **Orchestration** | Agent decides next steps | Graph defines possible flows |
| **Navigation** | Tool-based handoffs | Command-based graph navigation |
| **Extensibility** | Limited to agent patterns | Full graph customization |

This implementation shows how LangGraph provides more control and structure for complex multi-agent workflows compared to pure LangChain agent compositions.