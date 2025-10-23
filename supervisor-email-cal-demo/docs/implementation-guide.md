# Implementation Guide

## Code-to-Architecture Mapping

This guide shows how the code in `main.py` implements the architectural patterns described in `architecture.md`.

### Layer 1: API Tools

```python
@tool
def create_calendar_event(
    title: str,
    start_time: str,  # ISO format: "2024-01-15T14:00:00"
    end_time: str,
    attendees: list[str],
    location: str = ""
) -> str:
    """Create a calendar event. Requires exact ISO datetime format."""
    return f"✅ Event created: {title} from {start_time} to {end_time}"
```

**Architecture Role**: Bottom layer - rigid API requiring structured input

### Layer 2: Sub-Agents

```python
calendar_agent = create_agent(
    model,
    tools=[create_calendar_event, get_available_time_slots],
    system_prompt=CALENDAR_AGENT_PROMPT,
)
```

**Architecture Role**: Middle layer - translates natural language to API calls

### Layer 3: Supervisor

```python
supervisor_agent = create_agent(
    model,
    tools=[schedule_event, manage_email],
    system_prompt=SUPERVISOR_PROMPT,
)
```

**Architecture Role**: Top layer - orchestrates workflow across domains

## Flow Examples

### Simple Request Flow

```
User: "Schedule meeting tomorrow 9am"
  ↓
Supervisor: Identifies calendar domain
  ↓
schedule_event tool: Wraps calendar agent
  ↓
Calendar Agent: Parses "tomorrow 9am" → ISO
  ↓
create_calendar_event: Executes API call
  ↓
Response flows back up the chain
```

### Multi-Domain Request Flow

```
User: "Schedule meeting Tuesday 2pm, send email reminder"
  ↓
Supervisor: Identifies calendar + email domains
  ↓
schedule_event tool → Calendar Agent → API
  ↓
manage_email tool → Email Agent → API
  ↓
Supervisor synthesizes both results
```

## Key Implementation Patterns

### 1. Tool Wrapping Pattern

```python
@tool
def schedule_event(request: str) -> str:
    result = calendar_agent.invoke({
        "messages": [{"role": "user", "content": request}]
    })
    return result["messages"][-1].content
```

This wraps the sub-agent as a tool the supervisor can call.

### 2. Context Isolation

Each sub-agent only receives:
- The specific sub-request (not full conversation)
- Domain-specific tools
- Domain-specific system prompt

### 3. Natural Language Boundaries

- **Input to Supervisor**: Natural language
- **Input to Sub-Agent**: Natural language (subset)
- **Input to API**: Structured data (ISO dates, emails)
- **Output from API**: Structured response
- **Output from Sub-Agent**: Natural language
- **Output to User**: Natural language

## Human-in-the-Loop Implementation

```python
calendar_agent = create_agent(
    model,
    tools=[create_calendar_event, get_available_time_slots],
    system_prompt=CALENDAR_AGENT_PROMPT,
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={"create_calendar_event": True},
        ),
    ],
)

supervisor_agent = create_agent(
    model,
    tools=[schedule_event, manage_email],
    system_prompt=SUPERVISOR_PROMPT,
    checkpointer=InMemorySaver(),  # Required for HITL
)
```

**Key Points**:
- Middleware on sub-agents intercepts tool calls
- Checkpointer on supervisor enables pause/resume
- State persisted between interrupt and resume

## Testing Strategy

1. **Unit Test Each Layer**:
   - Test API tools with structured inputs
   - Test sub-agents with natural language
   - Test supervisor with complex requests

2. **Integration Tests**:
   - Test full flow end-to-end
   - Test multi-domain coordination
   - Test error handling

3. **HITL Tests**:
   - Test interrupt triggers
   - Test approve/edit/reject flows
   - Test state persistence

## Extending the System

### Adding a New Sub-Agent

1. Define domain-specific tools
2. Create agent with those tools
3. Wrap agent as tool
4. Add to supervisor's tool list

Example:

```python
# 1. Define tools
@tool
def query_database(sql: str) -> str:
    """Execute SQL query."""
    pass

# 2. Create agent
db_agent = create_agent(
    model,
    tools=[query_database],
    system_prompt="You are a database assistant..."
)

# 3. Wrap as tool
@tool
def search_database(request: str) -> str:
    """Search database using natural language."""
    result = db_agent.invoke({
        "messages": [{"role": "user", "content": request}]
    })
    return result["messages"][-1].content

# 4. Add to supervisor
supervisor_agent = create_agent(
    model,
    tools=[schedule_event, manage_email, search_database],
    system_prompt=SUPERVISOR_PROMPT,
)
```

## Performance Considerations

- **Token Usage**: Each sub-agent invocation = 1 LLM call
- **Latency**: Sequential sub-agent calls add latency
- **Optimization**: Consider parallel execution for independent domains
- **Caching**: Cache sub-agent responses for repeated queries

## Debugging Tips

1. **Enable LangSmith tracing** to see all LLM calls
2. **Add logging** at each layer boundary
3. **Test sub-agents independently** before integration
4. **Use streaming** to see agent reasoning in real-time
5. **Check tool descriptions** - they guide supervisor routing

## Common Pitfalls

❌ **Sub-agent doesn't include tool results in final message**
- Fix: Update system prompt to emphasize including results

❌ **Supervisor calls wrong sub-agent**
- Fix: Improve tool descriptions to be more specific

❌ **Context too large for sub-agent**
- Fix: Pass only relevant subset of conversation

❌ **HITL not triggering**
- Fix: Ensure checkpointer is on supervisor, not sub-agents

❌ **State not persisting across interrupts**
- Fix: Use persistent checkpointer (PostgreSQL/Redis) not InMemorySaver
