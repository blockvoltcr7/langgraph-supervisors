"""
Hierarchical Multi-Agent Team Pattern with LangGraph

This demonstrates a supervisor-of-supervisors architecture where:
- Top Supervisor coordinates team supervisors
- Communication Team Supervisor manages email + slack agents
- Scheduling Team Supervisor manages calendar + meeting agents

Architecture:
                    Top Supervisor
                    /            \
        Communication Team    Scheduling Team
        Supervisor            Supervisor
        /        \            /          \
    Email      Slack      Calendar    Meeting
    Agent      Agent      Agent       Agent
"""

import os
from typing import Literal
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from langgraph.prebuilt import create_react_agent

# Load environment variables from .env file
from pathlib import Path
env_path = Path(__file__).parent / ".env"
if not env_path.exists():
    print(f"⚠️  Warning: .env file not found at {env_path}")
    print("   Please copy .env.example to .env and add your API keys")
    
load_dotenv(dotenv_path=env_path, override=True)

# ============================================================================
# Model Configuration (Load First)
# ============================================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY not found in .env file.\n"
        "Please:\n"
        "1. Copy .env.example to .env\n"
        "2. Add your OpenAI API key to .env\n"
        f"   File location: {env_path}"
    )

print("Using model: OpenAI GPT-4o-mini")
model = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)

# ============================================================================
# LangSmith Tracing Configuration (Optional)
# ============================================================================

LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"

if LANGSMITH_API_KEY and LANGSMITH_TRACING:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "hierarchical-teams-demo")
    print("✅ LangSmith tracing enabled")
    print(f"   Project: {os.environ['LANGCHAIN_PROJECT']}")
else:
    print("ℹ️  LangSmith tracing disabled")

# ============================================================================
# Define Tools (Stubbed for Demo)
# ============================================================================

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to a recipient."""
    return f"📧 Email sent to {to} with subject: '{subject}'"

@tool
def send_slack_message(channel: str, message: str) -> str:
    """Send a message to a Slack channel."""
    return f"💬 Slack message sent to #{channel}: '{message}'"

@tool
def create_calendar_event(title: str, start_time: str, duration_minutes: int, attendees: list[str]) -> str:
    """Create a calendar event."""
    return f"📅 Calendar event '{title}' created for {start_time} ({duration_minutes}min) with {len(attendees)} attendees"

@tool
def schedule_meeting_room(room_name: str, start_time: str, duration_minutes: int) -> str:
    """Reserve a meeting room."""
    return f"🏢 Meeting room '{room_name}' reserved for {start_time} ({duration_minutes}min)"

# ============================================================================
# State Definition
# ============================================================================

class HierarchicalState(MessagesState):
    """Extended state for hierarchical routing"""
    next_team: Literal["communication", "scheduling", "FINISH", "__start__"]
    next_agent: Literal["email", "slack", "calendar", "meeting", "FINISH", "__start__"]

# ============================================================================
# Worker Agents (Bottom Level)
# ============================================================================

# Communication Team Agents
email_agent = create_react_agent(
    model,
    tools=[send_email],
    prompt="""You are an email assistant.
    
Compose professional emails based on requests.
Extract recipient information and craft appropriate subject lines and body text.
Always confirm what was sent.""",
)

slack_agent = create_react_agent(
    model,
    tools=[send_slack_message],
    prompt="""You are a Slack messaging assistant.
    
Send messages to Slack channels based on requests.
Keep messages concise and professional.
Always confirm what was sent.""",
)

# Scheduling Team Agents
calendar_agent = create_react_agent(
    model,
    tools=[create_calendar_event],
    prompt="""You are a calendar scheduling assistant.
    
Parse scheduling requests and create calendar events.
Extract date, time, duration, and attendees from natural language.

IMPORTANT: Make reasonable defaults if information is missing:
- Default duration: 60 minutes for meetings, 30 minutes for standups
- Default attendees: ["team"] if not specified
- Use the information provided and don't ask for more details

Always confirm what was scheduled with the defaults you used.""",
)

meeting_agent = create_react_agent(
    model,
    tools=[schedule_meeting_room],
    prompt="""You are a meeting room booking assistant.
    
Reserve meeting rooms based on requests.
Extract room preferences, time, and duration.

IMPORTANT: Make reasonable defaults if information is missing:
- Default room: "Conference Room A" if not specified
- Default duration: Match the meeting duration (60 min for meetings, 30 min for standups)
- Use the information provided and don't ask for more details

Always confirm the reservation with the defaults you used.""",
)

# ============================================================================
# Worker Agent Nodes
# ============================================================================

def email_agent_node(state: HierarchicalState) -> dict:
    """Email agent node"""
    result = email_agent.invoke(state)
    return {"messages": result["messages"]}

def slack_agent_node(state: HierarchicalState) -> dict:
    """Slack agent node"""
    result = slack_agent.invoke(state)
    return {"messages": result["messages"]}

def calendar_agent_node(state: HierarchicalState) -> dict:
    """Calendar agent node"""
    result = calendar_agent.invoke(state)
    return {"messages": result["messages"]}

def meeting_agent_node(state: HierarchicalState) -> dict:
    """Meeting room agent node"""
    result = meeting_agent.invoke(state)
    return {"messages": result["messages"]}

# ============================================================================
# Team Supervisors (Middle Level)
# ============================================================================

def communication_supervisor_node(state: HierarchicalState) -> dict:
    """Communication team supervisor - routes to email or slack agents"""
    system_prompt = """You are the Communication Team Supervisor.
    
Your team handles all communication tasks:
- email: For sending emails
- slack: For sending Slack messages

Analyze the request and conversation history.

If an agent has ALREADY completed their task (you see a confirmation message), respond with "FINISH".
If the user's request needs email and it hasn't been sent yet, respond with "email".
If the user's request needs Slack and it hasn't been posted yet, respond with "slack".

Respond with ONLY ONE of: "email", "slack", or "FINISH"."""

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = model.invoke(messages)
    
    content = response.content.strip().lower()
    if "email" in content:
        next_agent = "email"
    elif "slack" in content:
        next_agent = "slack"
    else:
        next_agent = "FINISH"
    
    return {
        "messages": [response],
        "next_agent": next_agent
    }

def scheduling_supervisor_node(state: HierarchicalState) -> dict:
    """Scheduling team supervisor - routes to calendar or meeting agents"""
    system_prompt = """You are the Scheduling Team Supervisor.
    
Your team handles all scheduling tasks:
- calendar: For creating calendar events and appointments
- meeting: For booking meeting rooms

Analyze the request and conversation history.

If an agent has ALREADY completed their task (you see a confirmation message), respond with "FINISH".
If the user's request needs calendar work and it hasn't been done yet, respond with "calendar".
If the user's request needs room booking and it hasn't been done yet, respond with "meeting".

Respond with ONLY ONE of: "calendar", "meeting", or "FINISH"."""

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = model.invoke(messages)
    
    content = response.content.strip().lower()
    if "calendar" in content:
        next_agent = "calendar"
    elif "meeting" in content:
        next_agent = "meeting"
    else:
        next_agent = "FINISH"
    
    return {
        "messages": [response],
        "next_agent": next_agent
    }

# ============================================================================
# Top Supervisor (Top Level)
# ============================================================================

def top_supervisor_node(state: HierarchicalState) -> dict:
    """Top supervisor - routes to team supervisors"""
    system_prompt = """You are the Top-Level Supervisor coordinating specialized teams.

Your teams:
- communication: Handles emails and Slack messages (managed by Communication Team Supervisor)
- scheduling: Handles calendar events and meeting rooms (managed by Scheduling Team Supervisor)

Analyze the user's request and conversation history carefully.

DECISION RULES:
1. If you see confirmation messages from agents (like "Email sent", "Event created", "Room booked"), those tasks are DONE
2. If ALL required tasks are complete, respond with "FINISH"
3. If the user's request needs scheduling and it's NOT done yet, respond with "scheduling"
4. If the user's request needs communication and it's NOT done yet, respond with "communication"
5. For multi-step requests, handle one team at a time

Respond with ONLY ONE of: "communication", "scheduling", or "FINISH"."""

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = model.invoke(messages)
    
    content = response.content.strip().lower()
    if "communication" in content:
        next_team = "communication"
    elif "scheduling" in content:
        next_team = "scheduling"
    else:
        next_team = "FINISH"
    
    return {
        "messages": [response],
        "next_team": next_team
    }

# ============================================================================
# Routing Functions
# ============================================================================

def route_from_top_supervisor(state: HierarchicalState) -> Literal["communication_team", "scheduling_team", "__end__"]:
    """Route from top supervisor to team supervisors"""
    next_team = state.get("next_team", "FINISH")
    
    if next_team == "communication":
        return "communication_team"
    elif next_team == "scheduling":
        return "scheduling_team"
    else:
        return "__end__"

def route_from_communication_team(state: HierarchicalState) -> Literal["email", "slack", "__end__"]:
    """Route from communication supervisor to worker agents"""
    next_agent = state.get("next_agent", "FINISH")
    
    if next_agent == "email":
        return "email"
    elif next_agent == "slack":
        return "slack"
    else:
        return "__end__"

def route_from_scheduling_team(state: HierarchicalState) -> Literal["calendar", "meeting", "__end__"]:
    """Route from scheduling supervisor to worker agents"""
    next_agent = state.get("next_agent", "FINISH")
    
    if next_agent == "calendar":
        return "calendar"
    elif next_agent == "meeting":
        return "meeting"
    else:
        return "__end__"

# ============================================================================
# Create Hierarchical Graph
# ============================================================================

def create_hierarchical_graph():
    """Create the hierarchical multi-agent graph"""
    
    workflow = StateGraph(HierarchicalState)
    
    # Add all nodes
    workflow.add_node("top_supervisor", top_supervisor_node)
    workflow.add_node("communication_team", communication_supervisor_node)
    workflow.add_node("scheduling_team", scheduling_supervisor_node)
    workflow.add_node("email", email_agent_node)
    workflow.add_node("slack", slack_agent_node)
    workflow.add_node("calendar", calendar_agent_node)
    workflow.add_node("meeting", meeting_agent_node)
    
    # Entry point
    workflow.add_edge(START, "top_supervisor")
    
    # Top supervisor routes to team supervisors
    workflow.add_conditional_edges(
        "top_supervisor",
        route_from_top_supervisor,
        {
            "communication_team": "communication_team",
            "scheduling_team": "scheduling_team",
            "__end__": END
        }
    )
    
    # Communication team routes to email/slack agents
    workflow.add_conditional_edges(
        "communication_team",
        route_from_communication_team,
        {
            "email": "email",
            "slack": "slack",
            "__end__": END
        }
    )
    
    # Scheduling team routes to calendar/meeting agents
    workflow.add_conditional_edges(
        "scheduling_team",
        route_from_scheduling_team,
        {
            "calendar": "calendar",
            "meeting": "meeting",
            "__end__": END
        }
    )
    
    # Worker agents return to their team supervisor
    workflow.add_edge("email", "communication_team")
    workflow.add_edge("slack", "communication_team")
    workflow.add_edge("calendar", "scheduling_team")
    workflow.add_edge("meeting", "scheduling_team")
    
    # Team supervisors return to top supervisor
    workflow.add_edge("communication_team", "top_supervisor")
    workflow.add_edge("scheduling_team", "top_supervisor")
    
    return workflow.compile()

# Export for LangGraph server
graph = create_hierarchical_graph()

# ============================================================================
# Example Usage
# ============================================================================

def main():
    """Run example queries"""
    print("\n" + "="*80)
    print("HIERARCHICAL TEAMS PATTERN DEMO")
    print("="*80 + "\n")
    
    graph = create_hierarchical_graph()
    
    # Example 1: Communication task
    print("Example 1: Communication Task")
    print("-" * 80)
    query1 = "Send an email to the team about the project update and post it in #general Slack channel"
    
    for chunk in graph.stream({"messages": [HumanMessage(content=query1)]}):
        for node, values in chunk.items():
            print(f"\n✓ Node '{node}' executed")
            if "messages" in values and values["messages"]:
                last_msg = values["messages"][-1]
                content = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
                print(f"  Content: {content[:100]}...")
    
    print("\n" + "="*80)
    
    # Example 2: Scheduling task
    print("\nExample 2: Scheduling Task")
    print("-" * 80)
    query2 = "Schedule a team meeting for tomorrow at 2pm and book the conference room"
    
    for chunk in graph.stream({"messages": [HumanMessage(content=query2)]}):
        for node, values in chunk.items():
            print(f"\n✓ Node '{node}' executed")
            if "messages" in values and values["messages"]:
                last_msg = values["messages"][-1]
                content = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
                print(f"  Content: {content[:100]}...")
    
    print("\n" + "="*80)
    print("✅ Demo complete!")


if __name__ == "__main__":
    main()
