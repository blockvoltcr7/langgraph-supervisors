"""
Multi-Agent Collaboration with Shared State Pattern (LangGraph v1)

This demonstrates how multiple agents collaborate by sharing and building upon
a common state object. Each agent contributes their specialized knowledge to
the shared state, enabling complex workflows.

Architecture:
    User Query
        ↓
    Supervisor (reads shared state, routes based on progress)
        ↓
    ┌─────────────┬──────────────┬─────────────┐
    │   Research  │   Analysis   │   Report    │
    │   Agent     │   Agent      │   Agent     │
    └─────────────┴──────────────┴─────────────┘
         ↓              ↓              ↓
    Populates      Reads research  Reads analysis
    web_results    Writes analysis Writes summary

Shared State Flow:
    1. Research Agent → Adds web_results to state
    2. Analysis Agent → Reads web_results, adds analysis to state
    3. Report Agent → Reads analysis, adds final_report to state
    4. Supervisor → Sees all completed, returns result

Updated for LangGraph v1 / LangChain v1:
- Using create_agent instead of create_react_agent
- Using system_prompt parameter instead of prompt
"""

import os
from typing import Annotated, Literal
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import uuid

from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.agents import create_agent  # LangChain v1
import requests
import json

# ============================================================================
# Environment Setup
# ============================================================================

env_path = Path(__file__).parent / ".env"
if not env_path.exists():
    print(f"⚠️  Warning: .env file not found at {env_path}")
    print("   Please copy .env.example to .env and add your API keys")
    
load_dotenv(dotenv_path=env_path, override=True)

# ============================================================================
# API Keys Configuration
# ============================================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY not found in .env file.\n"
        "Please add your OpenAI API key to .env"
    )

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if not TAVILY_API_KEY:
    print("⚠️  Warning: TAVILY_API_KEY not found. Web search will not work.")
    print("   Get a free API key at: https://tavily.com")

# LangSmith Tracing (Optional)
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"

if LANGSMITH_API_KEY and LANGSMITH_TRACING:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "shared-state-demo")
    print("✅ LangSmith tracing enabled")
    print(f"   Project: {os.environ['LANGCHAIN_PROJECT']}")
else:
    print("ℹ️  LangSmith tracing disabled")

print("Using model: OpenAI GPT-4o-mini")
model = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)

# ============================================================================
# Shared State Schema
# ============================================================================

class ResearchState(TypedDict):
    """
    Shared state that all agents can read and write to.
    
    This is the KEY concept: agents collaborate by building up this shared state.
    Each agent adds their contribution, and subsequent agents can use it.
    """
    # Message history (standard)
    messages: Annotated[list, add_messages]
    
    # === Shared State Fields (agents collaborate through these) ===
    
    # Input
    research_query: str  # The original user question
    
    # Research Agent populates this
    web_results: list[dict]  # Raw web search results
    sources: list[str]  # URLs of sources
    
    # Analysis Agent reads web_results, populates this
    key_findings: list[str]  # Main points extracted
    analysis: str  # Detailed analysis
    confidence_score: float  # 0-1, how confident in the findings
    
    # Report Agent reads analysis, populates this
    final_report: str  # Formatted final output
    
    # Workflow tracking
    current_step: str  # Which step we're on
    completed_steps: list[str]  # Track progress
    next_agent: Literal["research", "analysis", "report", "FINISH", "__start__"]

# ============================================================================
# Helper Functions
# ============================================================================

def save_research_results(
    query: str,
    final_report: str,
    web_results: list[dict],
    sources: list[str],
    confidence_score: float
) -> str:
    """
    Save research results to a markdown file with unique ID.
    
    Args:
        query: The research query
        final_report: The final report content
        web_results: List of web search results
        sources: List of source URLs
        confidence_score: Confidence score of the analysis
        
    Returns:
        Path to the saved file
    """
    # Create results directory if it doesn't exist
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)
    
    # Generate unique ID
    unique_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"research_results_{timestamp}_{unique_id}.md"
    filepath = results_dir / filename
    
    # Create markdown content
    content = f"""# Research Report
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Query:** {query}
**Report ID:** {unique_id}
**Confidence Score:** {confidence_score:.2f}

---

{final_report}

---

## Research Sources

"""
    
    # Add sources
    if sources:
        for i, source in enumerate(sources, 1):
            content += f"{i}. {source}\n"
    else:
        content += "No sources available.\n"
    
    content += "\n---\n\n## Raw Research Data\n\n"
    
    # Add web results
    if web_results:
        for i, result in enumerate(web_results, 1):
            title = result.get("title", "No title")
            result_content = result.get("content", "No content")
            url = result.get("url", "No URL")
            content += f"### Source {i}: {title}\n\n"
            content += f"**URL:** {url}\n\n"
            content += f"{result_content}\n\n"
            content += "---\n\n"
    else:
        content += "No research data available.\n"
    
    # Write to file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    return str(filepath)

# ============================================================================
# Tools
# ============================================================================

@tool
def web_search(query: str) -> str:
    """Search the web for information using Tavily API.
    
    Args:
        query: The search query
        
    Returns:
        Search results as formatted text with sources
    """
    if not TAVILY_API_KEY or TAVILY_API_KEY == "your_tavily_api_key_here":
        return "Web search unavailable: No Tavily API key configured. Get one free at https://tavily.com"
    
    try:
        # Call Tavily API directly
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "max_results": 3,
            "search_depth": "basic",
            "include_answer": True,
            "include_raw_content": False
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Format results
        results = []
        if "results" in data:
            for i, result in enumerate(data["results"][:3], 1):
                title = result.get("title", "No title")
                content = result.get("content", "No content")
                url = result.get("url", "No URL")
                results.append(f"**Source {i}: {title}**\n{content}\nURL: {url}\n")
        
        if "answer" in data and data["answer"]:
            results.insert(0, f"**Quick Answer:** {data['answer']}\n")
        
        return "\n".join(results) if results else "No results found."
        
    except requests.exceptions.Timeout:
        return "Web search timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return f"Web search error: {str(e)}"
    except Exception as e:
        return f"Unexpected error during web search: {str(e)}"

# ============================================================================
# Worker Agents
# ============================================================================

# Research Agent - Gathers information from the web
research_agent = create_agent(
    model=model,
    tools=[web_search],
    system_prompt="""You are a Research Agent specialized in web research.

Your job:
1. Use the web_search tool to find relevant information about the user's query
2. Search for factual, recent information
3. The tool will return formatted results with sources

IMPORTANT:
- ALWAYS call the web_search tool with the user's query
- After getting results, summarize what you found
- List the key facts and sources from the search results
- Be thorough but concise
- Your findings will be used by other agents, so be clear

When done, confirm what you found and list the sources.""",
)

# Analysis Agent - Processes research findings (no tools needed)
def analysis_agent_node(state: ResearchState) -> dict:
    """
    Analysis Agent reads web_results from shared state and creates analysis.
    
    This demonstrates how agents READ from shared state.
    """
    system_prompt = """You are an Analysis Agent specialized in synthesizing information.

Your job:
1. Read the web search results from the research agent
2. Extract key findings and insights
3. Identify patterns and important points
4. Assess confidence in the findings (0-1 scale)

IMPORTANT:
- Be analytical and critical
- Highlight the most important information
- Note any contradictions or uncertainties
- Your analysis will be used to create the final report"""

    # Read from shared state
    web_results = state.get("web_results", [])
    research_query = state.get("research_query", "")
    
    if not web_results:
        return {
            "messages": [AIMessage(content="No research results to analyze.")],
            "key_findings": [],
            "analysis": "No data available for analysis.",
            "confidence_score": 0.0,
        }
    
    # Create context from web results
    results_text = "\n\n".join([
        f"Source {i+1}: {result.get('content', '')}"
        for i, result in enumerate(web_results)
    ])
    
    prompt = f"""Research Query: {research_query}

Web Search Results:
{results_text}

Please provide:
1. Key findings (3-5 bullet points)
2. Detailed analysis
3. Confidence score (0-1)

Format your response as:
KEY FINDINGS:
- [finding 1]
- [finding 2]
...

ANALYSIS:
[your detailed analysis]

CONFIDENCE: [0.0-1.0]"""

    messages = [SystemMessage(content=system_prompt), HumanMessage(content=prompt)]
    response = model.invoke(messages)
    
    # Parse response (simple parsing for demo)
    content = response.content
    
    # Extract key findings
    key_findings = []
    if "KEY FINDINGS:" in content:
        findings_section = content.split("KEY FINDINGS:")[1].split("ANALYSIS:")[0]
        key_findings = [
            line.strip("- ").strip()
            for line in findings_section.split("\n")
            if line.strip().startswith("-")
        ]
    
    # Extract confidence score
    confidence_score = 0.7  # Default
    if "CONFIDENCE:" in content:
        try:
            conf_text = content.split("CONFIDENCE:")[1].strip().split()[0]
            confidence_score = float(conf_text)
        except:
            pass
    
    # Write to shared state
    return {
        "messages": [response],
        "key_findings": key_findings,
        "analysis": content,
        "confidence_score": confidence_score,
    }

# Report Agent - Creates final formatted report (no tools needed)
def report_agent_node(state: ResearchState) -> dict:
    """
    Report Agent reads analysis from shared state and creates final report.
    
    This demonstrates how agents build upon previous agents' work.
    """
    system_prompt = """You are a Report Agent specialized in creating clear, professional reports.

Your job:
1. Read the analysis from the analysis agent
2. Create a well-formatted final report
3. Include sources and confidence assessment
4. Make it clear and actionable

IMPORTANT:
- Write in a professional but accessible style
- Structure the report clearly
- Include all key information
- This is the final output the user will see"""

    # Read from shared state
    research_query = state.get("research_query", "")
    key_findings = state.get("key_findings", [])
    analysis = state.get("analysis", "")
    confidence_score = state.get("confidence_score", 0.0)
    sources = state.get("sources", [])
    web_results = state.get("web_results", [])
    
    if not analysis:
        return {
            "messages": [AIMessage(content="No analysis available to create report.")],
            "final_report": "Unable to generate report: No analysis data.",
        }
    
    prompt = f"""Research Query: {research_query}

Key Findings:
{chr(10).join(f'- {finding}' for finding in key_findings)}

Analysis:
{analysis}

Confidence Score: {confidence_score}

Sources:
{chr(10).join(f'- {source}' for source in sources)}

Please create a professional final report that:
1. Starts with an executive summary
2. Presents the key findings
3. Provides the detailed analysis
4. Includes confidence assessment
5. Lists sources

Make it clear, well-structured, and actionable."""

    messages = [SystemMessage(content=system_prompt), HumanMessage(content=prompt)]
    response = model.invoke(messages)
    
    # Save results to file
    try:
        filepath = save_research_results(
            query=research_query,
            final_report=response.content,
            web_results=web_results,
            sources=sources,
            confidence_score=confidence_score
        )
        print(f"\n💾 Research results saved to: {filepath}")
    except Exception as e:
        print(f"\n⚠️  Warning: Could not save results to file: {e}")
    
    # Write to shared state
    return {
        "messages": [response],
        "final_report": response.content,
    }

# ============================================================================
# Agent Node Wrappers
# ============================================================================

def research_agent_node(state: ResearchState) -> dict:
    """Research agent node - gathers web information"""
    result = research_agent.invoke(state)
    
    # Extract web results from tool messages
    web_results = []
    sources = []
    search_content = ""
    
    for message in result["messages"]:
        # Check for ToolMessage (contains actual search results)
        if isinstance(message, ToolMessage):
            search_content = message.content
            # Extract URLs from the search results
            import re
            urls = re.findall(r'URL: (http[s]?://[^\s]+)', search_content)
            sources.extend(urls)
            
            # Parse the structured results
            sections = search_content.split("**Source")
            for section in sections[1:]:  # Skip first empty section
                if ":" in section:
                    # Extract content between title and URL
                    parts = section.split("\n")
                    title = parts[0].split("**")[0].strip() if parts else "No title"
                    content_lines = []
                    url = ""
                    for line in parts[1:]:
                        if line.startswith("URL:"):
                            url = line.replace("URL:", "").strip()
                            break
                        elif line.strip():
                            content_lines.append(line.strip())
                    
                    content = " ".join(content_lines)
                    if content and url:
                        web_results.append({
                            "title": title,
                            "content": content,
                            "url": url
                        })
    
    # If no structured results, create one from the search content
    if not web_results and search_content:
        web_results = [{
            "content": search_content[:500],  # First 500 chars
            "url": sources[0] if sources else "https://tavily.com"
        }]
    
    # Fallback if still no results
    if not web_results:
        web_results = [{
            "content": "Web search was called but no results were extracted. Check Tavily API key.",
            "url": "https://tavily.com"
        }]
    
    return {
        "messages": result["messages"],
        "web_results": web_results,
        "sources": sources if sources else ["https://tavily.com"],
    }

# ============================================================================
# Supervisor
# ============================================================================

def supervisor_node(state: ResearchState) -> dict:
    """
    Supervisor reads shared state and decides which agent to route to next.
    
    This demonstrates STATE-AWARE ROUTING - decisions based on what's in the state.
    """
    system_prompt = """You are the Supervisor coordinating a research workflow.

Your team:
- research: Gathers information from the web
- analysis: Analyzes research findings
- report: Creates final formatted report

DECISION RULES (check shared state):
1. If web_results is empty → route to "research"
2. If web_results exists but analysis is empty → route to "analysis"
3. If analysis exists but final_report is empty → route to "report"
4. If final_report exists → route to "FINISH"

Look at the conversation history and shared state to make your decision.
Respond with ONLY ONE of: "research", "analysis", "report", or "FINISH"."""

    # Check shared state to make routing decision
    completed_steps = state.get("completed_steps", [])
    web_results = state.get("web_results", [])
    analysis = state.get("analysis", "")
    final_report = state.get("final_report", "")
    
    # State-aware routing logic
    if not web_results:
        next_agent = "research"
        current_step = "Gathering research"
    elif not analysis:
        next_agent = "analysis"
        current_step = "Analyzing findings"
    elif not final_report:
        next_agent = "report"
        current_step = "Creating report"
    else:
        next_agent = "FINISH"
        current_step = "Complete"
    
    # Also ask the LLM for confirmation (demonstrates hybrid approach)
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = model.invoke(messages)
    
    # Update completed steps
    if next_agent != "FINISH" and current_step not in completed_steps:
        completed_steps = completed_steps + [current_step]
    
    return {
        "messages": [response],
        "next_agent": next_agent,
        "current_step": current_step,
        "completed_steps": completed_steps,
    }

# ============================================================================
# Routing Function
# ============================================================================

def route_supervisor(state: ResearchState) -> Literal["research", "analysis", "report", "__end__"]:
    """Route based on supervisor's decision in shared state"""
    next_agent = state.get("next_agent", "research")
    
    if next_agent == "research":
        return "research"
    elif next_agent == "analysis":
        return "analysis"
    elif next_agent == "report":
        return "report"
    else:
        return "__end__"

# ============================================================================
# Create Graph
# ============================================================================

def create_research_graph():
    """Create the multi-agent research graph with shared state"""
    
    workflow = StateGraph(ResearchState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("research", research_agent_node)
    workflow.add_node("analysis", analysis_agent_node)
    workflow.add_node("report", report_agent_node)
    
    # Entry point
    workflow.add_edge(START, "supervisor")
    
    # Supervisor routes to agents
    workflow.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "research": "research",
            "analysis": "analysis",
            "report": "report",
            "__end__": END
        }
    )
    
    # Agents return to supervisor
    workflow.add_edge("research", "supervisor")
    workflow.add_edge("analysis", "supervisor")
    workflow.add_edge("report", "supervisor")
    
    return workflow.compile()

# Export for LangGraph server
graph = create_research_graph()

# ============================================================================
# Example Usage
# ============================================================================

def main():
    """Run example research queries"""
    print("\n" + "="*80)
    print("MULTI-AGENT COLLABORATION WITH SHARED STATE DEMO")
    print("="*80 + "\n")
    
    graph = create_research_graph()
    
    # Example query
    query = "What are the latest developments in AI agents and LangGraph?"
    
    print(f"Query: {query}\n")
    print("-" * 80)
    
    # Initial state
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "research_query": query,
        "web_results": [],
        "sources": [],
        "key_findings": [],
        "analysis": "",
        "confidence_score": 0.0,
        "final_report": "",
        "current_step": "Starting",
        "completed_steps": [],
        "next_agent": "research",
    }
    
    # Run the graph
    for chunk in graph.stream(initial_state):
        for node, values in chunk.items():
            print(f"\n✓ Node '{node}' executed")
            
            # Show state updates
            if "current_step" in values:
                print(f"  Step: {values['current_step']}")
            
            if "web_results" in values and values["web_results"]:
                print(f"  📊 Added {len(values['web_results'])} web results to shared state")
            
            if "analysis" in values and values["analysis"]:
                print(f"  🔍 Added analysis to shared state")
            
            if "final_report" in values and values["final_report"]:
                print(f"  📝 Added final report to shared state")
    
    print("\n" + "="*80)
    print("✅ Research complete! All agents collaborated through shared state.")
    print("="*80)


if __name__ == "__main__":
    main()
