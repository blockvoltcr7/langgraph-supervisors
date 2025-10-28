#!/usr/bin/env python3
"""
Simple test to verify Supabase persistence works.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from main import create_project_workflow
from langchain_core.messages import HumanMessage

# Load environment
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

print("🧪 Simple Supabase Persistence Test")
print("=" * 50)

# Create graph
print("\n1. Creating workflow...")
graph = create_project_workflow()
print("   ✓ Workflow created")

# Create initial state
initial_state = {
    "messages": [HumanMessage(content="Test project")],
    "project_name": "Test Project",
    "project_description": "A simple test",
    "planning_complete": False,
    "execution_complete": False,
    "review_complete": False,
    "project_plan": "",
    "execution_results": [],
    "final_report": "",
    "current_stage": "planning",
    "completed_tasks": [],
    "pending_tasks": [],
    "started_at": "2025-01-01T00:00:00",
    "last_updated": "2025-01-01T00:00:00",
    "session_count": 1,
}

config = {"configurable": {"thread_id": "test-1"}}

print("\n2. Running workflow (will save to Supabase)...")
try:
    for i, event in enumerate(graph.stream(initial_state, config)):
        print(f"   Step {i+1}: {list(event.keys())}")
        if i > 5:  # Safety limit
            break
    print("   ✓ Workflow executed")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n3. Checking if data was saved...")
try:
    state = graph.get_state(config)
    if state and state.values:
        print(f"   ✓ State retrieved!")
        print(f"   Project: {state.values.get('project_name')}")
        print(f"   Stage: {state.values.get('current_stage')}")
    else:
        print("   ❌ No state found")
except Exception as e:
    print(f"   ❌ Error retrieving state: {e}")

print("\n✅ Test complete!")
print("=" * 50)
