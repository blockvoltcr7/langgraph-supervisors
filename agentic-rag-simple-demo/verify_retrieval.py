"""
Simple Retrieval Verification Script

Quick script to verify that:
1. Agent does NOT retrieve for simple queries
2. Agent DOES retrieve for technical queries

Run with: python verify_retrieval.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from main import create_agentic_rag

# Load environment
script_dir = Path(__file__).parent
env_path = script_dir / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
    print(f"✅ Environment loaded from: {env_path}\n")


def check_retrieval(graph, query, expected_retrieval):
    """
    Test a single query and check if retrieval matches expectation.
    
    Args:
        graph: The agentic RAG graph
        query: Query string to test
        expected_retrieval: True if we expect retrieval, False otherwise
    
    Returns:
        bool: True if behavior matches expectation
    """
    print(f"Query: \"{query}\"")
    print(f"Expected: {'🔍 Should retrieve' if expected_retrieval else '⚡ Should NOT retrieve'}")
    
    config = {"configurable": {"thread_id": f"verify-{hash(query)}"}}
    
    retrieval_used = False
    tool_calls_seen = False
    
    for chunk in graph.stream(
        {"messages": [HumanMessage(content=query)]},
        config
    ):
        for node, values in chunk.items():
            if "retrieval_used" in values:
                retrieval_used = values["retrieval_used"]
            
            # Also check for tool calls in messages
            if "messages" in values:
                for msg in values["messages"]:
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        tool_calls_seen = True
    
    actual = "🔍 Retrieved" if retrieval_used else "⚡ No retrieval"
    matches = retrieval_used == expected_retrieval
    status = "✅ PASS" if matches else "❌ FAIL"
    
    print(f"Actual: {actual}")
    print(f"Tool calls detected: {'Yes' if tool_calls_seen else 'No'}")
    print(f"Result: {status}\n")
    
    return matches


def main():
    """Run verification tests"""
    print("="*80)
    print("RETRIEVAL VERIFICATION - Quick Check")
    print("="*80)
    print("\nThis verifies the agent correctly decides when to retrieve.\n")
    
    # Create graph
    print("Initializing system...")
    graph = create_agentic_rag()
    print("✅ Ready\n")
    
    print("="*80)
    print("TEST 1: Simple Queries (Should NOT Retrieve)")
    print("="*80 + "\n")
    
    # Test cases that should NOT retrieve
    no_retrieval_tests = [
        "Hi! How are you?",
        "Thanks!",
        "What's 2 + 2?",
    ]
    
    no_retrieval_results = []
    for query in no_retrieval_tests:
        result = check_retrieval(graph, query, expected_retrieval=False)
        no_retrieval_results.append(result)
        print("-"*80 + "\n")
    
    print("="*80)
    print("TEST 2: Technical Queries (Should Retrieve)")
    print("="*80 + "\n")
    
    # Test cases that SHOULD retrieve
    retrieval_tests = [
        "What is LangGraph?",
        "How do I create a StateGraph?",
        "Explain checkpointers in LangGraph",
    ]
    
    retrieval_results = []
    for query in retrieval_tests:
        result = check_retrieval(graph, query, expected_retrieval=True)
        retrieval_results.append(result)
        print("-"*80 + "\n")
    
    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    
    no_ret_passed = sum(no_retrieval_results)
    ret_passed = sum(retrieval_results)
    total_passed = no_ret_passed + ret_passed
    total_tests = len(no_retrieval_results) + len(retrieval_results)
    
    print(f"\nNo Retrieval Tests: {no_ret_passed}/{len(no_retrieval_results)} passed")
    print(f"Retrieval Tests: {ret_passed}/{len(retrieval_results)} passed")
    print(f"\nTotal: {total_passed}/{total_tests} passed")
    
    if total_passed == total_tests:
        print("\n🎉 All verification tests passed!")
        print("✅ Agent correctly decides when to retrieve")
        return 0
    else:
        print(f"\n⚠️  {total_tests - total_passed} test(s) failed")
        print("❌ Agent decision-making needs adjustment")
        return 1


if __name__ == "__main__":
    import sys
    exit_code = main()
    sys.exit(exit_code)
