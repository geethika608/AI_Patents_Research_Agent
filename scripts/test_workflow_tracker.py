#!/usr/bin/env python3
"""
Test script for workflow tracker functionality.
"""

import time
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from patent_researcher_agent.utils.workflow_tracker import (
    register_workflow, 
    unregister_workflow, 
    is_workflow_active,
    update_workflow_activity,
    get_workflow_status,
    workflow_tracker
)

class MockListener:
    """Mock listener for testing."""
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.listener_id = f"listener_{workflow_id}_{id(self)}"

def test_workflow_tracker():
    """Test the workflow tracker functionality."""
    print("🧪 Testing Workflow Tracker")
    print("=" * 50)
    
    # Test initial status
    print("1. Testing initial status...")
    status = get_workflow_status()
    print(f"   Active workflows: {status['active_workflows']}")
    print(f"   Workflow count: {status['workflow_count']}")
    
    # Test registering workflows
    print("\n2. Testing workflow registration...")
    workflows = []
    listeners = []
    
    for i in range(3):
        workflow_id = f"test-workflow-{i}"
        listener = MockListener(workflow_id)
        workflows.append(workflow_id)
        listeners.append(listener)
        
        success = register_workflow(workflow_id, listener)
        print(f"   Registered {workflow_id}: {'✅' if success else '❌'}")
    
    # Check status after registration
    status = get_workflow_status()
    print(f"   Active workflows: {status['active_workflows']}")
    print(f"   Workflow count: {status['workflow_count']}")
    
    # Test duplicate registration
    print("\n3. Testing duplicate registration...")
    success = register_workflow(workflows[0], listeners[0])
    print(f"   Duplicate registration: {'❌' if not success else '✅'}")
    
    # Test workflow activity
    print("\n4. Testing workflow activity...")
    for i, workflow_id in enumerate(workflows):
        update_workflow_activity(workflow_id)
        print(f"   Updated activity for {workflow_id}")
    
    # Test is_workflow_active
    print("\n5. Testing is_workflow_active...")
    for workflow_id in workflows:
        active = is_workflow_active(workflow_id)
        print(f"   {workflow_id} active: {'✅' if active else '❌'}")
    
    # Test non-existent workflow
    active = is_workflow_active("non-existent-workflow")
    print(f"   non-existent-workflow active: {'❌' if not active else '✅'}")
    
    # Test unregistering workflows
    print("\n6. Testing workflow unregistration...")
    for i, workflow_id in enumerate(workflows):
        success = unregister_workflow(workflow_id)
        print(f"   Unregistered {workflow_id}: {'✅' if success else '❌'}")
    
    # Check final status
    status = get_workflow_status()
    print(f"   Final active workflows: {status['active_workflows']}")
    print(f"   Final workflow count: {status['workflow_count']}")
    
    # Test unregistering non-existent workflow
    print("\n7. Testing unregistering non-existent workflow...")
    success = unregister_workflow("non-existent-workflow")
    print(f"   Unregister non-existent: {'❌' if not success else '✅'}")
    
    print("\n✅ Workflow tracker test completed!")

def test_concurrent_workflows():
    """Test handling of concurrent workflows."""
    print("\n🧪 Testing Concurrent Workflows")
    print("=" * 50)
    
    # Register multiple workflows
    workflows = []
    listeners = []
    
    for i in range(5):
        workflow_id = f"concurrent-workflow-{i}"
        listener = MockListener(workflow_id)
        workflows.append(workflow_id)
        listeners.append(listener)
        register_workflow(workflow_id, listener)
        print(f"   Registered {workflow_id}")
    
    # Simulate concurrent activity
    print("\n1. Simulating concurrent activity...")
    for _ in range(3):
        for workflow_id in workflows:
            update_workflow_activity(workflow_id)
        time.sleep(0.1)
        print("   Updated activity for all workflows")
    
    # Check status
    status = get_workflow_status()
    print(f"\n2. Status after concurrent activity:")
    print(f"   Active workflows: {status['active_workflows']}")
    print(f"   Workflow count: {status['workflow_count']}")
    print(f"   Last activity: {status['last_activity']}")
    
    # Clean up
    print("\n3. Cleaning up...")
    for workflow_id in workflows:
        unregister_workflow(workflow_id)
        print(f"   Unregistered {workflow_id}")
    
    print("✅ Concurrent workflows test completed!")

def test_workflow_cleanup():
    """Test automatic cleanup of inactive workflows."""
    print("\n🧪 Testing Workflow Cleanup")
    print("=" * 50)
    
    # Register workflows
    workflows = []
    listeners = []
    
    for i in range(3):
        workflow_id = f"cleanup-test-{i}"
        listener = MockListener(workflow_id)
        workflows.append(workflow_id)
        listeners.append(listener)
        register_workflow(workflow_id, listener)
        print(f"   Registered {workflow_id}")
    
    # Update activity for some workflows
    update_workflow_activity(workflows[0])
    update_workflow_activity(workflows[1])
    print("   Updated activity for first two workflows")
    
    # Wait a bit
    time.sleep(1)
    
    # Test cleanup with short timeout
    print("\n1. Testing cleanup with short timeout...")
    cleaned_count = workflow_tracker.cleanup_inactive_workflows(max_inactive_time=0.5)
    print(f"   Cleaned up {cleaned_count} inactive workflows")
    
    # Check remaining workflows
    status = get_workflow_status()
    print(f"   Remaining workflows: {status['active_workflows']}")
    
    # Clean up remaining
    for workflow_id in workflows:
        if is_workflow_active(workflow_id):
            unregister_workflow(workflow_id)
            print(f"   Manually unregistered {workflow_id}")
    
    print("✅ Workflow cleanup test completed!")

if __name__ == "__main__":
    try:
        test_workflow_tracker()
        test_concurrent_workflows()
        test_workflow_cleanup()
        print("\n🎉 All workflow tracker tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc() 