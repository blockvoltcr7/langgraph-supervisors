#!/usr/bin/env python3
"""
Query the SQLite database to inspect checkpoints and state.
"""

import sqlite3
import json
import zlib
from datetime import datetime

def connect_to_db():
    """Connect to the SQLite database."""
    conn = sqlite3.connect("project_checkpoints.db")
    return conn

def list_projects():
    """List all projects in the database."""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT thread_id, COUNT(*) as checkpoint_count
        FROM checkpoints
        GROUP BY thread_id
    """)
    
    print("=== Projects in Database ===")
    for row in cursor.fetchall():
        print(f"Project: {row[0]}, Checkpoints: {row[1]}")
    
    conn.close()

def get_project_history(thread_id):
    """Get complete history for a project."""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT checkpoint_id, checkpoint, metadata
        FROM checkpoints
        WHERE thread_id = ?
        ORDER BY checkpoint_id
    """, (thread_id,))
    
    print(f"\n=== Project History: {thread_id} ===")
    
    checkpoints = cursor.fetchall()
    for i, (checkpoint_id, checkpoint_blob, metadata_blob) in enumerate(checkpoints):
        # Parse checkpoint data (decompress first)
        try:
            # Try to decompress if it's compressed
            decompressed = zlib.decompress(checkpoint_blob)
            checkpoint_data = json.loads(decompressed.decode('utf-8'))
        except:
            # If decompression fails, try direct JSON parse
            checkpoint_data = json.loads(checkpoint_blob)
        
        state = checkpoint_data.get("channel_values", {})
        
        print(f"\nCheckpoint {i+1}: {checkpoint_id[:8]}...")
        print(f"  Stage: {state.get('current_stage', 'unknown')}")
        print(f"  Planning complete: {state.get('planning_complete', False)}")
        print(f"  Execution complete: {state.get('execution_complete', False)}")
        print(f"  Review complete: {state.get('review_complete', False)}")
        print(f"  Completed tasks: {len(state.get('completed_tasks', []))}")
        print(f"  Pending tasks: {len(state.get('pending_tasks', []))}")
        print(f"  Messages: {len(state.get('messages', []))}")
        
        # Parse metadata for timestamp
        if metadata_blob:
            metadata = json.loads(metadata_blob)
            timestamp = metadata.get("source", {}).get("created_at", "unknown")
            print(f"  Created: {timestamp}")
    
    conn.close()
    return checkpoints

def get_checkpoint_details(thread_id, checkpoint_index=0):
    """Get detailed view of a specific checkpoint."""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT checkpoint_id, checkpoint, metadata
        FROM checkpoints
        WHERE thread_id = ?
        ORDER BY checkpoint_id
    """, (thread_id,))
    
    checkpoints = cursor.fetchall()
    
    if checkpoint_index >= len(checkpoints):
        print(f"Checkpoint {checkpoint_index} not found. Total checkpoints: {len(checkpoints)}")
        return
    
    checkpoint_id, checkpoint_blob, metadata_blob = checkpoints[checkpoint_index]
    
    print(f"\n=== Checkpoint Details: {checkpoint_id} ===")
    
    # Parse checkpoint (decompress first)
    try:
        decompressed = zlib.decompress(checkpoint_blob)
        checkpoint_data = json.loads(decompressed.decode('utf-8'))
    except:
        checkpoint_data = json.loads(checkpoint_blob)
    
    state = checkpoint_data.get("channel_values", {})
    
    print(f"\n📋 Project Info:")
    print(f"  Name: {state.get('project_name', 'N/A')}")
    print(f"  Description: {state.get('project_description', 'N/A')[:100]}...")
    
    print(f"\n🎯 Stage Status:")
    print(f"  Current Stage: {state.get('current_stage', 'unknown')}")
    print(f"  Planning Complete: {state.get('planning_complete', False)}")
    print(f"  Execution Complete: {state.get('execution_complete', False)}")
    print(f"  Review Complete: {state.get('review_complete', False)}")
    
    print(f"\n📝 Work Outputs:")
    project_plan = state.get('project_plan', '')
    if project_plan:
        print(f"  Project Plan: {project_plan[:200]}...")
    
    execution_results = state.get('execution_results', [])
    print(f"  Execution Results: {len(execution_results)} items")
    for i, result in enumerate(execution_results[:3]):
        print(f"    {i+1}. {result[:80]}...")
    
    final_report = state.get('final_report', '')
    if final_report:
        print(f"  Final Report: {final_report[:200]}...")
    
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
        msg_type = msg.get('type', 'unknown')
        content = msg.get('content', '')
        print(f"  {i+1}. [{msg_type}] {content[:100]}...")
    if len(messages) > 3:
        print(f"  ... and {len(messages) - 3} more messages")
    
    print(f"\n📊 Metadata:")
    print(f"  Started At: {state.get('started_at', 'N/A')}")
    print(f"  Last Updated: {state.get('last_updated', 'N/A')}")
    print(f"  Session Count: {state.get('session_count', 'N/A')}")
    
    conn.close()

def get_writes_for_checkpoint(thread_id, checkpoint_id):
    """Get all writes for a specific checkpoint."""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT channel, idx, value
        FROM writes
        WHERE thread_id = ? AND checkpoint_id = ?
        ORDER BY idx
    """, (thread_id, checkpoint_id))
    
    writes = cursor.fetchall()
    
    print(f"\n=== Writes for Checkpoint: {checkpoint_id[:8]}... ===")
    
    for channel, idx, value_blob in writes:
        # Parse write value (decompress if needed)
        try:
            decompressed = zlib.decompress(value_blob)
            value = json.loads(decompressed.decode('utf-8'))
        except:
            value = json.loads(value_blob)
        
        print(f"\nWrite {idx} - Channel: {channel}")
        print(f"  Keys: {list(value.keys())}")
        
        # Show some key values
        if 'messages' in value:
            print(f"  Messages: {len(value['messages'])}")
        if 'project_plan' in value:
            print(f"  Project Plan: {value['project_plan'][:100]}...")
        if 'completed_tasks' in value:
            print(f"  Completed Tasks: {len(value['completed_tasks'])}")
    
    conn.close()

def database_stats():
    """Show database statistics."""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    # Checkpoints count
    cursor.execute("SELECT COUNT(*) FROM checkpoints")
    checkpoint_count = cursor.fetchone()[0]
    
    # Writes count
    cursor.execute("SELECT COUNT(*) FROM writes")
    writes_count = cursor.fetchone()[0]
    
    # Database size
    cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
    db_size = cursor.fetchone()[0]
    
    print(f"\n=== Database Statistics ===")
    print(f"  Total Checkpoints: {checkpoint_count}")
    print(f"  Total Writes: {writes_count}")
    print(f"  Database Size: {db_size:,} bytes ({db_size/1024:.1f} KB)")
    
    conn.close()

def main():
    """Main function to run queries."""
    print("🔍 SQLite Database Query Tool")
    print("=" * 50)
    
    # Show stats
    database_stats()
    
    # List projects
    list_projects()
    
    # Get history for project-1
    get_project_history("project-1")
    
    # Show details for latest checkpoint
    get_checkpoint_details("project-1", -1)  # -1 = latest
    
    # Show writes for latest checkpoint
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT checkpoint_id FROM checkpoints 
        WHERE thread_id = 'project-1' 
        ORDER BY checkpoint_id DESC 
        LIMIT 1
    """)
    latest_checkpoint = cursor.fetchone()
    if latest_checkpoint:
        get_writes_for_checkpoint("project-1", latest_checkpoint[0])
    conn.close()

if __name__ == "__main__":
    main()
