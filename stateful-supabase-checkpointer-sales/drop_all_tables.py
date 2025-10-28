#!/usr/bin/env python3
"""
Drop all checkpoint-related tables.
"""

import os
import psycopg
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

DATABASE_URL = os.getenv("DATABASE_URL")
db_url = DATABASE_URL.replace('postgresql+psycopg://', 'postgresql://')

print("🗑️  Dropping All Checkpoint Tables")
print("=" * 50)

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        # Drop all checkpoint-related tables
        tables_to_drop = [
            'checkpoint_writes',
            'checkpoints', 
            'checkpoint_blobs',
            'checkpoint_migrations'
        ]
        
        for table in tables_to_drop:
            try:
                cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                print(f"   ✓ Dropped {table}")
            except Exception as e:
                print(f"   ⚠️  Could not drop {table}: {e}")
        
        conn.commit()

print("\n✅ All tables dropped!")
print("=" * 50)
