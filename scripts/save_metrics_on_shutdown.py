#!/usr/bin/env python
"""
Script to save metrics on shutdown.
"""

import signal
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    print(f"\nReceived signal {signum}, saving metrics...")
    try:
        from patent_researcher_agent.utils.prometheus_metrics import metrics
        metrics.shutdown()
    except Exception as e:
        print(f"Error saving metrics: {e}")
    sys.exit(0)

def main():
    """Main function to set up signal handlers."""
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal
    
    print("Metrics persistence script started. Press Ctrl+C to save metrics and exit.")
    
    # Keep the script running
    try:
        while True:
            signal.pause()
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main() 