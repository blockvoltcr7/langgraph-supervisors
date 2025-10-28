#!/usr/bin/env python3
"""
Check if LangGraph checkpoint tables exist in Supabase and create them if needed.
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

print("🔍 Checking Supabase Tables")
print("=" * 50)

try:
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            
            # Check if tables exist
            print("\n📊 Checking for LangGraph tables...")
            
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('checkpoints', 'checkpoint_writes')
                ORDER BY table_name
            """)
            
            existing_tables = [row[0] for row in cur.fetchall()]
            
            if 'checkpoints' in existing_tables and 'checkpoint_writes' in existing_tables:
                print(f"\n✅ All tables already exist!")
                for table in existing_tables:
                    print(f"   ✓ {table}")
                
                # Check row counts
                print("\n📊 Current Data:")
                for table in existing_tables:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cur.fetchone()[0]
                    print(f"   {table}: {count} rows")
                
                print("\n✅ Tables are ready to use!")
                
            else:
                print(f"\n⚠️  Tables missing. Found: {existing_tables if existing_tables else 'none'}")
                print("\n🔨 Creating tables...")
                
                # Drop existing tables first
                cur.execute("DROP TABLE IF EXISTS checkpoint_writes CASCADE")
                cur.execute("DROP TABLE IF NOT EXISTS checkpoints CASCADE")
                print("   ✓ Dropped old tables")
                
                # Create checkpoints table with JSONB (required by PostgresSaver)
                cur.execute("""
                    CREATE TABLE checkpoints (
                        thread_id TEXT NOT NULL,
                        checkpoint_ns TEXT NOT NULL DEFAULT '',
                        checkpoint_id TEXT NOT NULL,
                        parent_checkpoint_id TEXT,
                        type TEXT,
                        checkpoint JSONB,
                        metadata JSONB,
                        PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
                    )
                """)
                print("   ✓ Created 'checkpoints' table (JSONB)")
                
                # Create index on checkpoints
                cur.execute("""
                    CREATE INDEX idx_checkpoints_thread_id 
                    ON checkpoints(thread_id)
                """)
                print("   ✓ Created index on checkpoints.thread_id")
                
                # Create checkpoint_writes table with JSONB
                cur.execute("""
                    CREATE TABLE checkpoint_writes (
                        thread_id TEXT NOT NULL,
                        checkpoint_ns TEXT NOT NULL DEFAULT '',
                        checkpoint_id TEXT NOT NULL,
                        task_id TEXT NOT NULL,
                        idx INTEGER NOT NULL,
                        channel TEXT NOT NULL,
                        type TEXT,
                        value JSONB,
                        PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx)
                    )
                """)
                print("   ✓ Created 'checkpoint_writes' table (JSONB)")
                
                # Create indexes on checkpoint_writes
                cur.execute("""
                    CREATE INDEX idx_checkpoint_writes_thread_id 
                    ON checkpoint_writes(thread_id)
                """)
                print("   ✓ Created index on checkpoint_writes.thread_id")
                
                cur.execute("""
                    CREATE INDEX idx_checkpoint_writes_checkpoint_id 
                    ON checkpoint_writes(checkpoint_id)
                """)
                print("   ✓ Created index on checkpoint_writes.checkpoint_id")
                
                # Commit the changes
                conn.commit()
                
                print("\n✅ All tables created successfully!")
                print("\nYou can now:")
                print("  1. Run: python main.py")
                print("  2. View tables in Supabase Studio")
                print("  3. Query with: python query_with_langgraph.py")
            
except psycopg.OperationalError as e:
    print(f"\n❌ Connection error: {e}")
    print("\nTroubleshooting:")
    print("1. Check your internet connection")
    print("2. Verify Supabase project is active")
    print("3. Check DATABASE_URL in .env file")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
