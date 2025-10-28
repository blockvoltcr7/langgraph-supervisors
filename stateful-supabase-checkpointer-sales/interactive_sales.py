#!/usr/bin/env python3
"""
Interactive Sales Qualification CLI

Chat with the AI sales agent directly in your terminal.
All conversations persist in Supabase!
"""

from sales_qualification import (
    continue_conversation,
    start_new_conversation,
    get_conversation_status,
    view_conversation_history
)

def print_header():
    """Print welcome header"""
    print("\n" + "="*80)
    print("  💬 SALES QUALIFICATION - INTERACTIVE CHAT")
    print("="*80)
    print("\n📝 Commands:")
    print("   - Type your message to chat")
    print("   - 'status' - View your qualification status")
    print("   - 'history' - View conversation history")
    print("   - 'quit' - Exit")
    print("\n" + "="*80 + "\n")

def main():
    """Run interactive chat"""
    print_header()
    
    # Get user ID
    user_id = input("👤 Enter your username (e.g., @john_doe): ").strip()
    
    if not user_id:
        user_id = "@demo_user"
        print(f"   Using default: {user_id}")
    
    # Check if conversation exists
    from sales_qualification import graph
    config = {"configurable": {"thread_id": user_id}}
    state = graph.get_state(config)
    
    if state.values:
        print(f"\n✅ Found existing conversation for {user_id}")
        print(f"   Stage: {state.values.get('current_stage')}")
        print(f"   Qualified: {state.values.get('qualification')}")
        print("\n💬 Continuing conversation...\n")
    else:
        print(f"\n🆕 Starting new conversation for {user_id}\n")
    
    # Chat loop
    first_message = True
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() == 'quit':
                print("\n👋 Goodbye! Your conversation is saved in Supabase.\n")
                break
            
            elif user_input.lower() == 'status':
                get_conversation_status(user_id)
                continue
            
            elif user_input.lower() == 'history':
                view_conversation_history(user_id)
                continue
            
            # Send message
            if first_message and not state.values:
                start_new_conversation(user_id, user_input)
                first_message = False
            else:
                continue_conversation(user_id, user_input)
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Your conversation is saved in Supabase.\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    main()
