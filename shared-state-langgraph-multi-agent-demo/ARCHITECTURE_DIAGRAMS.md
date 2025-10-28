# Shared State Multi-Agent Collaboration - Architecture Diagrams

This document provides comprehensive visual explanations of the **shared state pattern** where agents collaborate by reading from and writing to a common state object.

---

## 1. High-Level Architecture

```mermaid
graph TB
    User[👤 User Query:<br/>"What are latest AI developments?"]
    
    subgraph "Shared State Object"
        State[📦 ResearchState<br/>research_query<br/>web_results<br/>analysis<br/>final_report]
    end
    
    subgraph "Supervisor"
        Sup[🎯 Supervisor<br/>State-Aware Routing]
    end
    
    subgraph "Worker Agents"
        Research[🔍 Research Agent<br/>WRITES: web_results]
        Analysis[📊 Analysis Agent<br/>READS: web_results<br/>WRITES: analysis]
        Report[📝 Report Agent<br/>READS: analysis<br/>WRITES: final_report]
    end
    
    User -->|Query| Sup
    Sup <-->|Read/Write| State
    
    Sup -->|Route based on state| Research
    Sup -->|Route based on state| Analysis
    Sup -->|Route based on state| Report
    
    Research -->|Update state| State
    Analysis -->|Update state| State
    Report -->|Update state| State
    
    Research -->|Return| Sup
    Analysis -->|Return| Sup
    Report -->|Return| Sup
    
    Sup -->|Final Result| User
    
    style State fill:#FFD700,color:#000
    style Sup fill:#4A90E2,color:#fff
    style Research fill:#50C878,color:#fff
    style Analysis fill:#9B59B6,color:#fff
    style Report fill:#E74C3C,color:#fff
```

**Key Concept:** All agents share and build upon a common state object, enabling sequential collaboration.

---

## 2. State Evolution Timeline

```mermaid
sequenceDiagram
    participant U as User
    participant S as Supervisor
    participant State as Shared State
    participant R as Research Agent
    participant A as Analysis Agent
    participant Rep as Report Agent
    
    U->>S: "What are AI agents?"
    S->>State: Check state (empty)
    State->>S: web_results: []
    S->>R: Route to Research
    
    Note over R: Searches web
    R->>State: WRITE web_results: [{...}, {...}]
    R->>S: Done
    
    S->>State: Check state
    State->>S: web_results: ✅, analysis: ❌
    S->>A: Route to Analysis
    
    Note over A: Reads web_results
    A->>State: READ web_results
    State->>A: [{...}, {...}]
    A->>State: WRITE analysis: "..."
    A->>S: Done
    
    S->>State: Check state
    State->>S: analysis: ✅, final_report: ❌
    S->>Rep: Route to Report
    
    Note over Rep: Reads analysis
    Rep->>State: READ analysis
    State->>Rep: "..."
    Rep->>State: WRITE final_report: "..."
    Rep->>S: Done
    
    S->>State: Check state
    State->>S: All fields populated ✅
    S->>U: Return final_report
```

---

## 3. State Schema Structure

```mermaid
classDiagram
    class ResearchState {
        <<TypedDict>>
        +Annotated~list~ messages
        +str research_query
        +list~dict~ web_results
        +list~str~ sources
        +list~str~ key_findings
        +str analysis
        +float confidence_score
        +str final_report
        +str current_step
        +list~str~ completed_steps
        +Literal next_agent
    }
    
    class ResearchAgent {
        +web_search tool
        WRITES: web_results
        WRITES: sources
    }
    
    class AnalysisAgent {
        READS: web_results
        WRITES: key_findings
        WRITES: analysis
        WRITES: confidence_score
    }
    
    class ReportAgent {
        READS: analysis
        READS: key_findings
        READS: sources
        WRITES: final_report
    }
    
    class Supervisor {
        READS: all fields
        WRITES: next_agent
        WRITES: current_step
    }
    
    ResearchAgent --> ResearchState : updates
    AnalysisAgent --> ResearchState : reads & updates
    ReportAgent --> ResearchState : reads & updates
    Supervisor --> ResearchState : reads & routes
    
    note for ResearchState "Central shared state\nAll agents collaborate through this"
```

---

## 4. State Flow: Field Population

```mermaid
flowchart LR
    subgraph "Initial State"
        I1[research_query: ✅]
        I2[web_results: ❌]
        I3[analysis: ❌]
        I4[final_report: ❌]
    end
    
    subgraph "After Research Agent"
        R1[research_query: ✅]
        R2[web_results: ✅]
        R3[analysis: ❌]
        R4[final_report: ❌]
    end
    
    subgraph "After Analysis Agent"
        A1[research_query: ✅]
        A2[web_results: ✅]
        A3[analysis: ✅]
        A4[final_report: ❌]
    end
    
    subgraph "After Report Agent"
        F1[research_query: ✅]
        F2[web_results: ✅]
        F3[analysis: ✅]
        F4[final_report: ✅]
    end
    
    I1 --> R1
    I2 --> R2
    I3 --> R3
    I4 --> R4
    
    R1 --> A1
    R2 --> A2
    R3 --> A3
    R4 --> A4
    
    A1 --> F1
    A2 --> F2
    A3 --> F3
    A4 --> F4
    
    style R2 fill:#50C878,color:#fff
    style A3 fill:#9B59B6,color:#fff
    style F4 fill:#E74C3C,color:#fff
```

---

## 5. State-Aware Routing Logic

```mermaid
flowchart TD
    Start[Supervisor Checks State] --> Check1{web_results<br/>populated?}
    
    Check1 -->|No| Route1[Route to<br/>Research Agent]
    Check1 -->|Yes| Check2{analysis<br/>populated?}
    
    Check2 -->|No| Route2[Route to<br/>Analysis Agent]
    Check2 -->|Yes| Check3{final_report<br/>populated?}
    
    Check3 -->|No| Route3[Route to<br/>Report Agent]
    Check3 -->|Yes| Finish[FINISH<br/>Return result]
    
    Route1 --> Execute1[Research Agent<br/>Writes web_results]
    Route2 --> Execute2[Analysis Agent<br/>Writes analysis]
    Route3 --> Execute3[Report Agent<br/>Writes final_report]
    
    Execute1 --> Back1[Return to Supervisor]
    Execute2 --> Back2[Return to Supervisor]
    Execute3 --> Back3[Return to Supervisor]
    
    Back1 --> Start
    Back2 --> Start
    Back3 --> Start
    
    style Check1 fill:#FFB84D,color:#000
    style Check2 fill:#FFB84D,color:#000
    style Check3 fill:#FFB84D,color:#000
    style Route1 fill:#50C878,color:#fff
    style Route2 fill:#9B59B6,color:#fff
    style Route3 fill:#E74C3C,color:#fff
```

**Key Insight:** Routing decisions are based on what's in the state, not just messages.

---

## 6. Agent Collaboration Pattern

```mermaid
graph TB
    subgraph "Research Agent"
        R1[Receive State] --> R2[Use web_search tool]
        R2 --> R3[Extract results]
        R3 --> R4[WRITE to state:<br/>web_results<br/>sources]
    end
    
    subgraph "Analysis Agent"
        A1[Receive State] --> A2[READ from state:<br/>web_results]
        A2 --> A3[Analyze data<br/>with LLM]
        A3 --> A4[WRITE to state:<br/>analysis<br/>key_findings<br/>confidence_score]
    end
    
    subgraph "Report Agent"
        Rep1[Receive State] --> Rep2[READ from state:<br/>analysis<br/>key_findings<br/>sources]
        Rep2 --> Rep3[Generate report<br/>with LLM]
        Rep3 --> Rep4[WRITE to state:<br/>final_report]
        Rep4 --> Rep5[Save to file]
    end
    
    R4 -->|State updated| A1
    A4 -->|State updated| Rep1
    
    style R4 fill:#50C878,color:#fff
    style A2 fill:#9B59B6,color:#fff
    style A4 fill:#9B59B6,color:#fff
    style Rep2 fill:#E74C3C,color:#fff
    style Rep4 fill:#E74C3C,color:#fff
```

---

## 7. Complete Graph Structure

```mermaid
graph TB
    START([START]) --> Sup[supervisor]
    
    Sup -->|next_agent:<br/>research| Res[research]
    Sup -->|next_agent:<br/>analysis| Ana[analysis]
    Sup -->|next_agent:<br/>report| Rep[report]
    Sup -->|next_agent:<br/>FINISH| END([END])
    
    Res -->|Always| Sup
    Ana -->|Always| Sup
    Rep -->|Always| Sup
    
    subgraph "State Updates"
        Res -.->|web_results| StateObj[(Shared State)]
        Ana -.->|analysis| StateObj
        Rep -.->|final_report| StateObj
        Sup -.->|Reads all| StateObj
    end
    
    style START fill:#4A90E2,color:#fff
    style END fill:#50C878,color:#fff
    style Sup fill:#FFB84D,color:#000
    style StateObj fill:#FFD700,color:#000
```

---

## 8. Data Flow: Complete Workflow

```mermaid
flowchart TD
    Input[User Query] --> Init[Initialize State<br/>research_query = query]
    
    Init --> Sup1[Supervisor: Check State]
    Sup1 --> Dec1{State Check}
    Dec1 -->|Empty| Res[Research Agent]
    
    Res --> Web[Call web_search tool]
    Web --> Parse[Parse results]
    Parse --> Write1[Write to state:<br/>web_results, sources]
    Write1 --> Sup2[Supervisor: Check State]
    
    Sup2 --> Dec2{State Check}
    Dec2 -->|Has web_results| Ana[Analysis Agent]
    
    Ana --> Read1[Read web_results]
    Read1 --> LLM1[LLM: Analyze data]
    LLM1 --> Write2[Write to state:<br/>analysis, key_findings]
    Write2 --> Sup3[Supervisor: Check State]
    
    Sup3 --> Dec3{State Check}
    Dec3 -->|Has analysis| Rep[Report Agent]
    
    Rep --> Read2[Read analysis,<br/>key_findings, sources]
    Read2 --> LLM2[LLM: Generate report]
    LLM2 --> Write3[Write to state:<br/>final_report]
    Write3 --> Save[Save to file]
    Save --> Sup4[Supervisor: Check State]
    
    Sup4 --> Dec4{State Check}
    Dec4 -->|Complete| Output[Return final_report]
    
    style Init fill:#4A90E2,color:#fff
    style Write1 fill:#50C878,color:#fff
    style Write2 fill:#9B59B6,color:#fff
    style Write3 fill:#E74C3C,color:#fff
    style Output fill:#FFD700,color:#000
```

---

## 9. State Read/Write Permissions

```mermaid
graph LR
    subgraph "Research Agent"
        RR[READS:<br/>research_query]
        RW[WRITES:<br/>web_results<br/>sources]
    end
    
    subgraph "Analysis Agent"
        AR[READS:<br/>web_results<br/>research_query]
        AW[WRITES:<br/>analysis<br/>key_findings<br/>confidence_score]
    end
    
    subgraph "Report Agent"
        RepR[READS:<br/>analysis<br/>key_findings<br/>sources<br/>web_results]
        RepW[WRITES:<br/>final_report]
    end
    
    subgraph "Supervisor"
        SR[READS:<br/>ALL fields]
        SW[WRITES:<br/>next_agent<br/>current_step<br/>completed_steps]
    end
    
    State[(Shared State)]
    
    RR -.-> State
    RW ==> State
    AR -.-> State
    AW ==> State
    RepR -.-> State
    RepW ==> State
    SR -.-> State
    SW ==> State
    
    style State fill:#FFD700,color:#000
    style RW fill:#50C878,color:#fff
    style AW fill:#9B59B6,color:#fff
    style RepW fill:#E74C3C,color:#fff
```

**Legend:**
- Dotted lines (-.->): READ operations
- Solid lines (==>): WRITE operations

---

## 10. Comparison with Other Patterns

```mermaid
graph TB
    subgraph "Flat Supervisor (Messages Only)"
        F1[User] --> F2[Supervisor]
        F2 --> F3[Agent 1]
        F2 --> F4[Agent 2]
        F3 -->|Messages| F2
        F4 -->|Messages| F2
        
        Note1[State: Messages only<br/>No data sharing]
    end
    
    subgraph "Hierarchical Teams (Routing State)"
        H1[User] --> H2[Top Supervisor]
        H2 --> H3[Team Supervisor]
        H3 --> H4[Agent 1]
        H3 --> H5[Agent 2]
        
        Note2[State: Messages + next_agent<br/>Limited data sharing]
    end
    
    subgraph "Shared State (Rich Collaboration)"
        S1[User] --> S2[Supervisor]
        S2 --> S3[Agent 1]
        S2 --> S4[Agent 2]
        S2 --> S5[Agent 3]
        
        SharedState[(Rich State<br/>web_results<br/>analysis<br/>final_report)]
        
        S3 <-->|Read/Write| SharedState
        S4 <-->|Read/Write| SharedState
        S5 <-->|Read/Write| SharedState
        S2 <-->|Read| SharedState
        
        Note3[State: Messages + Domain Data<br/>Full collaboration]
    end
    
    style SharedState fill:#FFD700,color:#000
    style Note3 fill:#50C878,color:#fff
```

---

## 11. File Saving Feature

```mermaid
flowchart LR
    Report[Report Agent<br/>Completes] --> Extract[Extract Data:<br/>query, report,<br/>web_results, sources]
    
    Extract --> Generate[Generate Markdown:<br/>- Executive summary<br/>- Key findings<br/>- Sources<br/>- Raw data]
    
    Generate --> UUID[Create Unique ID<br/>+ Timestamp]
    
    UUID --> Save[Save to:<br/>results/research_results_<br/>YYYYMMDD_HHMMSS_<id>.md]
    
    Save --> Confirm[✅ File saved<br/>Path returned]
    
    style Save fill:#50C878,color:#fff
    style Confirm fill:#4A90E2,color:#fff
```

**File Structure:**
```
results/
  research_results_20251027_143022_a7b3c4d5.md
  research_results_20251027_150133_e8f9g0h1.md
```

---

## 12. State Accumulation Over Time

```mermaid
gantt
    title State Field Population Timeline
    dateFormat X
    axisFormat %s
    
    section State Fields
    research_query (Input)     :done, 0, 1
    web_results (Research)     :active, 1, 3
    sources (Research)         :active, 1, 3
    key_findings (Analysis)    :crit, 4, 2
    analysis (Analysis)        :crit, 4, 2
    confidence_score (Analysis):crit, 4, 2
    final_report (Report)      :milestone, 6, 2
```

**Timeline:**
- **0-1s**: Initial state with query
- **1-4s**: Research agent populates web data
- **4-6s**: Analysis agent processes and adds insights
- **6-8s**: Report agent creates final output

---

## 13. Agent Dependencies

```mermaid
graph LR
    Query[research_query] --> Research[Research Agent]
    
    Research -->|Produces| WebResults[web_results<br/>sources]
    
    WebResults --> Analysis[Analysis Agent]
    
    Analysis -->|Produces| AnalysisData[analysis<br/>key_findings<br/>confidence_score]
    
    AnalysisData --> Report[Report Agent]
    WebResults -.->|Also reads| Report
    
    Report -->|Produces| FinalReport[final_report]
    
    style Query fill:#4A90E2,color:#fff
    style WebResults fill:#50C878,color:#fff
    style AnalysisData fill:#9B59B6,color:#fff
    style FinalReport fill:#E74C3C,color:#fff
```

**Dependency Chain:** Each agent depends on the previous agent's output.

---

## 14. Error Handling & Fallbacks

```mermaid
flowchart TD
    Agent[Agent Executes] --> Check{State Valid?}
    
    Check -->|Yes| Process[Process Data]
    Check -->|No| Fallback[Use Fallback]
    
    Process --> Write{Write Success?}
    Fallback --> Write
    
    Write -->|Yes| Return[Return to Supervisor]
    Write -->|No| Error[Log Error]
    
    Error --> DefaultValue[Write Default Value]
    DefaultValue --> Return
    
    style Check fill:#FFB84D,color:#000
    style Fallback fill:#E74C3C,color:#fff
    style Error fill:#E74C3C,color:#fff
```

**Example Fallbacks:**
- No web results → Empty list `[]`
- No analysis → Default string `"No data available"`
- API error → Error message in state

---

## 15. Real-World Use Cases

```mermaid
mindmap
    root((Shared State<br/>Pattern))
        Research & Analysis
            Academic research
            Market research
            Competitive analysis
            Literature review
        Customer Support
            Triage issue
            Diagnose problem
            Propose solution
            Generate response
        Data Pipelines
            Extract data
            Transform data
            Validate data
            Load data
        Content Creation
            Research topic
            Create outline
            Write draft
            Edit & polish
        Business Intelligence
            Gather metrics
            Analyze trends
            Generate insights
            Create dashboard
```

---

## Key Concepts Summary

| Aspect | Description |
|--------|-------------|
| **Pattern Name** | Shared State Collaboration |
| **Key Concept** | Agents build knowledge together through shared state |
| **State Schema** | Rich domain data (not just messages) |
| **Routing** | State-aware (decisions based on state contents) |
| **Collaboration** | Sequential (each agent builds on previous work) |
| **Best For** | Complex workflows with data dependencies |

---

## State Management Best Practices

### 1. Type Your State
```python
class ResearchState(TypedDict):
    field: str  # Clear types
    data: list[dict]  # Specific structures
```

### 2. Document Fields
```python
# Research Agent populates this
web_results: list[dict]  # Raw web search results

# Analysis Agent reads web_results, populates this
analysis: str  # Detailed analysis
```

### 3. Use Reducers
```python
messages: Annotated[list, add_messages]  # Merges messages
```

### 4. Validate Updates
```python
def agent_node(state: MyState) -> dict:
    result = process(state)
    if not result:
        raise ValueError("Invalid result")
    return {"field": result}
```

---

## When to Use This Pattern

### ✅ Use Shared State When:
- Agents need to build upon each other's work
- Workflow has clear sequential dependencies
- You need rich domain data (not just messages)
- State inspection is important for debugging
- Multiple agents contribute to a final output

### ❌ Don't Use When:
- Agents work independently (use flat supervisor)
- Simple routing is sufficient
- No data dependencies between agents
- State would be too complex to manage

---

## Conclusion

The **Shared State Pattern** enables sophisticated multi-agent collaboration by:

1. **Centralized Knowledge**: All agents contribute to shared state
2. **Sequential Building**: Each agent builds on previous work
3. **State-Aware Routing**: Decisions based on state contents
4. **Rich Data**: Beyond messages, full domain objects
5. **Debuggability**: Inspect state at any point
6. **Scalability**: Add agents without changing architecture

**Perfect for:** Research workflows, data pipelines, content creation, and any scenario where agents need to collaborate through shared data.

**Built with LangGraph v1** 🦜🔗
