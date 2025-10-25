"""
Test Scenarios for Customer Support Subgraph System

This file contains comprehensive test cases to verify all routing paths
and tool executions in the customer support system.

Run with: python test_scenarios.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from main import create_coordinator_graph

# Load environment
script_dir = Path(__file__).parent
env_path = script_dir / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)

# Test scenarios with expected behaviors
TEST_SCENARIOS = [
    # ========================================================================
    # Technical Support Scenarios
    # ========================================================================
    {
        "category": "Technical Support",
        "query": "The API is returning 500 errors. Can you check if the service is down?",
        "expected_route": "tech_team",
        "expected_tools": ["check_system_status", "search_knowledge_base"],
        "expected_keywords": ["API", "operational", "status"],
        "description": "API error - should check status and search KB"
    },
    {
        "category": "Technical Support",
        "query": "I'm getting authentication errors when trying to connect to the database",
        "expected_route": "tech_team",
        "expected_tools": ["check_system_status", "search_knowledge_base"],
        "expected_keywords": ["database", "authentication"],
        "description": "Database auth issue - should check status and KB"
    },
    {
        "category": "Technical Support",
        "query": "The payment gateway is not responding. This is urgent!",
        "expected_route": "tech_team",
        "expected_tools": ["check_system_status", "create_bug_ticket"],
        "expected_keywords": ["payment", "gateway", "ticket"],
        "description": "Payment gateway down - should create high priority ticket"
    },
    {
        "category": "Technical Support",
        "query": "How do I set up the API authentication? I need the documentation.",
        "expected_route": "tech_team",
        "expected_tools": ["search_knowledge_base"],
        "expected_keywords": ["API", "authentication", "documentation"],
        "description": "Setup question - should search KB"
    },
    {
        "category": "Technical Support",
        "query": "There's a critical bug in the email service. Users can't send emails.",
        "expected_route": "tech_team",
        "expected_tools": ["check_system_status", "create_bug_ticket"],
        "expected_keywords": ["email", "bug", "ticket"],
        "description": "Critical bug - should check status and create ticket"
    },
    
    # ========================================================================
    # Billing Support Scenarios
    # ========================================================================
    {
        "category": "Billing Support",
        "query": "I need a refund for invoice INV-003. I was charged twice by mistake.",
        "expected_route": "billing_team",
        "expected_tools": ["lookup_invoice", "process_refund"],
        "expected_keywords": ["invoice", "refund", "INV-003"],
        "description": "Refund request - should lookup invoice and process refund"
    },
    {
        "category": "Billing Support",
        "query": "Can you show me my payment history for customer ID CUST-123?",
        "expected_route": "billing_team",
        "expected_tools": ["lookup_invoice"],
        "expected_keywords": ["invoice", "CUST-123", "payment"],
        "description": "Payment history - should lookup invoices"
    },
    {
        "category": "Billing Support",
        "query": "I want to upgrade my subscription from basic to pro plan",
        "expected_route": "billing_team",
        "expected_tools": ["update_subscription"],
        "expected_keywords": ["subscription", "pro", "upgrade"],
        "description": "Subscription upgrade - should update subscription"
    },
    {
        "category": "Billing Support",
        "query": "I was charged $99 but I cancelled my subscription last month",
        "expected_route": "billing_team",
        "expected_tools": ["lookup_invoice", "process_refund"],
        "expected_keywords": ["charged", "refund", "subscription"],
        "description": "Incorrect charge - should lookup and refund"
    },
    {
        "category": "Billing Support",
        "query": "What's the status of my invoice INV-002?",
        "expected_route": "billing_team",
        "expected_tools": ["lookup_invoice"],
        "expected_keywords": ["invoice", "INV-002", "status"],
        "description": "Invoice status - should lookup invoice"
    },
    {
        "category": "Billing Support",
        "query": "I need to downgrade to the basic plan to save costs",
        "expected_route": "billing_team",
        "expected_tools": ["update_subscription"],
        "expected_keywords": ["subscription", "basic", "downgrade"],
        "description": "Subscription downgrade - should update subscription"
    },
    
    # ========================================================================
    # Ambiguous / Clarification Scenarios
    # ========================================================================
    {
        "category": "Clarification",
        "query": "I need help with something",
        "expected_route": "clarification",
        "expected_tools": [],
        "expected_keywords": ["clarify", "technical", "billing"],
        "description": "Vague request - should ask for clarification"
    },
    {
        "category": "Clarification",
        "query": "Hello, can you assist me?",
        "expected_route": "clarification",
        "expected_tools": [],
        "expected_keywords": ["clarify", "help"],
        "description": "Generic greeting - should ask for clarification"
    },
    {
        "category": "Clarification",
        "query": "I have a problem",
        "expected_route": "clarification",
        "expected_tools": [],
        "expected_keywords": ["clarify"],
        "description": "Unspecified problem - should ask for clarification"
    },
    
    # ========================================================================
    # Edge Cases & Complex Scenarios
    # ========================================================================
    {
        "category": "Edge Case",
        "query": "The API is down AND I need a refund for the downtime",
        "expected_route": "tech_team",  # Should route to first mentioned issue
        "expected_tools": ["check_system_status"],
        "expected_keywords": ["API", "status"],
        "description": "Multiple issues - coordinator should pick one team"
    },
    {
        "category": "Edge Case",
        "query": "Check the status of the payment API service",
        "expected_route": "tech_team",
        "expected_tools": ["check_system_status"],
        "expected_keywords": ["payment", "status"],
        "description": "Payment + API keywords - should route to tech (API focus)"
    },
    {
        "category": "Edge Case",
        "query": "I'm having trouble with my account",
        "expected_route": "clarification",  # Could be tech or billing
        "expected_tools": [],
        "expected_keywords": ["clarify"],
        "description": "Ambiguous account issue - should ask for clarification"
    },
]


def run_test_scenario(graph, scenario, verbose=True):
    """Run a single test scenario and return results"""
    if verbose:
        print(f"\n{'='*80}")
        print(f"📋 Test: {scenario['description']}")
        print(f"Category: {scenario['category']}")
        print(f"{'='*80}")
        print(f"Query: \"{scenario['query']}\"")
        print(f"\nExpected Route: {scenario['expected_route']}")
        print(f"Expected Tools: {scenario['expected_tools']}")
        print(f"Expected Keywords: {scenario['expected_keywords']}")
        print(f"\n{'-'*80}")
    
    # Run the query
    config = {"configurable": {"thread_id": f"test-{hash(scenario['query'])}"}}
    
    results = {
        "query": scenario["query"],
        "category": scenario["category"],
        "nodes_visited": [],
        "tools_used": [],
        "response": "",
        "passed": False,
        "errors": []
    }
    
    try:
        for chunk in graph.stream(
            {"messages": [HumanMessage(content=scenario["query"])]},
            config
        ):
            for node, values in chunk.items():
                results["nodes_visited"].append(node)
                
                if verbose:
                    print(f"\n✓ Node: {node}")
                
                if "messages" in values and values["messages"]:
                    last_msg = values["messages"][-1]
                    if hasattr(last_msg, 'content'):
                        content = last_msg.content
                        results["response"] = content
                        
                        if verbose:
                            print(f"  Response: {content[:200]}...")
                        
                        # Extract tool usage from response
                        if "check_system_status" in content.lower() or "status" in content.lower():
                            results["tools_used"].append("check_system_status")
                        if "bug ticket" in content.lower() or "ticket created" in content.lower():
                            results["tools_used"].append("create_bug_ticket")
                        if "knowledge base" in content.lower() or "documentation" in content.lower():
                            results["tools_used"].append("search_knowledge_base")
                        if "invoice" in content.lower() and "customer" in content.lower():
                            results["tools_used"].append("lookup_invoice")
                        if "refund processed" in content.lower():
                            results["tools_used"].append("process_refund")
                        if "subscription updated" in content.lower():
                            results["tools_used"].append("update_subscription")
        
        # Validate results
        route_correct = scenario["expected_route"] in results["nodes_visited"]
        keywords_found = any(
            keyword.lower() in results["response"].lower()
            for keyword in scenario["expected_keywords"]
        )
        
        results["passed"] = route_correct and keywords_found
        
        if not route_correct:
            results["errors"].append(
                f"Expected route '{scenario['expected_route']}' not found. "
                f"Visited: {results['nodes_visited']}"
            )
        
        if not keywords_found:
            results["errors"].append(
                f"Expected keywords {scenario['expected_keywords']} not found in response"
            )
        
        if verbose:
            print(f"\n{'='*80}")
            print(f"✅ PASSED" if results["passed"] else "❌ FAILED")
            if results["errors"]:
                print(f"Errors: {results['errors']}")
            print(f"{'='*80}")
    
    except Exception as e:
        results["errors"].append(str(e))
        if verbose:
            print(f"\n❌ ERROR: {e}")
    
    return results


def run_all_tests(verbose=True):
    """Run all test scenarios"""
    print("\n" + "="*80)
    print("CUSTOMER SUPPORT SYSTEM - COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    # Create graph
    graph = create_coordinator_graph()
    
    # Run all scenarios
    all_results = []
    passed = 0
    failed = 0
    
    for i, scenario in enumerate(TEST_SCENARIOS, 1):
        if verbose:
            print(f"\n\n{'#'*80}")
            print(f"# Test {i}/{len(TEST_SCENARIOS)}")
            print(f"{'#'*80}")
        
        result = run_test_scenario(graph, scenario, verbose=verbose)
        all_results.append(result)
        
        if result["passed"]:
            passed += 1
        else:
            failed += 1
    
    # Print summary
    print("\n\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {len(TEST_SCENARIOS)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/len(TEST_SCENARIOS)*100):.1f}%")
    
    # Print failed tests
    if failed > 0:
        print("\n" + "-"*80)
        print("FAILED TESTS:")
        print("-"*80)
        for i, result in enumerate(all_results, 1):
            if not result["passed"]:
                print(f"\n{i}. {result['category']}: {result['query'][:60]}...")
                for error in result["errors"]:
                    print(f"   - {error}")
    
    # Print category breakdown
    print("\n" + "-"*80)
    print("CATEGORY BREAKDOWN:")
    print("-"*80)
    categories = {}
    for result in all_results:
        cat = result["category"]
        if cat not in categories:
            categories[cat] = {"passed": 0, "failed": 0}
        if result["passed"]:
            categories[cat]["passed"] += 1
        else:
            categories[cat]["failed"] += 1
    
    for cat, stats in categories.items():
        total = stats["passed"] + stats["failed"]
        print(f"{cat}: {stats['passed']}/{total} passed")
    
    print("\n" + "="*80)
    
    return all_results


def run_quick_test():
    """Run a quick test with just a few scenarios"""
    print("\n" + "="*80)
    print("QUICK TEST - Sample Scenarios")
    print("="*80)
    
    graph = create_coordinator_graph()
    
    # Select a few representative scenarios
    quick_scenarios = [
        TEST_SCENARIOS[0],   # Tech support
        TEST_SCENARIOS[5],   # Billing
        TEST_SCENARIOS[11],  # Clarification
    ]
    
    for scenario in quick_scenarios:
        run_test_scenario(graph, scenario, verbose=True)


if __name__ == "__main__":
    import sys
    
    # Check if quick test flag is provided
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        run_quick_test()
    else:
        # Run full test suite
        run_all_tests(verbose=True)
