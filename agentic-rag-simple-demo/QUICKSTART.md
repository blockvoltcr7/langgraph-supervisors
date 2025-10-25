# 🚀 Quick Start Guide - Agentic RAG

Get up and running with Agentic RAG in 5 minutes!

## Prerequisites

- Python 3.12+
- `uv` package manager (or `pip`)
- OpenAI API key

## Setup Steps

### 1. Navigate to Project

```bash
cd /path/to/agentic-rag-simple-demo
```

### 2. Install Dependencies

```bash
uv sync
```

This installs:
- LangGraph (graph framework)
- LangChain (LLM tools)
- FAISS (vector store)
- OpenAI (embeddings & LLM)

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
OPENAI_API_KEY=sk-proj-your_actual_key_here
```

### 4. Activate Virtual Environment

```bash
source .venv/bin/activate
```

### 5. Run the Demo

```bash
python main.py
```

## Expected Output

```
✅ Loaded environment from: /path/to/.env
ℹ️  LangSmith tracing disabled

📚 Creating knowledge base...
   Split into 12 chunks
   ✅ Vector store created with 12 chunks

================================================================================
AGENTIC RAG DEMO - Agent Decides When to Retrieve
================================================================================

================================================================================
📋 Query 1/6
================================================================================
Question: "Hi! How are you today?"
Expected: No retrieval (general greeting)
--------------------------------------------------------------------------------

💬 Response: Hello! I'm here and ready to help...

📊 Retrieval used: ❌ NO

================================================================================
📋 Query 2/6
================================================================================
Question: "What is LangGraph and what are its key features?"
Expected: Retrieval needed (specific technical question)
--------------------------------------------------------------------------------

🔍 Retrieving docs for: 'What is LangGraph and what are its key features?'
   ✅ Retrieved 2 relevant documents

💬 Response: LangGraph is a framework for building stateful...

📊 Retrieval used: ✅ YES

[... 4 more queries ...]

================================================================================

✅ Demo complete!

💡 Key Takeaways:
   - Agent decides when retrieval is needed
   - Simple queries answered directly (faster, cheaper)
   - Technical queries trigger retrieval (accurate, grounded)
   - Best of both worlds: speed + accuracy
```

## What Just Happened?

1. **Vector Store Created** - 6 documents about LangGraph split into 12 chunks
2. **Embeddings Generated** - OpenAI creates vector representations
3. **6 Test Queries Run** - Mix of simple and technical questions
4. **Agent Decides** - For each query, agent chooses to retrieve or not
5. **Results Shown** - You see when retrieval was used

## Understanding the Results

### ❌ No Retrieval (3 queries)
- "Hi! How are you today?" - Greeting
- "What's 2 + 2?" - General knowledge
- "Thanks for your help!" - Acknowledgment

**Why:** Agent knows these don't need documentation lookup

### ✅ Retrieval Used (3 queries)
- "What is LangGraph?" - Technical definition
- "How do I create a StateGraph?" - API question
- "Explain checkpointers" - Specific concept

**Why:** Agent needs specific information from docs

## Try Your Own Queries

Modify `main.py` to test your own questions:

```python
test_queries = [
    {
        "query": "Your question here",
        "expected": "What you expect",
        "thread_id": "test-custom"
    }
]
```

## Common Issues

### "OPENAI_API_KEY not configured"
**Solution:** Edit `.env` file with your actual API key

### "Module not found"
**Solution:** 
```bash
uv sync
source .venv/bin/activate
```

### "Rate limit exceeded"
**Solution:** Wait a minute or upgrade your OpenAI plan

## Next Steps

1. **Read the README** - Understand how it works
2. **Modify the documents** - Add your own knowledge base
3. **Adjust parameters** - Tune chunk size, retrieval count
4. **Integrate with subgraph** - Use in your customer support system

## Quick Commands

```bash
# Setup
uv sync
cp .env.example .env
source .venv/bin/activate

# Run
python main.py

# Deploy (optional)
langgraph dev
```

## Success Criteria

You're ready when you see:
- ✅ Vector store created
- ✅ 6 queries processed
- ✅ Mix of retrieval/no-retrieval
- ✅ No errors

---

**Time to complete:** ~5 minutes  
**Difficulty:** Easy  
**Next:** Read README.md for deep dive
