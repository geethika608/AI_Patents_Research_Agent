#!/usr/bin/env python3
"""
Test script for advanced metrics in Patent Research AI Agent.
Generates test data for available metrics.
"""

import time
import random
import requests
import threading
from datetime import datetime

def test_requests_patching():
    """Test that requests library is properly patched."""
    print("🧪 Testing Requests Library Patching...")
    
    # These should be automatically tracked
    test_urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/status/200",
        "https://httpbin.org/status/404"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"  ✅ Requests call: {url} - status: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Requests call: {url} - failed: {e}")
        
        time.sleep(0.5)

def generate_continuous_metrics(duration: int = 60):
    """Generate continuous metrics for the specified duration."""
    print(f"🔄 Generating continuous metrics for {duration} seconds...")
    
    start_time = time.time()
    
    def requests_worker():
        while time.time() - start_time < duration:
            test_requests_patching()
            time.sleep(10)
    
    # Start worker in separate thread
    thread = threading.Thread(target=requests_worker, daemon=True)
    thread.start()
    
    # Wait for completion
    thread.join()
    
    print("✅ Continuous metrics generation completed!")

def main():
    """Main test function."""
    print("🚀 Starting Advanced Metrics Test Suite")
    print("=" * 50)
    
    # Run individual tests
    test_requests_patching()
    print()
    
    # Run continuous generation for 30 seconds
    print("🔄 Starting continuous metrics generation...")
    generate_continuous_metrics(duration=30)
    
    print("\n🎉 All tests completed!")
    print("📊 Check your metrics at: http://localhost:8000/metrics")
    print("📈 Check your Grafana dashboard for the new metrics!")

if __name__ == "__main__":
    main() 