#!/usr/bin/env python3
"""
Check the raw format of checkpoint data.
"""

import sqlite3
import pickle
import json

def check_raw_data():
    """Check the raw format of checkpoint data."""
    conn = sqlite3.connect("project_checkpoints.db")
    cursor = conn.cursor()
    
    # Get first checkpoint
    cursor.execute("""
        SELECT checkpoint_id, checkpoint, metadata
        FROM checkpoints
        WHERE thread_id = 'project-1'
        ORDER BY checkpoint_id
        LIMIT 1
    """)
    
    checkpoint_id, checkpoint_blob, metadata_blob = cursor.fetchone()
    
    print(f"Checkpoint ID: {checkpoint_id}")
    print(f"Checkpoint size: {len(checkpoint_blob)} bytes")
    print(f"First 50 bytes: {checkpoint_blob[:50]}")
    print(f"Hex of first 20 bytes: {checkpoint_blob[:20].hex()}")
    
    # Try different deserialization methods
    print("\n=== Trying different formats ===")
    
    # Try pickle
    try:
        data = pickle.loads(checkpoint_blob)
        print("✅ Pickle format works!")
        print(f"Type: {type(data)}")
        if isinstance(data, dict):
            print(f"Keys: {list(data.keys())}")
            if 'channel_values' in data:
                state = data['channel_values']
                print(f"Current stage: {state.get('current_stage', 'unknown')}")
    except Exception as e:
        print(f"❌ Pickle failed: {e}")
    
    # Try JSON with different encodings
    for encoding in ['utf-8', 'latin-1', 'ascii']:
        try:
            text = checkpoint_blob.decode(encoding)
            data = json.loads(text)
            print(f"✅ JSON with {encoding} works!")
            print(f"Type: {type(data)}")
            break
        except Exception as e:
            print(f"❌ JSON with {encoding} failed: {e}")
    
    # Check metadata
    print(f"\n=== Metadata ===")
    print(f"Metadata size: {len(metadata_blob)} bytes")
    if metadata_blob:
        try:
            metadata = pickle.loads(metadata_blob)
            print(f"Metadata type: {type(metadata)}")
            print(f"Metadata keys: {list(metadata.keys()) if isinstance(metadata, dict) else 'Not a dict'}")
        except Exception as e:
            print(f"Metadata pickle failed: {e}")
    
    conn.close()

if __name__ == "__main__":
    check_raw_data()
