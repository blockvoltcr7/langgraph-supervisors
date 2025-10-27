#!/usr/bin/env python3
"""
View detailed state using LangGraph API.
"""

from main import create_project_workflow

def view_project_state(thread_id="project-1"):
    """View complete project state."""
    graph = create_project_workflow()
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"🎯 Project State: {thread_id}")
    print("=" * 50)
    
    # Get current state
    state = graph.get_state(config)
    
    if not state.values:
        print("❌ No state found for this project")
        return
    
    values = state.values
    
    print(f"\n📋 Project Info:")
    print(f"   Name: {values.get('project_name', 'N/A')}")
    print(f"   Description: {values.get('project_description', 'N/A')[:100]}...")
    
    print(f"\n🎯 Stage Status:")
    print(f"   Current Stage: {values.get('current_stage', 'unknown')}")
    print(f"   Planning Complete: {values.get('planning_complete', False)}")
    print(f"   Execution Complete: {values.get('execution_complete', False)}")
    print(f"   Review Complete: {values.get('review_complete', False)}")
    
    print(f"\n✅ Task Progress:")
    completed = values.get('completed_tasks', [])
    pending = values.get('pending_tasks', [])
    print(f"   Completed: {len(completed)} tasks")
    print(f"   Pending: {len(pending)} tasks")
    
    if completed:
        print(f"   Completed Tasks:")
        for i, task in enumerate(completed[:5]):
            print(f"     {i+1}. {task[:80]}...")
        if len(completed) > 5:
            print(f"     ... and {len(completed) - 5} more")
    
    if pending:
        print(f"   Pending Tasks:")
        for i, task in enumerate(pending[:5]):
            print(f"     {i+1}. {task[:80]}...")
        if len(pending) > 5:
            print(f"     ... and {len(pending) - 5} more")
    
    print(f"\n📝 Work Outputs:")
    if values.get('project_plan'):
        plan = values['project_plan']
        print(f"   Project Plan: {len(plan)} characters")
        print(f"   Preview: {plan[:150]}...")
    
    if values.get('execution_results'):
        results = values['execution_results']
        print(f"   Execution Results: {len(results)} items")
        for i, result in enumerate(results[:3]):
            print(f"     {i+1}. {result[:80]}...")
    
    if values.get('final_report'):
        report = values['final_report']
        print(f"   Final Report: {len(report)} characters")
        print(f"   Preview: {report[:150]}...")
    
    print(f"\n💬 Messages:")
    messages = values.get('messages', [])
    print(f"   Total Messages: {len(messages)}")
    for i, msg in enumerate(messages[:3]):
        msg_type = msg.__class__.__name__
        content = str(msg.content)[:100] if hasattr(msg, 'content') else str(msg)[:100]
        print(f"     {i+1}. [{msg_type}] {content}...")
    
    print(f"\n📊 Metadata:")
    print(f"   Started At: {values.get('started_at', 'N/A')}")
    print(f"   Last Updated: {values.get('last_updated', 'N/A')}")
    print(f"   Session Count: {values.get('session_count', 'N/A')}")

def view_project_history(thread_id="project-1"):
    """View project checkpoint history."""
    graph = create_project_workflow()
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"\n📜 Project History: {thread_id}")
    print("=" * 50)
    
    history = list(graph.get_state_history(config))
    
    for i, checkpoint in enumerate(history):
        values = checkpoint.values
        print(f"\nCheckpoint {i+1}:")
        print(f"   Stage: {values.get('current_stage', 'unknown')}")
        print(f"   Planning: {values.get('planning_complete', False)}")
        print(f"   Execution: {values.get('execution_complete', False)}")
        print(f"   Review: {values.get('review_complete', False)}")
        print(f"   Completed: {len(values.get('completed_tasks', []))}")
        print(f"   Pending: {len(values.get('pending_tasks', []))}")
        print(f"   Messages: {len(values.get('messages', []))}")

if __name__ == "__main__":
    view_project_state()
    view_project_history()
