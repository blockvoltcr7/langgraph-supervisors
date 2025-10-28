#!/usr/bin/env python3
"""
Query the database using LangGraph's built-in methods.
"""

import sqlite3
from main import create_project_workflow

def inspect_database():
    """Inspect the database using LangGraph's methods."""
    
    # Create graph with checkpointer
    graph = create_project_workflow()
    
    # Configuration for project-1
    config = {"configurable": {"thread_id": "project-1"}}
    
    print("🔍 Inspecting Database with LangGraph")
    print("=" * 50)
    
    # Get current state
    current_state = graph.get_state(config)
    
    print("\n=== Current State ===")
    if current_state.values:
        state = current_state.values
        print(f"Project Name: {state.get('project_name', 'N/A')}")
        print(f"Current Stage: {state.get('current_stage', 'unknown')}")
        print(f"Planning Complete: {state.get('planning_complete', False)}")
        print(f"Execution Complete: {state.get('execution_complete', False)}")
        print(f"Review Complete: {state.get('review_complete', False)}")
        print(f"Completed Tasks: {len(state.get('completed_tasks', []))}")
        print(f"Pending Tasks: {len(state.get('pending_tasks', []))}")
        print(f"Messages: {len(state.get('messages', []))}")
        print(f"Last Updated: {state.get('last_updated', 'N/A')}")
    else:
        print("No state found for project-1")
    
    # Get history
    print("\n=== Project History ===")
    history = list(graph.get_state_history(config))
    print(f"Total checkpoints: {len(history)}")
    
    for i, checkpoint in enumerate(history):
        state = checkpoint.values
        print(f"\nCheckpoint {i+1}:")
        print(f"  Stage: {state.get('current_stage', 'unknown')}")
        print(f"  Planning: {state.get('planning_complete', False)}")
        print(f"  Execution: {state.get('execution_complete', False)}")
        print(f"  Review: {state.get('review_complete', False)}")
        print(f"  Completed tasks: {len(state.get('completed_tasks', []))}")
        print(f"  Pending tasks: {len(state.get('pending_tasks', []))}")
        print(f"  Messages: {len(state.get('messages', []))}")
        
        # Show some details for first few checkpoints
        if i < 3:
            if state.get('project_plan'):
                print(f"  Project Plan: {state['project_plan'][:100]}...")
            if state.get('execution_results'):
                print(f"  Execution Results: {len(state['execution_results'])} items")
            if state.get('final_report'):
                print(f"  Final Report: {state['final_report'][:100]}...")
    
    # Show detailed view of latest checkpoint
    if history:
        latest = history[0]
        print(f"\n=== Latest Checkpoint Details ===")
        state = latest.values
        
        print(f"\n📋 Project Info:")
        print(f"  Name: {state.get('project_name', 'N/A')}")
        print(f"  Description: {state.get('project_description', 'N/A')[:200]}...")
        
        print(f"\n🎯 Stage Status:")
        print(f"  Current Stage: {state.get('current_stage', 'unknown')}")
        print(f"  Planning Complete: {state.get('planning_complete', False)}")
        print(f"  Execution Complete: {state.get('execution_complete', False)}")
        print(f"  Review Complete: {state.get('review_complete', False)}")
        
        print(f"\n📝 Work Outputs:")
        if state.get('project_plan'):
            print(f"  Project Plan: {state['project_plan'][:300]}...")
        
        execution_results = state.get('execution_results', [])
        print(f"  Execution Results: {len(execution_results)} items")
        for i, result in enumerate(execution_results[:3]):
            print(f"    {i+1}. {result[:100]}...")
        
        if state.get('final_report'):
            print(f"  Final Report: {state['final_report'][:300]}...")
        
        print(f"\n✅ Task Lists:")
        completed = state.get('completed_tasks', [])
        pending = state.get('pending_tasks', [])
        
        print(f"  Completed Tasks ({len(completed)}):")
        for task in completed[:5]:
            print(f"    ✓ {task}")
        if len(completed) > 5:
            print(f"    ... and {len(completed) - 5} more")
        
        print(f"  Pending Tasks ({len(pending)}):")
        for task in pending[:5]:
            print(f"    ○ {task}")
        if len(pending) > 5:
            print(f"    ... and {len(pending) - 5} more")
        
        print(f"\n💬 Messages ({len(state.get('messages', []))}):")
        messages = state.get('messages', [])
        for i, msg in enumerate(messages[:3]):
            msg_type = msg.__class__.__name__
            content = str(msg.content)[:150] if hasattr(msg, 'content') else str(msg)[:150]
            print(f"  {i+1}. [{msg_type}] {content}...")
        if len(messages) > 3:
            print(f"  ... and {len(messages) - 3} more messages")
        
        print(f"\n📊 Metadata:")
        print(f"  Started At: {state.get('started_at', 'N/A')}")
        print(f"  Last Updated: {state.get('last_updated', 'N/A')}")
        print(f"  Session Count: {state.get('session_count', 'N/A')}")

def check_database_directly():
    """Check database directly with SQL."""
    conn = sqlite3.connect("project_checkpoints.db")
    cursor = conn.cursor()
    
    print("\n=== Direct Database Query ===")
    
    # Count checkpoints
    cursor.execute("SELECT COUNT(*) FROM checkpoints")
    checkpoint_count = cursor.fetchone()[0]
    
    # Count writes
    cursor.execute("SELECT COUNT(*) FROM writes")
    writes_count = cursor.fetchone()[0]
    
    # Get database size
    cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
    db_size = cursor.fetchone()[0]
    
    print(f"Total Checkpoints: {checkpoint_count}")
    print(f"Total Writes: {writes_count}")
    print(f"Database Size: {db_size:,} bytes ({db_size/1024:.1f} KB)")
    
    # List all projects
    cursor.execute("""
        SELECT DISTINCT thread_id, COUNT(*) as checkpoint_count
        FROM checkpoints
        GROUP BY thread_id
    """)
    
    print("\nProjects:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} checkpoints")
    
    # Show checkpoint sizes
    cursor.execute("""
        SELECT checkpoint_id, length(checkpoint) as size
        FROM checkpoints
        WHERE thread_id = 'project-1'
        ORDER BY checkpoint_id
    """)
    
    print("\nCheckpoint sizes for project-1:")
    for row in cursor.fetchall():
        print(f"  {row[0][:8]}...: {row[1]} bytes")
    
    conn.close()

if __name__ == "__main__":
    inspect_database()
    check_database_directly()
