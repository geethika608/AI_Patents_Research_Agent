import os
from pathlib import Path
from typing import Dict, Any


def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure a directory exists, create it if it doesn't.
    """
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def get_project_root() -> Path:
    """
    Get the project root directory.
    """
    return Path(__file__).parent.parent.parent.parent


def load_environment_variables() -> Dict[str, str]:
    """
    Load environment variables from .env file.
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "SERPER_API_KEY": os.getenv("SERPER_API_KEY"),
    }


def validate_required_env_vars(required_vars: list) -> None:
    """
    Validate that required environment variables are set.
    """
    env_vars = load_environment_variables()
    missing_vars = [var for var in required_vars if not env_vars.get(var)]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}") 