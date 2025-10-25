# 🧪 Test Cases for Customer Support System

This document lists all test queries and their expected behaviors.

## How to Run Tests

```bash
# Run full test suite
python test_scenarios.py

# Run quick test (3 scenarios)
python test_scenarios.py --quick
```

---

## Technical Support Test Cases

### ✅ Test 1: API Error
**Query:** `"The API is returning 500 errors. Can you check if the service is down?"`

**Expected Behavior:**
- Route to: `tech_team`
- Tools used: `check_system_status`, `search_knowledge_base`
- Response should mention: API status, operational status, documentation

---

### ✅ Test 2: Database Authentication
**Query:** `"I'm getting authentication errors when trying to connect to the database"`

**Expected Behavior:**
- Route to: `tech_team`
- Tools used: `check_system_status`, `search_knowledge_base`
- Response should mention: database, authentication, troubleshooting steps

---

### ✅ Test 3: Payment Gateway Down (Urgent)
**Query:** `"The payment gateway is not responding. This is urgent!"`

**Expected Behavior:**
- Route to: `tech_team`
- Tools used: `check_system_status`, `create_bug_ticket`
- Response should mention: payment gateway status, bug ticket created, priority

---

### ✅ Test 4: API Setup Documentation
**Query:** `"How do I set up the API authentication? I need the documentation."`

**Expected Behavior:**
- Route to: `tech_team`
- Tools used: `search_knowledge_base`
- Response should mention: API documentation, authentication setup, Bearer token

---

### ✅ Test 5: Critical Email Bug
**Query:** `"There's a critical bug in the email service. Users can't send emails."`

**Expected Behavior:**
- Route to: `tech_team`
- Tools used: `check_system_status`, `create_bug_ticket`
- Response should mention: email service status, bug ticket, priority

---

## Billing Support Test Cases

### ✅ Test 6: Refund Request
**Query:** `"I need a refund for invoice INV-003. I was charged twice by mistake."`

**Expected Behavior:**
- Route to: `billing_team`
- Tools used: `lookup_invoice`, `process_refund`
- Response should mention: invoice INV-003, refund processed, 3-5 business days

---

### ✅ Test 7: Payment History
**Query:** `"Can you show me my payment history for customer ID CUST-123?"`

**Expected Behavior:**
- Route to: `billing_team`
- Tools used: `lookup_invoice`
- Response should mention: customer CUST-123, invoice history, payment status

---

### ✅ Test 8: Subscription Upgrade
**Query:** `"I want to upgrade my subscription from basic to pro plan"`

**Expected Behavior:**
- Route to: `billing_team`
- Tools used: `update_subscription`
- Response should mention: subscription updated, pro plan, effective immediately

---

### ✅ Test 9: Incorrect Charge
**Query:** `"I was charged $99 but I cancelled my subscription last month"`

**Expected Behavior:**
- Route to: `billing_team`
- Tools used: `lookup_invoice`, `process_refund`
- Response should mention: invoice lookup, refund, cancellation

---

### ✅ Test 10: Invoice Status
**Query:** `"What's the status of my invoice INV-002?"`

**Expected Behavior:**
- Route to: `billing_team`
- Tools used: `lookup_invoice`
- Response should mention: invoice INV-002, payment status (Paid)

---

### ✅ Test 11: Subscription Downgrade
**Query:** `"I need to downgrade to the basic plan to save costs"`

**Expected Behavior:**
- Route to: `billing_team`
- Tools used: `update_subscription`
- Response should mention: subscription updated, basic plan, prorated

---

## Clarification Test Cases

### ✅ Test 12: Vague Request
**Query:** `"I need help with something"`

**Expected Behavior:**
- Route to: `clarification`
- Tools used: None
- Response should ask: "Could you please clarify if this is a technical issue or a billing question?"

---

### ✅ Test 13: Generic Greeting
**Query:** `"Hello, can you assist me?"`

**Expected Behavior:**
- Route to: `clarification`
- Tools used: None
- Response should ask for clarification about the type of issue

---

### ✅ Test 14: Unspecified Problem
**Query:** `"I have a problem"`

**Expected Behavior:**
- Route to: `clarification`
- Tools used: None
- Response should ask for more details

---

## Edge Cases & Complex Scenarios

### ✅ Test 15: Multiple Issues
**Query:** `"The API is down AND I need a refund for the downtime"`

**Expected Behavior:**
- Route to: `tech_team` (first mentioned issue)
- Tools used: `check_system_status`
- Response should address: API status
- Note: Coordinator picks one team; user may need to ask separately for refund

---

### ✅ Test 16: Payment API Status
**Query:** `"Check the status of the payment API service"`

**Expected Behavior:**
- Route to: `tech_team` (API/service focus)
- Tools used: `check_system_status`
- Response should mention: payment service status

---

### ✅ Test 17: Ambiguous Account Issue
**Query:** `"I'm having trouble with my account"`

**Expected Behavior:**
- Route to: `clarification` (could be tech or billing)
- Tools used: None
- Response should ask: technical issue or billing question?

---

## Test Coverage Summary

| Category | Test Count | Coverage |
|----------|-----------|----------|
| **Technical Support** | 5 tests | System status, KB search, bug tickets |
| **Billing Support** | 6 tests | Invoices, refunds, subscriptions |
| **Clarification** | 3 tests | Vague/ambiguous requests |
| **Edge Cases** | 3 tests | Multiple issues, ambiguous routing |
| **Total** | **17 tests** | All routing paths covered |

## Tools Coverage

| Tool | Test Cases Using It |
|------|-------------------|
| `check_system_status` | Tests 1, 2, 3, 5, 15, 16 |
| `search_knowledge_base` | Tests 1, 2, 4 |
| `create_bug_ticket` | Tests 3, 5 |
| `lookup_invoice` | Tests 6, 7, 9, 10 |
| `process_refund` | Tests 6, 9 |
| `update_subscription` | Tests 8, 11 |

## Expected Success Criteria

For each test to pass:
1. ✅ Correct routing (coordinator sends to right team)
2. ✅ Appropriate tools used
3. ✅ Response contains expected keywords
4. ✅ No errors during execution

## Running Specific Tests

To test specific scenarios manually:

```python
from test_scenarios import TEST_SCENARIOS, run_test_scenario
from main import create_coordinator_graph

graph = create_coordinator_graph()

# Run test 1 (API error)
run_test_scenario(graph, TEST_SCENARIOS[0], verbose=True)

# Run test 6 (refund request)
run_test_scenario(graph, TEST_SCENARIOS[5], verbose=True)
```

## Interpreting Results

**✅ PASSED** - Test behaved as expected:
- Routed to correct team
- Used appropriate tools
- Response contained expected information

**❌ FAILED** - Test did not meet expectations:
- Wrong routing
- Missing tool usage
- Response missing key information

## Notes

- Tests use simulated tools (no real API calls)
- Each test runs in isolated thread (different thread_id)
- LLM responses may vary slightly but should follow expected patterns
- Some tests may show deprecation warnings (safe to ignore)
