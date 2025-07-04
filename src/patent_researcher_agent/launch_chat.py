#!/usr/bin/env python
"""
Launch chat interface for Patent Research AI Agent
"""

from patent_researcher_agent.ui.chat_ui import launch_chat as launch_chat_ui
from .utils.logger import setup_logger
from .utils.helpers import validate_required_env_vars

# Setup logger
logger = setup_logger(__name__)


def launch_chat():
    """
    Launch the Gradio chat interface.
    """
    logger.info("Starting chat interface launch process")
    
    # Validate environment variables
    try:
        validate_required_env_vars(["OPENAI_API_KEY"])
        logger.info("Environment variables validated successfully")
    except ValueError as e:
        logger.error(f"Environment validation failed: {e}")
        print(f"❌ Environment Error: {e}")
        return
    
    try:
        logger.info("Launching chat UI")
        launch_chat_ui()
    except Exception as e:
        logger.error(f"Failed to launch chat UI: {e}")
        raise


if __name__ == "__main__":
    print("🚀 Launching Patent Research AI Agent Chat Interface...")
    print("📱 The interface will be available at: http://localhost:7860")
    print("🔄 Press Ctrl+C to stop the server")
    print()
    
    try:
        launch_chat()
    except KeyboardInterrupt:
        logger.info("Chat interface stopped by user")
        print("\n👋 Chat interface stopped. Goodbye!")
    except Exception as e:
        logger.error(f"Error launching chat interface: {e}")
        print(f"❌ Error launching chat interface: {e}")
        import sys
        sys.exit(1) 