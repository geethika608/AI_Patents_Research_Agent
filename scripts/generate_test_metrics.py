#!/usr/bin/env python3
"""
Script to generate test metrics for the Patent Research AI Agent.
This will create sample data to populate the Grafana dashboard.
"""

import time
import random
from datetime import datetime, timedelta

def generate_test_metrics():
    """Generate test metrics for demonstration."""
    
    print("🚀 Generating test metrics for Patent Research AI Agent...")
    
    # Import metrics after ensuring the server is started
    from patent_researcher_agent.utils.prometheus_metrics import metrics
    
    # Simulate agent executions
    agents = ["fetcher_agent", "analyzer_agent", "reporter_agent"]
    
    for i in range(20):
        # Random agent
        agent_name = random.choice(agents)
        
        # Simulate execution time (1-10 seconds)
        execution_time = random.uniform(1.0, 10.0)
        
        # Simulate success/failure
        success = random.random() > 0.1  # 90% success rate
        
        # Track agent execution
        metrics.track_agent_execution(agent_name, execution_time, success)
        
        # Simulate task execution
        task_name = f"task_{agent_name.replace('_agent', '')}"
        task_time = execution_time * 0.8  # Tasks are usually faster
        metrics.track_task_execution(task_name, task_time, success)
        
        # Simulate API calls
        api_time = random.uniform(0.1, 2.0)
        metrics.track_api_request("openai_api", api_time, success)
        
        # Simulate rate limiting
        if random.random() > 0.95:  # 5% chance of rate limit
            remaining_calls = random.randint(0, 10)
            reset_time = time.time() + random.uniform(60, 300)
            metrics.track_rate_limit("openai_api", remaining_calls, reset_time)
        
        print(f"  ✅ Generated metrics for {agent_name} (duration: {execution_time:.2f}s, success: {success})")
        
        # Wait a bit between metrics
        time.sleep(0.5)
    
    print(f"📊 Generated {20} test metric entries")
    print("🌐 Check your Grafana dashboard at http://localhost:3000")
    print("📈 Metrics endpoint: http://localhost:8000/metrics")
    
    # Keep the server running
    print("🔄 Keeping metrics server running... Press Ctrl+C to stop")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping metrics server...")

if __name__ == "__main__":
    generate_test_metrics() 