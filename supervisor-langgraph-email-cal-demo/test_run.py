"""Quick test script to verify the supervisor works"""
from main import create_supervisor_graph
from langchain_core.messages import HumanMessage

print("Testing supervisor graph...")
supervisor = create_supervisor_graph()

query = "Schedule a team standup for tomorrow at 9am"
print(f"\nQuery: {query}\n")

try:
    for chunk in supervisor.stream(
        {"messages": [HumanMessage(content=query)]}
    ):
        for node_name, node_update in chunk.items():
            print(f"✓ Node '{node_name}' executed")
            if node_update.get("messages"):
                last_msg = node_update["messages"][-1]
                if hasattr(last_msg, 'content') and last_msg.content:
                    print(f"  Content: {last_msg.content[:100]}...")
    
    print("\n✅ Test completed successfully!")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
