"""
LangGraph Supervisor Agent Demo

This demonstrates a proper LangGraph supervisor pattern using StateGraph
where a central supervisor agent coordinates specialized calendar and email agents.

Unlike LangChain-only implementations, this uses LangGraph's graph-based
orchestration with explicit state management, nodes, and edges.
"""

import os
from typing import Annotated, Literal
from dotenv import load_dotenv, dotenv_values
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from langgraph.prebuilt import create_react_agent
from typing_extensions import TypedDict

# Load environment variables
load_dotenv(override=False)

# ============================================================================
# LangSmith Tracing Configuration (Optional)
# ============================================================================

_config = dotenv_values()

# Enable LangSmith tracing if API key is provided
LANGSMITH_API_KEY = _config.get("LANGSMITH_API_KEY")
LANGSMITH_TRACING = _config.get("LANGSMITH_TRACING", "false").lower() == "true"

if LANGSMITH_API_KEY and LANGSMITH_TRACING:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = _config.get("LANGCHAIN_PROJECT", "langgraph-supervisor-demo")
    print("✅ LangSmith tracing enabled")
    print(f"   Project: {os.environ['LANGCHAIN_PROJECT']}")
else:
    print("ℹ️  LangSmith tracing disabled (set LANGSMITH_TRACING=true in .env to enable)")

# ============================================================================
# Model Configuration
# ============================================================================

OPENAI_API_KEY = _config.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env. Please add it to your .env file.")

print("Using model: OpenAI GPT-4o-mini")
model = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)

# ============================================================================
# Define Low-Level Tools (stubbed for demo)
# ============================================================================

@tool
def create_calendar_event(
    title: str,
    start_time: str,  # ISO format: "2024-01-15T14:00:00"
    end_time: str,    # ISO format: "2024-01-15T15:00:00"
    attendees: list[str],  # email addresses
    location: str = ""
) -> str:
    """Create a calendar event. Requires exact ISO datetime format."""
    # Stub: In practice, this would call Google Calendar API, Outlook API, etc.
    return f"✅ Event created: {title} from {start_time} to {end_time} with {len(attendees)} attendees"


@tool
def send_email(
    to: list[str],  # email addresses
    subject: str,
    body: str,
    cc: list[str] = []
) -> str:
    """Send an email via email API. Requires properly formatted addresses."""
    # Stub: In practice, this would call SendGrid, Gmail API, etc.
    return f"📧 Email sent to {', '.join(to)} - Subject: {subject}"


@tool
def get_available_time_slots(
    attendees: list[str],
    date: str,  # ISO format: "2024-01-15"
    duration_minutes: int
) -> list[str]:
    """Check calendar availability for given attendees on a specific date."""
    # Stub: In practice, this would query calendar APIs
    return ["09:00", "14:00", "16:00"]


# ============================================================================
# Define State with Routing Decision
# ============================================================================

class SupervisorState(MessagesState):
    """Extended state that includes routing decisions"""
    next_agent: Literal["calendar", "email", "FINISH", "__start__"]


# ============================================================================
# Supervisor Node - Makes Routing Decisions
# ============================================================================

def supervisor_node(state: SupervisorState) -> dict:
    """
    Supervisor analyzes the conversation and decides which agent to route to next.
    Uses the LLM to make intelligent routing decisions.
    """
    # System prompt for the supervisor
    system_prompt = """You are a supervisor managing calendar and email agents.

Your job is to analyze the user's request and decide which agent should handle it next.

Available agents:
- calendar: Handles scheduling, availability checks, and calendar events
- email: Handles email composition and sending

Respond with ONLY ONE of these options:
- "calendar" - if the task involves scheduling, meetings, or calendar operations
- "email" - if the task involves sending emails or composing messages  
- "FINISH" - if all tasks are complete and you can provide a final response to the user

Look at the conversation history. If an agent has already completed their task, decide what to do next.
If both calendar and email tasks are needed, handle them one at a time."""

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    
    response = model.invoke(messages)
    
    # Extract the routing decision from the response
    content = response.content.strip().lower()
    
    if "calendar" in content:
        next_agent = "calendar"
    elif "email" in content:
        next_agent = "email"
    else:
        next_agent = "FINISH"
    
    return {
        "messages": [response],
        "next_agent": next_agent
    }


# ============================================================================
# Worker Agent Nodes
# ============================================================================

# Create calendar agent using prebuilt create_react_agent
calendar_agent = create_react_agent(
    model,
    tools=[create_calendar_event, get_available_time_slots],
    prompt="""You are a calendar scheduling assistant.
    
Parse natural language scheduling requests into proper ISO datetime formats.
Use the available tools to check availability and create calendar events.
Always confirm what was scheduled in your response.""",
)

def calendar_agent_node(state: SupervisorState) -> dict:
    """Calendar agent handles scheduling tasks"""
    # Invoke the prebuilt agent - it handles all tool calling logic
    result = calendar_agent.invoke(state)
    return {"messages": result["messages"]}


# Create email agent using prebuilt create_react_agent
email_agent = create_react_agent(
    model,
    tools=[send_email],
    prompt="""You are an email assistant.
    
Compose professional emails based on natural language requests.
Extract recipient information and craft appropriate subject lines and body text.
Use the send_email tool to send messages.
Always confirm what was sent in your response.""",
)

def email_agent_node(state: SupervisorState) -> dict:
    """Email agent handles email tasks"""
    # Invoke the prebuilt agent - it handles all tool calling logic
    result = email_agent.invoke(state)
    return {"messages": result["messages"]}


# ============================================================================
# Routing Function
# ============================================================================

def route_after_supervisor(state: SupervisorState) -> Literal["calendar", "email", "__end__"]:
    """Route to the next agent based on supervisor's decision"""
    next_agent = state.get("next_agent", "FINISH")
    
    if next_agent == "calendar":
        return "calendar"
    elif next_agent == "email":
        return "email"
    else:
        return "__end__"


# ============================================================================
# Create the Multi-Agent Graph
# ============================================================================

def create_supervisor_graph():
    """Create the LangGraph supervisor system with calendar and email agents."""

    # Create the state graph
    workflow = StateGraph(SupervisorState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("calendar", calendar_agent_node)
    workflow.add_node("email", email_agent_node)
    
    # Set entry point
    workflow.add_edge(START, "supervisor")
    
    # Add conditional routing from supervisor
    workflow.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "calendar": "calendar",
            "email": "email",
            "__end__": END
        }
    )
    
    # Worker agents return to supervisor
    workflow.add_edge("calendar", "supervisor")
    workflow.add_edge("email", "supervisor")
    
    return workflow.compile()


# ============================================================================
# Export Graph for LangGraph Server
# ============================================================================

# This is used by langgraph.json to expose the graph
graph = create_supervisor_graph()


# ============================================================================
# Example Usage
# ============================================================================

def run_example_1():
    """Example 1: Simple single-domain request (calendar only)"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Simple calendar request")
    print("="*80 + "\n")

    supervisor = create_supervisor_graph()
    query = "Schedule a team standup for tomorrow at 9am"

    print(f"User Request: {query}\n")
    print("Supervisor coordinating with calendar agent...\n")

    for chunk in supervisor.stream(
        {"messages": [HumanMessage(content=query)]}
    ):
        for node_name, node_update in chunk.items():
            print(f"Update from {node_name}:")
            for message in node_update["messages"][-1:]:  # Show only latest message
                if hasattr(message, 'pretty_print'):
                    message.pretty_print()
                else:
                    print(f"  {message}")
            print()


def run_example_2():
    """Example 2: Complex multi-domain request (calendar + email)"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Complex multi-domain request")
    print("="*80 + "\n")

    supervisor = create_supervisor_graph()
    query = (
        "Schedule a meeting with the design team next Tuesday at 2pm for 1 hour, "
        "and send them an email reminder about reviewing the new mockups."
    )

    print(f"User Request: {query}\n")
    print("Supervisor coordinating between calendar and email agents...\n")

    for chunk in supervisor.stream(
        {"messages": [HumanMessage(content=query)]}
    ):
        for node_name, node_update in chunk.items():
            print(f"Update from {node_name}:")
            for message in node_update["messages"][-1:]:  # Show only latest message
                if hasattr(message, 'pretty_print'):
                    message.pretty_print()
                else:
                    print(f"  {message}")
            print()


def run_interactive():
    """Interactive mode - chat with the supervisor"""
    print("\n" + "="*80)
    print("INTERACTIVE MODE")
    print("="*80)
    print("Chat with your LangGraph supervisor! (Type 'quit' to exit)\n")

    supervisor = create_supervisor_graph()

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break

        if not user_input:
            continue

        print("\nSupervisor coordinating agents...\n")
        for chunk in supervisor.stream(
            {"messages": [HumanMessage(content=user_input)]}
        ):
            for node_name, node_update in chunk.items():
                # Only show final responses from the supervisor
                if node_name == "supervisor" and node_update["messages"]:
                    latest_message = node_update["messages"][-1]
                    if hasattr(latest_message, 'content') and latest_message.content:
                        print(f"Supervisor: {latest_message.content}")
        print()


def main():
    """Main entry point"""
    print("\n🤖 LangGraph Supervisor Agent Demo")
    print("=" * 80)

    # Check for API key
    if not OPENAI_API_KEY:
        print("❌ ERROR: OPENAI_API_KEY not found in environment variables")
        print("Please create a .env file with your API key:")
        print("  OPENAI_API_KEY=your_key_here")
        return

    print("✅ Environment configured")
    print("✅ LangGraph supervisor system initialized")
    print("\nChoose a mode:")
    print("  1. Run Example 1 (Simple calendar request)")
    print("  2. Run Example 2 (Complex multi-domain request)")
    print("  3. Interactive mode")
    print("  4. Run all examples")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        run_example_1()
    elif choice == "2":
        run_example_2()
    elif choice == "3":
        run_interactive()
    elif choice == "4":
        run_example_1()
        run_example_2()
    else:
        print("Invalid choice. Running all examples...")
        run_example_1()
        run_example_2()


if __name__ == "__main__":
    main()
