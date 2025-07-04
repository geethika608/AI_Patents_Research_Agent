#!/usr/bin/env python
import warnings
from datetime import datetime
from patent_researcher_agent.launch_chat import launch_chat
from .utils.logger import setup_logger, force_disable_all_logging
from .utils.helpers import validate_required_env_vars

# Force disable all console logging at startup
force_disable_all_logging()

# Setup logger
logger = setup_logger(__name__)

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic")
warnings.filterwarnings("ignore", message=".*Using extra keyword arguments on `Field` is deprecated.*")
warnings.filterwarnings("ignore", message=".*There is no current event loop.*")


def run():
    """
    Run the research crew with proper logging and validation.
    """
    logger.info("Starting patent research agent")
    
    # Validate environment variables
    try:
        validate_required_env_vars(["OPENAI_API_KEY"])
        logger.info("Environment validation passed")
    except ValueError as e:
        logger.error(f"Environment validation failed: {e}")
        print(f"❌ Environment Error: {e}")
        return
    
    try:
        logger.info("Launching chat interface")
        launch_chat()
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    logger.info("Patent Research Agent starting up")
    run() 