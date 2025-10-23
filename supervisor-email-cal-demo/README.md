# Supervisor Multi-Agent Pattern Demo

This project demonstrates the **supervisor pattern** in LangGraph - a multi-agent architecture where a central supervisor agent coordinates specialized worker agents.

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Supervisor Agent                │
│  (Coordinates high-level workflow)      │
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

### Three-Layer Architecture

1. **Bottom Layer**: Rigid API tools (calendar, email) requiring exact formats
2. **Middle Layer**: Sub-agents that translate natural language → structured API calls
3. **Top Layer**: Supervisor that routes to capabilities and synthesizes results

## 📋 Prerequisites

- Python 3.12+
- `uv` package manager (already installed ✅)
- Anthropic API key

## 🚀 Installation

### 1. Set up environment variables

Create a `.env` file with your API key:

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
LANGSMITH_TRACING=true  # Optional
LANGSMITH_API_KEY=your-langsmith-key  # Optional
```

### 2. Dependencies are already installed! ✅

The following packages are ready:
- `langchain` - Agent framework
- `langchain-anthropic` - Anthropic integration
- `langchain-core` - Core abstractions
- `langgraph` - Graph orchestration
- `python-dotenv` - Environment management

## 🎯 Usage

### Basic Example (No HITL)

Run the basic supervisor demo:

```bash
python main.py
```

You'll see a menu:
```
Choose a mode:
  1. Run Example 1 (Simple request)
  2. Run Example 2 (Complex request)
  3. Interactive mode
  4. Run all examples
```

**Example 1**: Simple single-domain request
- "Schedule a team standup for tomorrow at 9am"
- Supervisor → Calendar Agent → API

**Example 2**: Complex multi-domain request
- "Schedule a meeting with the design team next Tuesday at 2pm for 1 hour, and send them an email reminder about reviewing the new mockups."
- Supervisor → Calendar Agent + Email Agent → APIs

**Example 3**: Interactive mode
- Chat directly with your personal assistant
- Type natural language requests
- Type 'quit' to exit

### Advanced Example (With Human-in-the-Loop)

Run the HITL demo:

```bash
python main_with_hitl.py
```

This version:
- ⏸️  **Pauses** before executing calendar events and sending emails
- ✅ Lets you **approve**, ✏️ **edit**, or ❌ **reject** each action
- 🔄 **Resumes** execution with your decisions

## 🧠 How It Works

### Step 1: Define Low-Level Tools

```python
@tool
def create_calendar_event(title: str, start_time: str, ...):
    """Create a calendar event. Requires exact ISO datetime format."""
    # Calls Google Calendar API, Outlook API, etc.
    
@tool
def send_email(to: list[str], subject: str, body: str):
    """Send an email via email API."""
    # Calls SendGrid, Gmail API, etc.
```

### Step 2: Create Specialized Sub-Agents

```python
calendar_agent = create_agent(
    model,
    tools=[create_calendar_event, get_available_time_slots],
    system_prompt="You are a calendar scheduling assistant..."
)

email_agent = create_agent(
    model,
    tools=[send_email],
    system_prompt="You are an email assistant..."
)
```

### Step 3: Wrap Sub-Agents as Tools

```python
@tool
def schedule_event(request: str) -> str:
    """Schedule calendar events using natural language."""
    result = calendar_agent.invoke({"messages": [{"role": "user", "content": request}]})
    return result["messages"][-1].content
```

### Step 4: Create Supervisor

```python
supervisor_agent = create_agent(
    model,
    tools=[schedule_event, manage_email],
    system_prompt="You are a helpful personal assistant..."
)
```

### Step 5: Use It!

```python
supervisor_agent.stream({
    "messages": [{"role": "user", "content": "Schedule a meeting..."}]
})
```

## 🎓 Key Concepts

### Why Use the Supervisor Pattern?

✅ **Separation of concerns**: Each agent has a focused responsibility  
✅ **Scalability**: Add new domains without affecting existing ones  
✅ **Testability**: Test and iterate on each layer independently  
✅ **Tool partitioning**: Avoid overwhelming a single agent with too many tools  
✅ **Context management**: Each sub-agent sees only relevant information  

### When to Use It

Use the supervisor pattern when:
- ✅ You have multiple distinct domains (calendar, email, CRM, database)
- ✅ Each domain has multiple tools or complex logic
- ✅ You want centralized workflow control
- ✅ Sub-agents don't need to converse directly with users

**Don't use it when:**
- ❌ You only have a few simple tools (use a single agent)
- ❌ Agents need to have conversations with users (use handoffs)
- ❌ You need peer-to-peer collaboration (consider other patterns)

## 🔍 Debugging with LangSmith

If you set up LangSmith (optional), you can:
- 🔍 Trace execution paths
- 📊 View all LLM calls and prompts
- 🐛 Debug multi-agent workflows
- 📈 Monitor performance

Visit [smith.langchain.com](https://smith.langchain.com) to view traces.

## 📚 Documentation

### 📖 Comprehensive Documentation Available

We've created extensive documentation with visual diagrams to help you understand the system:

- **[📚 Documentation Index](./docs/README.md)** - Start here! Navigation guide for all docs
- **[📐 Architecture Overview](./docs/architecture.md)** - Complete system design with Mermaid diagrams
- **[📊 Data Flow & Message Passing](./docs/data-flow.md)** - How data moves through the system
- **[💻 Implementation Guide](./docs/implementation-guide.md)** - Code examples and best practices
- **[👁️ Visual Summary](./docs/visual-summary.md)** - One-page visual reference

### 🎯 Quick Links by Role

- **Solution Architects**: Start with [Architecture Overview](./docs/architecture.md)
- **Developers**: Read [Implementation Guide](./docs/implementation-guide.md)
- **First-time Users**: Check [Visual Summary](./docs/visual-summary.md)
- **Data Engineers**: Review [Data Flow](./docs/data-flow.md)

### 📚 External Resources

- [LangChain Supervisor Tutorial](https://docs.langchain.com/oss/python/langchain/supervisor)
- [Multi-Agent Systems](https://docs.langchain.com/oss/python/langchain/multi-agent)
- [Human-in-the-Loop](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

## 🛠️ Customization

### Add a New Sub-Agent

1. Define tools for the new domain
2. Create a specialized agent with those tools
3. Wrap it as a tool for the supervisor
4. Add the tool to the supervisor's tool list

### Customize Information Flow

Control what each agent sees:

```python
@tool
def schedule_event(request: str, runtime: ToolRuntime) -> str:
    # Access full conversation context
    original_message = runtime.state["messages"][0]
    # Pass custom context to sub-agent
    prompt = f"Original request: {original_message}\nSub-task: {request}"
    ...
```

### Add More HITL Controls

```python
calendar_agent = create_agent(
    model,
    tools=[...],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "create_calendar_event": True,
                "delete_calendar_event": True,  # Add more tools
            },
        ),
    ],
)
```

## 🤝 Contributing

This is a learning project! Feel free to:
- Add more sub-agents (e.g., CRM, database, file management)
- Implement real API integrations
- Add more sophisticated routing logic
- Experiment with different LLM models

## 📝 License

MIT License - feel free to use this for learning and building!
