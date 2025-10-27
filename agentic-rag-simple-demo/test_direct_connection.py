"""
Test Supabase Connection

This script tests your Supabase database connection using credentials from .env file.

Usage:
    python test_direct_connection.py
"""

import psycopg2
from psycopg2 import OperationalError
import os
from pathlib import Path
from dotenv import load_dotenv

# ============================================================================
# Load Environment Variables
# ============================================================================

script_dir = Path(__file__).parent
env_path = script_dir / ".env"

if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
    print(f"✅ Loaded environment from: {env_path}\n")
else:
    print(f"❌ Error: .env file not found at {env_path}")
    exit(1)

# ============================================================================
# Get Connection Parameters from Environment
# ============================================================================

# Read from .env file
# Try psycopg2-specific URL first, fallback to DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL_PSYCOPG2") or os.getenv("DATABASE_URL")
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Fix DATABASE_URL for psycopg2 (remove SQLAlchemy prefix if present)
if DATABASE_URL and DATABASE_URL.startswith("postgresql+psycopg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")
    print("ℹ️  Converted SQLAlchemy URL format to psycopg2 format\n")
elif DATABASE_URL and "DATABASE_URL_PSYCOPG2" in os.environ:
    print("ℹ️  Using DATABASE_URL_PSYCOPG2 from .env\n")

# Build connection config
DB_CONFIG = {
    "user": USER,
    "password": PASSWORD,
    "host": HOST,
    "port": PORT,
    "dbname": DBNAME,
    "sslmode": "require"  # SSL is required for Supabase
}

# Validate required variables
if not all([USER, PASSWORD, HOST, PORT, DBNAME]):
    print("❌ Error: Missing required environment variables in .env file")
    print("   Required: user, password, host, port, dbname")
    exit(1)

print("=" * 80)
print("SUPABASE DIRECT CONNECTION TEST")
print("=" * 80)
print()

# ============================================================================
# Test 1: Using Connection String
# ============================================================================

print("🧪 Test 1: Connecting with connection string...")
print(f"   URL: {DATABASE_URL.replace(DB_CONFIG['password'], '***')}")
print()

try:
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    print("✅ Connection successful with connection string!")
    
    cur = conn.cursor()
    
    # Test query
    cur.execute("SELECT NOW();")
    result = cur.fetchone()
    print(f"   Current Time: {result[0]}")
    
    # Check pgvector
    cur.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';")
    result = cur.fetchone()
    if result:
        print(f"   ✅ pgvector extension: version {result[1]}")
    else:
        print("   ⚠️  pgvector extension NOT installed")
    
    cur.close()
    conn.close()
    print()
    
except OperationalError as e:
    print(f"❌ Connection failed: {e}")
    print()
    print("💡 This error means:")
    if "could not translate host name" in str(e):
        print("   - Your Mac cannot resolve the Supabase hostname")
        print("   - This usually means IPv6 is not configured")
        print("   - You MUST use the pooler connection instead")
    elif "password authentication failed" in str(e):
        print("   - Your password is incorrect")
        print("   - Update YOUR_PASSWORD in this script")
    elif "Tenant or user not found" in str(e):
        print("   - Username or project ID is wrong")
        print("   - Or your project might be paused")
    print()

# ============================================================================
# Test 2: Using Individual Parameters
# ============================================================================

print("🧪 Test 2: Connecting with individual parameters...")
print(f"   Host: {DB_CONFIG['host']}")
print(f"   Port: {DB_CONFIG['port']}")
print(f"   User: {DB_CONFIG['user']}")
print(f"   Database: {DB_CONFIG['dbname']}")
print(f"   SSL Mode: {DB_CONFIG['sslmode']}")
print()

try:
    conn = psycopg2.connect(**DB_CONFIG)
    print("✅ Connection successful with parameters!")
    
    cur = conn.cursor()
    
    # Get PostgreSQL version
    cur.execute("SELECT version();")
    result = cur.fetchone()
    print(f"   PostgreSQL: {result[0][:60]}...")
    
    cur.close()
    conn.close()
    print()
    
except OperationalError as e:
    print(f"❌ Connection failed: {e}")
    print()

# ============================================================================
# Summary
# ============================================================================

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()
print("If BOTH tests failed with 'could not translate host name':")
print("   → Your Mac does not support IPv6")
print("   → The direct connection will NOT work")
print("   → You MUST use Supabase's connection pooler")
print()
print("To find the pooler connection:")
print("   1. Go to: https://supabase.com/dashboard/project/nycwzpxobcjkvihhrpjf")
print("   2. Click 'Connect' button")
print("   3. Look for 'Connection pooling' or 'Session mode'")
print("   4. Copy the connection string with '*.pooler.supabase.com'")
print()
print("If tests succeeded:")
print("   ✅ Your connection works!")
print("   ✅ Update your .env file with these credentials")
print("   ✅ Run: python main.py")
print()
print("=" * 80)
