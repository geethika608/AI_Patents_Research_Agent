#!/usr/bin/env python3
"""
Test script to verify logger functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from patent_researcher_agent.utils.logger import setup_logger

def test_logger():
    """Test the logger functionality."""
    print("🧪 Testing logger functionality...")
    
    # Setup logger
    logger = setup_logger("test_logger")
    
    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test with context
    logger.info("Testing structured logging", 
                test_id="123", 
                component="logger_test",
                status="running")
    
    print("✅ Logger test completed. Check the logs directory for output files.")
    
    # List log files
    logs_dir = "./logs"
    if os.path.exists(logs_dir):
        print(f"\n📁 Log files created in {logs_dir}:")
        for file in os.listdir(logs_dir):
            filepath = os.path.join(logs_dir, file)
            size = os.path.getsize(filepath)
            print(f"  📄 {file} ({size} bytes)")
    else:
        print("❌ No logs directory found")

if __name__ == "__main__":
    test_logger() 