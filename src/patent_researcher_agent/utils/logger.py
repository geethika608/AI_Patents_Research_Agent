"""
Logging configuration for Patent Research AI Agent.
"""

import logging
import sys
from typing import Optional

# Try to import structlog, fallback to standard logging if not available
try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False
    print("Warning: structlog not available, using standard logging")


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Setup a logger with structured logging if available.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger
    """
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