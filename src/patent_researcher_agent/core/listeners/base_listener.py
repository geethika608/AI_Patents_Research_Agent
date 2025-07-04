"""
Base event listener for monitoring CrewAI execution events.
"""

import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from crewai.utilities.events.base_event_listener import BaseEventListener

from ...utils.prometheus_metrics import metrics
from ...utils.logger import setup_logger

class BaseMonitoringListener(BaseEventListener):
    """
    Base class for monitoring event listeners with Prometheus metrics.
    """
    
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.logger = setup_logger(__name__)
        self.execution_data: Dict[str, Dict[str, Any]] = {}
        self.start_times: Dict[str, float] = {}
        self.is_active = True  # Track if listener is still active
        
        # Call parent constructor
        super().__init__()
    
    def cleanup(self):
        """Mark listener as inactive and clear tracking data."""
        self.is_active = False
        self.start_times.clear()
        self.execution_data.clear()
        self.logger.info(f"Cleaned up listener for workflow: {self.workflow_id}")
    
    def _get_step_id(self, step_type: str, step_name: str) -> str:
        """Generate a unique step ID."""
        # Use a simpler ID that's more predictable for tracking
        return f"{step_type}_{step_name}_{self.workflow_id}"
    
    def _start_tracking(self, step_id: str) -> None:
        """Start tracking execution time for a step."""
        self.start_times[step_id] = time.time()
        self.logger.debug(f"Started tracking step: {step_id}")
    
    def _end_tracking(self, step_id: str) -> float:
        """End tracking and return duration."""
        if step_id in self.start_times:
            duration = time.time() - self.start_times[step_id]
            del self.start_times[step_id]
            self.logger.debug(f"Ended tracking step: {step_id}, duration: {duration:.3f}s")
            return duration
        self.logger.warning(f"Step {step_id} not found in start_times")
        return 0.0
    
    def _log_execution(self, step_id: str, status: str, **kwargs):
        """Log execution event."""
        self.logger.info(f"Step execution - step_id={step_id}, status={status}, {kwargs}")
    
    def _log_error(self, step_id: str, error: Exception, **kwargs):
        """Log execution error."""
        self.logger.error(f"Step execution failed - step_id={step_id}, error={str(error)}, {kwargs}")
    
    def get_execution_data(self) -> Dict[str, Dict[str, Any]]:
        """Get all execution data for this listener."""
        return self.execution_data.copy() 