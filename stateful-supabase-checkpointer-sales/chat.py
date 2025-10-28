#!/usr/bin/env python3
"""
Simple Chat Interface for Sales Qualification

This is the EASIEST way to use the sales qualification system.
Just run: python chat.py
"""

from main import continue_conversation, start_new_conversation, graph

def chat_with_user(username: str):
    """
    Simple chat loop for a user.
    
    Args:
        username: User's identifier (e.g., @john_doe)
    """
    print(f"\n{'='*80}")
    print(f"  💬 CHAT WITH {username}")
    print(f"{'='*80}\n")
    
    # Check if conversation exists
    config = {"configurable": {"thread_id": username}}
    state = graph.get_state(config)
    
    if state.values:
        print(f"✅ Continuing existing conversation")
        print(f"   Current Stage: {state.values.get('current_stage')}")
        print(f"   Qualified: {state.values.get('qualification')}\n")
    else:
        print(f"🆕 Starting new conversation\n")
    
    print("💡 Commands:")
    print("   - Type your message to chat")
    print("   - 'quit' or 'exit' to end")
    print(f"\n{'-'*80}\n")
    
    first_message = True
    
    while True:
        try:
            # Get user input
            user_input = input("👤 You: ").strip()
            
            if not user_input:
                continue
            
            # Check for quit
            if user_input.lower() in ['quit', 'exit', 'q']:
                print(f"\n👋 Goodbye! Your conversation is saved in Supabase.\n")
                break
            
            # Send message
            print()  # Blank line for spacing
            
            if first_message and not state.values:
                # New conversation
                start_new_conversation(username, user_input)
                first_message = False
            else:
                # Continue existing conversation
                continue_conversation(username, user_input)
            
            print()  # Blank line after response
            
        except KeyboardInterrupt:
            print(f"\n\n👋 Goodbye! Your conversation is saved in Supabase.\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            break

def main():
    """Main entry point"""
    print("\n" + "🎯"*40)
    print("  SALES QUALIFICATION - CHAT INTERFACE")
    print("🎯"*40 + "\n")
    
    # Get username
    username = input("👤 Enter your username (e.g., @john_doe): ").strip()
    
    if not username:
        username = "@demo_user"
        print(f"   Using default: {username}")
    
    # Start chat
    chat_with_user(username)

if __name__ == "__main__":
    main()
