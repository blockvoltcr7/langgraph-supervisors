# 🏗️ Hierarchical Multi-Agent Teams Pattern

A **supervisor-of-supervisors** architecture demonstrating how to scale multi-agent systems using LangGraph's hierarchical team pattern.

## 📐 Architecture

```
                    Top Supervisor
                    /            \
        Communication Team    Scheduling Team
        Supervisor            Supervisor
        /        \            /          \
    Email      Slack      Calendar    Meeting
    Agent      Agent      Agent       Agent
```

### Three Levels of Coordination:

1. **Top Supervisor** - Coordinates team supervisors
2. **Team Supervisors** - Manage specialized worker agents
3. **Worker Agents** - Execute specific tasks with tools

## 🎯 Features

- ✅ **3-Level Hierarchy** - Top supervisor → Team supervisors → Worker agents
- ✅ **2 Specialized Teams** - Communication & Scheduling
- ✅ **4 Worker Agents** - Email, Slack, Calendar, Meeting Room
- ✅ **Intelligent Routing** - Each level makes smart delegation decisions
- ✅ **Agent Chat UI Ready** - Works with LangSmith Studio
- ✅ **LangSmith Tracing** - Full observability across all levels

## 🚀 Quick Start

### 1. Install Dependencies

```bash
uv sync
```

### 2. Set Up Environment

Copy `.env.example` to `.env` and add your keys:

```bash
cp .env.example .env
```

Edit `.env`:
```env
OPENAI_API_KEY=your_key_here
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_key
```

### 3. Run the Demo

```bash
source .venv/bin/activate
python main.py
```

## 💬 Example Queries

### Communication Tasks:
```
"Send an email to the team about the project update and post it in #general Slack channel"
```

**Flow:**
1. Top Supervisor → Routes to Communication Team
2. Communication Supervisor → Routes to Email Agent
3. Email Agent → Sends email
4. Communication Supervisor → Routes to Slack Agent
5. Slack Agent → Posts message
6. Top Supervisor → Returns final response

### Scheduling Tasks:
```
"Schedule a team meeting for tomorrow at 2pm and book the conference room"
```

**Flow:**
1. Top Supervisor → Routes to Scheduling Team
2. Scheduling Supervisor → Routes to Calendar Agent
3. Calendar Agent → Creates event
4. Scheduling Supervisor → Routes to Meeting Agent
5. Meeting Agent → Books room
6. Top Supervisor → Returns final response

## 🎨 Use with Agent Chat UI

### Start the LangGraph Server:

```bash
langgraph dev
```

### Connect to Agent Chat UI:

1. Go to: **https://agentchat.vercel.app**
2. Fill in:
   ```
   Deployment URL: http://localhost:2024
   Assistant / Graph ID: hierarchical
   LangSmith API Key: <your-key>
   ```
3. Start chatting!

## 📊 How It Works

### State Management

```python
class HierarchicalState(MessagesState):
    next_team: Literal["communication", "scheduling", "FINISH"]
    next_agent: Literal["email", "slack", "calendar", "meeting", "FINISH"]
```

### Routing Pattern

**Top Supervisor** → Decides which team
**Team Supervisors** → Decide which agent
**Worker Agents** → Execute tasks

## 🛠️ Customization

### Add More Teams

```python
# Add a CRM team
def crm_supervisor_node(state):
    # Route to contacts, deals, reports agents
    pass
```

### Add Real APIs

Replace stubbed tools with:
- Gmail API
- Slack API
- Google Calendar API
- Room booking systems

## 📚 Resources

- [LangGraph Hierarchical Teams Tutorial](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/hierarchical_agent_teams/)
- [Multi-Agent Patterns](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)
- [Agent Chat UI](https://github.com/langchain-ai/agent-chat-ui)

---

**Built with LangGraph** 🦜🔗