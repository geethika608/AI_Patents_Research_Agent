"""
Logging configuration for Patent Research AI Agent.
"""

import logging
import sys
from typing import Optional
import os
from datetime import datetime

# Try to import structlog, fallback to standard logging if not available
try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False
    print("Warning: structlog not available, using standard logging")


def disable_console_logging():
    """Disable console logging globally for all loggers."""
    # Disable console logging for the root logger
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
            root_logger.removeHandler(handler)
    
    # Set root logger to only WARNING level to suppress most output
    root_logger.setLevel(logging.WARNING)
    
    # Disable console logging for common libraries and our modules
    logger_names = [
        'crewai', 
        'crewai.utilities', 
        'crewai.utilities.events',
        'patent_researcher_agent',
        'patent_researcher_agent.core.listeners',
        'patent_researcher_agent.core.listeners.base_listener',
        'patent_researcher_agent.core.listeners.agent_listener',
        'patent_researcher_agent.core.listeners.task_listener',
        'patent_researcher_agent.core.listeners.crew_listener',
        'patent_researcher_agent.core.listeners.monitoring_listener'
    ]
    
    for logger_name in logger_names:
        logger = logging.getLogger(logger_name)
        # Remove any existing StreamHandlers
        for handler in logger.handlers[:]:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                logger.removeHandler(handler)
        # Set level to WARNING to suppress INFO and DEBUG
        logger.setLevel(logging.WARNING)
        # Prevent propagation to parent loggers
        logger.propagate = False


def force_disable_all_logging():
    """Force disable all logging output to console."""
    # Disable console logging first
    disable_console_logging()
    
    # Override the basicConfig to prevent new handlers
    logging.basicConfig(level=logging.WARNING, handlers=[])
    
    # Disable all existing loggers
    for name in logging.root.manager.loggerDict:
        logger = logging.getLogger(name)
        logger.handlers = []
        logger.propagate = False
        logger.setLevel(logging.WARNING)


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Setup a logger with structured logging if available.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger
    """
    # Disable console logging globally first
    disable_console_logging()
    
    if STRUCTLOG_AVAILABLE:
        return setup_structlog_logger(name, level)
    else:
        return setup_standard_logger(name, level)


def setup_structlog_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Setup structured logging with structlog."""
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    logger = structlog.get_logger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    return logger


def setup_standard_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Setup standard logging as fallback."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Disable console logging by not adding a StreamHandler
    # To re-enable console logging, uncomment the following lines:
    # if not logger.handlers:
    #     handler = logging.StreamHandler(sys.stdout)
    #     formatter = logging.Formatter(
    #         '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    #     )
    #     handler.setFormatter(formatter)
    #     logger.addHandler(handler)
    
    return logger


def get_log_files_info() -> dict:
    """
    Get information about log files.
    """
    logs_dir = "./logs"
    if not os.path.exists(logs_dir):
        return {"message": "Logs directory does not exist"}
    
    log_files = {}
    for filename in os.listdir(logs_dir):
        if filename.endswith('.log') or filename.endswith('.json'):
            filepath = os.path.join(logs_dir, filename)
            stat = os.stat(filepath)
            log_files[filename] = {
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "path": filepath
            }
    
    return log_files


def get_json_logger(name: str = "patent_researcher_agent") -> structlog.BoundLogger:
    """
    Get a structlog logger for JSON structured logging.
    """
    return structlog.get_logger(f"{name}_json") 