#!/usr/bin/env python
"""
Script to manually restore metrics from persistence file.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def main():
    """Main function to restore metrics."""
    try:
        from patent_researcher_agent.utils.prometheus_metrics import metrics
        from patent_researcher_agent.utils.metrics_persistence import MetricsPersistence
        
        persistence = MetricsPersistence()
        
        # Check if metrics should be restored
        if persistence.should_restore_metrics():
            print("Restoring metrics from persistence file...")
            metrics._restore_metrics()
            print("Metrics restored successfully!")
        else:
            print("No valid metrics to restore (too old or no file found)")
            
    except Exception as e:
        print(f"Error restoring metrics: {e}")

if __name__ == "__main__":
    main() 