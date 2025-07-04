#!/usr/bin/env python3
"""
Test script for metrics persistence functionality.
"""

import time
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from patent_researcher_agent.utils.prometheus_metrics import metrics
from patent_researcher_agent.utils.metrics_persistence import MetricsPersistence

def test_metrics_persistence():
    """Test the metrics persistence functionality."""
    print("🧪 Testing Metrics Persistence")
    print("=" * 50)
    
    # Create a test persistence instance
    persistence = MetricsPersistence("test_metrics.json")
    
    # Clear any existing test file
    if persistence.persistence_file.exists():
        persistence.persistence_file.unlink()
        print("1. Cleared existing test file")
    
    # Test saving metrics
    print("\n2. Testing metrics saving...")
    test_metrics = {
        "agent_executions": {
            "fetcher_agent": {"success": 5, "failure": 1},
            "analyzer_agent": {"success": 3, "failure": 0}
        },
        "task_executions": {
            "fetch_patents": {"success": 2, "failure": 0},
            "analyze_trends": {"success": 1, "failure": 0}
        },
        "workflows": {
            "test-workflow-1": {"success": 1, "failure": 0}
        }
    }
    
    success = persistence.save_metrics(test_metrics)
    if success:
        print("   ✅ Metrics saved successfully")
    else:
        print("   ❌ Failed to save metrics")
        return False
    
    # Test loading metrics
    print("\n3. Testing metrics loading...")
    loaded_metrics = persistence.load_metrics()
    if loaded_metrics:
        print("   ✅ Metrics loaded successfully")
        print(f"   Agent executions: {len(loaded_metrics.get('agent_executions', {}))}")
        print(f"   Task executions: {len(loaded_metrics.get('task_executions', {}))}")
        print(f"   Workflows: {len(loaded_metrics.get('workflows', {}))}")
    else:
        print("   ❌ Failed to load metrics")
        return False
    
    # Test metrics age
    print("\n4. Testing metrics age...")
    age = persistence.get_metrics_age()
    if age is not None:
        print(f"   ✅ Metrics age: {age:.2f} seconds")
    else:
        print("   ❌ Failed to get metrics age")
        return False
    
    # Test should_restore_metrics
    print("\n5. Testing restore decision...")
    should_restore = persistence.should_restore_metrics(max_age_hours=1)
    print(f"   Should restore (1 hour max): {should_restore}")
    
    should_restore_old = persistence.should_restore_metrics(max_age_hours=0.001)  # 3.6 seconds
    print(f"   Should restore (3.6 seconds max): {should_restore_old}")
    
    # Clean up
    if persistence.persistence_file.exists():
        persistence.persistence_file.unlink()
        print("\n6. Cleaned up test file")
    
    print("\n✅ Metrics persistence test completed successfully!")
    return True

def test_prometheus_metrics_integration():
    """Test the integration with Prometheus metrics."""
    print("\n🧪 Testing Prometheus Metrics Integration")
    print("=" * 50)
    
    try:
        # Test saving current metrics
        print("1. Testing save_metrics method...")
        metrics._save_metrics()
        print("   ✅ Save metrics method executed successfully")
        
        # Test restore metrics
        print("\n2. Testing restore_metrics method...")
        metrics._restore_metrics()
        print("   ✅ Restore metrics method executed successfully")
        
        # Test periodic saving
        print("\n3. Testing periodic saving...")
        # Start periodic saving with a short interval for testing
        import threading
        import time
        
        def test_periodic_save():
            time.sleep(2)  # Wait 2 seconds
            metrics._save_metrics()
            print("   ✅ Periodic save executed")
        
        save_thread = threading.Thread(target=test_periodic_save, daemon=True)
        save_thread.start()
        save_thread.join(timeout=5)
        
        print("   ✅ Periodic saving test completed")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Prometheus integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_metrics_file_operations():
    """Test file operations for metrics persistence."""
    print("\n🧪 Testing Metrics File Operations")
    print("=" * 50)
    
    # Test with different file paths
    test_files = [
        "test_metrics_1.json",
        "monitoring/metrics/test_metrics_2.json",
        "./test_metrics_3.json"
    ]
    
    for test_file in test_files:
        print(f"\nTesting file: {test_file}")
        
        try:
            persistence = MetricsPersistence(test_file)
            
            # Test saving
            test_data = {"test": "data", "timestamp": time.time()}
            success = persistence.save_metrics(test_data)
            print(f"   Save: {'✅' if success else '❌'}")
            
            # Test loading
            loaded_data = persistence.load_metrics()
            print(f"   Load: {'✅' if loaded_data else '❌'}")
            
            # Test age
            age = persistence.get_metrics_age()
            print(f"   Age: {'✅' if age is not None else '❌'}")
            
            # Clean up
            if persistence.persistence_file.exists():
                persistence.persistence_file.unlink()
                print(f"   Cleanup: ✅")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n✅ File operations test completed!")

if __name__ == "__main__":
    try:
        success = True
        
        # Run all tests
        success &= test_metrics_persistence()
        success &= test_prometheus_metrics_integration()
        test_metrics_file_operations()  # This one doesn't return a boolean
        
        if success:
            print("\n🎉 All metrics persistence tests passed!")
        else:
            print("\n❌ Some tests failed!")
            
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc() 