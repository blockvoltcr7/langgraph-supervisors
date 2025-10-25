# Limitless OS - State Schema Design

**Complete state management specification for sales conversations**

---

## Overview

The state schema is the **most critical design decision** in this architecture. It must:
- ✅ Persist across multiple sessions (days/weeks apart)
- ✅ Track qualification progress
- ✅ Maintain conversation context
- ✅ Support all agent operations
- ✅ Enable resume capability

---

## Complete State Schema

```python
from typing import Annotated, Literal, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from datetime import datetime

class SalesConversationState(TypedDict):
    """
    Complete state for Limitless OS sales conversations.
    
    This state persists to PostgreSQL via LangGraph's checkpointing system.
    Every field is carefully designed to support the sales workflow.
    """
    
    # ========================================================================
    # IDENTITY & SESSION MANAGEMENT
    # ========================================================================
    
    instagram_handle: str
    """Unique identifier for the lead (e.g., '@fitcoach_sam')"""
    
    thread_id: str
    """LangGraph thread ID for persistence (e.g., 'lead-12345')"""
    
    campaign_code: str
    """Campaign code that brought this lead (e.g., 'ABC123')"""
    
    campaign_id: str
    """Database ID of the campaign for analytics tracking"""
    
    # ========================================================================
    # MESSAGE HISTORY
    # ========================================================================
    
    messages: Annotated[list, add_messages]
    """
    Full conversation history using LangGraph's add_messages reducer.
    Automatically merges new messages while maintaining order.
    
    Contains: HumanMessage, AIMessage, ToolMessage objects
    """
    
    # ========================================================================
    # CONVERSATION STAGE
    # ========================================================================
    
    current_stage: Literal[
        "greeting",       # Initial welcome & niche verification
        "qualification",  # Asking qualification questions
        "pitch",         # Delivering sales pitch
        "objection",     # Handling objections
        "closing",       # Sending payment link
        "followup",      # Follow-up sequence
        "complete",      # Deal won (payment received)
        "nurture"        # Not qualified, save for future
    ]
    """Current stage of the conversation"""
    
    stage_history: list[str]
    """
    Track stage transitions for analytics.
    Example: ['greeting', 'qualification', 'qualification', 'pitch', 'objection', 'closing']
    """
    
    # ========================================================================
    # QUALIFICATION STATUS
    # ========================================================================
    
    qualified: bool
    """
    Main qualification flag. True if lead meets criteria:
    - Right niche (health/fitness/wellness)
    - Revenue $3K-$10K/month
    - Clear pain point
    - Ready to invest
    """
    
    qualification_score: float
    """
    Calculated score from 0.0 to 1.0
    - 0.0-0.4: Not qualified → nurture
    - 0.4-0.7: Maybe qualified → cold pitch
    - 0.7-1.0: Qualified → warm pitch
    
    Calculation:
    - Business type match: 0.3
    - Revenue range: 0.3
    - Has pain point: 0.2
    - Ready to invest: 0.2
    """
    
    # ========================================================================
    # QUALIFICATION DATA (collected during qualification stage)
    # ========================================================================
    
    business_type: Optional[str]
    """
    Type of business the lead runs.
    Examples: 'fitness coaching', 'health coaching', 'wellness coaching', 'agency', 'course creator'
    """
    
    monthly_revenue: Optional[str]
    """
    Current monthly revenue.
    Examples: 'less than $3K', '$3K-$10K', '$10K-$20K', 'over $20K'
    """
    
    current_tools: Optional[list[str]]
    """
    Tools/systems they're currently using.
    Examples: ['Instagram', 'Google Sheets', 'Calendly', 'ClickFunnels', 'Mailchimp']
    Used to calculate cost savings in pitch.
    """
    
    main_pain_point: Optional[str]
    """
    Their biggest challenge.
    Examples: 'tech overwhelm', 'inconsistent leads', 'broken tools', 'admin overload', 'low DM conversion'
    Used to personalize pitch.
    """
    
    ready_to_invest: Optional[bool]
    """
    Willingness to invest now (from qualification question 5).
    True = ready now, False = not ready, None = not asked yet
    """
    
    questions_asked: int
    """
    Count of qualification questions asked (0-5).
    Used to track progress through qualification stage.
    """
    
    # ========================================================================
    # SALES PROGRESS
    # ========================================================================
    
    pitch_delivered: bool
    """True if sales pitch has been delivered"""
    
    pitch_type: Optional[Literal["warm", "cold"]]
    """
    Which pitch was used:
    - 'warm': For high-scoring leads (>= 0.7) - shorter, assumes interest
    - 'cold': For medium-scoring leads (0.4-0.7) - longer, more detail
    """
    
    pricing_discussed: bool
    """True if pricing options have been presented"""
    
    objections_raised: list[str]
    """
    Track all objections the lead has raised.
    Examples: ['too expensive', 'no time', 'tried before', 'not tech savvy']
    Used for analytics and to avoid repeating handled objections.
    """
    
    objections_handled: list[str]
    """
    Track which objections have been addressed.
    Should be subset of objections_raised.
    """
    
    payment_link_sent: bool
    """True if Stripe payment link has been sent"""
    
    payment_completed: bool
    """True if payment has been confirmed (via Stripe webhook)"""
    
    # ========================================================================
    # USER PREFERENCES
    # ========================================================================
    
    preferred_plan: Optional[Literal["option1", "option2"]]
    """
    Which pricing plan the user prefers:
    - 'option1': $297/month + $997 one-time funnel build
    - 'option2': $497/month with funnel build included
    """
    
    email: Optional[str]
    """Email address if collected (for payment & onboarding)"""
    
    urgency_triggered: bool
    """
    Whether urgency/scarcity messaging has been used.
    Prevents overusing urgency tactics.
    """
    
    # ========================================================================
    # WORKFLOW TRACKING
    # ========================================================================
    
    total_interactions: int
    """Total number of message exchanges (back-and-forth count)"""
    
    next_agent: Literal[
        "greeter",
        "qualifier",
        "pitcher",
        "objection_handler",
        "closer",
        "followup",
        "FINISH"
    ]
    """
    Routing decision made by supervisor.
    Determines which agent should handle the next message.
    """
    
    # ========================================================================
    # METADATA & TIMESTAMPS
    # ========================================================================
    
    created_at: str
    """ISO 8601 timestamp when conversation started"""
    
    last_updated: str
    """ISO 8601 timestamp of last state update"""
    
    last_message_at: str
    """ISO 8601 timestamp of last user message (for follow-up timing)"""
    
    session_count: int
    """Number of times user has resumed conversation (1 = first session)"""
    
    # ========================================================================
    # ERROR TRACKING & DEBUGGING
    # ========================================================================
    
    errors: list[str]
    """
    Track any errors for debugging.
    Examples: ['llm_timeout', 'tool_execution_failed', 'state_validation_error']
    """
```

---

## State Initialization

### New Lead (First Contact)

```python
def create_initial_state(instagram_handle: str, campaign_code: str, campaign_id: str) -> SalesConversationState:
    """Create initial state for a new lead"""
    thread_id = f"lead-{instagram_handle.strip('@')}-{uuid.uuid4().hex[:8]}"
    
    return {
        # Identity
        "instagram_handle": instagram_handle,
        "thread_id": thread_id,
        "campaign_code": campaign_code,
        "campaign_id": campaign_id,
        
        # Messages
        "messages": [],
        
        # Stage
        "current_stage": "greeting",
        "stage_history": [],
        
        # Qualification
        "qualified": False,
        "qualification_score": 0.0,
        "business_type": None,
        "monthly_revenue": None,
        "current_tools": None,
        "main_pain_point": None,
        "ready_to_invest": None,
        "questions_asked": 0,
        
        # Sales Progress
        "pitch_delivered": False,
        "pitch_type": None,
        "pricing_discussed": False,
        "objections_raised": [],
        "objections_handled": [],
        "payment_link_sent": False,
        "payment_completed": False,
        
        # Preferences
        "preferred_plan": None,
        "email": None,
        "urgency_triggered": False,
        
        # Workflow
        "total_interactions": 0,
        "next_agent": "greeter",
        
        # Metadata
        "created_at": datetime.utcnow().isoformat(),
        "last_updated": datetime.utcnow().isoformat(),
        "last_message_at": datetime.utcnow().isoformat(),
        "session_count": 1,
        
        # Errors
        "errors": []
    }
```

---

## State Transitions

### Example: Greeting → Qualification

```python
# Initial State (Day 1, 9:00 AM)
{
    "current_stage": "greeting",
    "qualified": False,
    "qualification_score": 0.0,
    "questions_asked": 0,
    "next_agent": "greeter",
    "total_interactions": 1
}

# After Greeter Agent (Day 1, 9:01 AM)
{
    "current_stage": "qualification",  # ← Stage changed
    "stage_history": ["greeting"],     # ← History updated
    "qualified": False,
    "qualification_score": 0.0,
    "questions_asked": 0,
    "next_agent": "qualifier",         # ← Routing changed
    "total_interactions": 2            # ← Incremented
}
```

### Example: Building Qualification Data

```python
# After Question 1 (Business Type)
{
    "current_stage": "qualification",
    "business_type": "fitness coaching",  # ← Collected
    "qualification_score": 0.3,           # ← Updated
    "questions_asked": 1,                 # ← Incremented
}

# After Question 2 (Revenue)
{
    "current_stage": "qualification",
    "business_type": "fitness coaching",
    "monthly_revenue": "$5K",             # ← Collected
    "qualification_score": 0.6,           # ← Updated (0.3 + 0.3)
    "questions_asked": 2,
}

# After Question 5 (Ready to Invest)
{
    "current_stage": "qualification",
    "business_type": "fitness coaching",
    "monthly_revenue": "$5K",
    "main_pain_point": "tech overwhelm",
    "ready_to_invest": True,              # ← Collected
    "qualification_score": 0.85,          # ← Final score
    "questions_asked": 5,                 # ← All questions asked
    "qualified": True,                    # ← Flag set
    "next_agent": "pitcher"               # ← Ready for pitch
}
```

### Example: Multi-Session Resume

```python
# Session 1 - Day 1 (stopped during qualification)
{
    "instagram_handle": "@fitcoach_sam",
    "thread_id": "lead-fitcoach_sam-a1b2c3d4",
    "current_stage": "qualification",
    "qualification_score": 0.6,
    "questions_asked": 2,
    "business_type": "fitness coaching",
    "monthly_revenue": "$5K",
    "session_count": 1,
    "last_message_at": "2025-10-24T09:10:00Z"
}

# Session 2 - Day 3 (resumed 2 days later)
{
    "instagram_handle": "@fitcoach_sam",
    "thread_id": "lead-fitcoach_sam-a1b2c3d4",  # ← Same thread
    "current_stage": "qualification",             # ← Continues where left off
    "qualification_score": 0.6,                   # ← Preserved
    "questions_asked": 2,                         # ← Preserved
    "business_type": "fitness coaching",          # ← Preserved
    "monthly_revenue": "$5K",                     # ← Preserved
    "session_count": 2,                           # ← Incremented
    "last_message_at": "2025-10-26T15:30:00Z"     # ← Updated
}
```

---

## State Validation

```python
def validate_state(state: SalesConversationState) -> tuple[bool, list[str]]:
    """
    Validate state consistency and completeness.
    Returns (is_valid, error_messages)
    """
    errors = []
    
    # Required fields
    if not state.get("instagram_handle"):
        errors.append("instagram_handle is required")
    
    if not state.get("thread_id"):
        errors.append("thread_id is required")
    
    # Stage consistency
    current_stage = state.get("current_stage")
    
    if current_stage == "pitch" and not state.get("qualified"):
        errors.append("Cannot be in pitch stage without being qualified")
    
    if current_stage == "closing" and not state.get("pitch_delivered"):
        errors.append("Cannot be in closing stage without pitch delivered")
    
    if state.get("payment_completed") and not state.get("payment_link_sent"):
        errors.append("Payment cannot be completed without link being sent")
    
    # Qualification consistency
    if state.get("qualified") and state.get("qualification_score", 0) < 0.4:
        errors.append("Qualified flag true but score too low")
    
    # Objection consistency
    handled = state.get("objections_handled", [])
    raised = state.get("objections_raised", [])
    
    for obj in handled:
        if obj not in raised:
            errors.append(f"Objection '{obj}' marked as handled but not in raised list")
    
    return len(errors) == 0, errors
```

---

## State Serialization & Storage

### PostgreSQL Storage

LangGraph automatically serializes state to JSON and stores in `checkpoints` table:

```sql
-- Automatically created by LangGraph
CREATE TABLE checkpoints (
    thread_id TEXT NOT NULL,
    checkpoint_id TEXT NOT NULL,
    parent_checkpoint_id TEXT,
    checkpoint JSONB NOT NULL,  -- Full state stored here
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (thread_id, checkpoint_id)
);

-- Example query to view state
SELECT 
    thread_id,
    checkpoint->>'instagram_handle' as instagram_handle,
    checkpoint->>'current_stage' as stage,
    checkpoint->>'qualified' as qualified,
    checkpoint->>'qualification_score' as score,
    created_at
FROM checkpoints
WHERE thread_id = 'lead-fitcoach_sam-a1b2c3d4'
ORDER BY created_at DESC;
```

### Custom Indexes for Performance

```sql
-- Index for fast user lookup by Instagram handle
CREATE INDEX idx_instagram_handle 
ON checkpoints((checkpoint->>'instagram_handle'));

-- Index for finding leads in specific stages
CREATE INDEX idx_current_stage 
ON checkpoints((checkpoint->>'current_stage'));

-- Index for finding qualified leads
CREATE INDEX idx_qualified 
ON checkpoints((checkpoint->>'qualified'))
WHERE checkpoint->>'qualified' = 'true';

-- Index for finding leads needing follow-up
CREATE INDEX idx_last_message_at 
ON checkpoints((checkpoint->>'last_message_at'));
```

---

## State Query Patterns

### Find All Active Conversations

```python
def get_active_conversations(since_hours: int = 24) -> list[dict]:
    """Get all conversations with activity in last N hours"""
    cutoff = datetime.utcnow() - timedelta(hours=since_hours)
    
    query = """
    SELECT DISTINCT ON (thread_id)
        thread_id,
        checkpoint->>'instagram_handle' as instagram_handle,
        checkpoint->>'current_stage' as stage,
        checkpoint->>'last_message_at' as last_message_at
    FROM checkpoints
    WHERE (checkpoint->>'last_message_at')::timestamp > %s
    ORDER BY thread_id, created_at DESC
    """
    
    # Execute query...
    return results
```

### Find Leads Needing Follow-up

```python
def get_leads_for_followup() -> list[dict]:
    """Find leads who should receive follow-up messages"""
    
    # Day 1 follow-up: Leads who saw pitch but didn't respond
    # Day 3 follow-up: Leads still in objection stage
    # Day 5 follow-up: Final urgency message
    
    query = """
    SELECT DISTINCT ON (thread_id)
        thread_id,
        checkpoint->>'instagram_handle' as instagram_handle,
        checkpoint->>'current_stage' as stage,
        checkpoint->>'last_message_at' as last_message_at
    FROM checkpoints
    WHERE 
        checkpoint->>'current_stage' IN ('pitch', 'objection', 'followup')
        AND checkpoint->>'payment_link_sent' = 'false'
        AND (checkpoint->>'last_message_at')::timestamp < NOW() - INTERVAL '24 hours'
    ORDER BY thread_id, created_at DESC
    """
    
    return results
```

### Analytics: Conversion Funnel

```python
def get_conversion_metrics() -> dict:
    """Calculate conversion metrics across all leads"""
    
    query = """
    WITH latest_states AS (
        SELECT DISTINCT ON (thread_id)
            checkpoint->>'current_stage' as stage,
            checkpoint->>'qualified' as qualified,
            checkpoint->>'payment_completed' as payment_completed
        FROM checkpoints
        ORDER BY thread_id, created_at DESC
    )
    SELECT
        COUNT(*) as total_leads,
        COUNT(*) FILTER (WHERE qualified = 'true') as qualified_leads,
        COUNT(*) FILTER (WHERE stage IN ('pitch', 'objection', 'closing', 'followup', 'complete')) as pitched_leads,
        COUNT(*) FILTER (WHERE payment_completed = 'true') as converted_leads
    FROM latest_states
    """
    
    # Returns: {total_leads: 100, qualified_leads: 75, pitched_leads: 60, converted_leads: 15}
```

---

## State Size Optimization

### Problem: State Can Grow Large

With long conversations (50+ messages), state JSON can exceed 100KB.

### Solution 1: Message Pruning

```python
def prune_old_messages(state: SalesConversationState, keep_last_n: int = 20):
    """Keep only recent messages to reduce state size"""
    messages = state.get("messages", [])
    
    if len(messages) > keep_last_n:
        # Always keep system messages and key tool messages
        important_messages = [m for m in messages if is_important(m)]
        recent_messages = messages[-keep_last_n:]
        
        state["messages"] = important_messages + recent_messages
    
    return state
```

### Solution 2: Separate Message Storage

```python
# Store full conversation in separate table
CREATE TABLE conversation_messages (
    thread_id TEXT NOT NULL,
    message_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (thread_id, message_id)
);

# Keep only last 10 messages in state
# Retrieve full history when needed for analysis
```

---

## Best Practices

### 1. Always Update Timestamps

```python
def agent_node(state: SalesConversationState) -> dict:
    # ... agent logic ...
    
    return {
        "messages": response_messages,
        "last_updated": datetime.utcnow().isoformat(),
        # ... other updates ...
    }
```

### 2. Increment Counters

```python
return {
    "questions_asked": state["questions_asked"] + 1,
    "total_interactions": state["total_interactions"] + 1,
}
```

### 3. Append to Lists (Don't Replace)

```python
# ❌ WRONG - Replaces entire list
return {"objections_raised": ["new_objection"]}

# ✅ CORRECT - Appends to existing list
return {
    "objections_raised": state["objections_raised"] + ["new_objection"]
}
```

### 4. Track Stage Transitions

```python
new_stage = "pitch"
if state["current_stage"] != new_stage:
    return {
        "current_stage": new_stage,
        "stage_history": state["stage_history"] + [state["current_stage"]]
    }
```

### 5. Validate Before Transitions

```python
def can_transition_to_pitch(state: SalesConversationState) -> bool:
    return (
        state["questions_asked"] >= 4 and
        state["qualification_score"] >= 0.4 and
        state["business_type"] is not None
    )
```

---

**This state schema is the foundation of the entire sales agent system. Every agent reads from and writes to this shared state, enabling seamless conversation flow across multiple sessions.**
