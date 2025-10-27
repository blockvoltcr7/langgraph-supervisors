#!/usr/bin/env python3
"""
Simple database inspector - no dependencies needed.
"""

import sqlite3
import json

def inspect_database():
    """Inspect the SQLite database."""
    conn = sqlite3.connect("project_checkpoints.db")
    cursor = conn.cursor()
    
    print("🔍 Database Inspector")
    print("=" * 40)
    
    # Basic stats
    cursor.execute("SELECT COUNT(*) FROM checkpoints")
    checkpoints = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM writes")
    writes = cursor.fetchone()[0]
    
    print(f"\n📊 Database Stats:")
    print(f"   Checkpoints: {checkpoints}")
    print(f"   Writes: {writes}")
    
    # Projects
    cursor.execute("""
        SELECT DISTINCT thread_id, COUNT(*) as count
        FROM checkpoints
        GROUP BY thread_id
    """)
    
    print(f"\n📁 Projects:")
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} checkpoints")
    
    # Checkpoint details
    cursor.execute("""
        SELECT checkpoint_id, length(checkpoint) as size
        FROM checkpoints
        WHERE thread_id = 'project-1'
        ORDER BY checkpoint_id
    """)
    
    print(f"\n📈 Checkpoint Sizes:")
    for i, row in enumerate(cursor.fetchall()):
        print(f"   {i+1:2d}. {row[0][:8]}...: {row[1]:6,} bytes")
    
    # Write channels
    cursor.execute("""
        SELECT channel, COUNT(*) as count
        FROM writes
        WHERE thread_id = 'project-1'
        GROUP BY channel
        ORDER BY count DESC
    """)
    
    print(f"\n📝 Write Channels:")
    for row in cursor.fetchall():
        print(f"   {row[0]:20s}: {row[1]:3d} writes")
    
    conn.close()

if __name__ == "__main__":
    inspect_database()
