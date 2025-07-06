"""
Prometheus metrics for Patent Research AI Agent.

This module provides comprehensive metrics collection for the Patent Research AI Agent,
including agent execution times, task performance, workflow success rates, and evaluation scores.
All metrics are exposed via Prometheus format and can be scraped by monitoring systems.
"""

import time
from typing import Dict, Any, Optional
from prometheus_client import (
    Counter, Gauge, Histogram, 
    start_http_server, generate_latest
)
from functools import wraps
from .metrics_persistence import MetricsPersistence

# =============================================================================
# PROMETHEUS METRIC DEFINITIONS
# =============================================================================

# Agent Performance Metrics
# Track execution time and count for each agent type
AGENT_EXECUTION_TIME = Histogram(
    'patent_agent_execution_duration_seconds',
    'Time spent executing agent tasks',
    ['agent_name', 'status']  # Labels: agent type and success/failure status
)

AGENT_EXECUTIONS_TOTAL = Counter(
    'patent_agent_executions_total',
    'Total number of agent executions',
    ['agent_name', 'status']  # Labels: agent type and success/failure status
)

AGENT_ERRORS_TOTAL = Counter(
    'patent_agent_errors_total',
    'Total number of agent errors',
    ['agent_name', 'error_type']  # Labels: agent type and specific error category
)

# Task Performance Metrics
# Track execution time and count for each task type
TASK_EXECUTION_TIME = Histogram(
    'patent_task_execution_duration_seconds',
    'Time spent executing tasks',
    ['task_name', 'status']  # Labels: task type and success/failure status
)

TASK_EXECUTIONS_TOTAL = Counter(
    'patent_task_executions_total',
    'Total number of task executions',
    ['task_name', 'status']  # Labels: task type and success/failure status
)

# Workflow Performance Metrics
# Track complete workflow execution and success rates
WORKFLOW_DURATION = Histogram(
    'patent_workflow_duration_seconds',
    'Time spent on complete workflows',
    ['workflow_id', 'status']  # Labels: unique workflow ID and success/failure status
)

WORKFLOW_EXECUTIONS_TOTAL = Counter(
    'patent_workflow_executions_total',
    'Total number of workflow executions',
    ['workflow_id', 'status']  # Labels: unique workflow ID and success/failure status
)

WORKFLOW_SUCCESS_RATE = Gauge(
    'patent_workflow_success_rate',
    'Success rate of workflows',
    ['workflow_id']  # Labels: unique workflow ID
)

# Evaluation Quality Metrics
# Track evaluation scores and performance (not persisted across restarts)
EVALUATION_SCORE = Histogram(
    'patent_evaluation_score',
    'Evaluation scores for workflow outputs',
    ['workflow_id', 'metric_name']  # Labels: workflow ID and evaluation metric type
)

EVALUATION_DURATION = Histogram(
    'patent_evaluation_duration_seconds',
    'Time spent on evaluations',
    ['workflow_id']  # Labels: unique workflow ID
)

OVERALL_EVALUATION_SCORE = Gauge(
    'patent_overall_evaluation_score',
    'Overall evaluation score for workflows',
    ['workflow_id']  # Labels: unique workflow ID
)

EVALUATION_COUNT = Counter(
    'patent_evaluations_total',
    'Total number of evaluations performed',
    ['metric_name']  # Labels: evaluation metric type
)

class PrometheusMetrics:
    """
    Prometheus metrics manager for Patent Research AI Agent.
    
    This class manages all Prometheus metrics collection, persistence, and restoration.
    It provides methods to track agent, task, and workflow performance metrics,
    and handles automatic saving/restoration of metrics across application restarts.
    """
    
    def __init__(self, metrics_port: int = 8000):
        """
        Initialize the Prometheus metrics manager.
        
        Args:
            metrics_port (int): Port number for the Prometheus metrics server (default: 8000)
        """
        self.metrics_port = metrics_port
        self.persistence = MetricsPersistence()  # Initialize metrics persistence
        self._restore_metrics()  # Restore metrics from previous session
        self._start_metrics_server()  # Start the metrics HTTP server
    
    def _start_metrics_server(self):
        """
        Start the Prometheus metrics HTTP server.
        
        This server exposes metrics in Prometheus format at /metrics endpoint,
        allowing monitoring systems to scrape the metrics.
        """
        try:
            start_http_server(self.metrics_port)
        except Exception as e:
            print(f"Failed to start metrics server: {e}")
    
    def _save_metrics(self):
        """
        Save all current Prometheus metrics to persistence file.
        
        This method:
        1. Generates current metrics in Prometheus text format
        2. Parses the metrics using regex patterns
        3. Filters out metrics that cannot be properly restored
        4. Saves the filtered metrics to JSON persistence file
        
        Evaluation metrics are excluded from persistence as they are session-specific.
        """
        try:
            from prometheus_client import generate_latest
            import re
            import json

            # Generate current metrics in Prometheus text format
            metrics_text = generate_latest().decode('utf-8')
            metrics_list = []
            
            # Regex patterns to parse Prometheus metric format
            # Format: metric_name{label1="value1",label2="value2"} metric_value
            metric_line_pattern = re.compile(r'^(?P<name>[a-zA-Z_:][a-zA-Z0-9_:]*)\{(?P<labels>[^}]*)\} (?P<value>[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)$', re.MULTILINE)
            label_pattern = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)="([^"]*)"')

            # Parse each metric line
            for match in metric_line_pattern.finditer(metrics_text):
                name = match.group('name')
                labels_str = match.group('labels')
                value = match.group('value')
                labels = {k: v for k, v in label_pattern.findall(labels_str)}
                
                # Filter metrics for persistence - only save what we can restore
                
                # Skip histogram bucket metrics (too many, not useful for restoration)
                if name.endswith('_bucket'):
                    continue
                
                # Skip evaluation metrics (session-specific)
                if (name.startswith('patent_evaluation') or 
                    name == 'patent_evaluations_total' or
                    name == 'patent_overall_evaluation_score'):
                    continue
                
                # Save histogram sum metrics (can be restored by simulating observations)
                if name.endswith('_sum'):
                    metrics_list.append({
                        "name": name,
                        "labels": labels,
                        "value": float(value) if '.' in value or 'e' in value.lower() else int(value)
                    })
                    continue
                
                # Save all other metrics (counters, gauges, histogram counts)
                metrics_list.append({
                    "name": name,
                    "labels": labels,
                    "value": float(value) if '.' in value or 'e' in value.lower() else int(value)
                })

            # Save to persistence file
            self.persistence.save_metrics(metrics_list)
        except Exception as e:
            print(f"Failed to save metrics: {e}")
            import traceback
            traceback.print_exc()

    def _restore_metrics(self):
        """
        Restore all Prometheus metrics from persistence file.
        
        This method:
        1. Checks if metrics should be restored (based on age)
        2. Loads saved metrics from persistence file
        3. For each metric, determines the appropriate restoration strategy:
           - Counters: Increment to match saved value
           - Gauges: Set to saved value
           - Histograms: Simulate observations to restore statistics
        4. Skips metrics that cannot be properly restored
        
        Evaluation metrics are skipped as they are session-specific.
        """
        # Check if metrics should be restored (not too old)
        if not self.persistence.should_restore_metrics():
            return
        
        # Load saved metrics from persistence file
        saved_metrics = self.persistence.load_metrics()
        if not saved_metrics:
            return
        
        try:
            restored_count = 0
            skipped_count = 0
            
            # Process each saved metric
            for metric in saved_metrics:
                name = metric.get("name")
                labels = metric.get("labels", {})
                value = metric.get("value")
                
                # Get current value from Prometheus text for comparison
                # This helps avoid double-counting if metrics were already restored
                from prometheus_client import generate_latest
                import re
                metrics_text = generate_latest().decode('utf-8')
                pattern = rf'{name}{{' + ','.join([f'{k}="{v}"' for k, v in labels.items()]) + r'}} ([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)'
                match = re.search(pattern, metrics_text)
                current_value = float(match.group(1)) if match else 0
                
                try:
                    # =============================================================================
                    # COUNTER METRICS RESTORATION
                    # =============================================================================
                    # Counters can only go up, so we increment them to match saved values
                    if name.endswith('_total') or name.endswith('_count'):
                        # Map metric names to their corresponding Prometheus counter objects
                        if name == 'patent_agent_executions_total':
                            counter = AGENT_EXECUTIONS_TOTAL.labels(**labels)
                        elif name == 'patent_task_executions_total':
                            counter = TASK_EXECUTIONS_TOTAL.labels(**labels)
                        elif name == 'patent_workflow_executions_total':
                            counter = WORKFLOW_EXECUTIONS_TOTAL.labels(**labels)
                        elif name == 'patent_agent_errors_total':
                            counter = AGENT_ERRORS_TOTAL.labels(**labels)
                        # Skip evaluation metrics (session-specific)
                        elif name.startswith('patent_evaluation'):
                            skipped_count += 1
                            continue
                        # Skip histogram count metrics (cannot be properly restored)
                        elif name.endswith('_count'):
                            skipped_count += 1
                            continue
                        else:
                            # Unknown counter metric
                            skipped_count += 1
                            continue
                        
                        # Increment counter to match saved value (avoid double-counting)
                        if value > current_value:
                            increment_amount = int(value) - int(current_value)
                            for _ in range(increment_amount):
                                counter.inc()
                            restored_count += 1
                    
                    # =============================================================================
                    # GAUGE METRICS RESTORATION
                    # =============================================================================
                    # Gauges can be set directly to any value
                    elif (name.endswith('_rate') or name.endswith('_usage_bytes') or 
                          name.endswith('_entries_total') or name.endswith('_remaining') or 
                          name.endswith('_reset_time') or name == 'patent_workflow_success_rate'):
                        if name == 'patent_workflow_success_rate':
                            gauge = WORKFLOW_SUCCESS_RATE.labels(**labels)
                            gauge.set(value)  # Set gauge to saved value
                            restored_count += 1
                        else:
                            # Unknown gauge metric
                            skipped_count += 1
                            continue
                    
                    # =============================================================================
                    # HISTOGRAM METRICS RESTORATION
                    # =============================================================================
                    # Histograms are restored by simulating observations
                    elif name == 'patent_workflow_duration_seconds':
                        # Simulate an observation with the saved value to restore histogram statistics
                        histogram = WORKFLOW_DURATION.labels(**labels)
                        histogram.observe(value)
                        restored_count += 1
                    
                    # =============================================================================
                    # HISTOGRAM SUM METRICS RESTORATION
                    # =============================================================================
                    # Histogram sums are restored by simulating observations with the sum value
                    elif name.endswith('_sum'):
                        # Skip evaluation metrics (session-specific)
                        if name.startswith('patent_evaluation'):
                            skipped_count += 1
                            continue
                        # Handle supported histogram sum metrics
                        elif name in ['patent_workflow_duration_seconds_sum', 
                                     'patent_agent_execution_duration_seconds_sum',
                                     'patent_task_execution_duration_seconds_sum']:
                            # Map sum metric names to their corresponding histogram objects
                            if name == 'patent_workflow_duration_seconds_sum':
                                workflow_id = labels.get('workflow_id', 'unknown')
                                status = labels.get('status', 'success')
                                histogram = WORKFLOW_DURATION.labels(workflow_id=workflow_id, status=status)
                            elif name == 'patent_agent_execution_duration_seconds_sum':
                                agent_name = labels.get('agent_name', 'unknown')
                                status = labels.get('status', 'success')
                                histogram = AGENT_EXECUTION_TIME.labels(agent_name=agent_name, status=status)
                            elif name == 'patent_task_execution_duration_seconds_sum':
                                task_name = labels.get('task_name', 'unknown')
                                status = labels.get('status', 'success')
                                histogram = TASK_EXECUTION_TIME.labels(task_name=task_name, status=status)
                            
                            # Simulate observation with saved sum value to restore histogram statistics
                            histogram.observe(value)
                            restored_count += 1
                        else:
                            # Unknown histogram sum metric
                            skipped_count += 1
                            continue
                    
                    # Skip histogram bucket metrics and other unknown metrics
                    else:
                        skipped_count += 1
                        continue
                        
                except Exception as e:
                    print(f"Failed to restore metric {name}: {e}")
                    skipped_count += 1
            
        except Exception as e:
            print(f"Failed to restore metrics: {e}")
            import traceback
            traceback.print_exc()
    
    def save_metrics_periodically(self, interval_seconds: int = 60):
        """
        Start periodic metrics saving in a background thread.
        
        This method creates a daemon thread that saves metrics at regular intervals,
        ensuring metrics are persisted even if the application crashes.
        
        Args:
            interval_seconds (int): Interval between saves in seconds (default: 60)
        """
        import threading
        
        def save_loop():
            """Background loop for periodic metrics saving."""
            while True:
                time.sleep(interval_seconds)
                self._save_metrics()
        
        # Start daemon thread (will be terminated when main thread exits)
        save_thread = threading.Thread(target=save_loop, daemon=True)
        save_thread.start()
    
    def track_agent_execution(self, agent_name: str, duration: float, success: bool, 
                            error_type: Optional[str] = None):
        """
        Track agent execution metrics.
        
        Records execution time, success/failure count, and error details for agents.
        
        Args:
            agent_name (str): Name of the agent being tracked
            duration (float): Execution time in seconds
            success (bool): Whether the execution was successful
            error_type (Optional[str]): Type of error if execution failed
        """
        status = "success" if success else "failure"
        
        # Record execution time in histogram
        AGENT_EXECUTION_TIME.labels(agent_name=agent_name, status=status).observe(duration)
        
        # Increment execution counter
        AGENT_EXECUTIONS_TOTAL.labels(agent_name=agent_name, status=status).inc()
        
        # Track specific error types if execution failed
        if not success and error_type:
            AGENT_ERRORS_TOTAL.labels(agent_name=agent_name, error_type=error_type).inc()
    
    def track_task_execution(self, task_name: str, duration: float, success: bool):
        """
        Track task execution metrics.
        
        Records execution time and success/failure count for tasks.
        
        Args:
            task_name (str): Name of the task being tracked
            duration (float): Execution time in seconds
            success (bool): Whether the execution was successful
        """
        status = "success" if success else "failure"
        
        # Record execution time in histogram
        TASK_EXECUTION_TIME.labels(task_name=task_name, status=status).observe(duration)
        
        # Increment execution counter
        TASK_EXECUTIONS_TOTAL.labels(task_name=task_name, status=status).inc()
    
    def track_workflow(self, workflow_id: str, duration: float, success: bool):
        """
        Track workflow execution metrics.
        
        Records workflow duration, execution count, and success rate.
        
        Args:
            workflow_id (str): Unique identifier for the workflow
            duration (float): Total execution time in seconds
            success (bool): Whether the workflow completed successfully
        """
        status = "success" if success else "failure"
        
        # Record workflow duration in histogram
        WORKFLOW_DURATION.labels(workflow_id=workflow_id, status=status).observe(duration)
        
        # Increment workflow execution counter
        WORKFLOW_EXECUTIONS_TOTAL.labels(workflow_id=workflow_id, status=status).inc()
        
        # Update success rate gauge (1.0 for success, 0.0 for failure)
        success_rate = 1.0 if success else 0.0
        WORKFLOW_SUCCESS_RATE.labels(workflow_id=workflow_id).set(success_rate)
    
    def track_evaluation_score(self, workflow_id: str, overall_score: float, evaluation_duration: float):
        """
        Track overall evaluation metrics for a workflow.
        
        Records the overall evaluation score and evaluation duration.
        
        Args:
            workflow_id (str): Unique identifier for the workflow
            overall_score (float): Overall evaluation score (0-10)
            evaluation_duration (float): Time spent on evaluation in seconds
        """
        # Record overall evaluation score in gauge
        OVERALL_EVALUATION_SCORE.labels(workflow_id=workflow_id).set(overall_score)
        
        # Record evaluation duration in histogram
        EVALUATION_DURATION.labels(workflow_id=workflow_id).observe(evaluation_duration)
    
    def track_metric_score(self, workflow_id: str, metric_name: str, score: float):
        """
        Track individual evaluation metric scores.
        
        Records individual metric scores and increments evaluation count.
        
        Args:
            workflow_id (str): Unique identifier for the workflow
            metric_name (str): Name of the evaluation metric (e.g., 'relevance', 'accuracy')
            score (float): Score for this specific metric (0-10)
        """
        # Record individual metric score in histogram
        EVALUATION_SCORE.labels(workflow_id=workflow_id, metric_name=metric_name).observe(score)
        
        # Increment evaluation count for this metric type
        EVALUATION_COUNT.labels(metric_name=metric_name).inc()
    
    def track_memory_usage(self, memory_type: str, usage_bytes: int, entries_count: int):
        """
        Track memory usage metrics.
        
        Args:
            memory_type (str): Type of memory being tracked
            usage_bytes (int): Memory usage in bytes
            entries_count (int): Number of entries in memory
        """
        # Memory tracking implementation will be added in future versions
        pass
    
    def get_metrics(self) -> str:
        """
        Get current metrics in Prometheus text format.
        
        Returns:
            str: Current metrics in Prometheus exposition format
        """
        return generate_latest()
    
    def shutdown(self):
        """
        Save metrics before application shutdown.
        
        Ensures all current metrics are persisted before the application exits.
        """
        print("Saving metrics before shutdown...")
        self._save_metrics()
        print("Metrics saved successfully")

# =============================================================================
# GLOBAL METRICS INSTANCE AND INITIALIZATION
# =============================================================================

# Global metrics instance - used throughout the application
metrics = PrometheusMetrics()

# Start periodic metrics saving every 30 seconds
# This ensures metrics are persisted even if the application crashes
metrics.save_metrics_periodically(interval_seconds=30)

# =============================================================================
# METRIC TRACKING DECORATORS
# =============================================================================

def track_agent_metrics(agent_name: str):
    """
    Decorator to automatically track agent execution metrics.
    
    This decorator wraps agent functions and automatically records:
    - Execution duration
    - Success/failure status
    - Error types (if any)
    
    Args:
        agent_name (str): Name of the agent for metric labeling
        
    Returns:
        function: Decorated function with automatic metric tracking
        
    Example:
        @track_agent_metrics("patent_researcher")
        def research_patents(query):
            # Agent logic here
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            error_type = None
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                error_type = type(e).__name__
                raise
            finally:
                # Always record metrics, even if function fails
                duration = time.time() - start_time
                metrics.track_agent_execution(agent_name, duration, success, error_type)
        
        return wrapper
    return decorator

def track_task_metrics(task_name: str):
    """
    Decorator to automatically track task execution metrics.
    
    This decorator wraps task functions and automatically records:
    - Execution duration
    - Success/failure status
    
    Args:
        task_name (str): Name of the task for metric labeling
        
    Returns:
        function: Decorated function with automatic metric tracking
        
    Example:
        @track_task_metrics("patent_search")
        def search_patents(query):
            # Task logic here
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception:
                raise
            finally:
                # Always record metrics, even if function fails
                duration = time.time() - start_time
                metrics.track_task_execution(task_name, duration, success)
        
        return wrapper
    return decorator

def track_workflow_metrics(workflow_id: str):
    """
    Decorator to automatically track workflow execution metrics.
    
    This decorator wraps workflow functions and automatically records:
    - Total execution duration
    - Success/failure status
    - Success rate updates
    
    Args:
        workflow_id (str): Unique identifier for the workflow
        
    Returns:
        function: Decorated function with automatic metric tracking
        
    Example:
        @track_workflow_metrics("workflow_123")
        def complete_patent_analysis(query):
            # Workflow logic here
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception:
                raise
            finally:
                # Always record metrics, even if function fails
                duration = time.time() - start_time
                metrics.track_workflow(workflow_id, duration, success)
        
        return wrapper
    return decorator 