#!/usr/bin/env python3
"""
Quick SQLite queries to inspect the database.
"""

import sqlite3

def run_quick_queries():
    """Run quick queries on the database."""
    conn = sqlite3.connect("project_checkpoints.db")
    cursor = conn.cursor()
    
    print("🔍 Quick Database Queries")
    print("=" * 40)
    
    # 1. Basic stats
    print("\n1. Database Overview:")
    cursor.execute("SELECT COUNT(*) FROM checkpoints")
    checkpoints = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM writes")
    writes = cursor.fetchone()[0]
    
    print(f"   Total Checkpoints: {checkpoints}")
    print(f"   Total Writes: {writes}")
    
    # 2. Projects
    print("\n2. Projects:")
    cursor.execute("""
        SELECT DISTINCT thread_id, COUNT(*) as count
        FROM checkpoints
        GROUP BY thread_id
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} checkpoints")
    
    # 3. Checkpoint sizes
    print("\n3. Checkpoint Sizes (project-1):")
    cursor.execute("""
        SELECT checkpoint_id, length(checkpoint) as size
        FROM checkpoints
        WHERE thread_id = 'project-1'
        ORDER BY size DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"   {row[0][:8]}...: {row[1]:,} bytes")
    
    # 4. Write channels
    print("\n4. Write Channels:")
    cursor.execute("""
        SELECT DISTINCT channel, COUNT(*) as count
        FROM writes
        WHERE thread_id = 'project-1'
        GROUP BY channel
        ORDER BY count DESC
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} writes")
    
    # 5. Recent activity
    print("\n5. Checkpoint Timeline (project-1):")
    cursor.execute("""
        SELECT checkpoint_id, length(checkpoint) as size
        FROM checkpoints
        WHERE thread_id = 'project-1'
        ORDER BY checkpoint_id
        LIMIT 10
    """)
    for i, row in enumerate(cursor.fetchall()):
        print(f"   {i+1}. {row[0][:8]}...: {row[1]:,} bytes")
    
    conn.close()

if __name__ == "__main__":
    run_quick_queries()
