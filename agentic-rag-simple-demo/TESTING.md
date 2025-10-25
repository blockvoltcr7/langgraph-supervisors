# 🧪 Testing Guide - Agentic RAG

Complete guide for testing and verifying the Agentic RAG system's retrieval behavior.

## Test Scripts

### 1. `verify_retrieval.py` - Quick Verification ⚡

**Purpose:** Fast check that agent correctly decides when to retrieve

**Usage:**
```bash
python verify_retrieval.py
```

**What it tests:**
- ✅ 3 simple queries (should NOT retrieve)
- ✅ 3 technical queries (should retrieve)
- ✅ Total: 6 tests

**Output:**
```
================================================================================
RETRIEVAL VERIFICATION - Quick Check
================================================================================

TEST 1: Simple Queries (Should NOT Retrieve)
Query: "Hi! How are you?"
Expected: ⚡ Should NOT retrieve
Actual: ⚡ No retrieval
Result: ✅ PASS

[... more tests ...]

SUMMARY
No Retrieval Tests: 3/3 passed
Retrieval Tests: 3/3 passed

Total: 6/6 passed
🎉 All verification tests passed!
```

**Time:** ~1-2 minutes

---

### 2. `test_agentic_rag.py` - Comprehensive Test Suite 🔬

**Purpose:** Thorough testing of all retrieval scenarios

**Usage:**
```bash
# Full test suite (14 tests)
python test_agentic_rag.py

# Quick test (4 tests)
python test_agentic_rag.py --quick
```

**What it tests:**
- ✅ 6 cases where retrieval should NOT be used
- ✅ 8 cases where retrieval SHOULD be used
- ✅ Multiple categories: greetings, technical, API, concepts
- ✅ Edge cases and variations

**Output:**
```
================================================================================
AGENTIC RAG TEST SUITE - Retrieval Verification
================================================================================

Total test cases: 14
  - Should NOT retrieve: 6
  - Should retrieve: 8

[... detailed test results ...]

TEST SUMMARY
📊 Overall Results:
   Total Tests: 14
   ✅ Passed: 14
   ❌ Failed: 0
   Success Rate: 100.0%

📋 By Category:
   Greeting: 3/3 passed
   Technical Definition: 2/2 passed
   API Question: 2/2 passed
   [...]

🎯 Retrieval Decision Accuracy:
   No Retrieval Cases: 6/6 correct
   Retrieval Cases: 8/8 correct
```

**Time:** ~3-5 minutes

---

## Test Categories

### Category 1: No Retrieval Needed ❌

These queries should be answered directly without retrieving:

| Query | Category | Why No Retrieval |
|-------|----------|------------------|
| "Hi! How are you?" | Greeting | Social interaction |
| "Hello there!" | Greeting | Social interaction |
| "Thanks for your help!" | Acknowledgment | Polite response |
| "What's 2 + 2?" | General Knowledge | Basic math |
| "Can you help me?" | Generic | Too vague |
| "Good morning!" | Greeting | Social interaction |

**Expected Behavior:**
- ⚡ Fast response (no vector search)
- 💰 Lower cost (fewer API calls)
- 💬 Natural conversation

---

### Category 2: Retrieval Required ✅

These queries need information from the knowledge base:

| Query | Category | Why Retrieval Needed |
|-------|----------|---------------------|
| "What is LangGraph?" | Technical Definition | Specific framework info |
| "How do I create a StateGraph?" | API Question | Implementation details |
| "Explain checkpointers" | Concept | Technical concept |
| "What are LangGraph's key features?" | Technical Details | Specific features |
| "How does persistence work?" | Feature Question | Technical feature |
| "Tell me about subgraphs" | Advanced Concept | Complex topic |
| "What is human-in-the-loop?" | Pattern Question | Specific pattern |
| "How do I use multi-agent systems?" | Implementation | Technical how-to |

**Expected Behavior:**
- 🔍 Retrieves relevant docs
- 🎯 Accurate, grounded answers
- 📚 Cites documentation

---

## Understanding Test Results

### ✅ PASS Criteria

A test passes when:
1. **Expected NO retrieval** → Agent responds directly
2. **Expected retrieval** → Agent uses retrieval tool
3. No errors during execution

### ❌ FAIL Scenarios

A test fails when:
1. **Expected NO retrieval** → Agent retrieved (over-retrieval)
2. **Expected retrieval** → Agent didn't retrieve (under-retrieval)
3. Error or exception occurred

### 📊 Metrics Tracked

- **Retrieval Used**: Boolean flag
- **Tool Calls Detected**: Whether agent called tools
- **Response Preview**: First 100 chars of response
- **Category**: Type of query
- **Pass/Fail**: Test result

---

## Running Tests

### Quick Verification (Recommended First)

```bash
# Fast check - 6 tests
python verify_retrieval.py
```

**Use when:**
- Quick sanity check
- After code changes
- Before committing

---

### Comprehensive Testing

```bash
# Full suite - 14 tests
python test_agentic_rag.py
```

**Use when:**
- Thorough validation needed
- Before deployment
- Investigating issues

---

### Quick Subset

```bash
# 4 representative tests
python test_agentic_rag.py --quick
```

**Use when:**
- Faster than full suite
- Still covers key scenarios

---

## Interpreting Results

### Perfect Score (100%)

```
Total: 14/14 passed
Success Rate: 100.0%
No Retrieval Cases: 6/6 correct
Retrieval Cases: 8/8 correct
```

**Meaning:** Agent perfectly decides when to retrieve ✅

---

### Partial Score (e.g., 85%)

```
Total: 12/14 passed
Success Rate: 85.7%
No Retrieval Cases: 6/6 correct
Retrieval Cases: 6/8 correct
```

**Meaning:** Agent over-retrieves or under-retrieves ⚠️

**Common causes:**
- Prompt needs tuning
- Model temperature too high
- Ambiguous queries

---

### Low Score (<70%)

```
Total: 8/14 passed
Success Rate: 57.1%
```

**Meaning:** Agent decision-making is inconsistent ❌

**Troubleshooting:**
1. Check prompt instructions
2. Verify model is correct
3. Review tool descriptions
4. Check for API errors

---

## Debugging Failed Tests

### Step 1: Run with Verbose Output

Both scripts already run verbose by default. Look for:

```
🧪 Test: with_retrieval_1
Query: "What is LangGraph?"
Expected: ✅ RETRIEVE
Actual: ❌ NO RETRIEVAL
Result: ❌ FAIL
```

### Step 2: Check Tool Calls

```
🔧 Tool calls detected: No
```

If expected retrieval but no tool calls → Agent didn't recognize need

### Step 3: Review Response

```
💬 Response preview: I don't have specific information...
```

If agent says "I don't know" → Should have retrieved

### Step 4: Enable LangSmith

```env
# In .env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_key
```

Then view traces at https://smith.langchain.com

---

## Common Issues & Solutions

### Issue 1: Over-Retrieval

**Symptom:** Agent retrieves for simple queries like "Hi!"

**Solution:**
```python
# In main.py, strengthen prompt:
prompt="""...
1. For general questions or greetings, respond directly WITHOUT using tools
   Examples: "Hi", "Thanks", "What's 2+2" → NO TOOLS
2. ONLY use tools for specific LangGraph technical questions
..."""
```

---

### Issue 2: Under-Retrieval

**Symptom:** Agent doesn't retrieve for technical questions

**Solution:**
```python
# Make tool description more prominent:
@tool
def retrieve_langgraph_docs(query: str) -> str:
    """
    🔍 IMPORTANT: Use this for ANY LangGraph technical question!
    
    Search the LangGraph documentation...
    """
```

---

### Issue 3: Inconsistent Results

**Symptom:** Same query sometimes retrieves, sometimes doesn't

**Solution:**
```python
# Lower temperature for more consistent behavior:
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
```

---

### Issue 4: All Tests Failing

**Symptom:** 0% pass rate

**Checklist:**
- [ ] `.env` file exists with valid API key
- [ ] Dependencies installed (`uv sync`)
- [ ] Virtual environment activated
- [ ] No API errors in output

---

## Adding Custom Tests

### Add to `test_agentic_rag.py`

```python
TEST_CASES.append({
    "id": "custom_test_1",
    "query": "Your custom query here",
    "should_retrieve": True,  # or False
    "reason": "Why this behavior is expected",
    "category": "Your Category"
})
```

### Add to `verify_retrieval.py`

```python
# For no-retrieval tests
no_retrieval_tests.append("Your query")

# For retrieval tests
retrieval_tests.append("Your query")
```

---

## Best Practices

### ✅ Do:
- Run `verify_retrieval.py` after every change
- Run full suite before deployment
- Add tests for edge cases you discover
- Check LangSmith traces for failures
- Test with real user queries

### ❌ Don't:
- Skip tests before committing
- Ignore failing tests
- Test without proper `.env` setup
- Modify expected results without reason
- Run tests without virtual environment

---

## Performance Benchmarks

### Expected Performance

| Metric | Target | Acceptable |
|--------|--------|------------|
| **Overall Accuracy** | 100% | ≥90% |
| **No Retrieval Accuracy** | 100% | ≥85% |
| **Retrieval Accuracy** | 100% | ≥95% |
| **Test Duration** | <5 min | <10 min |

### Optimization Tips

1. **Cache Vector Store** - Don't recreate every test
2. **Batch Tests** - Reuse graph instance
3. **Parallel Testing** - Run independent tests concurrently
4. **Mock Embeddings** - Use fake embeddings for speed

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test Agentic RAG

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install uv
          uv sync
      
      - name: Run tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          source .venv/bin/activate
          python test_agentic_rag.py
```

---

## Summary

### Quick Commands

```bash
# Fast verification (recommended)
python verify_retrieval.py

# Full test suite
python test_agentic_rag.py

# Quick subset
python test_agentic_rag.py --quick
```

### Success Criteria

- ✅ All tests pass (100%)
- ✅ No over-retrieval (fast responses for simple queries)
- ✅ No under-retrieval (accurate answers for technical queries)
- ✅ Consistent behavior across runs

### Next Steps

1. Run `verify_retrieval.py` to confirm setup
2. Review any failures
3. Run full suite for comprehensive validation
4. Add custom tests for your use cases
5. Integrate into CI/CD pipeline

---

**Testing ensures your Agentic RAG system makes smart retrieval decisions!** 🧪✨
