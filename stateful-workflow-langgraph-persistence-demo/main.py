"""
Stateful Workflows with Persistence Pattern

This demonstrates how to build long-running workflows that:
1. Save state at every step (checkpointing)
2. Resume from where they left off
3. Support time-travel (go back to previous states)
4. Work across multiple sessions
5. Handle interruptions gracefully

Use Case: Multi-Day Project Management Workflow
- Day 1: Plan project
- Day 2: Execute tasks
- Day 3: Review and finalize
- Can pause/resume at any point
- Can go back and change decisions
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
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

# ============================================================================
# Environment Setup
# ============================================================================

env_path = Path(__file__).parent / ".env"
if not env_path.exists():
    print(f"⚠️  Warning: .env file not found at {env_path}")
    print("   Please copy .env.example to .env and add your API keys")
    
load_dotenv(dotenv_path=env_path, override=True)

# ============================================================================
# API Keys Configuration
# ============================================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY not found in .env file.\n"
        "Please add your OpenAI API key to .env"
    )

# LangSmith Tracing (Optional)
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"

if LANGSMITH_API_KEY and LANGSMITH_TRACING:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "stateful-workflow-demo")
    print("✅ LangSmith tracing enabled")
    print(f"   Project: {os.environ['LANGCHAIN_PROJECT']}")
else:
    print("ℹ️  LangSmith tracing disabled")

print("Using model: OpenAI GPT-4o-mini")
model = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)

# ============================================================================
# State Schema with Persistence Fields
# ============================================================================

class ProjectState(TypedDict):
    """
    State for a multi-day project workflow.
    
    This state persists across sessions, allowing work to be resumed.
    """
    # Message history
    messages: Annotated[list, add_messages]
    
    # Project information
    project_name: str
    project_description: str
    
    # Workflow stages (persisted)
    planning_complete: bool
    execution_complete: bool
    review_complete: bool
    
    # Stage outputs (persisted)
    project_plan: str  # Output from planning stage
    execution_results: list[str]  # Output from execution stage
    final_report: str  # Output from review stage
    
    # Workflow tracking
    current_stage: Literal["planning", "execution", "review", "complete", "start"]
    completed_tasks: list[str]
    pending_tasks: list[str]
    
    # Metadata
    started_at: str
    last_updated: str
    session_count: int

# ============================================================================
# Stage Nodes
# ============================================================================

def planning_stage(state: ProjectState) -> dict:
    """
    Stage 1: Project Planning
    
    Creates a detailed project plan based on the project description.
    This can take time, so state is checkpointed after completion.
    """
    system_prompt = """You are a Project Planning Expert.

Your job:
1. Analyze the project description
2. Break it down into concrete tasks
3. Estimate effort and dependencies
4. Create a structured plan

Be thorough and realistic."""

    project_desc = state.get("project_description", "")
    
    prompt = f"""Project: {state.get('project_name', 'Unnamed Project')}

Description:
{project_desc}

Please create a detailed project plan with:
1. Main objectives
2. Task breakdown (5-10 tasks)
3. Estimated timeline
4. Key dependencies
5. Success criteria

Format as a structured plan."""

    messages = [SystemMessage(content=system_prompt), HumanMessage(content=prompt)]
    response = model.invoke(messages)
    
    # Extract tasks from the plan (simple parsing for demo)
    plan_text = response.content
    tasks = []
    for line in plan_text.split("\n"):
        if any(marker in line.lower() for marker in ["task", "step", "phase"]):
            task = line.strip("- *123456789. ")
            if task and len(task) > 10:
                tasks.append(task[:100])  # Limit length
    
    return {
        "messages": [response],
        "project_plan": plan_text,
        "planning_complete": True,
        "pending_tasks": tasks[:10] if tasks else ["Task 1", "Task 2", "Task 3"],
        "current_stage": "execution",
        "last_updated": datetime.now().isoformat(),
    }

def execution_stage(state: ProjectState) -> dict:
    """
    Stage 2: Task Execution
    
    Simulates executing tasks from the plan.
    In a real system, this might take days and involve multiple sessions.
    """
    system_prompt = """You are a Task Execution Manager.

Your job:
1. Review the pending tasks
2. Simulate execution progress
3. Report on completed work
4. Identify any blockers

Be realistic about what can be accomplished."""

    plan = state.get("project_plan", "")
    pending = state.get("pending_tasks", [])
    completed = state.get("completed_tasks", [])
    
    prompt = f"""Project Plan:
{plan}

Pending Tasks:
{chr(10).join(f'- {task}' for task in pending[:5])}

Already Completed:
{chr(10).join(f'✓ {task}' for task in completed)}

Simulate executing the next 2-3 tasks and report progress."""

    messages = [SystemMessage(content=system_prompt), HumanMessage(content=prompt)]
    response = model.invoke(messages)
    
    # Simulate task completion
    tasks_to_complete = min(3, len(pending))
    newly_completed = pending[:tasks_to_complete]
    remaining_pending = pending[tasks_to_complete:]
    
    execution_results = state.get("execution_results", [])
    execution_results.append(response.content)
    
    # Check if all tasks are done
    all_done = len(remaining_pending) == 0
    
    return {
        "messages": [response],
        "execution_results": execution_results,
        "completed_tasks": completed + newly_completed,
        "pending_tasks": remaining_pending,
        "execution_complete": all_done,
        "current_stage": "review" if all_done else "execution",
        "last_updated": datetime.now().isoformat(),
    }

def review_stage(state: ProjectState) -> dict:
    """
    Stage 3: Review and Finalize
    
    Reviews all work and creates final report.
    """
    system_prompt = """You are a Project Review Specialist.

Your job:
1. Review the project plan and execution
2. Assess completion quality
3. Create a final report
4. Provide recommendations

Be thorough and constructive."""

    plan = state.get("project_plan", "")
    results = state.get("execution_results", [])
    completed = state.get("completed_tasks", [])
    
    prompt = f"""Project: {state.get('project_name', '')}

Original Plan:
{plan}

Completed Tasks ({len(completed)}):
{chr(10).join(f'✓ {task}' for task in completed)}

Execution Reports:
{chr(10).join(f'Report {i+1}: {result[:200]}...' for i, result in enumerate(results))}

Create a final project report with:
1. Executive summary
2. What was accomplished
3. Quality assessment
4. Lessons learned
5. Recommendations"""

    messages = [SystemMessage(content=system_prompt), HumanMessage(content=prompt)]
    response = model.invoke(messages)
    
    return {
        "messages": [response],
        "final_report": response.content,
        "review_complete": True,
        "current_stage": "complete",
        "last_updated": datetime.now().isoformat(),
    }

# ============================================================================
# Router
# ============================================================================

def route_workflow(state: ProjectState) -> Literal["planning", "execution", "review", "__end__"]:
    """
    Route based on current stage and completion status.
    
    This demonstrates state-aware routing with persistence.
    """
    current_stage = state.get("current_stage", "start")
    
    # Check completion flags
    planning_done = state.get("planning_complete", False)
    execution_done = state.get("execution_complete", False)
    review_done = state.get("review_complete", False)
    
    if current_stage == "complete" or review_done:
        return "__end__"
    elif not planning_done:
        return "planning"
    elif not execution_done:
        return "execution"
    else:
        return "review"

# ============================================================================
# Create Workflow with Persistence
# ============================================================================

def create_project_workflow(db_path: str = "project_checkpoints.db"):
    """
    Create a stateful workflow with SQLite persistence.
    
    Args:
        db_path: Path to SQLite database for checkpoints
        
    Returns:
        Compiled graph with checkpointer
    """
    # Create checkpointer (persists to SQLite)
    # Create connection and initialize checkpointer
    conn = sqlite3.connect(db_path, check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    
    # Build workflow
    workflow = StateGraph(ProjectState)
    
    # Add stage nodes
    workflow.add_node("planning", planning_stage)
    workflow.add_node("execution", execution_stage)
    workflow.add_node("review", review_stage)
    
    # Entry point
    workflow.add_edge(START, "planning")
    
    # Conditional routing based on state
    workflow.add_conditional_edges(
        "planning",
        route_workflow,
        {
            "planning": "planning",
            "execution": "execution",
            "review": "review",
            "__end__": END
        }
    )
    
    workflow.add_conditional_edges(
        "execution",
        route_workflow,
        {
            "planning": "planning",
            "execution": "execution",
            "review": "review",
            "__end__": END
        }
    )
    
    workflow.add_conditional_edges(
        "review",
        route_workflow,
        {
            "planning": "planning",
            "execution": "execution",
            "review": "review",
            "__end__": END
        }
    )
    
    # Compile with checkpointer
    return workflow.compile(checkpointer=checkpointer)

# Export for LangGraph server
graph = create_project_workflow()

# ============================================================================
# Helper Functions
# ============================================================================

def start_new_project(graph, project_name: str, project_description: str, thread_id: str = "project-1"):
    """Start a new project workflow"""
    initial_state = {
        "messages": [HumanMessage(content=f"Starting project: {project_name}")],
        "project_name": project_name,
        "project_description": project_description,
        "planning_complete": False,
        "execution_complete": False,
        "review_complete": False,
        "project_plan": "",
        "execution_results": [],
        "final_report": "",
        "current_stage": "planning",
        "completed_tasks": [],
        "pending_tasks": [],
        "started_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "session_count": 1,
    }
    
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"\n🚀 Starting new project: {project_name}")
    print(f"📝 Thread ID: {thread_id}")
    print("-" * 80)
    
    for event in graph.stream(initial_state, config):
        for node, values in event.items():
            print(f"\n✓ {node.upper()} stage completed")
            if "current_stage" in values:
                print(f"  Next: {values['current_stage']}")
    
    return config

def resume_project(graph, thread_id: str = "project-1"):
    """Resume a project from its last checkpoint"""
    config = {"configurable": {"thread_id": thread_id}}
    
    # Get current state
    state = graph.get_state(config)
    
    if not state or not state.values:
        print(f"❌ No project found with thread_id: {thread_id}")
        return None
    
    print(f"\n🔄 Resuming project: {state.values.get('project_name', 'Unknown')}")
    print(f"📍 Current stage: {state.values.get('current_stage', 'unknown')}")
    print(f"📊 Progress:")
    print(f"  - Planning: {'✅' if state.values.get('planning_complete') else '⏳'}")
    print(f"  - Execution: {'✅' if state.values.get('execution_complete') else '⏳'}")
    print(f"  - Review: {'✅' if state.values.get('review_complete') else '⏳'}")
    print("-" * 80)
    
    # Continue from where we left off
    for event in graph.stream(None, config):
        for node, values in event.items():
            print(f"\n✓ {node.upper()} stage completed")
            if "current_stage" in values:
                print(f"  Next: {values['current_stage']}")
    
    return config

def get_project_history(graph, thread_id: str = "project-1"):
    """Get all checkpoints for a project (time-travel)"""
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"\n📜 Project History (Thread: {thread_id})")
    print("=" * 80)
    
    checkpoints = list(graph.get_state_history(config))
    
    for i, checkpoint in enumerate(checkpoints):
        print(f"\nCheckpoint {i + 1}:")
        print(f"  Stage: {checkpoint.values.get('current_stage', 'unknown')}")
        print(f"  Completed tasks: {len(checkpoint.values.get('completed_tasks', []))}")
        print(f"  Pending tasks: {len(checkpoint.values.get('pending_tasks', []))}")
        print(f"  Last updated: {checkpoint.values.get('last_updated', 'N/A')}")
    
    return checkpoints

# ============================================================================
# Example Usage
# ============================================================================

def main():
    """Demonstrate stateful workflow with persistence"""
    print("\n" + "="*80)
    print("STATEFUL WORKFLOW WITH PERSISTENCE DEMO")
    print("="*80 + "\n")
    
    # Create workflow with SQLite persistence
    db_path = "project_checkpoints.db"
    graph = create_project_workflow(db_path)
    
    print(f"💾 Using SQLite database: {db_path}")
    print(f"   (State persists across sessions)\n")
    
    # Example 1: Start a new project
    project_name = "AI Agent Platform"
    project_description = """
    Build a production-ready AI agent platform with:
    - Multi-agent collaboration
    - State management
    - Persistence layer
    - Human-in-the-loop
    - Monitoring and observability
    """
    
    config = start_new_project(graph, project_name, project_description, "project-1")
    
    print("\n" + "="*80)
    print("✅ Project workflow complete!")
    print("="*80)
    
    # Show how to resume
    print("\n💡 To resume this project later:")
    print("   python -c \"from main import resume_project, create_project_workflow; resume_project(create_project_workflow(), 'project-1')\"")
    
    # Show how to view history
    print("\n💡 To view project history:")
    print("   python -c \"from main import get_project_history, create_project_workflow; get_project_history(create_project_workflow(), 'project-1')\"")


if __name__ == "__main__":
    main()
