# Limitless OS AI Sales Agent - Complete Documentation

**A production-ready LangGraph architecture for automated sales conversations**

---

## 📚 Documentation Index

### Core Technical Documents

1. **[ARCHITECTURE_OVERVIEW.md](./ARCHITECTURE_OVERVIEW.md)** - System architecture and tech stack decisions
2. **[ARCHITECTURE_DIAGRAMS.md](./ARCHITECTURE_DIAGRAMS.md)** - Visual architecture with Mermaid diagrams
3. **[STATE_SCHEMA.md](./STATE_SCHEMA.md)** - LangGraph state design with campaign tracking
4. **[TRADE_OFFS_ANALYSIS.md](./TRADE_OFFS_ANALYSIS.md)** - Architecture decisions and cost analysis

### Implementation Specifications

5. **[AGENT_DESIGNS.yaml](./AGENT_DESIGNS.yaml)** - Complete agent specifications and routing logic
6. **[TOOLS_API.yaml](./TOOLS_API.yaml)** - Tool definitions for all agents
7. **[DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)** - Supabase tables and Drizzle ORM schemas
8. **[API_ENDPOINTS.md](./API_ENDPOINTS.md)** - REST and streaming API specifications

### System Features

9. **[CAMPAIGN_SYSTEM.md](./CAMPAIGN_SYSTEM.md)** - Campaign codes, access control, and analytics
10. **[RAG_SYSTEM.md](./RAG_SYSTEM.md)** - Document upload and embedding architecture
11. **[EXAMPLE_CONVERSATIONS.md](./EXAMPLE_CONVERSATIONS.md)** - Sample conversation flows

### Business Logic

12. **[SALES_PLAYBOOK.md](./SALES_PLAYBOOK.md)** - Sales scripts, objection handling, and messaging

---

## 🎯 Executive Summary

### What We're Building
An AI sales agent that qualifies leads, handles objections, delivers pitches, and closes deals through multi-turn conversations **with full persistence across sessions** (resume after days/weeks).

### Technology Stack
- **Frontend:** Next.js (Vercel) with Vercel AI SDK
- **Backend:** Python (Google Cloud) with LangGraph
- **Database:** Supabase PostgreSQL with pgvector
- **ORM:** Drizzle
- **LLM:** OpenAI GPT-4o-mini
- **Storage:** Google Cloud Storage
- **Payments:** Stripe
- **Auth:** Supabase Auth

### Why This Architecture?
✅ **Persistence** - Conversations resume seamlessly  
✅ **Shared Context** - All agents access full history  
✅ **Cost Efficient** - Single LLM call per interaction  
✅ **Production Ready** - Scales to 1,000+ concurrent users  

---

## 🏗️ High-Level Flow

```
Lead Clicks Campaign URL → Validate Campaign Code → Enter Instagram Handle → 
Load/Create State → LangGraph Agent (with RAG) → Save Checkpoint → Stream Response
```

### Conversation Stages
```
Greeting → Qualification → Pitch → Objection Handling → Closing → Complete
```

### 6 Specialized Agents
1. **Greeter** - Welcome & verify niche
2. **Qualifier** - Ask questions, calculate score
3. **Pitcher** - Deliver warm/cold pitch
4. **Objection Handler** - Address concerns
5. **Closer** - Send payment link via Stripe
6. **Follow-up** - Nurture leads

---

## 💰 Cost Analysis

**Per 1,000 Conversations:**
- LLM (GPT-4o-mini): $3.00
- PostgreSQL: $5.00
- Observability: $0.50
- **Total:** $8.60

**Revenue:** 150 conversions × $497 = $74,550  
**Gross margin:** 99.99% 🚀

---

## 🔍 Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Architecture | Stateful + Shared State | Need persistence + full context |
| Database | PostgreSQL | Official support, ACID, scalable |
| Routing | Rule-based Supervisor | 80% cost reduction vs LLM routing |
| LLM Model | GPT-4o-mini | Best cost/performance ratio |
| State Storage | Shared across agents | Sales needs full context |

---

## 📖 Documentation Guide

### For Product/Business
1. **SALES_PLAYBOOK.md** - Complete sales strategy and messaging
2. **EXAMPLE_CONVERSATIONS.md** - See how the agent behaves
3. **CAMPAIGN_SYSTEM.md** - How to track lead sources

### For Full-Stack Developers
1. **ARCHITECTURE_OVERVIEW.md** - System design decisions
2. **DATABASE_SCHEMA.md** - Supabase tables and migrations
3. **API_ENDPOINTS.md** - Frontend-backend integration
4. **CAMPAIGN_SYSTEM.md** - Access control flow

### For AI/LangGraph Engineers
1. **AGENT_DESIGNS.yaml** - Agent specifications and routing
2. **TOOLS_API.yaml** - Tool definitions
3. **STATE_SCHEMA.md** - State management
4. **RAG_SYSTEM.md** - Document embeddings and search

### For Architects
1. **ARCHITECTURE_OVERVIEW.md** - High-level decisions
2. **ARCHITECTURE_DIAGRAMS.md** - Visual architecture
3. **TRADE_OFFS_ANALYSIS.md** - Decision rationale

---

## 🚀 Quick Start

See complete setup instructions in individual documentation files.

### Development Environment Setup

**Prerequisites:**
- Node.js 18+ (for Next.js)
- Python 3.11+ (for LangGraph backend)
- Supabase account
- Google Cloud account
- OpenAI API key
- Stripe account

### Key Implementation Files

**Frontend (Next.js):**
- `/app` - Next.js pages and API routes
- `/lib/supabase.ts` - Supabase client
- `/components` - React components

**Backend (Python):**
- `agents/` - LangGraph agent implementations
- `tools/` - Agent tools
- `main.py` - FastAPI server

**Database:**
- `drizzle/schema/` - Drizzle ORM schemas
- `drizzle/migrations/` - Database migrations

### Deployment

- **Frontend:** Vercel (automatic from GitHub)
- **Backend:** Google Cloud Run (containerized Python)
- **Database:** Supabase (PostgreSQL with pgvector)
- **Storage:** Google Cloud Storage

---

## 📊 System Capabilities

### Owner Features
- ✅ Create and manage campaign codes
- ✅ Upload documents (sales scripts, objection responses)
- ✅ View real-time conversation analytics
- ✅ Track conversion rates per campaign
- ✅ Dashboard with metrics

### AI Agent Features
- ✅ Multi-turn conversations with context retention
- ✅ Resume conversations after days/weeks
- ✅ Dynamic knowledge base via RAG
- ✅ Rule-based qualification scoring
- ✅ Automated objection handling
- ✅ Stripe payment integration
- ✅ Campaign tracking per lead

### Technical Features
- ✅ Vercel AI SDK streaming responses
- ✅ PostgreSQL with pgvector for embeddings
- ✅ LangSmith tracing for debugging
- ✅ Supabase branching (staging/prod)
- ✅ Google Cloud serverless scaling
- ✅ Drizzle ORM migrations

---

**Start with ARCHITECTURE_OVERVIEW.md for complete system design details.**
