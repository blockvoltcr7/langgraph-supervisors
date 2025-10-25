"""
Agentic RAG - Retrieval-Augmented Generation with Agent Decision Making

This demonstrates:
- Agent decides WHEN to retrieve from knowledge base
- Vector store with semantic search
- Document preprocessing and chunking
- Real-world use case: Technical documentation Q&A

Key Concept: Unlike basic RAG (always retrieves), the agent intelligently
decides if retrieval is needed based on the query.
"""

import os
from pathlib import Path
from typing import Literal, TypedDict, Annotated
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

# ============================================================================
# Load Environment Variables
# ============================================================================

script_dir = Path(__file__).parent
env_path = script_dir / ".env"

if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
    print(f"✅ Loaded environment from: {env_path}")
else:
    print(f"⚠️  Warning: .env file not found at {env_path}")
    print("   Please copy .env.example to .env and add your API keys")

# ============================================================================
# Configuration
# ============================================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
    raise ValueError(
        "OPENAI_API_KEY not configured properly.\n"
        "Please:\n"
        "1. Copy .env.example to .env\n"
        "2. Edit .env and add your actual OpenAI API key\n"
        f"   File location: {env_path}"
    )

model = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)
embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

# Optional LangSmith tracing
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")

if LANGSMITH_TRACING and LANGSMITH_API_KEY and LANGSMITH_API_KEY != "your_langsmith_api_key_here":
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "agentic-rag-demo")
    print(f"✅ LangSmith tracing enabled - Project: {os.environ['LANGCHAIN_PROJECT']}")
else:
    print("ℹ️  LangSmith tracing disabled (set LANGSMITH_TRACING=true in .env to enable)")

# ============================================================================
# Step 1: Prepare Knowledge Base
# ============================================================================

def create_vectorstore():
    """
    Create a vector store from sample documents.
    In production, you'd load from your actual documentation.
    """
    print("\n📚 Creating knowledge base...")
    
    # Sample documents about LangGraph concepts
    # In production, use WebBaseLoader or load from files
    documents = [
        Document(
            page_content="""
            LangGraph is a framework for building stateful, multi-actor applications with LLMs.
            It extends LangChain with the ability to create cyclical graphs, which are essential
            for developing agent-like behaviors where you call an LLM in a loop.
            
            Key features:
            - Cycles and Branching: Implement loops and conditionals in your apps
            - Persistence: Automatically save state after each step
            - Human-in-the-Loop: Interrupt graph execution for human approval
            - Streaming Support: Stream outputs as they are produced
            """,
            metadata={"source": "langgraph_intro", "topic": "basics"}
        ),
        Document(
            page_content="""
            StateGraph is the main graph class in LangGraph. It allows you to define nodes
            (functions that do work) and edges (connections between nodes).
            
            To create a graph:
            1. Define your state schema (what data flows through the graph)
            2. Create a StateGraph with that schema
            3. Add nodes using add_node()
            4. Add edges using add_edge() or add_conditional_edges()
            5. Compile the graph with compile()
            
            Example:
            from langgraph.graph import StateGraph
            graph = StateGraph(MyState)
            graph.add_node("process", process_function)
            graph.add_edge(START, "process")
            app = graph.compile()
            """,
            metadata={"source": "langgraph_stategraph", "topic": "api"}
        ),
        Document(
            page_content="""
            Checkpointers in LangGraph enable persistence. They save the state of your graph
            at each step, allowing you to:
            - Resume execution after interruption
            - Implement time-travel (go back to previous states)
            - Debug by inspecting state at any point
            
            Available checkpointers:
            - MemorySaver: In-memory (for development)
            - SqliteSaver: SQLite database
            - PostgresSaver: PostgreSQL database
            
            Usage:
            from langgraph.checkpoint.memory import MemorySaver
            checkpointer = MemorySaver()
            app = graph.compile(checkpointer=checkpointer)
            """,
            metadata={"source": "langgraph_persistence", "topic": "persistence"}
        ),
        Document(
            page_content="""
            Subgraphs allow you to compose graphs within graphs. A subgraph is a complete
            graph that can be used as a node in a parent graph.
            
            Benefits:
            - Modularity: Build reusable components
            - Isolation: Each subgraph can have its own state schema
            - Organization: Break complex systems into manageable pieces
            
            Example use case:
            A customer support system with separate subgraphs for technical support
            and billing, each with their own specialized tools and state.
            """,
            metadata={"source": "langgraph_subgraphs", "topic": "advanced"}
        ),
        Document(
            page_content="""
            Human-in-the-loop in LangGraph allows you to pause execution and wait for
            human input. This is critical for:
            - Approval workflows (e.g., approve a refund)
            - Collecting additional information
            - Handling edge cases
            
            Use the interrupt() function:
            from langgraph.types import interrupt
            
            def my_node(state):
                user_input = interrupt("Need your approval")
                # Process user_input
                return state
            
            The graph will pause until you provide input via Command.
            """,
            metadata={"source": "langgraph_human_in_loop", "topic": "advanced"}
        ),
        Document(
            page_content="""
            Multi-agent systems in LangGraph can be built using several patterns:
            
            1. Supervisor Pattern: A central supervisor routes tasks to specialized agents
            2. Hierarchical Teams: Multiple levels of supervisors and agents
            3. Collaborative: Agents work together on shared tasks
            
            The supervisor pattern is most common:
            - Supervisor decides which agent to invoke
            - Agents are specialized (research, coding, etc.)
            - Communication flows through supervisor
            
            Use create_react_agent() to build individual agents with tools.
            """,
            metadata={"source": "langgraph_multi_agent", "topic": "patterns"}
        ),
    ]
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )
    
    splits = text_splitter.split_documents(documents)
    print(f"   Split into {len(splits)} chunks")
    
    # Create vector store
    vectorstore = FAISS.from_documents(splits, embeddings)
    print(f"   ✅ Vector store created with {len(splits)} chunks")
    
    return vectorstore

# Create the vector store (in production, you'd cache this)
vectorstore = create_vectorstore()

# ============================================================================
# Step 2: Create Retrieval Tool
# ============================================================================

@tool
def retrieve_langgraph_docs(query: str) -> str:
    """
    Search the LangGraph documentation for relevant information.
    Use this when you need specific information about LangGraph features, APIs, or concepts.
    
    Args:
        query: The search query (e.g., "How do I create a StateGraph?")
    
    Returns:
        Relevant documentation snippets
    """
    print(f"\n🔍 Retrieving docs for: '{query}'")
    
    # Perform similarity search
    docs = vectorstore.similarity_search(query, k=2)
    
    # Format results
    results = []
    for i, doc in enumerate(docs, 1):
        results.append(f"[Document {i}]\n{doc.page_content}\n")
    
    combined = "\n".join(results)
    print(f"   ✅ Retrieved {len(docs)} relevant documents")
    
    return combined

# ============================================================================
# Step 3: Create Agentic RAG System
# ============================================================================

class AgenticRAGState(MessagesState):
    """State for the agentic RAG system"""
    retrieval_used: bool = False

def create_agentic_rag():
    """
    Create an agentic RAG system where the agent decides when to retrieve.
    
    Key difference from basic RAG:
    - Basic RAG: ALWAYS retrieves for every query
    - Agentic RAG: Agent DECIDES if retrieval is needed
    """
    
    # Create the agent with retrieval tool
    agent = create_react_agent(
        model,
        tools=[retrieve_langgraph_docs],
        prompt="""You are a helpful assistant that answers questions about LangGraph.

IMPORTANT INSTRUCTIONS:
1. For general questions or greetings, respond directly WITHOUT using tools
2. For specific technical questions about LangGraph, USE the retrieve_langgraph_docs tool
3. Only retrieve when you need specific information you don't already know
4. After retrieving, synthesize the information into a clear, helpful answer
5. If the retrieved docs don't answer the question, say so

Examples:
- "Hi, how are you?" → Respond directly, NO retrieval
- "What is LangGraph?" → Retrieve docs, then answer
- "How do I create a StateGraph?" → Retrieve docs, then answer
- "Thanks!" → Respond directly, NO retrieval

Be concise and helpful!"""
    )
    
    def agent_node(state: AgenticRAGState):
        """Run the agent"""
        result = agent.invoke(state)
        
        # Check if retrieval was used
        messages = result.get("messages", [])
        retrieval_used = any(
            hasattr(msg, "tool_calls") and msg.tool_calls
            for msg in messages
        )
        
        return {
            "messages": result["messages"],
            "retrieval_used": retrieval_used
        }
    
    # Build the graph
    builder = StateGraph(AgenticRAGState)
    builder.add_node("agent", agent_node)
    builder.add_edge(START, "agent")
    builder.add_edge("agent", END)
    
    # Compile with checkpointer
    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)

# Export for LangGraph server
graph = create_agentic_rag()

# ============================================================================
# Demo Usage
# ============================================================================

def main():
    """Run example queries demonstrating agentic RAG"""
    print("\n" + "="*80)
    print("AGENTIC RAG DEMO - Agent Decides When to Retrieve")
    print("="*80)
    
    graph = create_agentic_rag()
    
    # Test queries
    test_queries = [
        {
            "query": "Hi! How are you today?",
            "expected": "No retrieval (general greeting)",
            "thread_id": "test-1"
        },
        {
            "query": "What is LangGraph and what are its key features?",
            "expected": "Retrieval needed (specific technical question)",
            "thread_id": "test-2"
        },
        {
            "query": "How do I create a StateGraph?",
            "expected": "Retrieval needed (API question)",
            "thread_id": "test-3"
        },
        {
            "query": "What's 2 + 2?",
            "expected": "No retrieval (general knowledge)",
            "thread_id": "test-4"
        },
        {
            "query": "Explain checkpointers and persistence in LangGraph",
            "expected": "Retrieval needed (specific concept)",
            "thread_id": "test-5"
        },
        {
            "query": "Thanks for your help!",
            "expected": "No retrieval (acknowledgment)",
            "thread_id": "test-6"
        },
    ]
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"📋 Query {i}/{len(test_queries)}")
        print(f"{'='*80}")
        print(f"Question: \"{test['query']}\"")
        print(f"Expected: {test['expected']}")
        print(f"{'-'*80}")
        
        config = {"configurable": {"thread_id": test["thread_id"]}}
        
        retrieval_used = False
        for chunk in graph.stream(
            {"messages": [HumanMessage(content=test["query"])]},
            config
        ):
            for node, values in chunk.items():
                if "retrieval_used" in values:
                    retrieval_used = values["retrieval_used"]
                
                if "messages" in values and values["messages"]:
                    last_msg = values["messages"][-1]
                    if hasattr(last_msg, 'content') and last_msg.content:
                        # Only print final AI response
                        if isinstance(last_msg, AIMessage) and not hasattr(last_msg, 'tool_calls'):
                            print(f"\n💬 Response: {last_msg.content}")
        
        print(f"\n📊 Retrieval used: {'✅ YES' if retrieval_used else '❌ NO'}")
    
    print("\n" + "="*80)
    print("\n✅ Demo complete!")
    print("\n💡 Key Takeaways:")
    print("   - Agent decides when retrieval is needed")
    print("   - Simple queries answered directly (faster, cheaper)")
    print("   - Technical queries trigger retrieval (accurate, grounded)")
    print("   - Best of both worlds: speed + accuracy")
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
