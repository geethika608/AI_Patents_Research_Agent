"""
Production-grade error handling and circuit breaker patterns for the Patent Research AI Agent.
"""

import time
import functools
import threading
from typing import Dict, Any, Optional, Callable, Type, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import traceback

from .logger import setup_logger

logger = setup_logger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, requests fail fast
    HALF_OPEN = "half_open"  # Testing if service is recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5  # Number of failures before opening circuit
    recovery_timeout: int = 60  # Seconds to wait before trying again
    expected_exception: Type[Exception] = Exception
    monitor_interval: int = 10  # Seconds between health checks


class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance."""
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        self.lock = threading.Lock()
        self.logger = logger
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._set_state(CircuitState.HALF_OPEN)
            else:
                raise CircuitBreakerOpenError(f"Circuit breaker '{self.name}' is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.config.expected_exception as e:
            self._on_failure(e)
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if not self.last_failure_time:
            return False
        
        return (datetime.now() - self.last_failure_time).total_seconds() >= self.config.recovery_timeout
    
    def _on_success(self):
        """Handle successful execution."""
        with self.lock:
            self.failure_count = 0
            self.last_success_time = datetime.now()
            
            if self.state == CircuitState.HALF_OPEN:
                self._set_state(CircuitState.CLOSED)
                self.logger.info(f"Circuit breaker '{self.name}' reset to CLOSED")
    
    def _on_failure(self, exception: Exception):
        """Handle failed execution."""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            self.logger.warning(f"Circuit breaker '{self.name}' failure",
                              failure_count=self.failure_count,
                              threshold=self.config.failure_threshold,
                              error=str(exception))
            
            if self.failure_count >= self.config.failure_threshold:
                self._set_state(CircuitState.OPEN)
    
    def _set_state(self, state: CircuitState):
        """Set circuit breaker state."""
        self.state = state
        self.logger.info(f"Circuit breaker '{self.name}' state changed to {state.value}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.config.failure_threshold,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "last_success_time": self.last_success_time.isoformat() if self.last_success_time else None,
            "recovery_timeout": self.config.recovery_timeout
        }


class RetryConfig:
    """Configuration for retry logic."""
    
    def __init__(self, 
                 max_attempts: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exponential_backoff: bool = True,
                 retry_exceptions: tuple = (Exception,)):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_backoff = exponential_backoff
        self.retry_exceptions = retry_exceptions


def retry(config: RetryConfig):
    """Retry decorator with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                    
                except config.retry_exceptions as e:
                    last_exception = e
                    
                    if attempt == config.max_attempts - 1:
                        logger.error(f"Function {func.__name__} failed after {config.max_attempts} attempts",
                                   error=str(e),
                                   attempts=attempt + 1)
                        raise
                    
                    # Calculate delay
                    if config.exponential_backoff:
                        delay = min(config.base_delay * (2 ** attempt), config.max_delay)
                    else:
                        delay = config.base_delay
                    
                    logger.warning(f"Function {func.__name__} failed, retrying in {delay}s",
                                 attempt=attempt + 1,
                                 max_attempts=config.max_attempts,
                                 error=str(e))
                    
                    time.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator


class ErrorHandler:
    """Centralized error handling and recovery."""
    
    def __init__(self):
        self.logger = logger
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.error_stats: Dict[str, int] = {}
        self.lock = threading.Lock()
    
    def add_circuit_breaker(self, name: str, config: CircuitBreakerConfig):
        """Add a circuit breaker."""
        self.circuit_breakers[name] = CircuitBreaker(name, config)
    
    def get_circuit_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Get a circuit breaker by name."""
        return self.circuit_breakers.get(name)
    
    def handle_error(self, error: Exception, context: str, workflow_id: Optional[str] = None):
        """Handle and log errors with context."""
        error_type = type(error).__name__
        
        with self.lock:
            self.error_stats[error_type] = self.error_stats.get(error_type, 0) + 1
        
        self.logger.error(f"Error in {context}",
                         error_type=error_type,
                         error_message=str(error),
                         workflow_id=workflow_id,
                         traceback=traceback.format_exc())
    
    def safe_execute(self, func: Callable, *args, 
                    circuit_breaker_name: Optional[str] = None,
                    retry_config: Optional[RetryConfig] = None,
                    context: str = "unknown",
                    workflow_id: Optional[str] = None,
                    **kwargs):
        """Safely execute a function with error handling."""
        try:
            # Apply retry if configured
            if retry_config:
                func = retry(retry_config)(func)
            
            # Apply circuit breaker if configured
            if circuit_breaker_name and circuit_breaker_name in self.circuit_breakers:
                circuit_breaker = self.circuit_breakers[circuit_breaker_name]
                return circuit_breaker.call(func, *args, **kwargs)
            
            # Execute function
            return func(*args, **kwargs)
            
        except Exception as e:
            self.handle_error(e, context, workflow_id)
            raise
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        with self.lock:
            return {
                "error_counts": dict(self.error_stats),
                "circuit_breakers": {
                    name: cb.get_status() 
                    for name, cb in self.circuit_breakers.items()
                }
            }


class AgentErrorHandler:
    """Specialized error handling for agent operations."""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.logger = logger
        
        # Configure circuit breakers for different agent types
        self._setup_circuit_breakers()
    
    def _setup_circuit_breakers(self):
        """Setup circuit breakers for different agent operations."""
        # OpenAI API circuit breaker
        openai_config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=30,
            expected_exception=(Exception,)
        )
        self.error_handler.add_circuit_breaker("openai_api", openai_config)
        
        # Serper API circuit breaker
        serper_config = CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=(Exception,)
        )
        self.error_handler.add_circuit_breaker("serper_api", serper_config)
        
        # Memory operations circuit breaker
        memory_config = CircuitBreakerConfig(
            failure_threshold=10,
            recovery_timeout=10,
            expected_exception=(Exception,)
        )
        self.error_handler.add_circuit_breaker("memory_ops", memory_config)
    
    def execute_agent_safely(self, agent_func: Callable, agent_name: str, 
                           workflow_id: str, *args, **kwargs):
        """Execute agent function with comprehensive error handling."""
        retry_config = RetryConfig(
            max_attempts=2,
            base_delay=2.0,
            exponential_backoff=True,
            retry_exceptions=(Exception,)
        )
        
        return self.error_handler.safe_execute(
            agent_func,
            *args,
            circuit_breaker_name="openai_api",
            retry_config=retry_config,
            context=f"agent_{agent_name}",
            workflow_id=workflow_id,
            **kwargs
        )
    
    def execute_search_safely(self, search_func: Callable, workflow_id: str, *args, **kwargs):
        """Execute search function with error handling."""
        retry_config = RetryConfig(
            max_attempts=3,
            base_delay=1.0,
            exponential_backoff=True,
            retry_exceptions=(Exception,)
        )
        
        return self.error_handler.safe_execute(
            search_func,
            *args,
            circuit_breaker_name="serper_api",
            retry_config=retry_config,
            context="patent_search",
            workflow_id=workflow_id,
            **kwargs
        )
    
    def execute_memory_safely(self, memory_func: Callable, workflow_id: str, *args, **kwargs):
        """Execute memory operation with error handling."""
        retry_config = RetryConfig(
            max_attempts=2,
            base_delay=0.5,
            exponential_backoff=False,
            retry_exceptions=(Exception,)
        )
        
        return self.error_handler.safe_execute(
            memory_func,
            *args,
            circuit_breaker_name="memory_ops",
            retry_config=retry_config,
            context="memory_operation",
            workflow_id=workflow_id,
            **kwargs
        )


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass


class AgentExecutionError(Exception):
    """Exception raised when agent execution fails."""
    pass


class TaskExecutionError(Exception):
    """Exception raised when task execution fails."""
    pass


class WorkflowExecutionError(Exception):
    """Exception raised when workflow execution fails."""
    pass


class TaskErrorHandler:
    """Specialized error handling for task operations."""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.logger = logger
        
        # Configure circuit breakers for task operations
        self._setup_circuit_breakers()
    
    def _setup_circuit_breakers(self):
        """Setup circuit breakers for different task operations."""
        # Task execution circuit breaker
        task_config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=30,
            expected_exception=(Exception,)
        )
        self.error_handler.add_circuit_breaker("task_execution", task_config)
        
        # Data processing circuit breaker
        processing_config = CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=(Exception,)
        )
        self.error_handler.add_circuit_breaker("data_processing", processing_config)
    
    def execute_task_safely(self, task_func: Callable, task_name: str, 
                           workflow_id: str, *args, **kwargs):
        """Execute task function with comprehensive error handling."""
        retry_config = RetryConfig(
            max_attempts=2,
            base_delay=2.0,
            exponential_backoff=True,
            retry_exceptions=(Exception,)
        )
        
        return self.error_handler.safe_execute(
            task_func,
            *args,
            circuit_breaker_name="task_execution",
            retry_config=retry_config,
            context=f"task_{task_name}",
            workflow_id=workflow_id,
            **kwargs
        )
    
    def process_data_safely(self, process_func: Callable, workflow_id: str, *args, **kwargs):
        """Execute data processing function with error handling."""
        retry_config = RetryConfig(
            max_attempts=3,
            base_delay=1.0,
            exponential_backoff=True,
            retry_exceptions=(Exception,)
        )
        
        return self.error_handler.safe_execute(
            process_func,
            *args,
            circuit_breaker_name="data_processing",
            retry_config=retry_config,
            context="data_processing",
            workflow_id=workflow_id,
            **kwargs
        )


class WorkflowErrorHandler:
    """Specialized error handling for workflow operations."""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.logger = logger
        
        # Configure circuit breakers for workflow operations
        self._setup_circuit_breakers()
    
    def _setup_circuit_breakers(self):
        """Setup circuit breakers for different workflow operations."""
        # Workflow execution circuit breaker
        workflow_config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=60,
            expected_exception=(Exception,)
        )
        self.error_handler.add_circuit_breaker("workflow_execution", workflow_config)
        
        # Crew coordination circuit breaker
        crew_config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=30,
            expected_exception=(Exception,)
        )
        self.error_handler.add_circuit_breaker("crew_coordination", crew_config)
    
    def execute_workflow_safely(self, workflow_func: Callable, workflow_name: str, 
                               workflow_id: str, *args, **kwargs):
        """Execute workflow function with comprehensive error handling."""
        retry_config = RetryConfig(
            max_attempts=1,  # Workflows typically shouldn't be retried
            base_delay=5.0,
            exponential_backoff=False,
            retry_exceptions=(Exception,)
        )
        
        return self.error_handler.safe_execute(
            workflow_func,
            *args,
            circuit_breaker_name="workflow_execution",
            retry_config=retry_config,
            context=f"workflow_{workflow_name}",
            workflow_id=workflow_id,
            **kwargs
        )
    
    def coordinate_crew_safely(self, crew_func: Callable, workflow_id: str, *args, **kwargs):
        """Execute crew coordination function with error handling."""
        retry_config = RetryConfig(
            max_attempts=2,
            base_delay=3.0,
            exponential_backoff=True,
            retry_exceptions=(Exception,)
        )
        
        return self.error_handler.safe_execute(
            crew_func,
            *args,
            circuit_breaker_name="crew_coordination",
            retry_config=retry_config,
            context="crew_coordination",
            workflow_id=workflow_id,
            **kwargs
        )


# Global error handler instances
error_handler = AgentErrorHandler()
task_error_handler = TaskErrorHandler()
workflow_error_handler = WorkflowErrorHandler() 