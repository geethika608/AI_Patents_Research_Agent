#!/usr/bin/env python
"""
Launch chat interface for Patent Research AI Agent
"""

from patent_researcher_agent.chat_ui import launch_chat as launch_chat_ui


def launch_chat():
    """
    Launch the Gradio chat interface.
    """
    launch_chat_ui()

if __name__ == "__main__":
    print("🚀 Launching Patent Research AI Agent Chat Interface...")
    print("📱 The interface will be available at: http://localhost:7860")
    print("🔄 Press Ctrl+C to stop the server")
    print()
    
    try:
        launch_chat()
    except KeyboardInterrupt:
        print("\n👋 Chat interface stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error launching chat interface: {e}")
        sys.exit(1) 