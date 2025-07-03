#!/usr/bin/env python
import warnings
from datetime import datetime
from patent_researcher_agent.launch_chat import launch_chat

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic")
warnings.filterwarnings("ignore", message=".*Using extra keyword arguments on `Field` is deprecated.*")
warnings.filterwarnings("ignore", message=".*There is no current event loop.*")


def run():
    """
    Run the research crew.
    """
    
    launch_chat()


if __name__ == "__main__":
    run()
