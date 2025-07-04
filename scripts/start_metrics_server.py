#!/usr/bin/env python3
"""
Start the metrics server and generate test data for Prometheus.
"""

import time
import random
from patent_researcher_agent.utils.prometheus_metrics import metrics

def generate_test_data():
    """Generate test metrics data."""
    print("🚀 Starting metrics server and generating test data...")
    
    # Generate some initial test data
    agents = ["fetcher_agent", "analyzer_agent", "reporter_agent"]
    
    for i in range(10):
        agent_name = random.choice(agents)
        execution_time = random.uniform(1.0, 5.0)
        success = random.random() > 0.1
        
        # Track agent execution
        metrics.track_agent_execution(agent_name, execution_time, success)
        
        # Track task execution
        task_name = f"task_{agent_name.replace('_agent', '')}"
        task_time = execution_time * 0.8
        metrics.track_task_execution(task_name, task_time, success)
        
        # Track API request
        api_time = random.uniform(0.1, 1.0)
        metrics.track_api_request("openai_api", api_time, success)
        
        print(f"  ✅ Generated metrics for {agent_name} (duration: {execution_time:.2f}s, success: {success})")
        time.sleep(0.5)
    
    print("📊 Initial test data generated!")
    print("🌐 Metrics available at: http://localhost:8000/metrics")
    print("📈 Prometheus should be scraping from: http://localhost:8000/metrics")
    print("🔄 Keeping server running... Press Ctrl+C to stop")
    
    # Keep the server running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping metrics server...")

if __name__ == "__main__":
    generate_test_data() 