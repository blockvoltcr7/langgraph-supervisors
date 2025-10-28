#!/usr/bin/env python3
"""
Drop and recreate tables with correct schema for PostgresSaver.
"""

import os
import psycopg
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in .env")
    exit(1)

# Convert URL format for psycopg
db_url = DATABASE_URL.replace('postgresql+psycopg://', 'postgresql://')

print("🔄 Recreating Tables with Correct Schema")
print("=" * 50)

try:
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            
            print("\n🗑️  Dropping old tables...")
            cur.execute("DROP TABLE IF EXISTS checkpoint_writes CASCADE")
            print("   ✓ Dropped checkpoint_writes")
            
            cur.execute("DROP TABLE IF EXISTS checkpoints CASCADE")
            print("   ✓ Dropped checkpoints")
            
            conn.commit()
            
            print("\n🔨 Creating tables with correct schema...")
            
            # Let PostgresSaver create the tables with correct schema
            from langgraph.checkpoint.postgres import PostgresSaver
            from psycopg_pool import ConnectionPool
            
            connection_kwargs = {
                "autocommit": True,
                "prepare_threshold": 0,
            }
            
            checkpointer = PostgresSaver(
                ConnectionPool(
                    conninfo=db_url,
                    max_size=20,
                    kwargs=connection_kwargs
                )
            )
            
            # This will create tables with the correct schema
            checkpointer.setup()
            
            print("   ✓ Created checkpoints table")
            print("   ✓ Created checkpoint_writes table")
            
            print("\n✅ Tables recreated successfully!")
            print("\nYou can now run: python main.py")
            
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
