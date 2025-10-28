# 🎨 LangGraph Studio Guide

This project is configured for **LangGraph Studio** - a visual interface to interact with and debug your LangGraph applications.

## 🚀 Quick Start

### 1. Start the LangGraph Server

```bash
uv run langgraph dev
```

You'll see:
```
╦  ┌─┐┌┐┌┌─┐╔═╗┬─┐┌─┐┌─┐┬ ┬
║  ├─┤││││ ┬║ ╦├┬┘├─┤├─┘├─┤
╩═╝┴ ┴┘└┘└─┘╚═╝┴└─┴ ┴┴  ┴ ┴

- 🚀 API: http://127.0.0.1:2024
- 🎨 Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- 📚 API Docs: http://127.0.0.1:2024/docs
```

### 2. Open LangGraph Studio

Click the Studio UI link or open:
```
https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

### 3. Select a Graph

You have two graphs available:
- **`prebuilt_supervisor`** - Easy supervisor using `create_supervisor` (~80 lines)
- **`manual_supervisor`** - Manual supervisor with full control (~200 lines)

## 📊 Available Graphs

### Graph 1: Prebuilt Supervisor
```json
{
  "graph": "prebuilt_supervisor",
  "path": "./prebuilt_supervisor.py:supervisor"
}
```

**Features:**
- ✅ Built with `create_supervisor` helper
- ✅ Automatic routing between agents
- ✅ Minimal code (~80 lines)
- ✅ Best for quick prototypes

**Architecture:**
```
User Input
    ↓
Supervisor (LLM)
    ↓
├─→ Flight Assistant (tools: book_flight, search_flights)
└─→ Hotel Assistant (tools: book_hotel, search_hotels)
    ↓
Response
```

### Graph 2: Manual Supervisor
```json
{
  "graph": "manual_supervisor",
  "path": "./manual_supervisor.py:graph"
}
```

**Features:**
- ✅ Built with `StateGraph` manually
- ✅ Explicit routing logic
- ✅ Full control (~200 lines)
- ✅ Best for production systems

**Architecture:**
```
START
  ↓
Supervisor Node (LLM decides routing)
  ↓
├─→ Flight Agent Node → back to Supervisor
└─→ Hotel Agent Node → back to Supervisor
  ↓
END (when supervisor decides FINISH)
```

## 🎮 Using the Studio

### 1. **Visual Graph View**
- See your graph structure visually
- Nodes, edges, and routing logic
- Click nodes to see their code

### 2. **Interactive Testing**
- Send messages to your graph
- See step-by-step execution
- Inspect state at each node

### 3. **Debug Mode**
- View all intermediate steps
- See tool calls and responses
- Inspect message history

### 4. **Example Queries**

Try these in the Studio:

**Simple Flight Booking:**
```
Book a flight from BOS to JFK on Dec 25th
```

**Multi-Agent Request:**
```
Book a flight from LAX to NYC on Jan 1st and a hotel in Manhattan
```

**Hotel Only:**
```
Find hotels in San Francisco for next week
```

## 📁 Configuration

### `langgraph.json`
```json
{
  "dependencies": ["."],
  "graphs": {
    "prebuilt_supervisor": "./prebuilt_supervisor.py:supervisor",
    "manual_supervisor": "./manual_supervisor.py:graph"
  },
  "env": ".env"
}
```

**Fields:**
- `dependencies`: Install local package
- `graphs`: Map graph names to Python paths
- `env`: Environment variables file

## 🔧 Troubleshooting

### Issue: "Failed to load graph"
**Solution:** Make sure you've run `uv sync` to install dependencies

### Issue: "Module not found"
**Solution:** Ensure your `.env` file exists with `OPENAI_API_KEY`

### Issue: "Graph not showing in Studio"
**Solution:** Check that the graph is properly exported:
```python
# prebuilt_supervisor.py
supervisor = create_supervisor(...).compile()

# manual_supervisor.py
graph = create_manual_supervisor()
```

### Issue: "Connection refused"
**Solution:** Make sure `langgraph dev` is running in the terminal

## 📚 API Endpoints

When the server is running, you can also use the REST API:

### List Graphs
```bash
curl http://127.0.0.1:2024/info
```

### Invoke a Graph
```bash
curl -X POST http://127.0.0.1:2024/threads/my-thread/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "prebuilt_supervisor",
    "input": {
      "messages": [
        {"role": "user", "content": "Book a flight from BOS to JFK"}
      ]
    }
  }'
```

### API Documentation
Open in browser:
```
http://127.0.0.1:2024/docs
```

## 🎯 Benefits of LangGraph Studio

1. **Visual Debugging**
   - See your graph structure
   - Understand execution flow
   - Identify bottlenecks

2. **Interactive Testing**
   - Test without writing code
   - Try different inputs quickly
   - See real-time results

3. **State Inspection**
   - View state at each step
   - Debug state transitions
   - Understand message flow

4. **Collaboration**
   - Share graph visualizations
   - Demo to stakeholders
   - Document architecture

## 🚀 Next Steps

1. **Customize the Graphs**
   - Add more agents
   - Add more tools
   - Modify routing logic

2. **Deploy to Production**
   - Use LangGraph Cloud
   - Or deploy with Docker
   - See deployment docs

3. **Add Persistence**
   - Use PostgreSQL checkpointer
   - Enable conversation history
   - Support multi-turn dialogs

## 📖 Resources

- [LangGraph Studio Docs](https://langchain-ai.github.io/langgraph/cloud/reference/cli/)
- [LangGraph v1 Guide](https://langchain-ai.github.io/langgraph/)
- [Supervisor Pattern](https://langchain-ai.github.io/langgraph/how-tos/supervisor/)

---

**Happy Visualizing!** 🎨✨
