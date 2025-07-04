"""
Agent-level event listener for monitoring agent execution.
"""

import time
from datetime import datetime
from crewai.utilities.events import (
    AgentExecutionStartedEvent,
    AgentExecutionCompletedEvent,
    AgentExecutionErrorEvent,
)

from .base_listener import BaseMonitoringListener
from patent_researcher_agent.utils.prometheus_metrics import metrics
from patent_researcher_agent.utils.workflow_tracker import is_workflow_active, update_workflow_activity

class AgentListener(BaseMonitoringListener):
    """
    Listener for agent-level events (start, complete, error).
    """
    
    def _extract_agent_name(self, source, event) -> str:
        """Extract agent name from source or event."""
        agent_name = 'unknown_agent'
        
        # Try to get from source object (this should be the agent instance)
        if hasattr(source, 'name') and source.name:
            agent_name = source.name
        elif hasattr(source, 'role') and source.role:
            # Extract agent type from role
            role = source.role.lower()
            if 'fetcher' in role or 'fetch' in role:
                agent_name = 'fetcher_agent'
            elif 'analyzer' in role or 'analyze' in role or 'trend' in role:
                agent_name = 'analyzer_agent'
            elif 'reporter' in role or 'report' in role or 'insights' in role:
                agent_name = 'reporter_agent'
            else:
                agent_name = source.role.split()[0].lower() + '_agent'
        elif hasattr(event, 'agent') and event.agent:
            if hasattr(event.agent, 'name') and event.agent.name:
                agent_name = event.agent.name
            elif hasattr(event.agent, 'role') and event.agent.role:
                role = event.agent.role.lower()
                if 'fetcher' in role or 'fetch' in role:
                    agent_name = 'fetcher_agent'
                elif 'analyzer' in role or 'analyze' in role or 'trend' in role:
                    agent_name = 'analyzer_agent'
                elif 'reporter' in role or 'report' in role or 'insights' in role:
                    agent_name = 'reporter_agent'
                else:
                    agent_name = event.agent.role.split()[0].lower() + '_agent'
        
        # Clean up agent name for metrics
        return agent_name.replace(' ', '_').lower()
    
    def setup_listeners(self, crewai_event_bus):
        """Setup agent event handlers."""
        
        @crewai_event_bus.on(AgentExecutionStartedEvent)
        def on_agent_execution_started(source, event: AgentExecutionStartedEvent):
            # Check if listener is still active
            if not hasattr(self, 'is_active') or not self.is_active:
                return
            
            # Check if this workflow is still active in the global tracker
            if not is_workflow_active(self.workflow_id):
                self.logger.info(f"SKIPPING EVENT - Workflow {self.workflow_id} is not active")
                return
            
            # Update workflow activity
            update_workflow_activity(self.workflow_id)
            
            # Add unique event identifier for debugging
            event_id = f"{id(event)}_{id(source)}_{time.time()}"
            self.logger.info(f"AGENT STARTED EVENT RECEIVED: {event_id}")
            
            # Get agent name first
            agent_name = self._extract_agent_name(source, event)
            step_id = self._get_step_id("agent", agent_name)
            
            # Check if we're already tracking this step (from another workflow)
            if step_id in self.start_times:
                self.logger.info(f"SKIPPING START EVENT - Already tracking step: {step_id}")
                return
            
            # Get agent info from source - try multiple ways to get the name
            agent_name = 'unknown_agent'
            agent_role = 'unknown_role'
            
            # Try to get from source object (this should be the agent instance)
            if hasattr(source, 'name') and source.name:
                agent_name = source.name
            elif hasattr(source, 'role') and source.role:
                # Extract agent type from role
                role = source.role.lower()
                if 'fetcher' in role or 'fetch' in role:
                    agent_name = 'fetcher_agent'
                elif 'analyzer' in role or 'analyze' in role or 'trend' in role:
                    agent_name = 'analyzer_agent'
                elif 'reporter' in role or 'report' in role or 'insights' in role:
                    agent_name = 'reporter_agent'
                else:
                    agent_name = source.role.split()[0].lower() + '_agent'
                agent_role = source.role
            elif hasattr(event, 'agent') and event.agent:
                if hasattr(event.agent, 'name') and event.agent.name:
                    agent_name = event.agent.name
                elif hasattr(event.agent, 'role') and event.agent.role:
                    role = event.agent.role.lower()
                    if 'fetcher' in role or 'fetch' in role:
                        agent_name = 'fetcher_agent'
                    elif 'analyzer' in role or 'analyze' in role or 'trend' in role:
                        agent_name = 'analyzer_agent'
                    elif 'reporter' in role or 'report' in role or 'insights' in role:
                        agent_name = 'reporter_agent'
                    else:
                        agent_name = event.agent.role.split()[0].lower() + '_agent'
                    agent_role = event.agent.role
            
            # Clean up agent name for metrics
            agent_name = agent_name.replace(' ', '_').lower()
            
            step_id = self._get_step_id("agent", agent_name)
            self.logger.info(f"Agent execution started: {agent_name}, step_id: {step_id}")
            self._start_tracking(step_id)
            
            self.execution_data[step_id] = {
                "agent_name": agent_name,
                "agent_role": agent_role,
                "start_time": datetime.now(),
                "status": "started"
            }
            
            self._log_execution(step_id, "started",
                              agent_name=agent_name,
                              agent_role=agent_role)

        @crewai_event_bus.on(AgentExecutionCompletedEvent)
        def on_agent_execution_completed(source, event: AgentExecutionCompletedEvent):
            # Check if listener is still active
            if not hasattr(self, 'is_active') or not self.is_active:
                return
            
            # Check if this workflow is still active in the global tracker
            if not is_workflow_active(self.workflow_id):
                self.logger.info(f"SKIPPING EVENT - Workflow {self.workflow_id} is not active")
                return
            
            # Update workflow activity
            update_workflow_activity(self.workflow_id)
            
            # Add unique event identifier for debugging
            event_id = f"{id(event)}_{id(source)}_{time.time()}"
            self.logger.info(f"AGENT COMPLETED EVENT RECEIVED: {event_id}")
            
            # Check if this event belongs to our workflow
            # We can't directly check workflow_id from the event, so we'll use a different approach
            # Only process events if we have active tracking for this agent
            agent_name = self._extract_agent_name(source, event)
            step_id = self._get_step_id("agent", agent_name)
            
            # Only process if we have started tracking this step
            if step_id not in self.start_times:
                self.logger.info(f"SKIPPING EVENT - No active tracking for step: {step_id}")
                return
            
            # Get agent name consistently with started event
            agent_name = 'unknown_agent'
            if hasattr(source, 'name') and source.name:
                agent_name = source.name
            elif hasattr(source, 'role') and source.role:
                # Extract agent type from role
                role = source.role.lower()
                if 'fetcher' in role or 'fetch' in role:
                    agent_name = 'fetcher_agent'
                elif 'analyzer' in role or 'analyze' in role or 'trend' in role:
                    agent_name = 'analyzer_agent'
                elif 'reporter' in role or 'report' in role or 'insights' in role:
                    agent_name = 'reporter_agent'
                else:
                    agent_name = source.role.split()[0].lower() + '_agent'
            elif hasattr(event, 'agent') and event.agent:
                if hasattr(event.agent, 'name') and event.agent.name:
                    agent_name = event.agent.name
                elif hasattr(event.agent, 'role') and event.agent.role:
                    role = event.agent.role.lower()
                    if 'fetcher' in role or 'fetch' in role:
                        agent_name = 'fetcher_agent'
                    elif 'analyzer' in role or 'analyze' in role or 'trend' in role:
                        agent_name = 'analyzer_agent'
                    elif 'reporter' in role or 'report' in role or 'insights' in role:
                        agent_name = 'reporter_agent'
                    else:
                        agent_name = event.agent.role.split()[0].lower() + '_agent'
            
            # Clean up agent name for metrics
            agent_name = agent_name.replace(' ', '_').lower()
            
            step_id = self._get_step_id("agent", agent_name)
            self.logger.info(f"Agent execution completed: {agent_name}, step_id: {step_id}")
            
            # Check if this step_id has already been processed
            if step_id in self.execution_data and self.execution_data[step_id].get("status") == "completed":
                self.logger.warning(f"SKIPPING ALREADY PROCESSED STEP: {step_id}")
                return
            
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
                self.logger.info(f"TRACKING AGENT EXECUTION: {agent_name}, duration: {duration}, success: True, step_id: {step_id}")
                metrics.track_agent_execution(agent_name, duration, True)
            else:
                self.logger.warning(f"SKIPPING AGENT EXECUTION TRACKING: {agent_name}, duration: {duration} (invalid), step_id: {step_id}")
            
            self._log_execution(step_id, "completed",
                              agent_name=agent_name,
                              duration=duration,
                              result_type=type(event.output).__name__,
                              result_length=len(str(event.output)) if event.output else 0)

        @crewai_event_bus.on(AgentExecutionErrorEvent)
        def on_agent_execution_error(source, event: AgentExecutionErrorEvent):
            # Check if listener is still active
            if not hasattr(self, 'is_active') or not self.is_active:
                return
            
            # Check if this workflow is still active in the global tracker
            if not is_workflow_active(self.workflow_id):
                self.logger.info(f"SKIPPING EVENT - Workflow {self.workflow_id} is not active")
                return
            
            # Update workflow activity
            update_workflow_activity(self.workflow_id)
            
            # Add unique event identifier for debugging
            event_id = f"{id(event)}_{id(source)}_{time.time()}"
            self.logger.info(f"AGENT ERROR EVENT RECEIVED: {event_id}")
            
            # Check if this event belongs to our workflow
            agent_name = self._extract_agent_name(source, event)
            step_id = self._get_step_id("agent", agent_name)
            
            # Only process if we have started tracking this step
            if step_id not in self.start_times:
                self.logger.info(f"SKIPPING ERROR EVENT - No active tracking for step: {step_id}")
                return
            
            # Get agent name consistently with started event
            agent_name = 'unknown_agent'
            if hasattr(source, 'name') and source.name:
                agent_name = source.name
            elif hasattr(source, 'role') and source.role:
                # Extract agent type from role
                role = source.role.lower()
                if 'fetcher' in role or 'fetch' in role:
                    agent_name = 'fetcher_agent'
                elif 'analyzer' in role or 'analyze' in role or 'trend' in role:
                    agent_name = 'analyzer_agent'
                elif 'reporter' in role or 'report' in role or 'insights' in role:
                    agent_name = 'reporter_agent'
                else:
                    agent_name = source.role.split()[0].lower() + '_agent'
            elif hasattr(event, 'agent') and event.agent:
                if hasattr(event.agent, 'name') and event.agent.name:
                    agent_name = event.agent.name
                elif hasattr(event.agent, 'role') and event.agent.role:
                    role = event.agent.role.lower()
                    if 'fetcher' in role or 'fetch' in role:
                        agent_name = 'fetcher_agent'
                    elif 'analyzer' in role or 'analyze' in role or 'trend' in role:
                        agent_name = 'analyzer_agent'
                    elif 'reporter' in role or 'report' in role or 'insights' in role:
                        agent_name = 'reporter_agent'
                    else:
                        agent_name = event.agent.role.split()[0].lower() + '_agent'
            
            # Clean up agent name for metrics
            agent_name = agent_name.replace(' ', '_').lower()
            
            step_id = self._get_step_id("agent", agent_name)
            self.logger.info(f"Agent execution error: {agent_name}, step_id: {step_id}")
            
            # Check if this step_id has already been processed
            if step_id in self.execution_data and self.execution_data[step_id].get("status") == "failed":
                self.logger.warning(f"SKIPPING ALREADY PROCESSED ERROR STEP: {step_id}")
                return
            
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
                self.logger.info(f"TRACKING AGENT EXECUTION ERROR: {agent_name}, duration: {duration}, error: {type(event.error).__name__}")
                metrics.track_agent_execution(agent_name, duration, False, type(event.error).__name__)
            else:
                self.logger.warning(f"SKIPPING AGENT EXECUTION ERROR TRACKING: {agent_name}, duration: {duration} (invalid)")
            
            self._log_error(step_id, event.error,
                           agent_name=agent_name,
                           duration=duration) 