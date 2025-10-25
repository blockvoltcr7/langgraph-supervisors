# ✅ Setup Checklist

Quick checklist to get up and running in 5 minutes.

## Prerequisites
- [ ] Python 3.12+ installed
- [ ] `uv` package manager installed (or `pip`)
- [ ] OpenAI API key ready

## Setup Steps

### 1. Environment Setup
```bash
# Navigate to project
cd /path/to/supervisor-subgraph-pattern-demo-langgraph

# Install dependencies (already done if you ran uv sync)
uv sync

# Activate virtual environment
source .venv/bin/activate
```
- [ ] Dependencies installed
- [ ] Virtual environment activated

### 2. Configure API Keys
```bash
# Copy example file
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

**In .env file, replace:**
```env
# CHANGE THIS:
OPENAI_API_KEY=your_openai_api_key_here

# TO YOUR ACTUAL KEY:
OPENAI_API_KEY=sk-proj-abc123...
```

- [ ] `.env` file created
- [ ] OpenAI API key added (starts with `sk-proj-` or `sk-`)
- [ ] Key is NOT the placeholder value

### 3. Optional: LangSmith Tracing
```env
# In .env file (optional)
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_actual_langsmith_key
LANGCHAIN_PROJECT=subgraph-customer-support
```
- [ ] LangSmith configured (optional)
- [ ] Or set `LANGSMITH_TRACING=false`

### 4. Verify Setup
```bash
python test_simple.py
```

**Expected output:**
```
✅ Loaded environment from: /path/to/.env
✅ All imports successful
✅ OPENAI_API_KEY is set
✅ Graph created successfully
✅ Subgraphs have isolated state
✅ ALL TESTS PASSED!
```

- [ ] All tests passed

### 5. Run Demo
```bash
python main.py
```

**Expected output:**
```
✅ Loaded environment from: /path/to/.env
ℹ️  LangSmith tracing disabled

================================================================================
CUSTOMER SUPPORT SYSTEM WITH SUBGRAPHS
================================================================================

📋 Example 1: Technical Support Request
...
```

- [ ] Demo runs successfully
- [ ] No authentication errors
- [ ] Examples complete

## Common Issues

### ❌ Authentication Error (401)
**Problem:** Invalid API key
**Solution:** 
1. Check `.env` file exists
2. Verify API key is correct (not placeholder)
3. Get new key from https://platform.openai.com/api-keys

### ❌ Module Not Found
**Problem:** Dependencies not installed
**Solution:**
```bash
uv sync
source .venv/bin/activate
```

### ❌ .env File Not Found
**Problem:** Forgot to copy `.env.example`
**Solution:**
```bash
cp .env.example .env
# Then edit .env with your API key
```

## Quick Commands Reference

```bash
# Setup
uv sync                          # Install dependencies
cp .env.example .env            # Create config file
source .venv/bin/activate       # Activate environment

# Test
python test_simple.py           # Verify setup

# Run
python main.py                  # Run demo

# Deploy (optional)
langgraph dev                   # Start dev server
```

## File Checklist

Your directory should have:
- [ ] `main.py` - Main implementation
- [ ] `.env` - Your configuration (with real API key)
- [ ] `.venv/` - Virtual environment
- [ ] `pyproject.toml` - Dependencies
- [ ] `README.md` - Documentation
- [ ] `test_simple.py` - Setup tests

## Next Steps

Once setup is complete:

1. **Read the docs:**
   - [GETTING_STARTED.md](GETTING_STARTED.md) - Tutorial
   - [SUBGRAPHS_VS_SUPERVISOR.md](SUBGRAPHS_VS_SUPERVISOR.md) - Comparison

2. **Explore the code:**
   - Open `main.py` and read the comments
   - Understand the subgraph pattern

3. **Experiment:**
   - Add your own tools
   - Create new subgraphs
   - Modify prompts

4. **Compare:**
   - Check `../hierarchical-team-pattern-langgraph`
   - See the differences in practice

## Success Criteria

You're ready when:
- ✅ `python test_simple.py` passes all tests
- ✅ `python main.py` runs without errors
- ✅ You see example outputs with tech/billing teams
- ✅ No authentication errors

## Need Help?

- **Troubleshooting:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Quick Start:** [QUICKSTART.md](QUICKSTART.md)
- **Full Guide:** [GETTING_STARTED.md](GETTING_STARTED.md)

---

**Time to complete:** ~5 minutes  
**Difficulty:** Easy  
**Prerequisites:** Python, OpenAI API key
