"""
Test script to verify web search is actually working
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from main import create_research_graph

# Load environment
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

def test_web_search():
    """Test that web search actually retrieves real data"""
    print("\n" + "="*80)
    print("TESTING REAL WEB SEARCH")
    print("="*80 + "\n")
    
    graph = create_research_graph()
    
    query = "What is LangGraph?"
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
    
    # Run the graph and collect final state
    final_state = None
    for chunk in graph.stream(initial_state):
        for node, values in chunk.items():
            print(f"\n✓ {node}")
            
            # Show web results when they're added
            if "web_results" in values and values["web_results"]:
                print(f"\n📊 WEB SEARCH RESULTS ({len(values['web_results'])} results):")
                print("-" * 80)
                for i, result in enumerate(values["web_results"][:3], 1):
                    print(f"\n{i}. {result.get('title', 'No title')}")
                    print(f"   Content: {result.get('content', 'No content')[:200]}...")
                    print(f"   URL: {result.get('url', 'No URL')}")
                print("-" * 80)
            
            # Show final report
            if "final_report" in values and values["final_report"]:
                print(f"\n📝 FINAL REPORT:")
                print("=" * 80)
                print(values["final_report"])
                print("=" * 80)
            
            final_state = values
    
    # Verify we got real data
    if final_state:
        web_results = final_state.get("web_results", [])
        sources = final_state.get("sources", [])
        
        print(f"\n\n✅ VERIFICATION:")
        print(f"   - Web results: {len(web_results)}")
        print(f"   - Sources: {len(sources)}")
        print(f"   - Real URLs: {any('http' in str(s) for s in sources)}")
        
        if len(web_results) > 1 and sources:
            print(f"\n🎉 SUCCESS! Web search is working and returning real data!")
        else:
            print(f"\n⚠️  Warning: Web search may not be working properly")
            print(f"   Check your TAVILY_API_KEY in .env")

if __name__ == "__main__":
    test_web_search()
