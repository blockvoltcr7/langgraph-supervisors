# 🧪 Testing Guide

Complete guide for testing the Customer Support Subgraph System.

## Quick Start

```bash
# Full test suite (17 tests)
python test_scenarios.py

# Quick test (3 tests)
python test_scenarios.py --quick
```

## Test Files

### 1. `test_scenarios.py`
**Automated test runner** - Runs all test cases and validates results

**Features:**
- 17 comprehensive test scenarios
- Automatic validation of routing and tool usage
- Detailed pass/fail reporting
- Category breakdown

**Usage:**
```bash
# Run all tests
python test_scenarios.py

# Run quick test
python test_scenarios.py --quick
```

### 2. `TEST_CASES.md`
**Reference documentation** - Lists all test cases with expected results

**Contents:**
- Query text for each test
- Expected routing path
- Expected tools to be used
- Expected response keywords
- Coverage summary

### 3. `test_simple.py`
**Setup verification** - Tests that environment is configured correctly

**Usage:**
```bash
python test_simple.py
```

## Test Categories

### 🔧 Technical Support (5 tests)
Tests routing to tech team and tool usage:
- API errors
- Database issues
- Bug reporting
- Documentation lookup
- System status checks

### 💰 Billing Support (6 tests)
Tests routing to billing team and tool usage:
- Refund requests
- Invoice lookups
- Subscription changes
- Payment history
- Charge disputes

### ❓ Clarification (3 tests)
Tests handling of ambiguous requests:
- Vague queries
- Generic greetings
- Unspecified problems

### ⚡ Edge Cases (3 tests)
Tests complex scenarios:
- Multiple issues in one query
- Ambiguous routing situations
- Mixed keywords

## What Gets Tested

### ✅ Routing Logic
- Coordinator correctly identifies issue type
- Routes to appropriate team (tech/billing/clarification)
- Handles edge cases appropriately

### ✅ Tool Usage
- Correct tools are invoked
- Tools receive appropriate parameters
- Tool results are included in response

### ✅ Response Quality
- Contains expected keywords
- Addresses the user's question
- Provides actionable information

### ✅ State Management
- Tech team state tracks tickets/resolution
- Billing team state tracks refunds/subscriptions
- Parent state tracks team assignment

## Test Output Example

```
================================================================================
📋 Test: API error - should check status and search KB
Category: Technical Support
================================================================================
Query: "The API is returning 500 errors. Can you check if the service is down?"

Expected Route: tech_team
Expected Tools: ['check_system_status', 'search_knowledge_base']
Expected Keywords: ['API', 'operational', 'status']

--------------------------------------------------------------------------------

✓ Node: coordinator
  Response: tech...

✓ Node: tech_team
  Response: I found relevant information in the knowledge base regarding API...

================================================================================
✅ PASSED
================================================================================
```

## Understanding Test Results

### ✅ PASSED
All criteria met:
- ✓ Routed to correct team
- ✓ Used expected tools
- ✓ Response contains keywords

### ❌ FAILED
One or more criteria not met:
- ✗ Wrong routing
- ✗ Missing tool usage
- ✗ Missing keywords

Example failure:
```
❌ FAILED
Errors: ['Expected route 'tech_team' not found. Visited: ['coordinator', 'clarification']']
```

## Test Summary Output

```
================================================================================
TEST SUMMARY
================================================================================
Total Tests: 17
✅ Passed: 15
❌ Failed: 2
Success Rate: 88.2%

--------------------------------------------------------------------------------
CATEGORY BREAKDOWN:
--------------------------------------------------------------------------------
Technical Support: 5/5 passed
Billing Support: 6/6 passed
Clarification: 2/3 passed
Edge Case: 2/3 passed
```

## Running Individual Tests

### Option 1: Use test_scenarios.py
```python
from test_scenarios import TEST_SCENARIOS, run_test_scenario
from main import create_coordinator_graph

graph = create_coordinator_graph()

# Run specific test by index
run_test_scenario(graph, TEST_SCENARIOS[0], verbose=True)
```

### Option 2: Manual testing
```python
from main import create_coordinator_graph
from langchain_core.messages import HumanMessage

graph = create_coordinator_graph()

# Test a query
for chunk in graph.stream(
    {"messages": [HumanMessage(content="Your test query here")]},
    {"configurable": {"thread_id": "test-123"}}
):
    print(chunk)
```

## Test Coverage Matrix

| Path | Test Cases | Status |
|------|-----------|--------|
| coordinator → tech_team | Tests 1-5, 15-16 | ✅ |
| coordinator → billing_team | Tests 6-11 | ✅ |
| coordinator → clarification | Tests 12-14, 17 | ✅ |
| tech_team → check_system_status | Tests 1-3, 5, 15-16 | ✅ |
| tech_team → search_knowledge_base | Tests 1-2, 4 | ✅ |
| tech_team → create_bug_ticket | Tests 3, 5 | ✅ |
| billing_team → lookup_invoice | Tests 6-7, 9-10 | ✅ |
| billing_team → process_refund | Tests 6, 9 | ✅ |
| billing_team → update_subscription | Tests 8, 11 | ✅ |

## Debugging Failed Tests

### 1. Check Routing
```python
# Add debug output in coordinator_node
print(f"Coordinator decision: {assigned_team}")
```

### 2. Check Tool Calls
```python
# Add debug output in agent nodes
print(f"Tools available: {[tool.name for tool in tools]}")
```

### 3. Check Response
```python
# Print full response
print(f"Full response: {result['messages'][-1].content}")
```

### 4. Enable LangSmith Tracing
```env
# In .env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_key
```

Then view detailed traces at https://smith.langchain.com

## Adding New Tests

To add a new test case to `test_scenarios.py`:

```python
{
    "category": "Your Category",
    "query": "Your test query here",
    "expected_route": "tech_team",  # or billing_team, clarification
    "expected_tools": ["tool_name"],
    "expected_keywords": ["keyword1", "keyword2"],
    "description": "Brief description of what this tests"
}
```

Add to the `TEST_SCENARIOS` list and re-run tests.

## Best Practices

### ✅ Do:
- Run tests after code changes
- Check all categories pass
- Review failed test details
- Add tests for new features
- Use LangSmith for debugging

### ❌ Don't:
- Ignore failing tests
- Skip edge case tests
- Test without .env configured
- Modify expected results without reason

## Continuous Testing

### Before Committing:
```bash
# 1. Verify setup
python test_simple.py

# 2. Run quick test
python test_scenarios.py --quick

# 3. If quick test passes, run full suite
python test_scenarios.py
```

### After Changes:
```bash
# Run full test suite
python test_scenarios.py

# Check success rate
# Should be > 90%
```

## Performance Notes

- Full test suite: ~2-3 minutes (17 tests with LLM calls)
- Quick test: ~30 seconds (3 tests)
- Each test makes 2-4 LLM calls
- Tests run sequentially (not parallel)

## Troubleshooting Tests

### "OPENAI_API_KEY not found"
```bash
cp .env.example .env
# Add your API key to .env
```

### "Rate limit exceeded"
```python
# Add delays in test_scenarios.py
import time
time.sleep(2)  # Between tests
```

### "All tests failing"
```bash
# Check environment
python test_simple.py

# Check main.py works
python main.py
```

### "Inconsistent results"
- LLM responses can vary
- Some keywords might be phrased differently
- Check LangSmith traces for details

## Summary

The test suite provides:
- ✅ **Comprehensive coverage** - All routing paths tested
- ✅ **Automated validation** - No manual checking needed
- ✅ **Clear reporting** - Easy to see what passed/failed
- ✅ **Easy to extend** - Add new tests easily
- ✅ **Documentation** - TEST_CASES.md for reference

Run tests regularly to ensure system works correctly!
