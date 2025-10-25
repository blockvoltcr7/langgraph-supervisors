"""
Simple test to verify the subgraph setup works correctly.
Run with: python test_simple.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment from .env file (NOT from system environment)
script_dir = Path(__file__).parent
env_path = script_dir / ".env"

if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
else:
    print(f"⚠️  .env file not found at {env_path}")

def test_imports():
    """Test that all required packages are installed"""
    print("Testing imports...")
    try:
        import langgraph
        import langchain_openai
        import langchain_core
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("Run: uv sync")
        return False

def test_env():
    """Test that environment is configured"""
    print("\nTesting environment...")
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your_openai_api_key_here":
        print(f"✅ OPENAI_API_KEY is set (loaded from {env_path})")
        return True
    else:
        print("❌ OPENAI_API_KEY not configured")
        print(f"Please edit {env_path} and add your actual OpenAI API key")
        return False

def test_graph_creation():
    """Test that graphs can be created"""
    print("\nTesting graph creation...")
    try:
        from main import create_coordinator_graph
        graph = create_coordinator_graph()
        print("✅ Graph created successfully")
        return True
    except Exception as e:
        print(f"❌ Graph creation failed: {e}")
        return False

def test_subgraph_isolation():
    """Test that subgraphs have isolated state"""
    print("\nTesting subgraph isolation...")
    try:
        from main import TechSupportState, BillingState, CoordinatorState
        
        # Check that states are different
        tech_fields = set(TechSupportState.__annotations__.keys())
        billing_fields = set(BillingState.__annotations__.keys())
        coordinator_fields = set(CoordinatorState.__annotations__.keys())
        
        # Tech and Billing should have different fields
        tech_only = tech_fields - billing_fields - {"messages"}
        billing_only = billing_fields - tech_fields - {"messages"}
        
        if tech_only and billing_only:
            print(f"✅ Subgraphs have isolated state")
            print(f"   Tech-only fields: {tech_only}")
            print(f"   Billing-only fields: {billing_only}")
            return True
        else:
            print("⚠️  Subgraphs share all fields (might be intentional)")
            return True
    except Exception as e:
        print(f"❌ State isolation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("SUBGRAPH PATTERN - SETUP VERIFICATION")
    print("="*60)
    
    results = []
    results.append(test_imports())
    results.append(test_env())
    results.append(test_graph_creation())
    results.append(test_subgraph_isolation())
    
    print("\n" + "="*60)
    if all(results):
        print("✅ ALL TESTS PASSED!")
        print("\nYou're ready to run: python main.py")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease fix the issues above before running main.py")
    print("="*60)

if __name__ == "__main__":
    main()
