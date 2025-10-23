# Agent Chat UI Setup Guide

This guide shows you how to connect your LangGraph supervisor agent to the Agent Chat UI for a professional chat interface.

## 🚀 Quick Start

### 1. Start the LangGraph Server

From your project directory, run:

```bash
langgraph dev
```

This will:
- Start a local LangGraph server on `http://localhost:2024`
- Expose your supervisor agent via API
- Enable hot-reloading for development

You should see output like:
```
Ready!
- API: http://localhost:2024
```

### 2. Connect to Agent Chat UI

1. Open your browser to: **https://agentchat.vercel.app**

2. Fill in the connection form:
   - **Deployment URL:** `http://localhost:2024`
   - **Assistant / Graph ID:** `agent`
   - **LangSmith API Key:** Your LangSmith key (from `.env`)

3. Click **Continue**

4. Start chatting with your supervisor agent! 🎉

## 📋 Configuration Details

### langgraph.json

This file tells the LangGraph server where to find your graph:

```json
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./main.py:create_supervisor_graph"
  },
  "env": ".env"
}
```

- `dependencies`: Python packages to install
- `graphs`: Maps graph IDs to Python functions
- `env`: Environment variables file

### Graph Export

In `main.py`, we export the graph at module level:

```python
# This is used by langgraph.json
graph = create_supervisor_graph()
```

The LangGraph server imports this and exposes it via API.

## 🎯 What You Can Do

### Chat with Your Supervisor

Try these queries:
- "Schedule a team meeting for tomorrow at 2pm"
- "Send an email to the design team about the new mockups"
- "Schedule a standup for Monday at 9am and email the team"

### See the Workflow

The UI will show:
1. **Supervisor's routing decision** (calendar/email/FINISH)
2. **Worker agent execution** (tool calls and results)
3. **Final response** from the supervisor

### Debug with LangSmith

Since you have LangSmith tracing enabled:
1. Every conversation is traced
2. View at: https://smith.langchain.com
3. See the full execution graph
4. Debug any issues

## 🔧 Advanced Configuration

### Custom Port

To use a different port:

```bash
langgraph dev --port 8000
```

Then use `http://localhost:8000` in Agent Chat UI.

### Production Deployment

For production, deploy to LangGraph Cloud:

```bash
langgraph deploy
```

Then use your production URL in Agent Chat UI.

## 🐛 Troubleshooting

### "Connection Failed"

**Problem:** Can't connect to `http://localhost:2024`

**Solutions:**
1. Make sure `langgraph dev` is running
2. Check the terminal for the actual port
3. Try `http://127.0.0.1:2024` instead

### "Graph Not Found"

**Problem:** Assistant ID `agent` not found

**Solutions:**
1. Check `langgraph.json` has the correct graph name
2. Restart `langgraph dev`
3. Check for Python errors in the terminal

### "Tool Execution Failed"

**Problem:** Calendar/email tools fail

**Solutions:**
1. These are stubbed tools for demo purposes
2. They return mock responses
3. Replace with real APIs for production

## 📚 Next Steps

### 1. Add More Agents

Edit `main.py` to add more worker agents:
```python
# Add a CRM agent
crm_agent = create_react_agent(
    model,
    tools=[create_contact, update_deal],
    prompt="You are a CRM assistant..."
)
```

### 2. Implement Real APIs

Replace stubbed tools with real integrations:
- Google Calendar API
- Gmail API
- Slack API
- etc.

### 3. Add Human-in-the-Loop

Add approval workflows:
```python
from langgraph.checkpoint.memory import MemorySaver

graph = create_supervisor_graph()
graph = graph.compile(checkpointer=MemorySaver())
```

### 4. Try Hierarchical Teams

Create supervisor of supervisors:
- Top supervisor coordinates multiple team supervisors
- Each team supervisor manages specialized agents
- Scale to complex multi-agent systems

## 🎨 UI Features

The Agent Chat UI supports:
- ✅ **Streaming responses** - See agent thinking in real-time
- ✅ **Tool call rendering** - View all tool executions
- ✅ **Message history** - Full conversation context
- ✅ **Human-in-the-loop** - Approve/reject actions
- ✅ **Generative UI** - Custom React components

## 📖 Resources

- [Agent Chat UI Docs](https://github.com/langchain-ai/agent-chat-ui)
- [LangGraph Platform](https://langchain-ai.github.io/langgraph/cloud/)
- [LangSmith Tracing](https://smith.langchain.com)
- [Multi-Agent Patterns](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)
