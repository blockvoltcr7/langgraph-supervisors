"""Simple test to verify the hierarchical pattern works"""

from main import create_hierarchical_graph
from langchain_core.messages import HumanMessage

def test_hierarchical():
    """Test the hierarchical graph"""
    print("\n🧪 Testing Hierarchical Teams Pattern\n")
    
    graph = create_hierarchical_graph()
    
    query = "Send an email to john@example.com about the meeting"
    print(f"Query: {query}\n")
    
    try:
        for chunk in graph.stream({"messages": [HumanMessage(content=query)]}):
            for node, values in chunk.items():
                print(f"✓ Node '{node}' executed")
                if "messages" in values and values["messages"]:
                    last_msg = values["messages"][-1]
                    if hasattr(last_msg, 'content'):
                        print(f"  Content: {last_msg.content[:80]}...")
        
        print("\n✅ Test passed!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_hierarchical()
