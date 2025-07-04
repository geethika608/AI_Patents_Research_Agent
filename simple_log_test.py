#!/usr/bin/env python3
"""
Simple test to verify basic logging functionality.
"""

import os
import sys
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_logging():
    """Test basic logging without structlog."""
    print("🧪 Testing basic logging functionality...")
    
    # Create logs directory
    logs_dir = "./logs"
    os.makedirs(logs_dir, exist_ok=True)
    
    # Create timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    
    # Setup basic logging
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.INFO)
    logger.propagate = False  # Prevent conflicts
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '🔍 %(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(f"{logs_dir}/test_log_{timestamp}.log")
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Test logging
    logger.info("This is a test info message")
    logger.warning("This is a test warning message")
    logger.error("This is a test error message")
    
    print("✅ Basic logging test completed!")
    
    # Check if log file was created
    log_file = f"{logs_dir}/test_log_{timestamp}.log"
    if os.path.exists(log_file):
        print(f"📄 Log file created: {log_file}")
        with open(log_file, 'r') as f:
            content = f.read()
            print(f"📊 Log file content ({len(content)} bytes):")
            print(content)
    else:
        print("❌ Log file was not created")

if __name__ == "__main__":
    test_basic_logging() 