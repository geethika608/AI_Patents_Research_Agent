"""
Crew-level event listener for monitoring crew execution.
"""

from datetime import datetime
from crewai.utilities.events import (
    CrewKickoffStartedEvent,
    CrewKickoffCompletedEvent,
    CrewKickoffFailedEvent,
)

from .base_listener import BaseMonitoringListener
from patent_researcher_agent.utils.prometheus_metrics import metrics

from patent_researcher_agent.utils.workflow_tracker import is_workflow_active, update_workflow_activity

class CrewListener(BaseMonitoringListener):
    """
    Listener for crew-level events (start, complete, fail).
    """
    
    def setup_listeners(self, crewai_event_bus):
        """Setup crew event handlers."""
        
        @crewai_event_bus.on(CrewKickoffStartedEvent)
        def on_crew_kickoff_started(source, event: CrewKickoffStartedEvent):
            # Check if listener is still active
            if not hasattr(self, 'is_active') or not self.is_active:
                return
            
            # Check if this workflow is still active in the global tracker
            if not is_workflow_active(self.workflow_id):
                self.logger.info(f"SKIPPING EVENT - Workflow {self.workflow_id} is not active")
                return
            
            # Update workflow activity
            update_workflow_activity(self.workflow_id)
            
            # Get crew info from source
            crew_name = getattr(source, 'name', 'unknown_crew')
            num_agents = len(getattr(source, 'agents', []))
            num_tasks = len(getattr(source, 'tasks', []))
            
            step_id = self._get_step_id("crew", crew_name)
            self.logger.info(f"Crew execution started: {crew_name}, step_id: {step_id}")
            self._start_tracking(step_id)
            
            self.execution_data[step_id] = {
                "crew_name": crew_name,
                "num_agents": num_agents,
                "num_tasks": num_tasks,
                "start_time": datetime.now(),
                "status": "started"
            }
            
            self._log_execution(step_id, "started",
                              crew_name=crew_name,
                              num_agents=num_agents,
                              num_tasks=num_tasks)

        @crewai_event_bus.on(CrewKickoffCompletedEvent)
        def on_crew_kickoff_completed(source, event: CrewKickoffCompletedEvent):
            # Check if listener is still active
            if not hasattr(self, 'is_active') or not self.is_active:
                return
            
            # Check if this workflow is still active in the global tracker
            if not is_workflow_active(self.workflow_id):
                self.logger.info(f"SKIPPING EVENT - Workflow {self.workflow_id} is not active")
                return
            
            # Update workflow activity
            update_workflow_activity(self.workflow_id)
            
            crew_name = getattr(source, 'name', 'unknown_crew')
            step_id = self._get_step_id("crew", crew_name)
            self.logger.info(f"Crew execution completed: {crew_name}, step_id: {step_id}")
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
                self.logger.info(f"TRACKING WORKFLOW EXECUTION: {self.workflow_id}, duration: {duration}, success: True")
                metrics.track_workflow(self.workflow_id, duration, True)
            else:
                self.logger.warning(f"SKIPPING WORKFLOW EXECUTION TRACKING: {self.workflow_id}, duration: {duration} (invalid)")
            
            self._log_execution(step_id, "completed",
                              crew_name=crew_name,
                              duration=duration,
                              result_type=type(event.output).__name__,
                              result_length=len(str(event.output)) if event.output else 0)

        @crewai_event_bus.on(CrewKickoffFailedEvent)
        def on_crew_kickoff_failed(source, event: CrewKickoffFailedEvent):
            # Check if listener is still active
            if not hasattr(self, 'is_active') or not self.is_active:
                return
            
            # Check if this workflow is still active in the global tracker
            if not is_workflow_active(self.workflow_id):
                self.logger.info(f"SKIPPING EVENT - Workflow {self.workflow_id} is not active")
                return
            
            # Update workflow activity
            update_workflow_activity(self.workflow_id)
            
            crew_name = getattr(source, 'name', 'unknown_crew')
            step_id = self._get_step_id("crew", crew_name)
            self.logger.info(f"Crew execution failed: {crew_name}, step_id: {step_id}")
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
                self.logger.info(f"TRACKING WORKFLOW EXECUTION ERROR: {self.workflow_id}, duration: {duration}, success: False")
                metrics.track_workflow(self.workflow_id, duration, False)
            else:
                self.logger.warning(f"SKIPPING WORKFLOW EXECUTION ERROR TRACKING: {self.workflow_id}, duration: {duration} (invalid)")
            
            self._log_error(step_id, event.error,
                           crew_name=crew_name,
                           duration=duration) 