"""
Personal Assistant Supervisor Example

This example demonstrates the supervisor pattern for multi-agent systems.
A supervisor agent coordinates specialized sub-agents (calendar and email)
that are wrapped as tools.
"""

import os
from dotenv import load_dotenv, dotenv_values
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

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
# Step 2: Create specialized sub-agents
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

calendar_agent = create_agent(
    model,
    tools=[create_calendar_event, get_available_time_slots],
    system_prompt=CALENDAR_AGENT_PROMPT,
)

EMAIL_AGENT_PROMPT = (
    "You are an email assistant. "
    "Compose professional emails based on natural language requests. "
    "Extract recipient information and craft appropriate subject lines and body text. "
    "Use send_email to send the message. "
    "Always confirm what was sent in your final response."
)

email_agent = create_agent(
    model,
    tools=[send_email],
    system_prompt=EMAIL_AGENT_PROMPT,
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
# Step 4: Create the supervisor agent
# ============================================================================

SUPERVISOR_PROMPT = (
    "You are a helpful personal assistant. "
    "You can schedule calendar events and send emails. "
    "Break down user requests into appropriate tool calls and coordinate the results. "
    "When a request involves multiple actions, use multiple tools in sequence."
)

supervisor_agent = create_agent(
    model,
    tools=[schedule_event, manage_email],
    system_prompt=SUPERVISOR_PROMPT,
)


# ============================================================================
# Step 5: Use the supervisor
# ============================================================================

def run_example_1():
    """Example 1: Simple single-domain request"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Simple single-domain request")
    print("="*80 + "\n")
    
    query = "Schedule a team standup for tomorrow at 9am"
    print(f"User Request: {query}\n")
    
    for step in supervisor_agent.stream(
        {"messages": [{"role": "user", "content": query}]}
    ):
        for update in step.values():
            for message in update.get("messages", []):
                message.pretty_print()


def run_example_2():
    """Example 2: Complex multi-domain request"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Complex multi-domain request")
    print("="*80 + "\n")
    
    query = (
        "Schedule a meeting with the design team next Tuesday at 2pm for 1 hour, "
        "and send them an email reminder about reviewing the new mockups."
    )
    print(f"User Request: {query}\n")
    
    for step in supervisor_agent.stream(
        {"messages": [{"role": "user", "content": query}]}
    ):
        for update in step.values():
            for message in update.get("messages", []):
                message.pretty_print()


def run_interactive():
    """Interactive mode - chat with the supervisor"""
    print("\n" + "="*80)
    print("INTERACTIVE MODE")
    print("="*80)
    print("Chat with your personal assistant! (Type 'quit' to exit)\n")
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        print("\nAssistant:")
        for step in supervisor_agent.stream(
            {"messages": [{"role": "user", "content": user_input}]}
        ):
            for update in step.values():
                for message in update.get("messages", []):
                    message.pretty_print()
        print()


def main():
    """Main entry point"""
    print("\n🤖 Personal Assistant Supervisor Demo")
    print("=" * 80)
    
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ERROR: ANTHROPIC_API_KEY not found in environment variables")
        print("Please create a .env file with your API key:")
        print("  ANTHROPIC_API_KEY=your_key_here")
        return
    
    print("✅ Environment configured")
    print("✅ Agents initialized")
    print("\nChoose a mode:")
    print("  1. Run Example 1 (Simple request)")
    print("  2. Run Example 2 (Complex request)")
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
