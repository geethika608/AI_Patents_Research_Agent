"""
Main monitoring event listener that combines all individual listeners.
"""

from typing import Dict, Any
from crewai.utilities.events.base_event_listener import BaseEventListener

from .crew_listener import CrewListener
from .agent_listener import AgentListener
from .task_listener import TaskListener

class MonitoringEventListener(BaseEventListener):
    """
    Main event listener that combines crew, agent, and task listeners.
    Provides a unified interface for monitoring all CrewAI events.
    """
    
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.listener_id = f"listener_{workflow_id}_{id(self)}"  # Unique identifier
        self.is_active = True  # Track if listener is still active
        
        # Initialize individual listeners
        self.crew_listener = CrewListener(workflow_id)
        self.agent_listener = AgentListener(workflow_id)
        self.task_listener = TaskListener(workflow_id)
        
        # Call parent constructor after initializing listeners
        super().__init__()
        
        print(f"CREATED MONITORING EVENT LISTENER: {self.listener_id} for workflow: {workflow_id}")
    
    def cleanup(self):
        """Clean up the event listener and mark as inactive."""
        self.is_active = False
        print(f"CLEANED UP MONITORING EVENT LISTENER: {self.listener_id} for workflow: {self.workflow_id}")
        
        # Clear any remaining tracking data
        self.crew_listener.start_times.clear()
        self.agent_listener.start_times.clear()
        self.task_listener.start_times.clear()
        
        self.crew_listener.execution_data.clear()
        self.agent_listener.execution_data.clear()
        self.task_listener.execution_data.clear()
    
    def setup_listeners(self, crewai_event_bus):
        """Setup all event handlers by delegating to individual listeners."""
        
        # Setup each listener's handlers
        self.crew_listener.setup_listeners(crewai_event_bus)
        self.agent_listener.setup_listeners(crewai_event_bus)
        self.task_listener.setup_listeners(crewai_event_bus)
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of all executions for this workflow."""
        
        crew_data = self.crew_listener.get_execution_data()
        agent_data = self.agent_listener.get_execution_data()
        task_data = self.task_listener.get_execution_data()
        
        # Calculate summary statistics
        total_agent_executions = len(agent_data)
        total_task_executions = len(task_data)
        successful_agent_executions = sum(1 for exec_info in agent_data.values() 
                                        if exec_info.get("status") == "completed")
        successful_task_executions = sum(1 for exec_info in task_data.values() 
                                       if exec_info.get("status") == "completed")
        failed_agent_executions = sum(1 for exec_info in agent_data.values() 
                                    if exec_info.get("status") == "failed")
        failed_task_executions = sum(1 for exec_info in task_data.values() 
                                   if exec_info.get("status") == "failed")
        
        return {
            "workflow_id": self.workflow_id,
            "crew_executions": crew_data,
            "agent_executions": agent_data,
            "task_executions": task_data,
            "summary": {
                "total_agent_executions": total_agent_executions,
                "total_task_executions": total_task_executions,
                "successful_agent_executions": successful_agent_executions,
                "successful_task_executions": successful_task_executions,
                "failed_agent_executions": failed_agent_executions,
                "failed_task_executions": failed_task_executions,
                "agent_success_rate": successful_agent_executions / total_agent_executions if total_agent_executions > 0 else 0,
                "task_success_rate": successful_task_executions / total_task_executions if total_task_executions > 0 else 0
            }
        } 