import os
from typing import Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Keys
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    serper_api_key: Optional[str] = Field(None, env="SERPER_API_KEY")
    
    # Application Settings
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # MLflow Settings
    mlflow_tracking_uri: str = Field("http://localhost:5000", env="MLFLOW_TRACKING_URI")
    mlflow_experiment_name: str = Field("CrewAI", env="MLFLOW_EXPERIMENT_NAME")
    
    # Memory Settings
    long_term_memory_path: str = Field("./memory/long_term.db", env="LONG_TERM_MEMORY_PATH")
    short_term_memory_path: str = Field("./memory/short_term", env="SHORT_TERM_MEMORY_PATH")
    entity_memory_path: str = Field("./memory/entity", env="ENTITY_MEMORY_PATH")
    
    # Output Settings
    output_dir: str = Field("./output", env="OUTPUT_DIR")
    knowledge_dir: str = Field("./knowledge", env="KNOWLEDGE_DIR")
    
    # Rate Limiting
    max_research_requests: int = Field(5, env="MAX_RESEARCH_REQUESTS")
    research_time_window: int = Field(300, env="RESEARCH_TIME_WINDOW")
    max_patent_search_requests: int = Field(20, env="MAX_PATENT_SEARCH_REQUESTS")
    patent_search_time_window: int = Field(60, env="PATENT_SEARCH_TIME_WINDOW")
    
    # UI Settings
    server_host: str = Field("0.0.0.0", env="SERVER_HOST")
    server_port: int = Field(7860, env="SERVER_PORT")
    share_interface: bool = Field(False, env="SHARE_INTERFACE")
    
    # Model Settings
    embedding_model: str = Field("text-embedding-3-small", env="EMBEDDING_MODEL")
    llm_model: str = Field("gpt-4o-mini", env="LLM_MODEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings() 