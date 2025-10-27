#!/usr/bin/env python3
"""
Interactive database query tool.
"""

from main import create_project_workflow

def interactive_query():
    """Interactive query interface."""
    graph = create_project_workflow()
    
    print("🔍 Interactive Database Query")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. List projects")
        print("2. View project state")
        print("3. View project history")
        print("4. Time-travel to checkpoint")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            # List projects
            import sqlite3
            conn = sqlite3.connect("project_checkpoints.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT thread_id, COUNT(*) as count
                FROM checkpoints
                GROUP BY thread_id
            """)
            print("\nProjects:")
            for row in cursor.fetchall():
                print(f"  {row[0]}: {row[1]} checkpoints")
            conn.close()
        
        elif choice == "2":
            # View project state
            thread_id = input("Enter thread ID (default: project-1): ").strip() or "project-1"
            config = {"configurable": {"thread_id": thread_id}}
            
            state = graph.get_state(config)
            if state.values:
                print(f"\nCurrent Stage: {state.values['current_stage']}")
                print(f"Planning Complete: {state.values['planning_complete']}")
                print(f"Execution Complete: {state.values['execution_complete']}")
                print(f"Review Complete: {state.values['review_complete']}")
                print(f"Completed Tasks: {len(state.values['completed_tasks'])}")
                print(f"Pending Tasks: {len(state.values['pending_tasks'])}")
            else:
                print("No state found for this project")
        
        elif choice == "3":
            # View project history
            thread_id = input("Enter thread ID (default: project-1): ").strip() or "project-1"
            config = {"configurable": {"thread_id": thread_id}}
            
            history = list(graph.get_state_history(config))
            print(f"\nFound {len(history)} checkpoints:")
            
            for i, checkpoint in enumerate(history):
                values = checkpoint.values
                print(f"  {i+1}. Stage: {values['current_stage']}, "
                      f"Completed: {len(values['completed_tasks'])}")
        
        elif choice == "4":
            # Time-travel
            thread_id = input("Enter thread ID (default: project-1): ").strip() or "project-1"
            config = {"configurable": {"thread_id": thread_id}}
            
            history = list(graph.get_state_history(config))
            if not history:
                print("No checkpoints found")
                continue
            
            print(f"\nAvailable checkpoints: {len(history)}")
            checkpoint_num = input(f"Enter checkpoint number (1-{len(history)}): ").strip()
            
            try:
                idx = int(checkpoint_num) - 1
                if 0 <= idx < len(history):
                    old_checkpoint = history[idx]
                    graph.update_state(config, old_checkpoint.values)
                    print(f"✅ Time-traveled to checkpoint {checkpoint_num}")
                    print(f"   Stage: {old_checkpoint.values['current_stage']}")
                    print(f"   Completed Tasks: {len(old_checkpoint.values['completed_tasks'])}")
                else:
                    print("Invalid checkpoint number")
            except ValueError:
                print("Please enter a valid number")
        
        elif choice == "5":
            print("Goodbye! 👋")
            break
        
        else:
            print("Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    interactive_query()
