# 🔍 How Stateful Workflow Persistence Works

This document explains in detail how the stateful workflow persistence demo works, focusing on state management and database operations.

## 📋 Table of Contents

1. [Overview](#overview)
2. [State Schema](#state-schema)
3. [Database Operations](#database-operations)
4. [Workflow Execution](#workflow-execution)
5. [Checkpointing Mechanism](#checkpointing-mechanism)
6. [Resume & Time-Travel](#resume--time-travel)

---

## Overview

This demo shows how to build **long-running workflows** that can:
- ✅ Save state at every step
- ✅ Resume from where they left off
- ✅ Work across multiple sessions (days/weeks)
- ✅ Support time-travel (go back to previous states)
- ✅ Handle interruptions gracefully

### Use Case: Multi-Day Project Management

```
Day 1: Plan project → Save to DB
Day 2: Execute tasks → Save to DB
Day 3: Review results → Save to DB
```

---

## State Schema

### What Gets Stored?

The `ProjectState` contains everything needed to resume the workflow:

```python
class ProjectState(TypedDict):
    # Message history (conversation with AI)
    messages: Annotated[list, add_messages]
    
    # Project information
    project_name: str
    project_description: str
    
    # Workflow stages (boolean flags)
    planning_complete: bool
    execution_complete: bool
    review_complete: bool
    
    # Stage outputs (actual work done)
    project_plan: str              # From planning stage
    execution_results: list[str]   # From execution stage
    final_report: str              # From review stage
    
    # Workflow tracking
    current_stage: Literal["planning", "execution", "review", "complete", "start"]
    completed_tasks: list[str]
    pending_tasks: list[str]
    
    # Metadata
    started_at: str
    last_updated: str
    session_count: int
```

### State Flow Diagram

```mermaid
graph TD
    A[Initial State] -->|Planning| B[State + project_plan]
    B -->|Execution| C[State + execution_results]
    C -->|Review| D[State + final_report]
    D -->|Complete| E[Final State]
    
```

---

## Database Operations

### SQLite Database Structure

The `SqliteSaver` creates and manages checkpoint tables:

```mermaid
erDiagram
    CHECKPOINTS {
        string thread_id PK
        string checkpoint_ns
        string checkpoint_id PK
        string parent_checkpoint_id
        blob checkpoint
        blob metadata
        timestamp created_at
    }
    
    WRITES {
        string thread_id FK
        string checkpoint_ns
        string checkpoint_id FK
        string task_id
        int idx
        string channel
        blob value
    }
```

### What Gets Written to Database?

#### 1. **Checkpoint Record** (Main State Snapshot)

Every time a node completes, a checkpoint is saved:

```json
{
  "thread_id": "project-1",
  "checkpoint_id": "1ef2a3b4-5678-90cd-ef12-34567890abcd",
  "checkpoint": {
    "v": 1,
    "ts": "2025-10-27T00:00:00",
    "channel_values": {
      "messages": [...],
      "project_name": "AI Agent Platform",
      "project_plan": "...",
      "current_stage": "execution",
      "planning_complete": true,
      "execution_complete": false,
      "completed_tasks": ["Task 1", "Task 2"],
      "pending_tasks": ["Task 3", "Task 4"],
      ...
    }
  }
}
```

#### 2. **Writes Record** (Incremental Updates)

Each node's output is recorded:

```json
{
  "thread_id": "project-1",
  "checkpoint_id": "1ef2a3b4-...",
  "channel": "planning",
  "value": {
    "project_plan": "...",
    "planning_complete": true,
    "pending_tasks": [...]
  }
}
```

### Database Operations Timeline

```mermaid
sequenceDiagram
    participant User
    participant Graph
    participant Node
    participant DB as SQLite DB
    
    User->>Graph: invoke(initial_state, config)
    Graph->>DB: Load checkpoint (thread_id)
    
    alt No checkpoint found
        DB-->>Graph: null
        Graph->>Node: Execute planning_stage
    else Checkpoint exists
        DB-->>Graph: Previous state
        Graph->>Node: Resume from current_stage
    end
    
    Node->>Node: Process & update state
    Node-->>Graph: Return updates
    Graph->>DB: Save checkpoint
    DB-->>Graph: Checkpoint ID
    Graph-->>User: Result
```

---

## Workflow Execution

### Complete Workflow Diagram

```mermaid
graph TB
    START([START]) --> Planning[Planning Stage]
    
    Planning -->|planning_complete=true| Execution[Execution Stage]
    Planning -->|Loop| Planning
    
    Execution -->|All tasks done| Review[Review Stage]
    Execution -->|More tasks| Execution
    
    Review -->|review_complete=true| END([END])
    
    Planning -.->|Checkpoint| DB[(SQLite DB)]
    Execution -.->|Checkpoint| DB
    Review -.->|Checkpoint| DB

```

### Stage-by-Stage Breakdown

#### **Stage 1: Planning**

```mermaid
flowchart LR
    A[Input: project_description] --> B[LLM: Create Plan]
    B --> C[Parse Tasks]
    C --> D[Update State]
    D --> E[Save Checkpoint]
    
    E --> F{State Updates}
    F -->|project_plan| G[Full plan text]
    F -->|pending_tasks| H[List of tasks]
    F -->|planning_complete| I[true]
    F -->|current_stage| J[execution]
```

**What's Written to DB:**
```python
{
    "project_plan": "Detailed project plan...",
    "pending_tasks": ["Task 1", "Task 2", "Task 3"],
    "planning_complete": True,
    "current_stage": "execution",
    "last_updated": "2025-10-27T00:00:00"
}
```

#### **Stage 2: Execution**

```mermaid
flowchart LR
    A[Read: pending_tasks] --> B[LLM: Execute Tasks]
    B --> C[Simulate Work]
    C --> D[Update Progress]
    D --> E[Save Checkpoint]
    
    E --> F{State Updates}
    F -->|completed_tasks| G[Append completed]
    F -->|pending_tasks| H[Remove completed]
    F -->|execution_results| I[Add results]
    F -->|current_stage| J[execution or review]
```

**What's Written to DB:**
```python
{
    "completed_tasks": ["Task 1", "Task 2"],
    "pending_tasks": ["Task 3", "Task 4"],
    "execution_results": ["Result 1", "Result 2"],
    "execution_complete": False,  # or True if done
    "current_stage": "execution",  # or "review"
    "last_updated": "2025-10-27T01:00:00"
}
```

#### **Stage 3: Review**

```mermaid
flowchart LR
    A[Read: execution_results] --> B[LLM: Review Work]
    B --> C[Generate Report]
    C --> D[Update State]
    D --> E[Save Checkpoint]
    
    E --> F{State Updates}
    F -->|final_report| G[Complete report]
    F -->|review_complete| H[true]
    F -->|current_stage| I[complete]
```

**What's Written to DB:**
```python
{
    "final_report": "Project completed successfully...",
    "review_complete": True,
    "current_stage": "complete",
    "last_updated": "2025-10-27T02:00:00"
}
```

---

## Checkpointing Mechanism

### How Checkpointing Works

```mermaid
sequenceDiagram
    participant Node
    participant Graph
    participant Checkpointer
    participant SQLite
    
    Note over Node,SQLite: Before Node Execution
    Graph->>Checkpointer: get_checkpoint(thread_id)
    Checkpointer->>SQLite: SELECT * WHERE thread_id=?
    SQLite-->>Checkpointer: Previous checkpoint
    Checkpointer-->>Graph: State snapshot
    
    Note over Node,SQLite: Node Execution
    Graph->>Node: invoke(state)
    Node->>Node: Process & update
    Node-->>Graph: Return updates
    
    Note over Node,SQLite: After Node Execution
    Graph->>Checkpointer: put_checkpoint(thread_id, new_state)
    Checkpointer->>SQLite: INSERT checkpoint
    Checkpointer->>SQLite: INSERT writes
    SQLite-->>Checkpointer: Success
    Checkpointer-->>Graph: Checkpoint ID
```

### Checkpoint Anatomy

Each checkpoint contains:

1. **Checkpoint ID**: Unique identifier (UUID)
2. **Thread ID**: Session identifier (e.g., "project-1")
3. **Parent Checkpoint ID**: Previous checkpoint (for time-travel)
4. **Channel Values**: Complete state snapshot
5. **Metadata**: Timestamp, version, etc.

```mermaid
graph TD
    A[Checkpoint 1<br/>Planning Complete] -->|parent_id| B[Checkpoint 2<br/>Task 1 Done]
    B -->|parent_id| C[Checkpoint 3<br/>Task 2 Done]
    C -->|parent_id| D[Checkpoint 4<br/>Review Complete]

```

---

## Resume & Time-Travel

### Resume from Last Checkpoint

```mermaid
flowchart TD
    A[User: Resume project-1] --> B{Load Checkpoint}
    B -->|Found| C[Read current_stage]
    B -->|Not Found| D[Start from beginning]
    
    C --> E{current_stage?}
    E -->|planning| F[Continue planning]
    E -->|execution| G[Continue execution]
    E -->|review| H[Continue review]
    E -->|complete| I[Already done]

```

### Time-Travel to Previous State

```mermaid
sequenceDiagram
    participant User
    participant Graph
    participant DB
    
    User->>Graph: get_state_history(thread_id)
    Graph->>DB: SELECT all checkpoints
    DB-->>Graph: List of checkpoints
    Graph-->>User: [checkpoint1, checkpoint2, ...]
    
    User->>Graph: Resume from checkpoint2
    Graph->>DB: Load checkpoint2
    DB-->>Graph: State at checkpoint2
    Graph->>Graph: Continue from there
```

### Example: Resume After 3 Days

```mermaid
gantt
    title Multi-Day Project Workflow
    dateFormat  YYYY-MM-DD
    section Day 1
    Planning Stage           :done, 2025-10-27, 1d
    Save Checkpoint 1        :milestone, 2025-10-27, 0d
    
    section Day 2
    Load Checkpoint 1        :milestone, 2025-10-28, 0d
    Execute Tasks 1-3        :done, 2025-10-28, 1d
    Save Checkpoint 2        :milestone, 2025-10-28, 0d
    
    section Day 3
    Load Checkpoint 2        :milestone, 2025-10-29, 0d
    Execute Tasks 4-5        :done, 2025-10-29, 0.5d
    Review Stage             :done, 2025-10-29, 0.5d
    Save Checkpoint 3        :milestone, 2025-10-29, 0d
```

---

## Key Concepts Summary

### 1. **Thread ID** = Session Identifier

```python
config = {"configurable": {"thread_id": "project-1"}}
```

- Same thread ID = Same project/session
- Different thread ID = Different project/session
- Thread ID links all checkpoints together

### 2. **Checkpoint** = State Snapshot

- Saved after every node execution
- Contains complete state
- Immutable (never modified, only new ones created)

### 3. **Resume** = Load + Continue

```python
# First session
result1 = graph.invoke(initial_state, config)

# Later session (same thread_id)
result2 = graph.invoke(None, config)  # Resumes automatically
```

### 4. **Time-Travel** = Load Old Checkpoint

```python
# Get history
history = list(graph.get_state_history(config))

# Go back to checkpoint 2
old_state = history[2]
graph.update_state(config, old_state.values)
```

---

## Database Query Examples

### What's in the Database?

```sql
-- View all checkpoints for a project
SELECT 
    checkpoint_id,
    thread_id,
    created_at,
    json_extract(checkpoint, '$.channel_values.current_stage') as stage
FROM checkpoints
WHERE thread_id = 'project-1'
ORDER BY created_at;

-- View state at specific checkpoint
SELECT 
    json_extract(checkpoint, '$.channel_values') as state
FROM checkpoints
WHERE checkpoint_id = '1ef2a3b4-...';

-- View all writes for a checkpoint
SELECT 
    channel,
    value
FROM writes
WHERE thread_id = 'project-1'
AND checkpoint_id = '1ef2a3b4-...'
ORDER BY idx;
```

---

## Complete Data Flow

```mermaid
graph TB
    subgraph "Session 1: Day 1"
        A1[User Input] --> B1[Planning Node]
        B1 --> C1[State Update]
        C1 --> D1[(DB: Checkpoint 1)]
    end
    
    subgraph "Session 2: Day 2"
        D1 -.->|Load| E2[Resume State]
        E2 --> F2[Execution Node]
        F2 --> G2[State Update]
        G2 --> H2[(DB: Checkpoint 2)]
    end
    
    subgraph "Session 3: Day 3"
        H2 -.->|Load| I3[Resume State]
        I3 --> J3[Execution Node]
        J3 --> K3[Review Node]
        K3 --> L3[State Update]
        L3 --> M3[(DB: Checkpoint 3)]
    end
    
```

---

## 🎯 Key Takeaways

1. **Everything is saved**: Complete state after every node
2. **Thread ID is key**: Links all checkpoints for a project
3. **Immutable checkpoints**: Never modified, only new ones created
4. **Resume is automatic**: Just use same thread_id
5. **Time-travel is possible**: Access any previous checkpoint
6. **SQLite is simple**: Just a file, no server needed
7. **State is complete**: Can reconstruct entire workflow history

This pattern enables:
- ✅ Long-running workflows (days/weeks)
- ✅ Fault tolerance (crash recovery)
- ✅ Audit trails (who did what when)
- ✅ Debugging (replay from any point)
- ✅ Collaboration (multiple users, same project)
