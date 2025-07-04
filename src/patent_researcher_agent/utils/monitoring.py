"""
Production-grade monitoring and observability for the Patent Research AI Agent.
"""

import time
import functools
import threading
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
import traceback

import mlflow
from .logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class AgentMetrics:
    """Metrics for individual agent performance."""
    agent_name: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_duration: float = 0.0
    avg_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    last_execution: Optional[datetime] = None
    error_count: int = 0
    token_usage: Dict[str, int] = field(default_factory=dict)
    
    def update(self, duration: float, success: bool, tokens: Optional[Dict[str, int]] = None):
        """Update metrics with execution results."""
        self.total_executions += 1
        self.total_duration += duration
        self.avg_duration = self.total_duration / self.total_executions
        self.min_duration = min(self.min_duration, duration)
        self.max_duration = max(self.max_duration, duration)
        self.last_execution = datetime.now()
        
        if success:
            self.successful_executions += 1
        else:
            self.failed_executions += 1
            self.error_count += 1
        
        if tokens:
            for key, value in tokens.items():
                self.token_usage[key] = self.token_usage.get(key, 0) + value


@dataclass
class TaskMetrics:
    """Metrics for task execution."""
    task_name: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_duration: float = 0.0
    avg_duration: float = 0.0
    dependencies: list = field(default_factory=list)
    last_execution: Optional[datetime] = None
    
    def update(self, duration: float, success: bool):
        """Update task metrics."""
        self.total_executions += 1
        self.total_duration += duration
        self.avg_duration = self.total_duration / self.total_executions
        self.last_execution = datetime.now()
        
        if success:
            self.successful_executions += 1
        else:
            self.failed_executions += 1


@dataclass
class WorkflowMetrics:
    """End-to-end workflow metrics."""
    workflow_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration: Optional[float] = None
    agent_metrics: Dict[str, AgentMetrics] = field(default_factory=dict)
    task_metrics: Dict[str, TaskMetrics] = field(default_factory=dict)
    status: str = "running"  # running, completed, failed
    error_message: Optional[str] = None
    user_input: Optional[str] = None
    output_quality_score: Optional[float] = None
    
    def complete(self, success: bool, error_message: Optional[str] = None):
        """Mark workflow as completed."""
        self.end_time = datetime.now()
        self.total_duration = (self.end_time - self.start_time).total_seconds()
        self.status = "completed" if success else "failed"
        self.error_message = error_message


class PerformanceMonitor:
    """Production-grade performance monitoring."""
    
    def __init__(self):
        self.logger = logger
        self.agent_metrics: Dict[str, AgentMetrics] = defaultdict(lambda: AgentMetrics(""))
        self.task_metrics: Dict[str, TaskMetrics] = defaultdict(lambda: TaskMetrics(""))
        self.workflow_metrics: Dict[str, WorkflowMetrics] = {}
        self.recent_requests: deque = deque(maxlen=1000)
        self.lock = threading.Lock()
        
        # Performance thresholds
        self.slow_threshold = 15.0  # seconds
        self.error_threshold = 0.1  # 10% error rate
        self.token_limit = 100000  # tokens per request
        
        # Initialize MLflow
        self._setup_mlflow()
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize names for MLflow compatibility."""
        # Replace invalid characters with underscores
        import re
        # Replace spaces, newlines, and other invalid chars with underscores
        sanitized = re.sub(r'[^\w\-_.: /]', '_', name)
        # Replace multiple underscores with single underscore
        sanitized = re.sub(r'_+', '_', sanitized)
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        # Limit length to avoid MLflow limits
        return sanitized[:100] if len(sanitized) > 100 else sanitized
    
    def _setup_mlflow(self):
        """Setup MLflow for experiment tracking."""
        try:
            mlflow.set_experiment("PatentResearchAgent")
            self.logger.info("MLflow experiment tracking initialized")
        except Exception as e:
            self.logger.warning(f"MLflow setup failed: {e}")
    
    def start_workflow(self, workflow_id: str, user_input: str) -> str:
        """Start monitoring a new workflow."""
        with self.lock:
            workflow = WorkflowMetrics(
                workflow_id=workflow_id,
                start_time=datetime.now(),
                user_input=user_input
            )
            self.workflow_metrics[workflow_id] = workflow
            
            # Log workflow start
            self.logger.info(f"Workflow started - workflow_id={workflow_id}, user_input_length={len(user_input)}")
            
            # Track in MLflow
            with mlflow.start_run(run_name=self._sanitize_name(f"workflow_{workflow_id}")):
                mlflow.log_param("workflow_id", workflow_id)
                mlflow.log_param("user_input_length", len(user_input))
                mlflow.log_param("start_time", workflow.start_time.isoformat())
            
            return workflow_id
    
    def end_workflow(self, workflow_id: str, success: bool, 
                    error_message: Optional[str] = None,
                    output_quality_score: Optional[float] = None):
        """End workflow monitoring."""
        with self.lock:
            if workflow_id in self.workflow_metrics:
                workflow = self.workflow_metrics[workflow_id]
                workflow.complete(success, error_message)
                workflow.output_quality_score = output_quality_score
                
                # Log workflow completion
                self.logger.info(f"Workflow completed - workflow_id={workflow_id}, success={success}, duration={workflow.total_duration}, error_message={error_message}")
                
                # Track in MLflow
                with mlflow.start_run(run_name=self._sanitize_name(f"workflow_{workflow_id}")):
                    mlflow.log_metric("workflow_duration", workflow.total_duration)
                    mlflow.log_metric("workflow_success", 1 if success else 0)
                    if output_quality_score:
                        mlflow.log_metric("output_quality", output_quality_score)
                    mlflow.log_param("end_time", workflow.end_time.isoformat())
    
    def track_agent_execution(self, agent_name: str, workflow_id: str, duration: float, success: bool, tokens: Optional[Dict[str, int]] = None):
        """Track agent execution metrics."""
        with self.lock:
            if agent_name not in self.agent_metrics:
                self.agent_metrics[agent_name] = AgentMetrics(agent_name)
            
            self.agent_metrics[agent_name].update(duration, success, tokens)
            
            # Check for performance issues
            if duration > self.slow_threshold:
                self.logger.warning(f"Slow agent execution: {agent_name} - duration={duration}, threshold={self.slow_threshold}")
            
            # Track in MLflow
            with mlflow.start_run(run_name=self._sanitize_name(f"agent_{agent_name}_{workflow_id}")):
                mlflow.log_metric(self._sanitize_name(f"{agent_name}_duration"), duration)
                mlflow.log_metric(self._sanitize_name(f"{agent_name}_success"), 1 if success else 0)
                if tokens:
                    for token_type, count in tokens.items():
                        mlflow.log_metric(self._sanitize_name(f"{agent_name}_{token_type}_tokens"), count)
    
    def track_agent_execution_decorator(self, agent_name: str, workflow_id: str):
        """Decorator to track agent execution."""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                success = False
                tokens = None
                
                try:
                    # Execute agent
                    result = func(*args, **kwargs)
                    success = True
                    
                    # Extract token usage if available
                    if hasattr(result, 'token_usage'):
                        tokens = result.token_usage
                    
                    return result
                    
                except Exception as e:
                    self.logger.error(f"Agent execution failed: {agent_name} - workflow_id={workflow_id}, error={str(e)}, traceback={traceback.format_exc()}")
                    raise
                    
                finally:
                    duration = time.time() - start_time
                    self.track_agent_execution(agent_name, workflow_id, duration, success, tokens)
            
            return wrapper
        return decorator
    
    def track_task_execution(self, task_name: str, workflow_id: str, duration: float, success: bool):
        """Track task execution metrics."""
        with self.lock:
            if task_name not in self.task_metrics:
                self.task_metrics[task_name] = TaskMetrics(task_name)
            
            self.task_metrics[task_name].update(duration, success)
            
            # Track in MLflow
            with mlflow.start_run(run_name=self._sanitize_name(f"task_{task_name}_{workflow_id}")):
                mlflow.log_metric(self._sanitize_name(f"{task_name}_duration"), duration)
                mlflow.log_metric(self._sanitize_name(f"{task_name}_success"), 1 if success else 0)
    
    def track_task_execution_decorator(self, task_name: str, workflow_id: str):
        """Decorator to track task execution."""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                success = False
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                    return result
                    
                except Exception as e:
                    self.logger.error(f"Task execution failed: {task_name} - workflow_id={workflow_id}, error={str(e)}")
                    raise
                    
                finally:
                    duration = time.time() - start_time
                    self.track_task_execution(task_name, workflow_id, duration, success)
            
            return wrapper
        return decorator
    
    def get_agent_metrics(self, agent_name: str) -> Optional[AgentMetrics]:
        """Get metrics for a specific agent."""
        return self.agent_metrics.get(agent_name)
    
    def get_task_metrics(self, task_name: str) -> Optional[TaskMetrics]:
        """Get metrics for a specific task."""
        return self.task_metrics.get(task_name)
    
    def get_workflow_metrics(self, workflow_id: str) -> Optional[WorkflowMetrics]:
        """Get metrics for a specific workflow."""
        return self.workflow_metrics.get(workflow_id)
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics."""
        with self.lock:
            total_agents = len(self.agent_metrics)
            total_tasks = len(self.task_metrics)
            total_workflows = len(self.workflow_metrics)
            
            # Calculate error rates
            agent_error_rate = 0.0
            if total_agents > 0:
                total_agent_executions = sum(m.total_executions for m in self.agent_metrics.values())
                total_agent_errors = sum(m.failed_executions for m in self.agent_metrics.values())
                if total_agent_executions > 0:
                    agent_error_rate = total_agent_errors / total_agent_executions
            
            # Calculate average response times
            avg_agent_duration = 0.0
            if total_agents > 0:
                avg_agent_duration = sum(m.avg_duration for m in self.agent_metrics.values()) / total_agents
            
            avg_task_duration = 0.0
            if total_tasks > 0:
                avg_task_duration = sum(m.avg_duration for m in self.task_metrics.values()) / total_tasks
            
            return {
                "status": "healthy" if agent_error_rate < self.error_threshold else "degraded",
                "timestamp": datetime.now().isoformat(),
                "metrics": {
                    "total_agents": total_agents,
                    "total_tasks": total_tasks,
                    "total_workflows": total_workflows,
                    "agent_error_rate": agent_error_rate,
                    "avg_agent_duration": avg_agent_duration,
                    "avg_task_duration": avg_task_duration,
                    "recent_requests": len(self.recent_requests)
                },
                "thresholds": {
                    "error_threshold": self.error_threshold,
                    "slow_threshold": self.slow_threshold,
                    "token_limit": self.token_limit
                }
            }
    
    def export_metrics(self) -> Dict[str, Any]:
        """Export all metrics for external monitoring systems."""
        with self.lock:
            return {
                "timestamp": datetime.now().isoformat(),
                "agent_metrics": {
                    name: {
                        "total_executions": metrics.total_executions,
                        "successful_executions": metrics.successful_executions,
                        "failed_executions": metrics.failed_executions,
                        "avg_duration": metrics.avg_duration,
                        "min_duration": metrics.min_duration,
                        "max_duration": metrics.max_duration,
                        "error_count": metrics.error_count,
                        "token_usage": metrics.token_usage,
                        "last_execution": metrics.last_execution.isoformat() if metrics.last_execution else None
                    }
                    for name, metrics in self.agent_metrics.items()
                },
                "task_metrics": {
                    name: {
                        "total_executions": metrics.total_executions,
                        "successful_executions": metrics.successful_executions,
                        "failed_executions": metrics.failed_executions,
                        "avg_duration": metrics.avg_duration,
                        "last_execution": metrics.last_execution.isoformat() if metrics.last_execution else None
                    }
                    for name, metrics in self.task_metrics.items()
                },
                "workflow_metrics": {
                    workflow_id: {
                        "status": workflow.status,
                        "total_duration": workflow.total_duration,
                        "start_time": workflow.start_time.isoformat(),
                        "end_time": workflow.end_time.isoformat() if workflow.end_time else None,
                        "error_message": workflow.error_message,
                        "output_quality_score": workflow.output_quality_score
                    }
                    for workflow_id, workflow in self.workflow_metrics.items()
                }
            }


# Global monitor instance
monitor = PerformanceMonitor() 