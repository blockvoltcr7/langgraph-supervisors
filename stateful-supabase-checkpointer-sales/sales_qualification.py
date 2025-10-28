"""
Sales Qualification Workflow with Supabase Persistence (No FastAPI)

This demonstrates a sales qualification workflow where:
1. Users are qualified based on budget ($300 minimum)
2. Qualified users are routed to a closer agent
3. Closer sends Stripe payment link
4. All state persists in Supabase across sessions

Run directly with Python - no API needed!
"""

import os
from typing import Annotated, Literal
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.postgres import PostgresSaver

# ============================================================================
# Environment Setup
# ============================================================================

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env file")

# LangSmith Tracing (Optional)
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"

if LANGSMITH_API_KEY and LANGSMITH_TRACING:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "sales-qualification-demo")
    print("✅ LangSmith tracing enabled")
else:
    print("ℹ️  LangSmith tracing disabled")

print("Using model: OpenAI GPT-4o-mini")
model = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)

# ============================================================================
# Initialize Checkpointer (Module Level)
# ============================================================================

_db_url = DATABASE_URL.replace('postgresql+psycopg://', 'postgresql://')
_checkpointer_cm = PostgresSaver.from_conn_string(_db_url)
_CHECKPOINTER = _checkpointer_cm.__enter__()

try:
    _CHECKPOINTER.setup()
    print(f"✅ Supabase checkpointer initialized for sales workflow")
except Exception as e:
    print(f"⚠️  Warning: Could not setup checkpointer: {e}")
    _CHECKPOINTER = None

# ============================================================================
# State Schema
# ============================================================================

class SalesState(TypedDict):
    """
    State for sales qualification workflow.
    
    This state persists across sessions in Supabase.
    """
    # Message history
    messages: Annotated[list, add_messages]
    
    # User identification
    user_id: str  # Instagram handle or unique identifier
    
    # Qualification status
    qualification: bool  # True if qualified, False if not
    can_afford: bool  # Can they afford $300?
    budget: int  # Their stated budget
    
    # Workflow stage
    current_stage: str  # "qualifying" | "closing" | "disqualified" | "complete"
    
    # Closer actions
    stripe_link_sent: bool
    stripe_link: str
    
    # Metadata
    started_at: str
    last_updated: str

# ============================================================================
# Agent Nodes
# ============================================================================

def qualifier_agent(state: SalesState):
    """
    Qualifier Agent - Determines if user can afford the $300 program.
    """
    messages = state.get("messages", [])
    
    # If we haven't asked about budget yet
    if state.get("can_afford") is None:
        system_prompt = """You are a friendly sales qualification agent.
        
Your job is to determine if the user can afford a $300 program.

Ask them directly: "Can you afford to invest $300 in this program?"

Be friendly and professional. Wait for their response."""
        
        response = model.invoke([
            SystemMessage(content=system_prompt),
            *messages
        ])
        
        return {
            "messages": [response],
            "current_stage": "qualifying",
            "last_updated": datetime.now().isoformat()
        }
    
    # Analyze their response
    last_message = messages[-1].content if messages else ""
    
    # Simple keyword detection (in production, use LLM to extract structured data)
    response_lower = last_message.lower()
    can_afford = any(word in response_lower for word in ["yes", "yeah", "sure", "afford", "can"])
    
    if can_afford:
        response = AIMessage(content="Excellent! You're qualified for our program. Let me connect you with our closer who will help you complete your enrollment.")
        
        return {
            "messages": [response],
            "qualification": True,
            "can_afford": True,
            "budget": 300,
            "current_stage": "closing",
            "last_updated": datetime.now().isoformat()
        }
    else:
        response = AIMessage(content="I understand. Unfortunately, this program requires a $300 investment. Feel free to reach out when you're ready!")
        
        return {
            "messages": [response],
            "qualification": False,
            "can_afford": False,
            "current_stage": "disqualified",
            "last_updated": datetime.now().isoformat()
        }

def closer_agent(state: SalesState):
    """
    Closer Agent - Sends Stripe payment link to qualified users.
    """
    messages = state.get("messages", [])
    
    # Generate Stripe link (in production, create actual Stripe checkout session)
    stripe_link = f"https://buy.stripe.com/test_{state['user_id']}_300"
    
    if not state.get("stripe_link_sent"):
        response = AIMessage(
            content=f"🎉 Perfect! Here's your payment link to enroll in the program:\n\n{stripe_link}\n\nClick the link to complete your $300 payment and get instant access!"
        )
        
        return {
            "messages": [response],
            "stripe_link_sent": True,
            "stripe_link": stripe_link,
            "current_stage": "complete",
            "last_updated": datetime.now().isoformat()
        }
    else:
        # Already sent link, just acknowledge
        response = AIMessage(
            content=f"I've already sent you the payment link: {state['stripe_link']}\n\nLet me know if you need any help!"
        )
        
        return {
            "messages": [response],
            "last_updated": datetime.now().isoformat()
        }

# ============================================================================
# Routing Logic
# ============================================================================

def route_conversation(state: SalesState) -> Literal["qualifier", "closer", "__end__"]:
    """
    Route to appropriate agent based on current stage.
    """
    current_stage = state.get("current_stage", "qualifying")
    
    if current_stage == "qualifying":
        return "qualifier"
    elif current_stage == "closing":
        return "closer"
    elif current_stage in ["disqualified", "complete"]:
        return END
    else:
        return "qualifier"  # Default to qualifier

# ============================================================================
# Build Graph
# ============================================================================

def create_sales_graph():
    """
    Create the sales qualification graph with Supabase persistence.
    """
    if not _CHECKPOINTER:
        raise ValueError("Checkpointer not initialized. Check DATABASE_URL in .env")
    
    # Build workflow
    workflow = StateGraph(SalesState)
    
    # Add agent nodes
    workflow.add_node("qualifier", qualifier_agent)
    workflow.add_node("closer", closer_agent)
    
    # Entry point
    workflow.add_edge(START, "qualifier")
    
    # Conditional routing
    workflow.add_conditional_edges(
        "qualifier",
        route_conversation,
        {
            "qualifier": "qualifier",
            "closer": "closer",
            "__end__": END
        }
    )
    
    workflow.add_conditional_edges(
        "closer",
        route_conversation,
        {
            "qualifier": "qualifier",
            "closer": "closer",
            "__end__": END
        }
    )
    
    # Compile with checkpointer
    return workflow.compile(checkpointer=_CHECKPOINTER)

# Export graph
graph = create_sales_graph()

# ============================================================================
# Helper Functions
# ============================================================================

def start_new_conversation(user_id: str, initial_message: str = "Hi, I'm interested in the program"):
    """
    Start a new sales conversation.
    
    Args:
        user_id: Unique identifier (e.g., Instagram handle)
        initial_message: User's first message
    """
    config = {"configurable": {"thread_id": user_id}}
    
    initial_state = {
        "messages": [HumanMessage(content=initial_message)],
        "user_id": user_id,
        "qualification": None,
        "can_afford": None,
        "budget": 0,
        "current_stage": "qualifying",
        "stripe_link_sent": False,
        "stripe_link": "",
        "started_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }
    
    print(f"\n🚀 Starting new conversation for {user_id}")
    print(f"👤 User: {initial_message}")
    print("-" * 80)
    
    for event in graph.stream(initial_state, config):
        for node, values in event.items():
            if "messages" in values and values["messages"]:
                ai_message = values["messages"][-1].content
                print(f"\n🤖 AI ({node}): {ai_message}")
            
            if "current_stage" in values:
                print(f"📊 Stage: {values['current_stage']}")
    
    return config

def continue_conversation(user_id: str, message: str):
    """
    Continue an existing conversation.
    
    Args:
        user_id: Unique identifier
        message: User's message
    """
    config = {"configurable": {"thread_id": user_id}}
    
    # Check if conversation exists
    state = graph.get_state(config)
    
    if not state.values:
        print(f"❌ No conversation found for {user_id}. Starting new conversation...")
        return start_new_conversation(user_id, message)
    
    print(f"\n💬 Continuing conversation for {user_id}")
    print(f"👤 User: {message}")
    print("-" * 80)
    
    for event in graph.stream({"messages": [HumanMessage(content=message)]}, config):
        for node, values in event.items():
            if "messages" in values and values["messages"]:
                ai_message = values["messages"][-1].content
                print(f"\n🤖 AI ({node}): {ai_message}")
            
            if "current_stage" in values:
                print(f"📊 Stage: {values['current_stage']}")
    
    return config

def get_conversation_status(user_id: str):
    """
    Get the current status of a conversation.
    """
    config = {"configurable": {"thread_id": user_id}}
    state = graph.get_state(config)
    
    if not state.values:
        print(f"\n❌ No conversation found for {user_id}")
        return None
    
    print(f"\n📊 Status for {user_id}")
    print("=" * 80)
    print(f"Qualified: {state.values.get('qualification')}")
    print(f"Can Afford: {state.values.get('can_afford')}")
    print(f"Current Stage: {state.values.get('current_stage')}")
    print(f"Stripe Link Sent: {state.values.get('stripe_link_sent')}")
    if state.values.get('stripe_link'):
        print(f"Stripe Link: {state.values.get('stripe_link')}")
    print(f"Started: {state.values.get('started_at')}")
    print(f"Last Updated: {state.values.get('last_updated')}")
    print(f"Total Messages: {len(state.values.get('messages', []))}")
    
    return state.values

def view_conversation_history(user_id: str):
    """
    View the full conversation history.
    """
    config = {"configurable": {"thread_id": user_id}}
    state = graph.get_state(config)
    
    if not state.values:
        print(f"\n❌ No conversation found for {user_id}")
        return
    
    messages = state.values.get("messages", [])
    
    print(f"\n📜 Conversation History for {user_id}")
    print("=" * 80)
    
    for i, msg in enumerate(messages, 1):
        msg_type = msg.__class__.__name__
        content = msg.content
        
        if msg_type == "HumanMessage":
            print(f"\n{i}. 👤 User:")
        elif msg_type == "AIMessage":
            print(f"\n{i}. 🤖 AI:")
        else:
            print(f"\n{i}. 📋 System:")
        
        print(f"   {content}")
    
    print("\n" + "=" * 80)

# ============================================================================
# Example Usage / Main Demo
# ============================================================================

def main():
    """
    Demonstrate the sales qualification workflow.
    """
    print("\n" + "="*80)
    print("SALES QUALIFICATION WORKFLOW - SUPABASE PERSISTENCE DEMO")
    print("="*80 + "\n")
    
    print("💾 Using Supabase database (PostgreSQL)")
    print("   (State persists in the cloud)\n")
    
    # Example 1: New user starts conversation
    print("\n" + "🔹"*40)
    print("  EXAMPLE 1: New User (@sarah_coach)")
    print("🔹"*40)
    
    config1 = start_new_conversation("@sarah_coach", "Hi, I'm interested in your program")
    
    # User responds
    print("\n" + "-"*80)
    continue_conversation("@sarah_coach", "Yes, I can afford $300")
    
    # Check status
    get_conversation_status("@sarah_coach")
    
    # Example 2: User who can't afford
    print("\n\n" + "🔹"*40)
    print("  EXAMPLE 2: Disqualified User (@broke_user)")
    print("🔹"*40)
    
    start_new_conversation("@broke_user", "Tell me about the program")
    print("\n" + "-"*80)
    continue_conversation("@broke_user", "No, I can't afford $300")
    
    # Example 3: Multi-session conversation
    print("\n\n" + "🔹"*40)
    print("  EXAMPLE 3: Multi-Session (@fitness_pro)")
    print("🔹"*40)
    
    print("\n📅 Day 1 (Monday):")
    start_new_conversation("@fitness_pro", "Hi there!")
    
    print("\n📅 Day 2 (Wednesday - User Returns):")
    continue_conversation("@fitness_pro", "I'm back! Yes, I can afford it")
    
    print("\n📅 Day 3 (Friday - Ready to Pay):")
    continue_conversation("@fitness_pro", "Send me the payment link")
    
    # View history
    view_conversation_history("@fitness_pro")
    
    print("\n" + "="*80)
    print("✅ Demo Complete!")
    print("="*80)
    
    print("\n💡 Key Takeaways:")
    print("   1. Conversations persist across sessions in Supabase")
    print("   2. Users can leave and return days later")
    print("   3. State is automatically saved to cloud database")
    print("   4. No re-qualification needed")
    print("   5. Works across any device/channel")
    
    print("\n🎉 Your sales qualification workflow is working with Supabase!\n")

if __name__ == "__main__":
    main()
