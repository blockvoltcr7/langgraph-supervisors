"""
Personal Assistant Supervisor with Human-in-the-Loop

This example adds human-in-the-loop review to the supervisor pattern,
allowing users to approve, edit, or reject actions before they execute.
"""

import os
from dotenv import load_dotenv, dotenv_values
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

# Load environment variables (do not override .env into process env)
load_dotenv(override=False)

# ============================================================================
# Model Configuration
# ============================================================================
# Using OpenAI GPT-4o-mini directly
# Always read the API key directly from .env (not from machine env)
_config = dotenv_values()
OPENAI_API_KEY = _config.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env. Please add it to your .env file.")

print("Using model: OpenAI GPT-4o-mini")
model = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)

# ============================================================================
# Step 1: Define low-level API tools (stubbed)
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
    return f"✅ Event created: {title} from {start_time} to {end_time} with {len(attendees)} attendees"


@tool
def send_email(
    to: list[str],  # email addresses
    subject: str,
    body: str,
    cc: list[str] = []
) -> str:
    """Send an email via email API. Requires properly formatted addresses."""
    return f"📧 Email sent to {', '.join(to)} - Subject: {subject}"


@tool
def get_available_time_slots(
    attendees: list[str],
    date: str,  # ISO format: "2024-01-15"
    duration_minutes: int
) -> list[str]:
    """Check calendar availability for given attendees on a specific date."""
    return ["09:00", "14:00", "16:00"]


# ============================================================================
# Step 2: Create specialized sub-agents with HITL middleware
# ============================================================================

# Model already initialized above

CALENDAR_AGENT_PROMPT = (
    "You are a calendar scheduling assistant. "
    "Parse natural language scheduling requests (e.g., 'next Tuesday at 2pm') "
    "into proper ISO datetime formats. "
    "Use get_available_time_slots to check availability when needed. "
    "Use create_calendar_event to schedule events. "
    "Always confirm what was scheduled in your final response."
)

# Add human-in-the-loop middleware to calendar agent
calendar_agent = create_agent(
    model,
    tools=[create_calendar_event, get_available_time_slots],
    system_prompt=CALENDAR_AGENT_PROMPT,
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={"create_calendar_event": True},
            description_prefix="📅 Calendar event pending approval",
        ),
    ],
)

EMAIL_AGENT_PROMPT = (
    "You are an email assistant. "
    "Compose professional emails based on natural language requests. "
    "Extract recipient information and craft appropriate subject lines and body text. "
    "Use send_email to send the message. "
    "Always confirm what was sent in your final response."
)

# Add human-in-the-loop middleware to email agent
email_agent = create_agent(
    model,
    tools=[send_email],
    system_prompt=EMAIL_AGENT_PROMPT,
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={"send_email": True},
            description_prefix="📧 Outbound email pending approval",
        ),
    ],
)


# ============================================================================
# Step 3: Wrap sub-agents as tools for the supervisor
# ============================================================================

@tool
def schedule_event(request: str) -> str:
    """Schedule calendar events using natural language.

    Use this when the user wants to create, modify, or check calendar appointments.
    Handles date/time parsing, availability checking, and event creation.

    Input: Natural language scheduling request (e.g., 'meeting with design team
    next Tuesday at 2pm')
    """
    result = calendar_agent.invoke({
        "messages": [{"role": "user", "content": request}]
    })
    return result["messages"][-1].content


@tool
def manage_email(request: str) -> str:
    """Send emails using natural language.

    Use this when the user wants to send notifications, reminders, or any email
    communication. Handles recipient extraction, subject generation, and email
    composition.

    Input: Natural language email request (e.g., 'send them a reminder about
    the meeting')
    """
    result = email_agent.invoke({
        "messages": [{"role": "user", "content": request}]
    })
    return result["messages"][-1].content


# ============================================================================
# Step 4: Create the supervisor agent with checkpointer
# ============================================================================

SUPERVISOR_PROMPT = (
    "You are a helpful personal assistant. "
    "You can schedule calendar events and send emails. "
    "Break down user requests into appropriate tool calls and coordinate the results. "
    "When a request involves multiple actions, use multiple tools in sequence."
)

# Add checkpointer to enable pause/resume for HITL
supervisor_agent = create_agent(
    model,
    tools=[schedule_event, manage_email],
    system_prompt=SUPERVISOR_PROMPT,
    checkpointer=InMemorySaver(),
)


# ============================================================================
# Step 5: Use the supervisor with HITL
# ============================================================================

def run_with_hitl():
    """Example with human-in-the-loop review"""
    print("\n" + "="*80)
    print("HUMAN-IN-THE-LOOP EXAMPLE")
    print("="*80 + "\n")
    
    query = (
        "Schedule a meeting with the design team next Tuesday at 2pm for 1 hour, "
        "and send them an email reminder about reviewing the new mockups."
    )
    print(f"User Request: {query}\n")
    
    config = {"configurable": {"thread_id": "demo-1"}}
    
    # First run - will interrupt for approval
    print("🔄 Running supervisor (will interrupt for approvals)...\n")
    interrupts = []
    
    for step in supervisor_agent.stream(
        {"messages": [{"role": "user", "content": query}]},
        config,
    ):
        for update in step.values():
            if isinstance(update, dict):
                for message in update.get("messages", []):
                    message.pretty_print()
            else:
                interrupt_ = update[0]
                interrupts.append(interrupt_)
                print(f"\n⏸️  INTERRUPTED: {interrupt_.id}")
    
    if not interrupts:
        print("\n✅ No interrupts - task completed!")
        return
    
    # Display interrupt details
    print("\n" + "="*80)
    print("PENDING APPROVALS")
    print("="*80 + "\n")
    
    for i, interrupt_ in enumerate(interrupts, 1):
        for request in interrupt_.value["action_requests"]:
            print(f"{i}. {request['description']}")
            print(f"   Tool: {request['tool']}")
            print(f"   Args: {request['arguments']}")
            print()
    
    # Get user decisions
    print("Options for each action:")
    print("  1. Approve")
    print("  2. Edit")
    print("  3. Reject")
    print()
    
    resume = {}
    for i, interrupt_ in enumerate(interrupts, 1):
        action_request = interrupt_.value["action_requests"][0]
        
        print(f"\nAction {i}: {action_request['tool']}")
        choice = input("Choose (1=approve, 2=edit, 3=reject): ").strip()
        
        if choice == "1":
            resume[interrupt_.id] = {"decisions": [{"type": "approve"}]}
            print("✅ Approved")
        elif choice == "2":
            edited_action = action_request.copy()
            
            # Allow editing specific fields
            if action_request['tool'] == 'send_email':
                new_subject = input(f"Edit subject (current: {action_request['arguments']['subject']}): ").strip()
                if new_subject:
                    edited_action["arguments"]["subject"] = new_subject
            elif action_request['tool'] == 'create_calendar_event':
                new_title = input(f"Edit title (current: {action_request['arguments']['title']}): ").strip()
                if new_title:
                    edited_action["arguments"]["title"] = new_title
            
            resume[interrupt_.id] = {
                "decisions": [{"type": "edit", "edited_action": edited_action}]
            }
            print("✏️  Edited and approved")
        elif choice == "3":
            resume[interrupt_.id] = {"decisions": [{"type": "reject"}]}
            print("❌ Rejected")
        else:
            # Default to approve
            resume[interrupt_.id] = {"decisions": [{"type": "approve"}]}
            print("✅ Approved (default)")
    
    # Resume execution with decisions
    print("\n" + "="*80)
    print("RESUMING EXECUTION")
    print("="*80 + "\n")
    
    for step in supervisor_agent.stream(
        Command(resume=resume),
        config,
    ):
        for update in step.values():
            if isinstance(update, dict):
                for message in update.get("messages", []):
                    message.pretty_print()
    
    print("\n✅ Task completed with your approvals!")


def main():
    """Main entry point"""
    print("\n🤖 Personal Assistant Supervisor with Human-in-the-Loop")
    print("=" * 80)
    
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ERROR: ANTHROPIC_API_KEY not found in environment variables")
        print("Please create a .env file with your API key:")
        print("  ANTHROPIC_API_KEY=your_key_here")
        return
    
    print("✅ Environment configured")
    print("✅ Agents initialized with HITL middleware")
    
    run_with_hitl()


if __name__ == "__main__":
    main()
