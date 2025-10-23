# 🚀 Quick Start - Your Supervisor is Live!

## ✅ Server is Running

Your LangGraph server is now running at: **http://localhost:2024**

## 🎯 Connect to Agent Chat UI

### Option 1: Use the Web UI (Easiest)

1. Go to: **https://agentchat.vercel.app**

2. Fill in the form:
   ```
   Deployment URL: http://localhost:2024
   Assistant / Graph ID: agent
   LangSmith API Key: <your-langsmith-api-key>
   ```

3. Click **Continue**

4. Start chatting! Try:
   - "Schedule a team meeting for tomorrow at 2pm"
   - "Send an email to the design team"
   - "Schedule a standup Monday at 9am and email the team"

### Option 2: Use LangSmith Studio

The server automatically opened LangSmith Studio in your browser at:
```
https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

This gives you a more advanced debugging interface.

## 🎨 What You'll See

### In Agent Chat UI:

1. **Your message** → Supervisor analyzes it
2. **Supervisor decides** → Routes to calendar or email agent
3. **Worker agent executes** → Uses tools, returns results
4. **Supervisor responds** → Provides final answer

### Example Flow:

```
You: "Schedule a meeting for tomorrow at 2pm and email the team"

Supervisor: [Routes to calendar agent]
Calendar Agent: ✅ Meeting scheduled for Oct 24, 2pm-3pm

Supervisor: [Routes to email agent]
Email Agent: 📧 Email sent to team about the meeting

Supervisor: "Done! I've scheduled the meeting and emailed the team."
```

## 🔍 Debug with LangSmith

Every conversation is traced at:
**https://smith.langchain.com/o/4ead951d-ee17-43a3-bb7a-7a92addc0cd3/projects/p/langgraph-supervisor-demo**

You can see:
- Full execution graph
- All LLM calls
- Tool executions
- Routing decisions
- Performance metrics

## 🛑 Stop the Server

Press `Ctrl+C` in the terminal where `langgraph dev` is running.

## 🔄 Restart After Code Changes

The server has **hot-reloading** enabled! Just save your changes to `main.py` and the server will automatically reload.

## 📝 Test Queries

Try these in Agent Chat UI:

### Simple Tasks:
- "Schedule a team standup for tomorrow at 9am"
- "Send an email to john@example.com about the project update"

### Complex Tasks:
- "Schedule a design review next Tuesday at 2pm and send invites to the design team"
- "Set up a weekly standup every Monday at 9am and email the team about it"

### Edge Cases:
- "What's the weather?" (Should handle gracefully - no weather agent)
- "Schedule a meeting" (Should ask for more details)

## 🎯 Next Steps

### 1. Add More Agents

Edit `main.py` and add new worker agents:
```python
# Add a Slack agent
slack_agent = create_react_agent(
    model,
    tools=[send_slack_message, create_channel],
    prompt="You are a Slack assistant..."
)
```

### 2. Try Hierarchical Teams

Create a supervisor of supervisors:
- Communication supervisor (email + slack agents)
- Scheduling supervisor (calendar + meeting agents)
- Top supervisor (coordinates both)

### 3. Add Real APIs

Replace stubbed tools with real integrations:
- Google Calendar API
- Gmail API
- Slack API

### 4. Deploy to Production

```bash
langgraph deploy
```

Then use your production URL in Agent Chat UI!

## 🐛 Troubleshooting

### Can't connect to Agent Chat UI?

- Make sure server is running (check terminal)
- Use `http://localhost:2024` not `https://`
- Try `http://127.0.0.1:2024` instead

### Graph not found?

- Check `langgraph.json` has `"agent"` as the graph ID
- Restart the server with `Ctrl+C` then `langgraph dev`

### Tool execution fails?

- These are demo/stubbed tools
- They return mock responses
- Replace with real APIs for production

## 📚 Resources

- [Agent Chat UI](https://github.com/langchain-ai/agent-chat-ui)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [LangSmith](https://smith.langchain.com)
- [Multi-Agent Patterns](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)
