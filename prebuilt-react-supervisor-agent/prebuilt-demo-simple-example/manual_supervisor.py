"""
Manual Supervisor Example (LangGraph v1)

This demonstrates the MANUAL way to create a supervisor multi-agent system.
400+ lines of code for full control.

Use Case: Travel Booking Assistant (Same as prebuilt)
- Flight booking agent
- Hotel booking agent  
- Supervisor coordinates them

Updated for LangGraph v1 / LangChain v1:
- Using create_agent instead of create_react_agent
- Using system_prompt parameter instead of prompt
"""

import os
from typing import Annotated, Literal
from pathlib import Path
from dotenv import load_dotenv

from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.agents import create_agent  # LangChain v1

# Load environment
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file")

model = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)

# ============================================================================
# Define Tools (Same as prebuilt)
# ============================================================================

@tool
def book_flight(from_airport: str, to_airport: str, date: str) -> str:
    """Book a flight from one airport to another on a specific date."""
    return f"✈️ Successfully booked flight from {from_airport} to {to_airport} on {date}"

@tool
def search_flights(from_airport: str, to_airport: str) -> str:
    """Search for available flights between two airports."""
    return f"🔍 Found 5 flights from {from_airport} to {to_airport}: AA101, UA202, DL303, SW404, B6505"

@tool
def book_hotel(hotel_name: str, check_in: str, check_out: str) -> str:
    """Book a hotel room for specific dates."""
    return f"🏨 Successfully booked {hotel_name} from {check_in} to {check_out}"

@tool
def search_hotels(location: str) -> str:
    """Search for available hotels in a location."""
    return f"🔍 Found 3 hotels in {location}: Marriott, Hilton, Hyatt"

# ============================================================================
# State Schema (Manual - need to define this)
# ============================================================================

class SupervisorState(TypedDict):
    """State for supervisor pattern"""
    messages: Annotated[list, add_messages]
    next_agent: Literal["flight", "hotel", "FINISH", "__start__"]

# ============================================================================
# Create Agents using create_agent (LangChain v1)
# ============================================================================

flight_agent = create_agent(
    model=model,
    tools=[book_flight, search_flights],
    system_prompt="You are a flight booking specialist. Help users search and book flights."
)

hotel_agent = create_agent(
    model=model,
    tools=[book_hotel, search_hotels],
    system_prompt="You are a hotel booking specialist. Help users search and book hotels."
)

# ============================================================================
# Agent Node Wrappers (Manual - need to wrap agents)
# ============================================================================

def flight_agent_node(state: SupervisorState) -> dict:
    """Flight agent node"""
    result = flight_agent.invoke(state)
    return {"messages": result["messages"]}

def hotel_agent_node(state: SupervisorState) -> dict:
    """Hotel agent node"""
    result = hotel_agent.invoke(state)
    return {"messages": result["messages"]}

# ============================================================================
# Supervisor Node (Manual - need to implement routing logic)
# ============================================================================

def supervisor_node(state: SupervisorState) -> dict:
    """
    Supervisor decides which agent to route to.
    This is what create_supervisor does automatically!
    """
    system_prompt = """You are a travel coordinator managing flight and hotel booking assistants.

Your team:
- flight: Handles flight searches and bookings
- hotel: Handles hotel searches and bookings

Analyze the user's request and decide which assistant should handle it.
Respond with ONLY ONE of: "flight", "hotel", or "FINISH" (if task is complete).

Look at the conversation history. If an assistant has completed their task, 
decide what to do next or finish."""

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = model.invoke(messages)
    
    # Parse response to determine routing
    content = response.content.strip().lower()
    if "flight" in content:
        next_agent = "flight"
    elif "hotel" in content:
        next_agent = "hotel"
    else:
        next_agent = "FINISH"
    
    return {
        "messages": [response],
        "next_agent": next_agent
    }

# ============================================================================
# Routing Function (Manual - need to implement)
# ============================================================================

def route_supervisor(state: SupervisorState) -> Literal["flight", "hotel", "__end__"]:
    """Route based on supervisor's decision"""
    next_agent = state.get("next_agent", "flight")
    
    if next_agent == "flight":
        return "flight"
    elif next_agent == "hotel":
        return "hotel"
    else:
        return "__end__"

# ============================================================================
# Build Graph (Manual - need to construct everything)
# ============================================================================

def create_manual_supervisor():
    """
    Manually build the supervisor graph.
    This is what create_supervisor does for you automatically!
    """
    # Create graph
    workflow = StateGraph(SupervisorState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("flight", flight_agent_node)
    workflow.add_node("hotel", hotel_agent_node)
    
    # Entry point
    workflow.add_edge(START, "supervisor")
    
    # Supervisor routes to agents
    workflow.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "flight": "flight",
            "hotel": "hotel",
            "__end__": END
        }
    )
    
    # Agents return to supervisor
    workflow.add_edge("flight", "supervisor")
    workflow.add_edge("hotel", "supervisor")
    
    # Compile
    return workflow.compile()

# Create the supervisor
supervisor = create_manual_supervisor()

# Export for LangGraph server
graph = supervisor

# ============================================================================
# Example Usage (Same as prebuilt)
# ============================================================================

def main():
    """Run example queries"""
    print("\n" + "="*80)
    print("MANUAL SUPERVISOR DEMO")
    print("="*80 + "\n")
    
    print("Using manual graph building - ~200 lines of code!\n")
    
    # Example 1: Simple flight booking
    print("Example 1: Book a flight")
    print("-" * 80)
    
    for chunk in supervisor.stream(
        {
            "messages": [HumanMessage(content="Book a flight from BOS to JFK on Dec 25th")],
            "next_agent": "flight"
        },
        stream_mode="values"
    ):
        if "messages" in chunk:
            last_message = chunk["messages"][-1]
            print(f"{last_message.type}: {last_message.content[:100]}...")
    
    print("\n" + "="*80)
    
    # Example 2: Multi-step request
    print("\nExample 2: Book flight AND hotel")
    print("-" * 80)
    
    for chunk in supervisor.stream(
        {
            "messages": [HumanMessage(content="Book a flight from LAX to NYC on Jan 1st and a hotel in Manhattan")],
            "next_agent": "flight"
        },
        stream_mode="values"
    ):
        if "messages" in chunk:
            last_message = chunk["messages"][-1]
            print(f"{last_message.type}: {last_message.content[:100]}...")
    
    print("\n" + "="*80)
    print("✅ Done! Notice how much more code this required!")
    print("="*80)


if __name__ == "__main__":
    main()
