# 🚀 Quick Start Guide

## Prerequisites

- Python 3.12+
- OpenAI API key
- `uv` package manager (recommended) or `pip`

## Setup (5 minutes)

### 1. Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt  # if you create one
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
```

### 3. Run the Demo

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the example scenarios
python main.py
```

## What You'll See

The demo runs 3 scenarios:

### Scenario 1: Technical Support
```
"The API is returning 500 errors. Can you check if the service is down?"
```
- Coordinator routes to Tech Support team
- Tech team checks system status
- Tech team searches knowledge base
- Creates bug ticket if needed

### Scenario 2: Billing Request
```
"I need a refund for invoice INV-003. I was charged twice by mistake."
```
- Coordinator routes to Billing team
- Billing looks up invoice history
- Processes refund request

### Scenario 3: Ambiguous Request
```
"I need help with something"
```
- Coordinator asks for clarification
- Demonstrates routing logic

## Understanding the Output

You'll see output like:

```
✓ Node: coordinator
  Content: tech

✓ Node: tech_team
  Content: I've checked the API status and it's currently operational...
```

This shows:
1. Which nodes are executing
2. What decisions are being made
3. What actions are taken

## Next Steps

### Modify the Example

1. **Add your own tools** in `main.py`
2. **Create new subgraphs** for different teams
3. **Customize prompts** for different behavior

### Deploy with LangGraph Server

```bash
# Start the development server
langgraph dev

# Access at http://localhost:2024
```

### Enable LangSmith Tracing

```bash
# In .env file
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_key
```

Then view traces at https://smith.langchain.com

## Common Issues

### "OPENAI_API_KEY not found"
- Make sure you copied `.env.example` to `.env`
- Add your OpenAI API key to `.env`

### Import errors
- Run `uv sync` to install dependencies
- Activate virtual environment: `source .venv/bin/activate`

### Rate limits
- The demo makes multiple API calls
- If you hit rate limits, add delays between examples

## Learn More

- Read the full [README.md](README.md) for architecture details
- Check [main.py](main.py) for implementation
- Compare with [hierarchical-team-pattern-langgraph](../hierarchical-team-pattern-langgraph) to see the differences
