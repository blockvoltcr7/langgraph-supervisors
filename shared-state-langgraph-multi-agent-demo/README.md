# 🏆 Multi-Agent Collaboration with Shared State

A production-ready implementation of the **shared state pattern** where multiple specialized agents collaborate by reading from and writing to a common state object.

## 🎯 What You'll Learn

This pattern teaches the most important concept in multi-agent systems:

**Agents don't just pass messages—they build shared knowledge together.**

### Key Concepts:

1. **Shared State Schema** - Typed state fields that agents collaborate through
2. **State-Aware Routing** - Supervisor makes decisions based on state contents
3. **Sequential Collaboration** - Each agent builds upon previous agents' work
4. **State Accumulation** - Knowledge grows as agents contribute

## 📐 Architecture

```
User Query: "What are the latest developments in AI agents?"
    ↓
┌─────────────────────────────────────────────────────────┐
│  Supervisor (reads state, routes based on progress)    │
└─────────────────────────────────────────────────────────┘
    ↓
┌──────────────┬───────────────┬──────────────┐
│   Research   │   Analysis    │    Report    │
│    Agent     │    Agent      │    Agent     │
└──────────────┴───────────────┴──────────────┘
       ↓              ↓               ↓
  Populates      Reads research   Reads analysis
  web_results    Writes analysis  Writes report
```

### State Flow:

```python
# Initial State
{
    "research_query": "What are AI agents?",
    "web_results": [],      # Empty
    "analysis": "",         # Empty
    "final_report": ""      # Empty
}

# After Research Agent
{
    "research_query": "What are AI agents?",
    "web_results": [{...}, {...}],  # ✅ Populated
    "analysis": "",
    "final_report": ""
}

# After Analysis Agent
{
    "research_query": "What are AI agents?",
    "web_results": [{...}, {...}],
    "analysis": "AI agents are...",  # ✅ Populated
    "final_report": ""
}

# After Report Agent
{
    "research_query": "What are AI agents?",
    "web_results": [{...}, {...}],
    "analysis": "AI agents are...",
    "final_report": "# Report..."  # ✅ Populated
}
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
uv sync
```

### 2. Set Up API Keys

```bash
cp .env.example .env
```

Edit `.env` and add:
```env
OPENAI_API_KEY=sk-your-key-here
TAVILY_API_KEY=tvly-your-key-here  # Get free at https://tavily.com
```

### 3. Run the Demo

```bash
source .venv/bin/activate
python main.py
```

**Output:**
- Research results displayed in terminal
- **Automatically saved to `results/research_results_<timestamp>_<id>.md`**

### 4. Use with Agent Chat UI

```bash
langgraph dev
```

Then connect at **https://agentchat.vercel.app**:
```
Deployment URL: http://localhost:2024
Assistant / Graph ID: research
LangSmith API Key: <your-key>
```

## 💾 Automatic File Saving

Every research query automatically saves results to:
```
results/research_results_YYYYMMDD_HHMMSS_<unique_id>.md
```

**Example:**
```
results/research_results_20251023_023301_e70c25c5.md
```

**Each file contains:**
- ✅ Complete research report
- ✅ All source URLs
- ✅ Raw web search data
- ✅ Confidence scores
- ✅ Timestamps and metadata

**View saved reports:**
```bash
ls -lt results/
cat results/research_results_*.md
```

## 💡 How Shared State Works

### The State Schema

```python
class ResearchState(TypedDict):
    # Standard
    messages: Annotated[list, add_messages]
    
    # === SHARED STATE (agents collaborate through these) ===
    
    # Input
    research_query: str
    
    # Research Agent writes here
    web_results: list[dict]
    sources: list[str]
    
    # Analysis Agent reads web_results, writes here
    key_findings: list[str]
    analysis: str
    confidence_score: float
    
    # Report Agent reads analysis, writes here
    final_report: str
    
    # Workflow tracking
    current_step: str
    completed_steps: list[str]
```

### Agent Collaboration Pattern

**Research Agent:**
```python
def research_agent_node(state: ResearchState) -> dict:
    # Uses web search tool
    result = research_agent.invoke(state)
    
    # WRITES to shared state
    return {
        "web_results": [...],  # Adds research findings
        "sources": [...]       # Adds source URLs
    }
```

**Analysis Agent:**
```python
def analysis_agent_node(state: ResearchState) -> dict:
    # READS from shared state
    web_results = state.get("web_results", [])
    
    # Processes the data
    analysis = analyze(web_results)
    
    # WRITES to shared state
    return {
        "analysis": analysis,
        "key_findings": [...],
        "confidence_score": 0.85
    }
```

**Report Agent:**
```python
def report_agent_node(state: ResearchState) -> dict:
    # READS from shared state
    analysis = state.get("analysis", "")
    key_findings = state.get("key_findings", [])
    
    # Creates final output
    report = create_report(analysis, key_findings)
    
    # WRITES to shared state
    return {
        "final_report": report
    }
```

### State-Aware Routing

```python
def supervisor_node(state: ResearchState) -> dict:
    # Check what's in the state
    web_results = state.get("web_results", [])
    analysis = state.get("analysis", "")
    final_report = state.get("final_report", "")
    
    # Route based on state contents
    if not web_results:
        return {"next_agent": "research"}
    elif not analysis:
        return {"next_agent": "analysis"}
    elif not final_report:
        return {"next_agent": "report"}
    else:
        return {"next_agent": "FINISH"}
```

## 🎯 Example Queries

### Research Query:
```
What are the latest developments in AI agents and LangGraph?
```

**Flow:**
1. Supervisor → Routes to Research Agent (state is empty)
2. Research Agent → Searches web, adds results to state
3. Supervisor → Routes to Analysis Agent (sees web_results)
4. Analysis Agent → Reads web_results, adds analysis to state
5. Supervisor → Routes to Report Agent (sees analysis)
6. Report Agent → Reads analysis, adds final_report to state
7. Supervisor → Returns FINISH (sees final_report)

### Technical Query:
```
How do LangGraph checkpoints work and when should I use them?
```

### Business Query:
```
What are the ROI benefits of implementing AI agents in customer support?
```

## 🔍 Key Differences from Other Patterns

| Aspect | Flat Supervisor | Hierarchical Teams | **Shared State** |
|--------|----------------|-------------------|------------------|
| Agents | 2-4 | 5+ | 3+ |
| Communication | Messages only | Messages + hierarchy | **Messages + State** |
| Collaboration | Independent | Team-based | **Sequential building** |
| State | Simple | Routing fields | **Rich domain data** |
| Best For | Simple tasks | Large teams | **Complex workflows** |

## 💎 Why This Pattern is Valuable

### 1. **Real-World Applicability**

✅ **Research & Analysis** - Gather data → Analyze → Report
✅ **Customer Support** - Triage → Diagnose → Resolve
✅ **Data Pipelines** - Extract → Transform → Load
✅ **Content Creation** - Research → Outline → Write → Edit

### 2. **Scalability**

- Add more agents without changing architecture
- Each agent focuses on one responsibility
- State schema documents the workflow

### 3. **Debuggability**

- Inspect state at any point
- See exactly what each agent contributed
- Track workflow progress

### 4. **Testability**

- Test agents independently with mock state
- Verify state updates
- Validate routing logic

## 🛠️ Customization

### Add More Agents

```python
# Add a Validation Agent
def validation_agent_node(state: ResearchState) -> dict:
    # Reads analysis
    analysis = state.get("analysis", "")
    
    # Validates quality
    is_valid = validate(analysis)
    
    # Writes validation result
    return {
        "validation_passed": is_valid,
        "validation_notes": "..."
    }
```

### Add More State Fields

```python
class ResearchState(TypedDict):
    # ... existing fields ...
    
    # Add new fields
    fact_check_results: dict
    citations: list[str]
    related_topics: list[str]
```

### Change the Workflow

```python
# Add parallel processing
workflow.add_edge("research", "analysis")
workflow.add_edge("research", "fact_check")  # Parallel
```

## 📊 State Management Best Practices

### 1. **Type Your State**
```python
class MyState(TypedDict):
    field: str  # Clear types
    data: list[dict]  # Specific structures
```

### 2. **Document State Fields**
```python
class MyState(TypedDict):
    web_results: list[dict]  # Raw search results from Research Agent
    analysis: str  # Synthesized analysis from Analysis Agent
```

### 3. **Use State Reducers**
```python
from langgraph.graph.message import add_messages

messages: Annotated[list, add_messages]  # Merges messages
```

### 4. **Validate State Updates**
```python
def agent_node(state: MyState) -> dict:
    result = process(state)
    
    # Validate before returning
    if not result:
        raise ValueError("Invalid result")
    
    return {"field": result}
```

## 🎓 Learning Path

### You've Learned:

✅ Flat supervisor pattern (simple routing)
✅ Hierarchical teams (scaling to many agents)
✅ **Shared state (agents collaborating through data)** ← You are here

### Next Steps:

1. **Add Persistence** - Save state across sessions
2. **Add Human-in-the-Loop** - Approve state changes
3. **Add Parallel Execution** - Multiple agents work simultaneously
4. **Add Error Recovery** - Handle failures gracefully

## 📚 Resources

- [LangGraph State Management](https://langchain-ai.github.io/langgraph/concepts/low_level/#state)
- [Multi-Agent Patterns](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)
- [Tavily Search API](https://tavily.com)
- [LangSmith Tracing](https://smith.langchain.com)

## 🤝 Comparison with Previous Patterns

### Flat Supervisor (Pattern 1):
- **Focus:** Simple routing
- **State:** Messages only
- **Use:** 2-4 agents, simple tasks

### Hierarchical Teams (Pattern 2):
- **Focus:** Team organization
- **State:** Messages + routing fields
- **Use:** 5+ agents, complex organization

### Shared State (Pattern 3 - This One):
- **Focus:** Data collaboration
- **State:** **Rich domain data + workflow tracking**
- **Use:** **Complex workflows where agents build upon each other's work**

---

**Built with LangGraph** 🦜🔗

**Pattern:** Multi-Agent Collaboration with Shared State
**Complexity:** Intermediate
**Production-Ready:** ✅