"""
Test Script for Agentic RAG - Verify Retrieval Behavior

This script tests that the agent correctly decides when to retrieve embeddings
and when to respond directly.

Run with: python test_agentic_rag.py
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

# ============================================================================
# Test Cases
# ============================================================================

TEST_CASES = [
    # Cases where retrieval should NOT be used
    {
        "id": "no_retrieval_1",
        "query": "Hi! How are you today?",
        "should_retrieve": False,
        "reason": "General greeting - no technical info needed",
        "category": "Greeting"
    },
    {
        "id": "no_retrieval_2",
        "query": "Hello there!",
        "should_retrieve": False,
        "reason": "Simple greeting",
        "category": "Greeting"
    },
    {
        "id": "no_retrieval_3",
        "query": "Thanks for your help!",
        "should_retrieve": False,
        "reason": "Acknowledgment",
        "category": "Acknowledgment"
    },
    {
        "id": "no_retrieval_4",
        "query": "What's 2 + 2?",
        "should_retrieve": False,
        "reason": "General knowledge math",
        "category": "General Knowledge"
    },
    {
        "id": "no_retrieval_5",
        "query": "Can you help me?",
        "should_retrieve": False,
        "reason": "Generic request",
        "category": "Generic"
    },
    {
        "id": "no_retrieval_6",
        "query": "Good morning!",
        "should_retrieve": False,
        "reason": "Greeting",
        "category": "Greeting"
    },
    
    # Cases where retrieval SHOULD be used
    {
        "id": "with_retrieval_1",
        "query": "What is LangGraph?",
        "should_retrieve": True,
        "reason": "Specific technical question about LangGraph",
        "category": "Technical Definition"
    },
    {
        "id": "with_retrieval_2",
        "query": "How do I create a StateGraph?",
        "should_retrieve": True,
        "reason": "API/implementation question",
        "category": "API Question"
    },
    {
        "id": "with_retrieval_3",
        "query": "Explain checkpointers in LangGraph",
        "should_retrieve": True,
        "reason": "Specific concept explanation",
        "category": "Concept Explanation"
    },
    {
        "id": "with_retrieval_4",
        "query": "What are the key features of LangGraph?",
        "should_retrieve": True,
        "reason": "Technical details question",
        "category": "Technical Details"
    },
    {
        "id": "with_retrieval_5",
        "query": "How does persistence work in LangGraph?",
        "should_retrieve": True,
        "reason": "Specific feature question",
        "category": "Feature Question"
    },
    {
        "id": "with_retrieval_6",
        "query": "Tell me about subgraphs in LangGraph",
        "should_retrieve": True,
        "reason": "Advanced concept question",
        "category": "Advanced Concept"
    },
    {
        "id": "with_retrieval_7",
        "query": "What is human-in-the-loop in LangGraph?",
        "should_retrieve": True,
        "reason": "Specific pattern question",
        "category": "Pattern Question"
    },
    {
        "id": "with_retrieval_8",
        "query": "How do I use multi-agent systems with LangGraph?",
        "should_retrieve": True,
        "reason": "Implementation question",
        "category": "Implementation"
    },
]

# ============================================================================
# Test Functions
# ============================================================================

def run_single_test(graph, test_case, verbose=True):
    """
    Run a single test case and verify retrieval behavior.
    
    Returns:
        dict: Test result with pass/fail status
    """
    if verbose:
        print(f"\n{'='*80}")
        print(f"🧪 Test: {test_case['id']}")
        print(f"{'='*80}")
        print(f"Query: \"{test_case['query']}\"")
        print(f"Expected: {'✅ RETRIEVE' if test_case['should_retrieve'] else '❌ NO RETRIEVAL'}")
        print(f"Reason: {test_case['reason']}")
        print(f"Category: {test_case['category']}")
        print(f"{'-'*80}")
    
    config = {"configurable": {"thread_id": f"test-{test_case['id']}"}}
    
    retrieval_used = False
    response_text = ""
    tool_calls_detected = False
    
    try:
        for chunk in graph.stream(
            {"messages": [HumanMessage(content=test_case["query"])]},
            config
        ):
            for node, values in chunk.items():
                # Check if retrieval was used
                if "retrieval_used" in values:
                    retrieval_used = values["retrieval_used"]
                
                # Get response text
                if "messages" in values and values["messages"]:
                    for msg in values["messages"]:
                        if isinstance(msg, AIMessage):
                            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                tool_calls_detected = True
                            if hasattr(msg, 'content') and msg.content:
                                response_text = msg.content
        
        # Determine if test passed
        passed = retrieval_used == test_case["should_retrieve"]
        
        if verbose:
            print(f"\n📊 Actual: {'✅ RETRIEVED' if retrieval_used else '❌ NO RETRIEVAL'}")
            if tool_calls_detected:
                print(f"🔧 Tool calls detected: Yes")
            print(f"\n💬 Response preview: {response_text[:150]}...")
            print(f"\n{'✅ PASS' if passed else '❌ FAIL'}")
            if not passed:
                print(f"   Expected retrieval: {test_case['should_retrieve']}")
                print(f"   Actual retrieval: {retrieval_used}")
        
        return {
            "test_id": test_case["id"],
            "query": test_case["query"],
            "category": test_case["category"],
            "expected_retrieval": test_case["should_retrieve"],
            "actual_retrieval": retrieval_used,
            "tool_calls_detected": tool_calls_detected,
            "passed": passed,
            "response_preview": response_text[:100] if response_text else ""
        }
    
    except Exception as e:
        if verbose:
            print(f"\n❌ ERROR: {e}")
        
        return {
            "test_id": test_case["id"],
            "query": test_case["query"],
            "category": test_case["category"],
            "expected_retrieval": test_case["should_retrieve"],
            "actual_retrieval": None,
            "tool_calls_detected": False,
            "passed": False,
            "error": str(e)
        }


def run_all_tests(verbose=True):
    """
    Run all test cases and generate a report.
    """
    print("\n" + "="*80)
    print("AGENTIC RAG TEST SUITE - Retrieval Verification")
    print("="*80)
    print(f"\nTotal test cases: {len(TEST_CASES)}")
    print(f"  - Should NOT retrieve: {sum(1 for t in TEST_CASES if not t['should_retrieve'])}")
    print(f"  - Should retrieve: {sum(1 for t in TEST_CASES if t['should_retrieve'])}")
    
    # Create graph
    print("\n📚 Initializing Agentic RAG system...")
    graph = create_agentic_rag()
    print("✅ System ready")
    
    # Run all tests
    results = []
    for i, test_case in enumerate(TEST_CASES, 1):
        if verbose:
            print(f"\n\n{'#'*80}")
            print(f"# Test {i}/{len(TEST_CASES)}")
            print(f"{'#'*80}")
        
        result = run_single_test(graph, test_case, verbose=verbose)
        results.append(result)
    
    # Generate summary
    print("\n\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for r in results if r["passed"])
    failed = len(results) - passed
    
    print(f"\n📊 Overall Results:")
    print(f"   Total Tests: {len(results)}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   Success Rate: {(passed/len(results)*100):.1f}%")
    
    # Category breakdown
    print(f"\n📋 By Category:")
    categories = {}
    for result in results:
        cat = result["category"]
        if cat not in categories:
            categories[cat] = {"passed": 0, "failed": 0}
        if result["passed"]:
            categories[cat]["passed"] += 1
        else:
            categories[cat]["failed"] += 1
    
    for cat, stats in sorted(categories.items()):
        total = stats["passed"] + stats["failed"]
        print(f"   {cat}: {stats['passed']}/{total} passed")
    
    # Retrieval accuracy
    print(f"\n🎯 Retrieval Decision Accuracy:")
    
    # Should NOT retrieve tests
    no_retrieve_tests = [r for r in results if not r["expected_retrieval"]]
    no_retrieve_correct = sum(1 for r in no_retrieve_tests if not r["actual_retrieval"])
    print(f"   No Retrieval Cases: {no_retrieve_correct}/{len(no_retrieve_tests)} correct")
    
    # Should retrieve tests
    retrieve_tests = [r for r in results if r["expected_retrieval"]]
    retrieve_correct = sum(1 for r in retrieve_tests if r["actual_retrieval"])
    print(f"   Retrieval Cases: {retrieve_correct}/{len(retrieve_tests)} correct")
    
    # Failed tests detail
    if failed > 0:
        print(f"\n❌ Failed Tests:")
        print("-"*80)
        for i, result in enumerate(results, 1):
            if not result["passed"]:
                print(f"\n{i}. {result['test_id']}")
                print(f"   Query: {result['query']}")
                print(f"   Expected: {'Retrieve' if result['expected_retrieval'] else 'No Retrieval'}")
                print(f"   Actual: {'Retrieve' if result['actual_retrieval'] else 'No Retrieval'}")
                if "error" in result:
                    print(f"   Error: {result['error']}")
    
    # Success cases
    if passed > 0:
        print(f"\n✅ Passed Tests Summary:")
        print("-"*80)
        
        # Group by expected behavior
        no_ret_passed = [r for r in results if r["passed"] and not r["expected_retrieval"]]
        ret_passed = [r for r in results if r["passed"] and r["expected_retrieval"]]
        
        if no_ret_passed:
            print(f"\n   Correctly avoided retrieval ({len(no_ret_passed)} tests):")
            for r in no_ret_passed:
                print(f"   ✓ {r['query'][:60]}...")
        
        if ret_passed:
            print(f"\n   Correctly used retrieval ({len(ret_passed)} tests):")
            for r in ret_passed:
                print(f"   ✓ {r['query'][:60]}...")
    
    print("\n" + "="*80)
    
    return results


def run_quick_test():
    """
    Run a quick subset of tests for fast verification.
    """
    print("\n" + "="*80)
    print("QUICK TEST - Sample Verification")
    print("="*80)
    
    # Select representative tests
    quick_tests = [
        TEST_CASES[0],   # No retrieval - greeting
        TEST_CASES[3],   # No retrieval - general knowledge
        TEST_CASES[6],   # With retrieval - technical question
        TEST_CASES[8],   # With retrieval - concept explanation
    ]
    
    print(f"\nRunning {len(quick_tests)} representative tests...")
    
    graph = create_agentic_rag()
    
    results = []
    for test in quick_tests:
        result = run_single_test(graph, test, verbose=True)
        results.append(result)
    
    passed = sum(1 for r in results if r["passed"])
    print(f"\n📊 Quick Test Results: {passed}/{len(results)} passed")
    
    return results


# ============================================================================
# Main
# ============================================================================

def main():
    """
    Main entry point for test script.
    """
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Quick test mode
        results = run_quick_test()
    else:
        # Full test suite
        results = run_all_tests(verbose=True)
    
    # Exit with appropriate code
    passed = sum(1 for r in results if r["passed"])
    if passed == len(results):
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
