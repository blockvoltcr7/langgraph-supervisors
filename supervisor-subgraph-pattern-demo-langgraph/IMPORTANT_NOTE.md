# ⚠️ Important Note About Subgraph Memory

## Key Clarification

This example demonstrates **isolated state schemas** in subgraphs, NOT separate memory/checkpointers.

### What This Example Shows

✅ **Isolated State Schemas:**
- Tech team has `TechSupportState` with `ticket_created`, `issue_resolved`
- Billing team has `BillingState` with `refund_processed`, `subscription_updated`
- Parent has `CoordinatorState` with `assigned_team`
- Each team tracks different information

✅ **Modular Components:**
- Subgraphs are self-contained units
- Can be reused in multiple parent graphs
- Easy to test independently

✅ **State Transformation:**
- Parent only sees shared `messages` key
- Team-specific state stays within subgraph
- Clean separation of concerns

### What This Example Does NOT Show

❌ **Separate Memory Checkpointers:**
- Subgraphs do NOT have `checkpointer=True`
- All persistence is handled by parent graph's checkpointer
- Conversation history is shared (via `messages` key)

### Why Not Separate Checkpointers?

When you invoke a subgraph as a node in a parent graph:
```python
# This DOES NOT WORK:
subgraph = builder.compile(checkpointer=True)

# Error: RuntimeError: checkpointer=True cannot be used for root graphs
```

The reason:
- `checkpointer=True` is only for graphs that will be deployed as standalone services
- When a subgraph is invoked as a node, it's not a "root" graph
- The parent graph's checkpointer handles all persistence

### How to Get Separate Memory (If Needed)

If you truly need separate conversation histories per team, you have two options:

#### Option 1: Use Different Thread IDs (Within Same Checkpointer)
```python
# In parent graph
def tech_team_node(state):
    # Use a different thread_id for tech team
    result = tech_subgraph.invoke(
        {"messages": state["messages"]},
        config={"configurable": {"thread_id": f"tech-{state['customer_id']}"}}
    )
    return {"messages": result["messages"]}
```

#### Option 2: Deploy Subgraphs as Separate Services
```python
# Deploy tech subgraph as standalone service
tech_subgraph = builder.compile(checkpointer=MemorySaver())

# Then call it via HTTP/API from parent graph
# (This is more complex but gives true isolation)
```

## What Makes This Example Valuable

Even without separate checkpointers, this example demonstrates:

1. **Different State Schemas** - Core subgraph feature
2. **Modular Architecture** - Reusable components
3. **Clean Interfaces** - Parent doesn't know team internals
4. **Real-world Pattern** - How to structure multi-agent systems

## Comparison Table

| Feature | This Example | With Separate Checkpointers |
|---------|-------------|----------------------------|
| **State Schemas** | ✅ Different per team | ✅ Different per team |
| **Modularity** | ✅ Fully modular | ✅ Fully modular |
| **Conversation History** | ❌ Shared | ✅ Separate |
| **Complexity** | Low | High |
| **Use Case** | Most applications | Privacy-critical systems |

## When You Need Separate Memory

Use separate checkpointers when:
- **Privacy/Security**: Teams must not see each other's conversations
- **Multi-tenant**: Different customers need isolated histories
- **Compliance**: Regulations require data separation
- **Scale**: Teams are deployed as separate services

For most applications, **shared memory with isolated state schemas** (this example) is sufficient!

## Summary

This example focuses on:
- ✅ **Isolated state schemas** (different fields per team)
- ✅ **Modular subgraphs** (reusable components)
- ✅ **Clean architecture** (separation of concerns)

Not on:
- ❌ Separate conversation histories
- ❌ Independent checkpointers
- ❌ Complete memory isolation

Both patterns are valid! This one is simpler and works for most use cases.
