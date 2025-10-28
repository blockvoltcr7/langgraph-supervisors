"""
Prebuilt Supervisor Example using create_supervisor (LangGraph v1)

This demonstrates the EASY way to create a supervisor multi-agent system.
Just 50 lines of code vs 400+ lines manual!

Use Case: Travel Booking Assistant
- Flight booking agent
- Hotel booking agent  
- Supervisor coordinates them

Updated for LangGraph v1 / LangChain v1:
- Using create_agent instead of create_react_agent
- Using system_prompt parameter instead of prompt
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent  # LangChain v1
from langgraph_supervisor import create_supervisor

# Load environment
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file")

# ============================================================================
# Define Tools (Same as manual approach)
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
# Create Agents using create_agent (LangChain v1)
# ============================================================================

# Initialize model
model = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)

# Flight agent - handles all flight-related tasks
flight_agent = create_agent(
    model=model,
    tools=[book_flight, search_flights],
    system_prompt="You are a flight booking specialist. Help users search and book flights.",
    name="flight_assistant"  # IMPORTANT: Name is required for supervisor
)

# Hotel agent - handles all hotel-related tasks
hotel_agent = create_agent(
    model=model,
    tools=[book_hotel, search_hotels],
    system_prompt="You are a hotel booking specialist. Help users search and book hotels.",
    name="hotel_assistant"  # IMPORTANT: Name is required for supervisor
)

# ============================================================================
# Create Supervisor using create_supervisor (Prebuilt Helper #2)
# ============================================================================

# This ONE function call does what took 400+ lines manually!
supervisor = create_supervisor(
    agents=[flight_agent, hotel_agent],
    model=ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY),
    prompt=(
        "You are a travel coordinator managing flight and hotel booking assistants. "
        "Route user requests to the appropriate assistant. "
        "The flight assistant handles flights, the hotel assistant handles hotels."
    )
).compile()

# ============================================================================
# That's it! The supervisor is ready to use!
# ============================================================================

def main():
    """Run example queries"""
    print("\n" + "="*80)
    print("PREBUILT SUPERVISOR DEMO")
    print("="*80 + "\n")
    
    print("Using create_supervisor - Just ~80 lines of code!\n")
    
    # Example 1: Simple flight booking
    print("Example 1: Book a flight")
    print("-" * 80)
    
    for chunk in supervisor.stream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Book a flight from BOS to JFK on Dec 25th"
                }
            ]
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
            "messages": [
                {
                    "role": "user",
                    "content": "Book a flight from LAX to NYC on Jan 1st and a hotel in Manhattan"
                }
            ]
        },
        stream_mode="values"
    ):
        if "messages" in chunk:
            last_message = chunk["messages"][-1]
            print(f"{last_message.type}: {last_message.content[:100]}...")
    
    print("\n" + "="*80)
    print("✅ Done! Notice how simple this was!")
    print("="*80)


if __name__ == "__main__":
    main()
