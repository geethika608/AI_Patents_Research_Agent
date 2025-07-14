"""
Global workflow tracking system to prevent multiple event listeners from processing the same events.
"""

import threading
import time
from typing import Dict, Optional, Set
import logging

logger = logging.getLogger(__name__)

class WorkflowTracker:
    """Global workflow tracking to prevent event listener conflicts."""
    
    def __init__(self):
        self._active_workflows: Set[str] = set()
        self._workflow_listeners: Dict[str, object] = {}  # workflow_id -> listener
        self._lock = threading.Lock()
        self._last_workflow_activity: Dict[str, float] = {}
    
    def register_workflow(self, workflow_id: str, listener: object) -> bool:
        """Register a workflow and its listener as active."""
        with self._lock:
            if workflow_id in self._active_workflows:
                logger.warning(f"Workflow {workflow_id} is already registered")
                return False
            
            self._active_workflows.add(workflow_id)
            self._workflow_listeners[workflow_id] = listener
            self._last_workflow_activity[workflow_id] = time.time()
            
            logger.info(f"Registered workflow {workflow_id} with listener {id(listener)}")
            logger.info(f"Active workflows: {list(self._active_workflows)}")
            return True
    
    def unregister_workflow(self, workflow_id: str) -> bool:
        """Unregister a workflow and its listener."""
        with self._lock:
            if workflow_id not in self._active_workflows:
                logger.warning(f"Workflow {workflow_id} is not registered")
                return False
            
            self._active_workflows.remove(workflow_id)
            if workflow_id in self._workflow_listeners:
                del self._workflow_listeners[workflow_id]
            if workflow_id in self._last_workflow_activity:
                del self._last_workflow_activity[workflow_id]
            
            logger.info(f"Unregistered workflow {workflow_id}")
            logger.info(f"Active workflows: {list(self._active_workflows)}")
            return True
    
    def is_workflow_active(self, workflow_id: str) -> bool:
        """Check if a workflow is currently active."""
        with self._lock:
            return workflow_id in self._active_workflows
    
    def get_active_workflows(self) -> Set[str]:
        """Get all currently active workflow IDs."""
        with self._lock:
            return self._active_workflows.copy()
    
    def update_workflow_activity(self, workflow_id: str):
        """Update the last activity time for a workflow."""
        with self._lock:
            if workflow_id in self._active_workflows:
                self._last_workflow_activity[workflow_id] = time.time()
    
    def get_workflow_listener(self, workflow_id: str) -> Optional[object]:
        """Get the listener for a specific workflow."""
        with self._lock:
            return self._workflow_listeners.get(workflow_id)
    
    def cleanup_inactive_workflows(self, max_inactive_time: float = 3600) -> int:
        """Clean up workflows that have been inactive for too long."""
        current_time = time.time()
        to_remove = []
        
        with self._lock:
            for workflow_id, last_activity in self._last_workflow_activity.items():
                if current_time - last_activity > max_inactive_time:
                    to_remove.append(workflow_id)
            
            for workflow_id in to_remove:
                self._active_workflows.discard(workflow_id)
                self._workflow_listeners.pop(workflow_id, None)
                self._last_workflow_activity.pop(workflow_id, None)
                logger.info(f"Cleaned up inactive workflow: {workflow_id}")
        
        return len(to_remove)
    
    def get_status(self) -> Dict:
        """Get current status of the workflow tracker."""
        with self._lock:
            return {
                "active_workflows": list(self._active_workflows),
                "workflow_count": len(self._active_workflows),
                "listener_count": len(self._workflow_listeners),
                "last_activity": {
                    workflow_id: time.time() - last_activity
                    for workflow_id, last_activity in self._last_workflow_activity.items()
                }
            }

# Global workflow tracker instance
workflow_tracker = WorkflowTracker()

def register_workflow(workflow_id: str, listener: object) -> bool:
    """Register a workflow with the global tracker."""
    return workflow_tracker.register_workflow(workflow_id, listener)

def unregister_workflow(workflow_id: str) -> bool:
    """Unregister a workflow from the global tracker."""
    return workflow_tracker.unregister_workflow(workflow_id)

def is_workflow_active(workflow_id: str) -> bool:
    """Check if a workflow is active."""
    return workflow_tracker.is_workflow_active(workflow_id)

def update_workflow_activity(workflow_id: str):
    """Update workflow activity timestamp."""
    workflow_tracker.update_workflow_activity(workflow_id)

def get_workflow_status() -> Dict:
    """Get current workflow tracker status."""
    return workflow_tracker.get_status() 