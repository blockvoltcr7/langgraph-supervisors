# 🤖 Agentic RAG - Intelligent Retrieval-Augmented Generation

A practical demonstration of **Agentic RAG** where an AI agent intelligently decides WHEN to retrieve from a knowledge base, unlike basic RAG which always retrieves.

## 🎯 What is Agentic RAG?

### Basic RAG (Traditional)
```
User Query → ALWAYS Retrieve → Generate Answer
```
- ❌ Retrieves even for simple questions ("Hi!")
- ❌ Slower (unnecessary vector search)
- ❌ More expensive (extra API calls)

### Agentic RAG (This Example)
```
User Query → Agent Decides → Retrieve if needed → Generate Answer
```
- ✅ Only retrieves when necessary
- ✅ Faster for simple queries
- ✅ More cost-effective
- ✅ Better user experience

## 🏗️ Architecture

```
┌─────────────┐
│ User Query  │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Agent (LLM)        │
│  - Analyzes query   │
│  - Decides action   │
└──────┬──────────────┘
       │
       ├─────────────┐
       │             │
       ▼             ▼
┌──────────┐   ┌──────────────┐
│ Respond  │   │ Retrieve     │
│ Directly │   │ from Vector  │
└──────────┘   │ Store        │
               └──────┬───────┘
                      │
                      ▼
               ┌──────────────┐
               │ Synthesize   │
               │ Answer       │
               └──────────────┘
```

## ✨ Key Features

- 🧠 **Intelligent Decision Making** - Agent decides when retrieval is needed
- 📚 **Vector Store** - FAISS for semantic search
- 🔍 **Similarity Search** - Find most relevant documents
- 💬 **Natural Conversation** - Handles greetings, follow-ups, technical questions
- 📊 **Retrieval Tracking** - See when retrieval was used
- 🎯 **Real-world Use Case** - LangGraph documentation Q&A

## 🚀 Quick Start

### 1. Install Dependencies

```bash
uv sync
```

### 2. Set Up Environment

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```env
OPENAI_API_KEY=sk-proj-your_key_here
```

### 3. Run the Demo

```bash
source .venv/bin/activate
python main.py
```

### 4. Verify Retrieval Behavior (Optional)

```bash
# Quick verification (6 tests)
python verify_retrieval.py

# Comprehensive test suite (14 tests)
python test_agentic_rag.py
```

See [TESTING.md](TESTING.md) for detailed testing guide.

## 💬 Example Queries

The demo runs 6 test queries demonstrating intelligent retrieval:

### ❌ No Retrieval Needed

**Query 1:** "Hi! How are you today?"
- **Agent Decision:** Respond directly
- **Why:** General greeting, no technical info needed
- **Result:** Fast, direct response

**Query 4:** "What's 2 + 2?"
- **Agent Decision:** Respond directly
- **Why:** General knowledge
- **Result:** No need to search docs

**Query 6:** "Thanks for your help!"
- **Agent Decision:** Respond directly
- **Why:** Acknowledgment
- **Result:** Polite response

### ✅ Retrieval Needed

**Query 2:** "What is LangGraph and what are its key features?"
- **Agent Decision:** Retrieve from docs
- **Why:** Specific technical question
- **Result:** Accurate, grounded answer

**Query 3:** "How do I create a StateGraph?"
- **Agent Decision:** Retrieve from docs
- **Why:** API/implementation question
- **Result:** Code examples and instructions

**Query 5:** "Explain checkpointers and persistence in LangGraph"
- **Agent Decision:** Retrieve from docs
- **Why:** Specific concept explanation
- **Result:** Detailed technical answer

## 📊 Expected Output

```
================================================================================
AGENTIC RAG DEMO - Agent Decides When to Retrieve
================================================================================

📚 Creating knowledge base...
   Split into 12 chunks
   ✅ Vector store created with 12 chunks

================================================================================
📋 Query 1/6
================================================================================
Question: "Hi! How are you today?"
Expected: No retrieval (general greeting)
--------------------------------------------------------------------------------

💬 Response: Hello! I'm here and ready to help you with any questions...

📊 Retrieval used: ❌ NO

================================================================================
📋 Query 2/6
================================================================================
Question: "What is LangGraph and what are its key features?"
Expected: Retrieval needed (specific technical question)
--------------------------------------------------------------------------------

🔍 Retrieving docs for: 'What is LangGraph and what are its key features?'
   ✅ Retrieved 2 relevant documents

💬 Response: LangGraph is a framework for building stateful, multi-actor...

📊 Retrieval used: ✅ YES
```

## 🔍 How It Works

### Step 1: Create Knowledge Base

```python
# Sample documents about LangGraph
documents = [
    Document(page_content="LangGraph is a framework..."),
    Document(page_content="StateGraph is the main..."),
    # ... more documents
]

# Split into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
splits = text_splitter.split_documents(documents)

# Create vector store
vectorstore = FAISS.from_documents(splits, embeddings)
```

### Step 2: Create Retrieval Tool

```python
@tool
def retrieve_langgraph_docs(query: str) -> str:
    """Search the LangGraph documentation"""
    docs = vectorstore.similarity_search(query, k=2)
    return format_results(docs)
```

### Step 3: Create Agent with Decision Making

```python
agent = create_react_agent(
    model,
    tools=[retrieve_langgraph_docs],
    prompt="""You are a helpful assistant.

IMPORTANT:
1. For general questions, respond directly WITHOUT tools
2. For technical questions, USE the retrieve_langgraph_docs tool
3. Only retrieve when you need specific information"""
)
```

## 🎓 Key Concepts Demonstrated

### 1. Vector Store (FAISS)
- Stores document embeddings
- Enables semantic search
- Fast similarity matching

### 2. Text Chunking
- Splits documents into manageable pieces
- Overlapping chunks for context
- Optimized for retrieval

### 3. Agent Decision Making
- LLM analyzes the query
- Decides if retrieval is needed
- Chooses appropriate action

### 4. Tool Calling
- Agent has access to retrieval tool
- Calls tool only when needed
- Synthesizes retrieved information

## 📈 Performance Comparison

| Scenario | Basic RAG | Agentic RAG |
|----------|-----------|-------------|
| **"Hi!"** | Retrieves (slow) | Direct response (fast) |
| **"What is X?"** | Retrieves (good) | Retrieves (good) |
| **"Thanks!"** | Retrieves (waste) | Direct response (efficient) |
| **Cost** | Higher | Lower |
| **Speed** | Slower | Faster (for simple queries) |
| **Accuracy** | Good | Good (when needed) |

## 🎯 When to Use Agentic RAG

### ✅ Use Agentic RAG When:
- Mix of simple and complex queries
- Cost optimization is important
- Speed matters for simple questions
- You want natural conversation flow
- Users ask greetings, follow-ups, etc.

### ❌ Use Basic RAG When:
- ALL queries need retrieval
- Simplicity is more important
- You have very few queries
- Every query is technical

## 🔧 Customization

### Add Your Own Documents

```python
# Load from web
from langchain_community.document_loaders import WebBaseLoader
loader = WebBaseLoader("https://your-docs.com")
docs = loader.load()

# Or load from files
from langchain_community.document_loaders import TextLoader
loader = TextLoader("your_docs.txt")
docs = loader.load()
```

### Adjust Retrieval Parameters

```python
# Change number of documents retrieved
docs = vectorstore.similarity_search(query, k=3)  # Get 3 instead of 2

# Change chunk size
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # Larger chunks
    chunk_overlap=100
)
```

### Modify Agent Behavior

```python
# Make agent more/less likely to retrieve
prompt="""You are a helpful assistant.

IMPORTANT:
1. ALWAYS use retrieval for ANY technical question  # More aggressive
2. Only use retrieval for very specific questions    # More conservative
"""
```

## 🆚 Comparison with Your Subgraph Example

| Feature | Subgraph Pattern | Agentic RAG |
|---------|-----------------|-------------|
| **Focus** | Routing & modularity | Intelligent retrieval |
| **State** | Different schemas per team | Tracks retrieval usage |
| **Decision** | Route to teams | Retrieve or not |
| **Use Case** | Multi-team systems | Knowledge base Q&A |
| **Complexity** | Higher | Lower |

**Can Combine:** Use Agentic RAG WITHIN a subgraph! For example, your tech support subgraph could use Agentic RAG for its knowledge base search.

## 💡 Next Steps

### 1. Integrate with Your Subgraph
```python
# In your tech support subgraph
@tool
def search_knowledge_base_smart(query: str) -> str:
    """Use agentic RAG instead of keyword search"""
    return retrieve_langgraph_docs(query)
```

### 2. Add More Documents
- Load your actual documentation
- Add product manuals
- Include FAQs

### 3. Improve Retrieval
- Try different embedding models
- Experiment with chunk sizes
- Add metadata filtering

### 4. Add Persistence
- Save vector store to disk
- Cache embeddings
- Use PostgreSQL for production

## 📚 Learn More

- **LangGraph Docs:** https://langchain-ai.github.io/langgraph/
- **FAISS:** https://github.com/facebookresearch/faiss
- **LangChain RAG:** https://python.langchain.com/docs/tutorials/rag/
- **Your Subgraph Example:** `../supervisor-subgraph-pattern-demo-langgraph/`

## 🎓 Key Takeaways

1. **Agentic RAG = Smart Retrieval** - Agent decides when to retrieve
2. **Better UX** - Fast responses for simple queries
3. **Cost Effective** - Only retrieve when needed
4. **Easy to Implement** - Just add retrieval as a tool
5. **Production Ready** - Use with real documentation

---

**Built with LangGraph** 🦜🔗