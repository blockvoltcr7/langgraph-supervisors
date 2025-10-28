#!/usr/bin/env python3
"""
Test Supabase/PostgreSQL connection for LangGraph checkpointer.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver

# Load environment
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

DATABASE_URL = os.getenv("DATABASE_URL")

print("🔍 Testing Supabase Connection")
print("=" * 50)

# Check if DATABASE_URL is set
if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not found in .env")
    print("\nPlease add DATABASE_URL to your .env file:")
    print("DATABASE_URL=postgresql+psycopg://user:password@host:port/database")
    exit(1)

# Show sanitized URL (hide password)
import re
sanitized_url = re.sub(r':[^:@]+@', ':****@', DATABASE_URL)
print(f"\n📍 Database URL: {sanitized_url}")

# Test connection
print("\n🔌 Attempting to connect...")

try:
    # Test basic psycopg connection first
    import psycopg
    test_url = DATABASE_URL.replace('postgresql+psycopg://', 'postgresql://')
    
    print("Testing basic PostgreSQL connection...")
    with psycopg.connect(test_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT version()")
            version = cur.fetchone()[0]
            print(f"✅ PostgreSQL connection successful!")
            print(f"   Version: {version[:50]}...")
    
    print("\n📊 Testing PostgresSaver...")
    # Create PostgresSaver (it's a context manager)
    checkpointer = PostgresSaver.from_conn_string(DATABASE_URL)
    print("✅ PostgresSaver created successfully")
    print("✅ Tables will be created automatically on first use")
    
    print("\n🎉 Supabase connection is working!")
    print("\nYou can now:")
    print("  1. Run: python main.py")
    print("  2. View data in Supabase Studio: https://app.supabase.com")
    print("  3. Query with: python query_with_langgraph.py")
    
except Exception as e:
    print(f"\n❌ Connection failed!")
    print(f"\nError: {e}")
    
    print("\n🔧 Troubleshooting:")
    print("1. Check DATABASE_URL format:")
    print("   - Must start with: postgresql+psycopg://")
    print("   - Example: postgresql+psycopg://user:password@host:port/database")
    print("\n2. Verify Supabase project is active")
    print("   - Go to https://app.supabase.com")
    print("   - Check project status")
    print("\n3. Check credentials:")
    print("   - Username: usually postgres.{project-ref}")
    print("   - Password: set during project creation")
    print("   - Host: For pooling use: aws-x-region.pooler.supabase.com")
    print("\n4. Try with SSL:")
    print("   - Add ?sslmode=require to end of URL")
    
    exit(1)
