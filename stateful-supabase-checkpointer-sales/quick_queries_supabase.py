#!/usr/bin/env python3
"""
Quick PostgreSQL/Supabase queries to inspect the database.
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

def run_quick_queries():
    """Run quick queries on the Supabase database."""
    
    # Convert URL format for psycopg if needed
    db_url = DATABASE_URL.replace('postgresql+psycopg://', 'postgresql://')
    
    print("🔍 Quick Supabase Database Queries")
    print("=" * 40)
    
    try:
        with psycopg.connect(db_url) as conn:
            with conn.cursor() as cur:
                
                # 1. Basic stats
                print("\n1. Database Overview:")
                cur.execute("SELECT COUNT(*) FROM checkpoints")
                checkpoints = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM checkpoint_writes")
                writes = cur.fetchone()[0]
                
                print(f"   Total Checkpoints: {checkpoints}")
                print(f"   Total Writes: {writes}")
                
                # 2. Projects
                print("\n2. Projects:")
                cur.execute("""
                    SELECT DISTINCT thread_id, COUNT(*) as count
                    FROM checkpoints
                    GROUP BY thread_id
                    ORDER BY count DESC
                """)
                for row in cur.fetchall():
                    print(f"   {row[0]}: {row[1]} checkpoints")
                
                # 3. Checkpoint sizes
                print("\n3. Top 5 Largest Checkpoints:")
                cur.execute("""
                    SELECT 
                        thread_id,
                        substring(checkpoint_id, 1, 8) as id,
                        length(checkpoint) as size
                    FROM checkpoints
                    ORDER BY size DESC
                    LIMIT 5
                """)
                for row in cur.fetchall():
                    print(f"   {row[0]} - {row[1]}...: {row[2]:,} bytes")
                
                # 4. Write channels
                print("\n4. Write Channels (project-1):")
                cur.execute("""
                    SELECT DISTINCT channel, COUNT(*) as count
                    FROM checkpoint_writes
                    WHERE thread_id = 'project-1'
                    GROUP BY channel
                    ORDER BY count DESC
                    LIMIT 10
                """)
                for row in cur.fetchall():
                    print(f"   {row[0]:20s}: {row[1]:3d} writes")
                
                # 5. Recent activity
                print("\n5. Recent Checkpoints (last 5):")
                cur.execute("""
                    SELECT 
                        thread_id,
                        substring(checkpoint_id, 1, 8) as id,
                        length(checkpoint) as size
                    FROM checkpoints
                    ORDER BY checkpoint_id DESC
                    LIMIT 5
                """)
                for i, row in enumerate(cur.fetchall(), 1):
                    print(f"   {i}. {row[0]} - {row[1]}...: {row[2]:,} bytes")
                
                print("\n✅ Query completed successfully!")
                
    except psycopg.OperationalError as e:
        print(f"\n❌ Connection error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify Supabase project is active")
        print("3. Check DATABASE_URL in .env file")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    run_quick_queries()
