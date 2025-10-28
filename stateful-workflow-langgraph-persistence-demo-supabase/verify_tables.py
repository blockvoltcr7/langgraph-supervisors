#!/usr/bin/env python3
"""
Verify tables exist in Supabase.
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

print("🔍 Verifying Tables in Supabase")
print("=" * 50)

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        # List all tables
        cur.execute("""
            SELECT table_name, table_schema
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cur.fetchall()
        print(f"\n📋 Tables in 'public' schema: {len(tables)}")
        for table, schema in tables:
            print(f"   - {table} (schema: {schema})")
        
        # Check for our specific tables
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('checkpoints', 'checkpoint_writes')
        """)
        
        our_tables = [row[0] for row in cur.fetchall()]
        
        if 'checkpoints' in our_tables and 'checkpoint_writes' in our_tables:
            print("\n✅ Both LangGraph tables exist!")
            
            # Check schema
            for table in ['checkpoints', 'checkpoint_writes']:
                cur.execute(f"""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position
                """)
                print(f"\n📋 Schema for {table}:")
                for col, dtype in cur.fetchall():
                    print(f"   {col}: {dtype}")
        else:
            print(f"\n❌ Missing tables: {set(['checkpoints', 'checkpoint_writes']) - set(our_tables)}")

print("\n" + "=" * 50)
