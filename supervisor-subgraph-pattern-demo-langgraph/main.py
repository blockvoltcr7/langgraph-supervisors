"""
Customer Support System with Subgraphs - LangGraph Demo

This demonstrates subgraph patterns with:
- Technical Support Team (subgraph with isolated memory)
- Billing Team (subgraph with isolated memory)
- Top-level Coordinator (routes to appropriate team)

Key Features:
✅ Each team has its own private conversation history
✅ Teams can have different state schemas
✅ Modular, reusable components
✅ State transformation between parent and subgraphs

Use Case: Customer support tickets are routed to specialized teams.
Each team maintains their own context without seeing other teams' conversations.
"""

import os
from pathlib import Path
from typing import Literal, Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

# ============================================================================
# Load Environment Variables from .env file (NOT from system environment)
# ============================================================================

# Get the directory where this script is located
script_dir = Path(__file__).parent
env_path = script_dir / ".env"

# Load .env file, overriding any existing environment variables
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
    print(f"✅ Loaded environment from: {env_path}")
else:
    print(f"⚠️  Warning: .env file not found at {env_path}")
    print("   Please copy .env.example to .env and add your API keys")

# ============================================================================
# Configuration
# ============================================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
    raise ValueError(
        "OPENAI_API_KEY not configured properly.\n"
        "Please:\n"
        "1. Copy .env.example to .env\n"
        "2. Edit .env and add your actual OpenAI API key\n"
        f"   File location: {env_path}"
    )

model = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)

# Optional LangSmith tracing
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")

if LANGSMITH_TRACING and LANGSMITH_API_KEY and LANGSMITH_API_KEY != "your_langsmith_api_key_here":
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "subgraph-customer-support")
    print(f"✅ LangSmith tracing enabled - Project: {os.environ['LANGCHAIN_PROJECT']}")
else:
    print("ℹ️  LangSmith tracing disabled (set LANGSMITH_TRACING=true in .env to enable)")

# ============================================================================
# Tools for Technical Support Team
# ============================================================================

@tool
def check_system_status(service_name: str) -> str:
    """Check if a system or service is operational."""
    # Simulated status check
    statuses = {
        "api": "✅ API is operational (99.9% uptime)",
        "database": "✅ Database is healthy",
        "payment": "⚠️ Payment gateway experiencing 2min delays",
        "email": "✅ Email service operational",
    }
    return statuses.get(service_name.lower(), f"✅ {service_name} is operational")

@tool
def create_bug_ticket(title: str, description: str, priority: Literal["low", "medium", "high"]) -> str:
    """Create a bug ticket in the tracking system."""
    ticket_id = f"BUG-{hash(title) % 10000:04d}"
    return f"🐛 Bug ticket created: {ticket_id}\nTitle: {title}\nPriority: {priority}\nStatus: Open"

@tool
def search_knowledge_base(query: str) -> str:
    """Search technical documentation and knowledge base."""
    # Simulated KB search
    kb_articles = {
        "api": "📚 API Documentation: Use Bearer token authentication. Rate limit: 1000 req/min.",
        "error": "📚 Common Errors: Check logs at /var/log/app.log. Restart service with 'systemctl restart app'.",
        "setup": "📚 Setup Guide: Install dependencies, configure .env file, run migrations.",
    }
    for key, article in kb_articles.items():
        if key in query.lower():
            return article
    return "📚 No specific articles found. Check docs.example.com for full documentation."

# ============================================================================
# Tools for Billing Team
# ============================================================================

@tool
def lookup_invoice(customer_id: str) -> str:
    """Look up customer invoice history."""
    # Simulated invoice lookup
    return f"💳 Customer {customer_id} Invoices:\n- INV-001: $99.00 (Paid - Jan 2025)\n- INV-002: $99.00 (Paid - Feb 2025)\n- INV-003: $99.00 (Due - Mar 2025)"

@tool
def process_refund(invoice_id: str, amount: float, reason: str) -> str:
    """Process a refund for a customer."""
    return f"💰 Refund processed:\nInvoice: {invoice_id}\nAmount: ${amount:.2f}\nReason: {reason}\nStatus: Approved - Funds will arrive in 3-5 business days"

@tool
def update_subscription(customer_id: str, plan: Literal["basic", "pro", "enterprise"]) -> str:
    """Update customer subscription plan."""
    return f"📊 Subscription updated for {customer_id}\nNew Plan: {plan.upper()}\nEffective: Immediately\nNext billing: Prorated on next cycle"

# ============================================================================
# Subgraph 1: Technical Support Team
# ============================================================================

class TechSupportState(MessagesState):
    """State for technical support team - includes private context"""
    ticket_created: bool = False
    issue_resolved: bool = False

def create_tech_support_subgraph():
    """Create technical support team as a subgraph with isolated memory"""
    
    # Create specialized agent for technical support
    tech_agent = create_react_agent(
        model,
        tools=[check_system_status, create_bug_ticket, search_knowledge_base],
        prompt="""You are a Technical Support Specialist.

Your responsibilities:
- Diagnose technical issues
- Check system status
- Search knowledge base for solutions
- Create bug tickets for unresolved issues

Be thorough and technical. Always check system status first, then search KB.
If you can't resolve the issue, create a bug ticket with details.

IMPORTANT: After taking actions, provide a clear summary of what you did."""
    )
    
    def tech_agent_node(state: TechSupportState):
        """Technical support agent node"""
        result = tech_agent.invoke(state)
        
        # Check if ticket was created or issue resolved
        last_message = result["messages"][-1]
        ticket_created = "ticket created" in str(last_message.content).lower()
        issue_resolved = "operational" in str(last_message.content).lower()
        
        return {
            "messages": result["messages"],
            "ticket_created": ticket_created,
            "issue_resolved": issue_resolved
        }
    
    # Build the subgraph
    builder = StateGraph(TechSupportState)
    builder.add_node("tech_agent", tech_agent_node)
    builder.add_edge(START, "tech_agent")
    builder.add_edge("tech_agent", END)
    
    # Compile without checkpointer - parent graph will handle persistence
    # Note: Subgraphs still maintain isolated state schemas
    return builder.compile()

# ============================================================================
# Subgraph 2: Billing Team
# ============================================================================

class BillingState(MessagesState):
    """State for billing team - includes private context"""
    refund_processed: bool = False
    subscription_updated: bool = False

def create_billing_subgraph():
    """Create billing team as a subgraph with isolated memory"""
    
    # Create specialized agent for billing
    billing_agent = create_react_agent(
        model,
        tools=[lookup_invoice, process_refund, update_subscription],
        prompt="""You are a Billing Support Specialist.

Your responsibilities:
- Look up customer invoices and payment history
- Process refunds when appropriate
- Update subscription plans

Be empathetic and clear about billing matters. Always look up invoice history first.
For refunds, verify the invoice exists before processing.

IMPORTANT: After taking actions, provide a clear summary of what you did."""
    )
    
    def billing_agent_node(state: BillingState):
        """Billing support agent node"""
        result = billing_agent.invoke(state)
        
        # Check if actions were taken
        last_message = result["messages"][-1]
        refund_processed = "refund processed" in str(last_message.content).lower()
        subscription_updated = "subscription updated" in str(last_message.content).lower()
        
        return {
            "messages": result["messages"],
            "refund_processed": refund_processed,
            "subscription_updated": subscription_updated
        }
    
    # Build the subgraph
    builder = StateGraph(BillingState)
    builder.add_node("billing_agent", billing_agent_node)
    builder.add_edge(START, "billing_agent")
    builder.add_edge("billing_agent", END)
    
    # Compile without checkpointer - parent graph will handle persistence
    # Note: Subgraphs still maintain isolated state schemas
    return builder.compile()

# ============================================================================
# Parent Graph: Customer Support Coordinator
# ============================================================================

class CoordinatorState(MessagesState):
    """Parent state for the coordinator"""
    assigned_team: Literal["tech", "billing", "none"] = "none"

def create_coordinator_graph():
    """Create the main coordinator graph that routes to subgraphs"""
    
    # Compile subgraphs
    tech_support_subgraph = create_tech_support_subgraph()
    billing_subgraph = create_billing_subgraph()
    
    def coordinator_node(state: CoordinatorState):
        """Coordinator decides which team to route to"""
        system_prompt = """You are a Customer Support Coordinator.

Analyze the customer's request and decide which team should handle it:
- "tech" - Technical issues, bugs, system status, API problems, errors
- "billing" - Payment issues, invoices, refunds, subscription changes
- "none" - If the request is unclear or you need more information

Respond with ONLY ONE WORD: "tech", "billing", or "none"."""
        
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = model.invoke(messages)
        
        content = response.content.strip().lower()
        if "tech" in content:
            assigned_team = "tech"
        elif "billing" in content:
            assigned_team = "billing"
        else:
            assigned_team = "none"
        
        return {
            "messages": [response],
            "assigned_team": assigned_team
        }
    
    def tech_team_node(state: CoordinatorState):
        """Route to technical support subgraph"""
        # Invoke the subgraph - it has isolated state schema
        result = tech_support_subgraph.invoke(
            {"messages": state["messages"]}
        )
        return {"messages": result["messages"]}
    
    def billing_team_node(state: CoordinatorState):
        """Route to billing subgraph"""
        # Invoke the subgraph - it has isolated state schema
        result = billing_subgraph.invoke(
            {"messages": state["messages"]}
        )
        return {"messages": result["messages"]}
    
    def clarification_node(state: CoordinatorState):
        """Ask for clarification if request is unclear"""
        clarification = AIMessage(
            content="I'd be happy to help! Could you please clarify if this is a technical issue or a billing question?"
        )
        return {"messages": [clarification]}
    
    def route_to_team(state: CoordinatorState) -> Literal["tech_team", "billing_team", "clarification", "__end__"]:
        """Route based on coordinator's decision"""
        assigned = state.get("assigned_team", "none")
        
        if assigned == "tech":
            return "tech_team"
        elif assigned == "billing":
            return "billing_team"
        elif assigned == "none":
            return "clarification"
        else:
            return "__end__"
    
    # Build the parent graph
    builder = StateGraph(CoordinatorState)
    builder.add_node("coordinator", coordinator_node)
    builder.add_node("tech_team", tech_team_node)
    builder.add_node("billing_team", billing_team_node)
    builder.add_node("clarification", clarification_node)
    
    builder.add_edge(START, "coordinator")
    builder.add_conditional_edges(
        "coordinator",
        route_to_team,
        {
            "tech_team": "tech_team",
            "billing_team": "billing_team",
            "clarification": "clarification",
            "__end__": END
        }
    )
    builder.add_edge("tech_team", END)
    builder.add_edge("billing_team", END)
    builder.add_edge("clarification", END)
    
    # Compile parent graph with checkpointer
    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)

# Export for LangGraph server
graph = create_coordinator_graph()

# ============================================================================
# Demo Usage
# ============================================================================

def main():
    """Run example customer support scenarios"""
    print("\n" + "="*80)
    print("CUSTOMER SUPPORT SYSTEM WITH SUBGRAPHS")
    print("="*80 + "\n")
    
    graph = create_coordinator_graph()
    
    # Example 1: Technical Support Request
    print("📋 Example 1: Technical Support Request")
    print("-" * 80)
    query1 = "The API is returning 500 errors. Can you check if the service is down?"
    
    config1 = {"configurable": {"thread_id": "customer-123"}}
    
    for chunk in graph.stream({"messages": [HumanMessage(content=query1)]}, config1):
        for node, values in chunk.items():
            print(f"\n✓ Node: {node}")
            if "messages" in values and values["messages"]:
                last_msg = values["messages"][-1]
                if hasattr(last_msg, 'content'):
                    print(f"  {last_msg.content[:200]}...")
    
    print("\n" + "="*80)
    
    # Example 2: Billing Request
    print("\n📋 Example 2: Billing Request")
    print("-" * 80)
    query2 = "I need a refund for invoice INV-003. I was charged twice by mistake."
    
    config2 = {"configurable": {"thread_id": "customer-456"}}
    
    for chunk in graph.stream({"messages": [HumanMessage(content=query2)]}, config2):
        for node, values in chunk.items():
            print(f"\n✓ Node: {node}")
            if "messages" in values and values["messages"]:
                last_msg = values["messages"][-1]
                if hasattr(last_msg, 'content'):
                    print(f"  {last_msg.content[:200]}...")
    
    print("\n" + "="*80)
    
    # Example 3: Ambiguous Request
    print("\n📋 Example 3: Ambiguous Request")
    print("-" * 80)
    query3 = "I need help with something"
    
    config3 = {"configurable": {"thread_id": "customer-789"}}
    
    for chunk in graph.stream({"messages": [HumanMessage(content=query3)]}, config3):
        for node, values in chunk.items():
            print(f"\n✓ Node: {node}")
            if "messages" in values and values["messages"]:
                last_msg = values["messages"][-1]
                if hasattr(last_msg, 'content'):
                    print(f"  {last_msg.content}")
    
    print("\n" + "="*80)
    print("\n✅ Demo complete!")
    print("\n💡 Key Takeaways:")
    print("   - Each team (tech/billing) has isolated STATE SCHEMAS")
    print("   - Tech tracks: ticket_created, issue_resolved")
    print("   - Billing tracks: refund_processed, subscription_updated")
    print("   - Coordinator routes requests to appropriate subgraphs")
    print("   - Subgraphs are modular and reusable components")


if __name__ == "__main__":
    main()
