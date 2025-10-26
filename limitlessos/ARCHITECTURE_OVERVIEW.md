# Limitless OS AI Sales Agent - Architecture Overview

**Version:** 1.0  
**Date:** 2025-10-24

---

## Executive Summary

The Limitless OS AI Sales Agent is a conversational AI system that qualifies leads, handles objections, and closes sales through multi-turn conversations. Based on analysis of existing LangGraph patterns, we recommend a **Hybrid Architecture**.

### Recommended Architecture

✅ **Stateful Workflow Pattern** + **Shared State Pattern** + **Supervisor Pattern**

### Technology Stack

**Frontend:**
- **Next.js 16** (Vercel) with Vercel AI SDK for streaming
- **Node.js 20.9+** (LTS) - Required for Next.js 16
- React 19.2 with React Server Components
- TypeScript 5.1+
- Supabase Auth for owner authentication
- Drizzle ORM for database queries
- Tailwind CSS + shadcn/ui for UI components

**Backend:**
- Python 3.11+ (Google Cloud Run) with LangGraph
- FastAPI for REST and streaming endpoints
- OpenAI GPT-5-mini for LLM
- text-embedding-3-small for embeddings

**Database:**
- Supabase PostgreSQL with pgvector extension
- LangGraph checkpoints for state persistence
- Drizzle migrations for schema management

**Storage & Services:**
- Google Cloud Storage for documents
- Stripe for payments
- LangSmith for observability

---

## Core Requirements

### 1. User Identification
- Each lead identified by unique ID (Instagram handle)
- Track user across multiple sessions
- Maintain conversation history per user

### 2. State Persistence
- Store qualification status (qualified: true/false)
- Save conversation history
- Resume conversations across sessions
- Support days/weeks between interactions

### 3. Conversation Flow
- Greeting & initial qualification
- Multi-turn qualification (4-5 questions)
- Dynamic pitch (warm vs cold lead)
- Objection handling
- Closing & payment link delivery
- Urgency/scarcity messaging

### 4. Scalability
- Handle multiple concurrent users
- Support production workloads
- Database connection pooling
- Async message processing

### 5. Campaign Management
- Owner creates campaign codes embedded in URLs
- Track lead sources and conversion metrics
- Campaign-level analytics (clicks, conversations, conversions)
- Simple activation/deactivation control

### 6. Document Management (RAG)
- Owner uploads sales documents (PDF, DOCX, MD, TXT)
- Automatic embedding generation and storage
- Vector similarity search for context retrieval
- Dynamic agent knowledge without code changes

---

## Architecture Options Analysis

### ❌ Option 1: Flat Supervisor Pattern
**Why Not:**
- No state persistence (restarts from scratch)
- No session management
- Loses conversation history on restart

### ❌ Option 2: Hierarchical Team Pattern
**Why Not:**
- Overkill for single sales flow
- Extra LLM calls = higher cost
- Doesn't add value for this use case

### ❌ Option 3: Subgraph Pattern
**Why Not:**
- Isolated memory prevents context sharing
- Need full context across conversation stages
- Makes objection handling difficult

### ✅ Option 4: Stateful Workflow + Shared State
**Why Yes:**
- ✅ Persistence across sessions
- ✅ Shared state for conversation context
- ✅ Resume capability
- ✅ Simple routing logic
- ✅ Cost-efficient (fewer LLM calls)
- ✅ Production-ready

---

## High-Level Flow

```
Lead Clicks Campaign URL (https://limitlessos.com/chat/ABC123)
    ↓
Validate Campaign Code (campaigns table)
    ↓
Lead Enters Instagram Handle
    ↓
Generate/Lookup Thread ID
    ↓
Load State from Supabase PostgreSQL
    ↓
User Message → Python Backend (FastAPI)
    ↓
LangGraph Supervisor (routes based on current_stage)
    ↓
┌────────────┬────────────┬────────────┬────────────┬────────────┐
│  Greeter   │ Qualifier  │  Pitcher   │ Objection  │   Closer   │
│   Agent    │   Agent    │   Agent    │  Handler   │   Agent    │
└────────────┴────────────┴────────────┴────────────┴────────────┘
    ↓ (Agents use RAG via search_knowledge_base tool)
    ↓
Query pgvector for Document Embeddings
    ↓
Return Top K Similar Chunks
    ↓
Agent Generates Response with Context
    ↓
Update Shared State
    ↓
Save Checkpoint to Supabase
    ↓
Stream Response to Frontend (SSE/WebSocket)
    ↓
Next.js + Vercel AI SDK → Display to User
```

---

## Key Components

### 1. Campaign & Access Control Layer
- Campaign code validation
- Lead source tracking
- Simple active/inactive status
- Analytics per campaign

### 2. Session Management Layer
- User identification by Instagram handle
- Thread ID generation/lookup
- State loading from database
- Campaign association

### 3. Orchestration Layer (LangGraph)
- Rule-based supervisor node for routing
- 5 specialized agents with tools
- Shared state management across all agents

### 4. RAG Knowledge Layer
- Document upload and processing (Python worker)
- Text extraction and chunking
- Embedding generation (text-embedding-3-small)
- Vector similarity search (pgvector)
- Context injection into agent prompts

### 5. Persistence Layer
- Supabase PostgreSQL with LangGraph checkpointing
- pgvector extension for embeddings
- Automatic state saving after each node
- Resume capability across sessions
- Drizzle ORM for application tables

### 6. Integration Layer
- Stripe payment API for checkout
- Google Cloud Storage for documents
- Supabase Auth for owner login
- LangSmith for tracing and debugging

---

## Database Choice

### PostgreSQL ✅ RECOMMENDED

**Why PostgreSQL:**
- ✅ Production-ready
- ✅ ACID compliance
- ✅ Concurrent connections
- ✅ Advanced indexing
- ✅ JSON column support
- ✅ Scales to millions of conversations
- ✅ Official LangGraph support

**Setup:**
```python
from langgraph.checkpoint.postgres import PostgresSaver
import psycopg

conn = psycopg.connect(
    "postgresql://user:password@localhost:5432/limitlessos_db",
    autocommit=True,
)
checkpointer = PostgresSaver(conn)
graph = workflow.compile(checkpointer=checkpointer)
```

### SQLite (Development Only)
```python
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

conn = sqlite3.connect("sales_agent.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)
```

### ❌ Redis NOT RECOMMENDED
- No official LangGraph support
- Would require custom implementation
- Not designed for large state objects
- Use for caching only, not primary storage

---

## State Schema

```python
class SalesConversationState(TypedDict):
    # === Core Identity ===
    instagram_handle: str
    thread_id: str
    
    # === Message History ===
    messages: Annotated[list, add_messages]
    
    # === Conversation Stage ===
    current_stage: Literal[
        "greeting", "qualification", "pitch", 
        "objection", "closing", "followup", 
        "complete", "nurture"
    ]
    
    # === Qualification Data ===
    qualified: bool
    qualification_score: float  # 0-1
    business_type: Optional[str]
    monthly_revenue: Optional[str]
    main_pain_point: Optional[str]
    ready_to_invest: Optional[bool]
    
    # === Sales Progress ===
    pitch_delivered: bool
    pitch_type: Optional[Literal["warm", "cold"]]
    objections_raised: list[str]
    objections_handled: list[str]
    payment_link_sent: bool
    
    # === Routing ===
    next_agent: Literal[
        "greeter", "qualifier", "pitcher",
        "objection_handler", "closer", "followup", "FINISH"
    ]
```

---

## Agents Overview

### 1. Greeter Agent
- **Purpose:** Initial contact and routing
- **Tools:** None
- **Transitions to:** Qualifier or Nurture

### 2. Qualifier Agent
- **Purpose:** Ask qualification questions
- **Tools:** `update_qualification_data`, `calculate_qualification_score`
- **Transitions to:** Pitcher or Nurture

### 3. Pitcher Agent
- **Purpose:** Deliver tailored sales pitch
- **Tools:** `get_personalized_pitch`
- **Transitions to:** Objection Handler or Closer

### 4. Objection Handler Agent
- **Purpose:** Address concerns
- **Tools:** `record_objection`, `mark_objection_handled`
- **Transitions to:** Closer or Follow-up

### 5. Closer Agent
- **Purpose:** Close deal and send payment link
- **Tools:** `send_stripe_payment_link`, `send_onboarding_email`
- **Transitions to:** Complete or Follow-up

### 6. Follow-up Agent
- **Purpose:** Nurture leads who didn't close
- **Tools:** `schedule_followup`
- **Transitions to:** Closer or Nurture

---

## Key Benefits of This Architecture

### 1. Persistence ✅
- Conversations resume across days/weeks
- No data loss on restarts
- Full audit trail

### 2. Scalability ✅
- PostgreSQL handles concurrent users
- Connection pooling for performance
- Horizontal scaling possible

### 3. Cost Efficiency ✅
- Single LLM call per user message
- No nested supervisor overhead
- Efficient state management

### 4. Maintainability ✅
- Clear agent responsibilities
- Modular design
- Easy to add new agents

### 5. Production Ready ✅
- Error handling
- Monitoring hooks
- Time-travel debugging

---

## Trade-offs & Decisions

### Trade-off 1: Simplicity vs Flexibility
**Decision:** Simple supervisor over hierarchical
- **Rationale:** Sales flow is linear, doesn't need nested teams
- **Trade-off:** Less flexibility, but 80% lower latency

### Trade-off 2: PostgreSQL vs Redis
**Decision:** PostgreSQL for primary storage
- **Rationale:** Built-in LangGraph support, better for conversation history
- **Trade-off:** Slightly higher latency, but 100% reliable persistence

### Trade-off 3: Shared State vs Isolated State
**Decision:** Shared state across all agents
- **Rationale:** Sales conversation needs full context
- **Trade-off:** Less privacy isolation, but seamless conversation flow

### Trade-off 4: ReAct Agents vs Custom Nodes
**Decision:** Mix of both
- **Rationale:** Use ReAct for complex agents (Qualifier), custom for simple ones (Greeter)
- **Trade-off:** Slightly more complex, but optimal performance

---

## Next Steps

1. **Review detailed documentation:**
   - `SALES_PLAYBOOK.md` - Sales scripts and messaging
   - `AGENT_DESIGNS.yaml` - Complete agent specifications
   - `TOOLS_API.yaml` - Tool implementations
   - `STATE_SCHEMA.md` - Complete state design
   - `DATABASE_SCHEMA.md` - Supabase tables and Drizzle schemas
   - `API_ENDPOINTS.md` - REST and streaming APIs
   - `CAMPAIGN_SYSTEM.md` - Campaign tracking and access control
   - `RAG_SYSTEM.md` - Document embeddings architecture
   - `EXAMPLE_CONVERSATIONS.md` - Sample conversation flows

2. **Development Setup:**
   - Set up Supabase project (PostgreSQL + Auth + Storage)
   - Configure Google Cloud project (Cloud Run + Cloud Storage)
   - Set up Next.js project with Vercel AI SDK
   - Create Python backend with LangGraph + FastAPI
   - Configure Stripe for payments

3. **Implementation Order:**
   - Phase 1: Campaign system and owner dashboard
   - Phase 2: LangGraph agents (Greeter, Qualifier, Pitcher, Closer)
   - Phase 3: RAG system for document uploads
   - Phase 4: Stripe integration
   - Phase 5: Analytics dashboard

4. **Production Deployment:**
   - Frontend: Deploy Next.js to Vercel
   - Backend: Containerize Python app, deploy to Google Cloud Run
   - Database: Use Supabase branching (staging → production)
   - Monitoring: LangSmith tracing + Google Cloud monitoring

---

**See accompanying documents for detailed implementation specifications.**
