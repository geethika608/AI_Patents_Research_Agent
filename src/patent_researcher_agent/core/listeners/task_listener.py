"""
Task-level event listener for monitoring task execution.
"""

from datetime import datetime
from crewai.utilities.events import (
    TaskStartedEvent,
    TaskCompletedEvent,
    TaskFailedEvent,
)

from .base_listener import BaseMonitoringListener
from patent_researcher_agent.utils.prometheus_metrics import metrics

from patent_researcher_agent.utils.workflow_tracker import is_workflow_active, update_workflow_activity

class TaskListener(BaseMonitoringListener):
    """
    Listener for task-level events (start, complete, error).
    """
    
    def _extract_task_name(self, source) -> str:
        """
        Extract a consistent task name from the source object.
        Returns a standardized task name for metrics tracking.
        """
        task_name = 'unknown_task'
        original_desc = None
        
        # Try to get description from source object
        if hasattr(source, 'description') and source.description:
            original_desc = source.description
            full_desc = source.description.lower()
            
            # Log the original description for debugging
            self.logger.info(f"Task description: '{original_desc}'")
            
            # More flexible and comprehensive task name mapping
            # Check for analyze_trends first (most specific)
            if 'analyze patent data' in full_desc:
                task_name = 'analyze_trends'
            elif any(word in full_desc for word in ['analyze', 'analysis', 'examine', 'study']) and any(word in full_desc for word in ['trend', 'trends', 'innovation', 'pattern', 'insight']):
                task_name = 'analyze_trends'
            # Check for fetch_patents (more specific)
            elif any(word in full_desc for word in ['fetch', 'search', 'retrieve']) and any(word in full_desc for word in ['patent', 'patents']) and 'analyze' not in full_desc:
                task_name = 'fetch_patents'
            # Check for generate_report
            elif any(word in full_desc for word in ['report', 'generate', 'create', 'produce']) and any(word in full_desc for word in ['report', 'insight', 'summary', 'findings']):
                task_name = 'generate_report'
            # Fallback conditions (less specific)
            elif any(word in full_desc for word in ['analyze', 'analysis', 'examine', 'study']):
                # If it contains analyze but not trend/innovation, still map to analyze_trends
                task_name = 'analyze_trends'
            elif any(word in full_desc for word in ['fetch', 'search', 'retrieve']):
                # If it contains fetch but not patent, still map to fetch_patents
                task_name = 'fetch_patents'
            elif any(word in full_desc for word in ['report', 'generate', 'create', 'produce']):
                # If it contains report/generate but not report/insight, still map to generate_report
                task_name = 'generate_report'
            else:
                # Fallback: create a more descriptive name from the description
                words = source.description.split()[:4]  # Take first 4 words
                task_name = '_'.join(words).lower().replace(' ', '_').replace(',', '').replace('.', '')
                # Limit length to avoid overly long names
                if len(task_name) > 30:
                    task_name = task_name[:30]
                
        elif hasattr(source, 'id') and source.id:
            task_name = source.id
        elif hasattr(source, 'name') and source.name:
            task_name = source.name
        elif hasattr(source, '__class__') and source.__class__.__name__:
            task_name = source.__class__.__name__.lower()
        
        # Log the mapping result
        self.logger.info(f"Task name mapped: '{original_desc}' -> '{task_name}'")
        
        return task_name
    
    def setup_listeners(self, crewai_event_bus):
        """Setup task event handlers."""
        
        @crewai_event_bus.on(TaskStartedEvent)
        def on_task_execution_started(source, event: TaskStartedEvent):
            # Check if listener is still active
            if not hasattr(self, 'is_active') or not self.is_active:
                return
            
            # Check if this workflow is still active in the global tracker
            if not is_workflow_active(self.workflow_id):
                self.logger.info(f"SKIPPING EVENT - Workflow {self.workflow_id} is not active")
                return
            
            # Update workflow activity
            update_workflow_activity(self.workflow_id)
            
            # Get task name first
            task_name = self._extract_task_name(source)
            step_id = self._get_step_id("task", task_name)
            
            # Check if we're already tracking this step (from another workflow)
            if step_id in self.start_times:
                self.logger.info(f"SKIPPING TASK START EVENT - Already tracking step: {step_id}")
                return
            
            # Get task info from source using improved extraction
            task_name = self._extract_task_name(source)
            task_id = getattr(source, 'id', 'unknown_task_id')
            
            step_id = self._get_step_id("task", task_name)
            self.logger.debug(f"Task execution started: {task_name}, step_id: {step_id}")
            self._start_tracking(step_id)
            
            self.execution_data[step_id] = {
                "task_name": task_name,
                "task_id": task_id,
                "start_time": datetime.now(),
                "status": "started"
            }
            
            self._log_execution(step_id, "started",
                              task_name=task_name,
                              task_id=task_id)

        @crewai_event_bus.on(TaskCompletedEvent)
        def on_task_execution_completed(source, event: TaskCompletedEvent):
            # Check if listener is still active
            if not hasattr(self, 'is_active') or not self.is_active:
                return
            
            # Check if this workflow is still active in the global tracker
            if not is_workflow_active(self.workflow_id):
                self.logger.info(f"SKIPPING EVENT - Workflow {self.workflow_id} is not active")
                return
            
            # Update workflow activity
            update_workflow_activity(self.workflow_id)
            
            # Get task name consistently with started event
            task_name = self._extract_task_name(source)
            step_id = self._get_step_id("task", task_name)
            
            # Only process if we have started tracking this step
            if step_id not in self.start_times:
                self.logger.info(f"SKIPPING TASK COMPLETED EVENT - No active tracking for step: {step_id}")
                return
            
            # Get task name consistently with started event
            task_name = self._extract_task_name(source)
            
            step_id = self._get_step_id("task", task_name)
            duration = self._end_tracking(step_id)
            
            if step_id in self.execution_data:
                self.execution_data[step_id].update({
                    "end_time": datetime.now(),
                    "duration": duration,
                    "status": "completed",
                    "result_type": type(event.output).__name__,
                    "result_length": len(str(event.output)) if event.output else 0
                })
            
            # Track in Prometheus only if we have a valid duration (not 0.0 from missing start time)
            if duration > 0:
                self.logger.info(f"TRACKING TASK EXECUTION: {task_name}, duration: {duration}, success: True")
                metrics.track_task_execution(task_name, duration, True)
            else:
                self.logger.warning(f"SKIPPING TASK EXECUTION TRACKING: {task_name}, duration: {duration} (invalid)")
            
            self._log_execution(step_id, "completed",
                              task_name=task_name,
                              duration=duration,
                              result_type=type(event.output).__name__,
                              result_length=len(str(event.output)) if event.output else 0)

        @crewai_event_bus.on(TaskFailedEvent)
        def on_task_execution_error(source, event: TaskFailedEvent):
            # Check if listener is still active
            if not hasattr(self, 'is_active') or not self.is_active:
                return
            
            # Check if this workflow is still active in the global tracker
            if not is_workflow_active(self.workflow_id):
                self.logger.info(f"SKIPPING EVENT - Workflow {self.workflow_id} is not active")
                return
            
            # Update workflow activity
            update_workflow_activity(self.workflow_id)
            
            # Get task name consistently with started event
            task_name = self._extract_task_name(source)
            step_id = self._get_step_id("task", task_name)
            
            # Only process if we have started tracking this step
            if step_id not in self.start_times:
                self.logger.info(f"SKIPPING TASK FAILED EVENT - No active tracking for step: {step_id}")
                return
            
            # Get task name consistently with started event
            task_name = self._extract_task_name(source)
            
            step_id = self._get_step_id("task", task_name)
            duration = self._end_tracking(step_id)
            
            if step_id in self.execution_data:
                self.execution_data[step_id].update({
                    "end_time": datetime.now(),
                    "duration": duration,
                    "status": "failed",
                    "error": str(event.error),
                    "error_type": type(event.error).__name__
                })
            
            # Track in Prometheus only if we have a valid duration (not 0.0 from missing start time)
            if duration > 0:
                self.logger.info(f"TRACKING TASK EXECUTION ERROR: {task_name}, duration: {duration}, success: False")
                metrics.track_task_execution(task_name, duration, False)
            else:
                self.logger.warning(f"SKIPPING TASK EXECUTION ERROR TRACKING: {task_name}, duration: {duration} (invalid)")
            
            self._log_error(step_id, event.error,
                           task_name=task_name,
                           duration=duration) 