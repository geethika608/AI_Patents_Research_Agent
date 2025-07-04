#!/usr/bin/env python
"""
Test script to verify the modular listener structure.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_listener_imports():
    """Test that all listener modules can be imported correctly."""
    try:
        from patent_researcher_agent.core.listeners import MonitoringEventListener
        from patent_researcher_agent.core.listeners.base_listener import BaseMonitoringListener
        from patent_researcher_agent.core.listeners.crew_listener import CrewListener
        from patent_researcher_agent.core.listeners.agent_listener import AgentListener
        from patent_researcher_agent.core.listeners.task_listener import TaskListener
        
        print("✅ All listener modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_listener_creation():
    """Test that listeners can be created without errors."""
    try:
        from patent_researcher_agent.core.listeners import MonitoringEventListener
        from patent_researcher_agent.utils.monitoring import monitor
        
        # Create a test listener
        listener = MonitoringEventListener(monitor, "test-workflow-123")
        print("✅ MonitoringEventListener created successfully")
        
        # Test that it has the expected attributes
        assert hasattr(listener, 'crew_listener'), "Missing crew_listener"
        assert hasattr(listener, 'agent_listener'), "Missing agent_listener"
        assert hasattr(listener, 'task_listener'), "Missing task_listener"
        assert hasattr(listener, 'get_execution_summary'), "Missing get_execution_summary"
        
        print("✅ Listener has all expected attributes")
        return True
    except Exception as e:
        print(f"❌ Listener creation error: {e}")
        return False

def test_execution_summary():
    """Test that execution summary can be generated."""
    try:
        from patent_researcher_agent.core.listeners import MonitoringEventListener
        from patent_researcher_agent.utils.monitoring import monitor
        
        listener = MonitoringEventListener(monitor, "test-workflow-123")
        summary = listener.get_execution_summary()
        
        # Check that summary has expected structure
        expected_keys = ['workflow_id', 'crew_executions', 'agent_executions', 'task_executions', 'summary']
        for key in expected_keys:
            assert key in summary, f"Missing key: {key}"
        
        # Check summary statistics
        summary_stats = summary['summary']
        expected_stats = ['total_agent_executions', 'total_task_executions', 
                         'successful_agent_executions', 'successful_task_executions',
                         'failed_agent_executions', 'failed_task_executions',
                         'agent_success_rate', 'task_success_rate']
        for stat in expected_stats:
            assert stat in summary_stats, f"Missing summary stat: {stat}"
        
        print("✅ Execution summary generated successfully")
        print(f"   Workflow ID: {summary['workflow_id']}")
        print(f"   Summary: {summary['summary']}")
        return True
    except Exception as e:
        print(f"❌ Execution summary error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing modular listener structure...")
    print()
    
    tests = [
        ("Import Test", test_listener_imports),
        ("Creation Test", test_listener_creation),
        ("Summary Test", test_execution_summary),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Modular listener structure is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 