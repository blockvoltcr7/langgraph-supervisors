# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### 1. Authentication Error (401)

**Error:**
```
openai.AuthenticationError: Error code: 401 - {'error': {'message': 'Incorrect API key provided...
```

**Solution:**
1. Make sure you have a `.env` file (not `.env.example`):
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and replace the placeholder with your **actual** OpenAI API key:
   ```env
   OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_KEY_HERE
   ```

3. Get your API key from: https://platform.openai.com/api-keys

4. The code now loads from `.env` file with `override=True`, so it will use your file values even if you have environment variables set.

### 2. .env File Not Found

**Error:**
```
⚠️  Warning: .env file not found at /path/to/.env
```

**Solution:**
```bash
# Copy the example file
cp .env.example .env

# Edit it with your API key
nano .env  # or use your preferred editor
```

### 3. Placeholder API Key

**Error:**
```
ValueError: OPENAI_API_KEY not configured properly.
```

**Cause:** You copied `.env.example` but didn't replace the placeholder value.

**Solution:**
Edit `.env` and change:
```env
# FROM:
OPENAI_API_KEY=your_openai_api_key_here

# TO:
OPENAI_API_KEY=sk-proj-your_actual_key_12345...
```

### 4. Deprecation Warnings

**Warning:**
```
LangGraphDeprecatedSinceV10: create_react_agent has been moved to `langchain.agents`
```

**Status:** This is just a warning, not an error. The code still works.

**Explanation:** LangGraph v1.0 moved `create_react_agent` to a different location. The old import still works but shows a deprecation warning.

**To Fix (Optional):**
Update the imports in `main.py`:
```python
# OLD:
from langgraph.prebuilt import create_react_agent

# NEW:
from langchain.agents import create_agent as create_react_agent
```

### 5. Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'langgraph'
```

**Solution:**
```bash
# Make sure you're in the project directory
cd /path/to/supervisor-subgraph-pattern-demo-langgraph

# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate

# Try again
python main.py
```

### 6. Environment Variables from System

**Issue:** The code is using system environment variables instead of `.env` file.

**Solution:** The code has been updated to use `override=True` when loading `.env`:
```python
load_dotenv(dotenv_path=env_path, override=True)
```

This ensures `.env` file values take precedence over system environment variables.

### 7. LangSmith Tracing Issues

**Issue:** LangSmith tracing not working or showing errors.

**Solution:**

1. **To disable tracing** (if you don't have LangSmith):
   ```env
   # In .env file
   LANGSMITH_TRACING=false
   ```

2. **To enable tracing** (if you have LangSmith):
   ```env
   LANGSMITH_TRACING=true
   LANGSMITH_API_KEY=your_actual_langsmith_key
   LANGCHAIN_PROJECT=subgraph-customer-support
   ```

3. Get your LangSmith API key from: https://smith.langchain.com

### 8. Rate Limit Errors

**Error:**
```
openai.RateLimitError: Rate limit exceeded
```

**Solution:**
1. Add delays between examples in `main.py`:
   ```python
   import time
   
   # After each example
   time.sleep(5)
   ```

2. Or run examples one at a time by commenting out others.

3. Check your OpenAI usage limits at: https://platform.openai.com/usage

## Verification Steps

### Step 1: Check .env File Exists
```bash
ls -la .env
```

Should show: `.env` file exists

### Step 2: Check .env Contents
```bash
cat .env
```

Should show:
- `OPENAI_API_KEY=sk-proj-...` (actual key, not placeholder)
- Other optional settings

### Step 3: Test Environment Loading
```bash
python test_simple.py
```

Should show:
```
✅ ALL TESTS PASSED!
```

### Step 4: Run Main Demo
```bash
python main.py
```

Should show:
```
✅ Loaded environment from: /path/to/.env
ℹ️  LangSmith tracing disabled
...
CUSTOMER SUPPORT SYSTEM WITH SUBGRAPHS
...
```

## Debug Mode

To see what environment variables are loaded:

```python
# Add to main.py temporarily
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')[:20]}...")  # First 20 chars
print(f"Loaded from: {env_path}")
print(f"File exists: {env_path.exists()}")
```

## Still Having Issues?

1. **Check Python version:**
   ```bash
   python --version  # Should be 3.12+
   ```

2. **Check virtual environment:**
   ```bash
   which python  # Should point to .venv
   ```

3. **Reinstall dependencies:**
   ```bash
   rm -rf .venv
   uv venv
   source .venv/bin/activate
   uv sync
   ```

4. **Check file permissions:**
   ```bash
   ls -la .env  # Should be readable
   ```

5. **Try absolute path:**
   ```python
   # In main.py, change to absolute path
   env_path = Path("/full/path/to/.env")
   ```

## Getting Help

If you're still stuck:

1. Check the error message carefully
2. Review [GETTING_STARTED.md](GETTING_STARTED.md)
3. Compare with [hierarchical-team-pattern-langgraph](../hierarchical-team-pattern-langgraph)
4. Open an issue on GitHub with:
   - Error message
   - Python version
   - OS version
   - Steps you've tried
