"""
Prometheus metrics for Patent Research AI Agent.
"""
import time
from typing import Dict, Any, Optional
from prometheus_client import (
    Counter, Gauge, Histogram, Summary, 
    start_http_server, generate_latest, CONTENT_TYPE_LATEST
)
from functools import wraps
from .metrics_persistence import MetricsPersistence

# Agent Metrics
AGENT_EXECUTION_TIME = Histogram(
    'patent_agent_execution_duration_seconds',
    'Time spent executing agent tasks',
    ['agent_name', 'status']
)

AGENT_EXECUTIONS_TOTAL = Counter(
    'patent_agent_executions_total',
    'Total number of agent executions',
    ['agent_name', 'status']
)

AGENT_ERRORS_TOTAL = Counter(
    'patent_agent_errors_total',
    'Total number of agent errors',
    ['agent_name', 'error_type']
)

# Task Metrics
TASK_EXECUTION_TIME = Histogram(
    'patent_task_execution_duration_seconds',
    'Time spent executing tasks',
    ['task_name', 'status']
)

TASK_EXECUTIONS_TOTAL = Counter(
    'patent_task_executions_total',
    'Total number of task executions',
    ['task_name', 'status']
)

# Workflow Metrics
WORKFLOW_DURATION = Histogram(
    'patent_workflow_duration_seconds',
    'Time spent on complete workflows',
    ['workflow_id', 'status']
)

WORKFLOW_SUCCESS_RATE = Gauge(
    'patent_workflow_success_rate',
    'Success rate of workflows',
    ['workflow_id']
)

class PrometheusMetrics:
    """Prometheus metrics manager for Patent Research AI Agent."""
    
    def __init__(self, metrics_port: int = 8000):
        self.metrics_port = metrics_port
        self.persistence = MetricsPersistence()
        self._restore_metrics()
        self._start_metrics_server()
    
    def _start_metrics_server(self):
        """Start the Prometheus metrics server."""
        try:
            start_http_server(self.metrics_port)
            print(f"Prometheus metrics server started on port {self.metrics_port}")
        except Exception as e:
            print(f"Failed to start metrics server: {e}")
    
    def _save_metrics(self):
        """Save all Prometheus metrics to persistence file."""
        try:
            from prometheus_client import generate_latest
            import re
            import json

            metrics_text = generate_latest().decode('utf-8')
            metrics_list = []
            metric_line_pattern = re.compile(r'^(?P<name>[a-zA-Z_:][a-zA-Z0-9_:]*)\{(?P<labels>[^}]*)\} (?P<value>[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)$', re.MULTILINE)
            label_pattern = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)="([^"]*)"')

            for match in metric_line_pattern.finditer(metrics_text):
                name = match.group('name')
                labels_str = match.group('labels')
                value = match.group('value')
                labels = {k: v for k, v in label_pattern.findall(labels_str)}
                metrics_list.append({
                    "name": name,
                    "labels": labels,
                    "value": float(value) if '.' in value or 'e' in value.lower() else int(value)
                })

            self.persistence.save_metrics(metrics_list)
            print(f"Successfully saved {len(metrics_list)} metrics to persistence file.")
        except Exception as e:
            print(f"Failed to save metrics: {e}")
            import traceback
            traceback.print_exc()

    def _restore_metrics(self):
        """Restore all Prometheus metrics from persistence file."""
        if not self.persistence.should_restore_metrics():
            print("Skipping metrics restoration - saved metrics are too old")
            return
        saved_metrics = self.persistence.load_metrics()
        if not saved_metrics:
            print("No saved metrics to restore")
            return
        try:
            restored_count = 0
            skipped_count = 0
            
            for metric in saved_metrics:
                name = metric.get("name")
                labels = metric.get("labels", {})
                value = metric.get("value")
                
                # Get current value from Prometheus text for comparison
                from prometheus_client import generate_latest
                import re
                metrics_text = generate_latest().decode('utf-8')
                pattern = rf'{name}{{' + ','.join([f'{k}="{v}"' for k, v in labels.items()]) + r'}} ([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)'
                match = re.search(pattern, metrics_text)
                current_value = float(match.group(1)) if match else 0
                
                try:
                    # Restore counters by incrementing
                    if name.endswith('_total') or name.endswith('_count'):
                        if name == 'patent_agent_executions_total':
                            counter = AGENT_EXECUTIONS_TOTAL.labels(**labels)
                        elif name == 'patent_task_executions_total':
                            counter = TASK_EXECUTIONS_TOTAL.labels(**labels)
                        elif name == 'patent_agent_errors_total':
                            counter = AGENT_ERRORS_TOTAL.labels(**labels)
                        # Histogram count metrics
                        elif name == 'patent_agent_execution_duration_seconds_count':
                            # For histogram counts, we need to simulate observations
                            # This is tricky, so we'll skip for now
                            print(f"Skipping histogram count metric {name} (not supported)")
                            skipped_count += 1
                            continue
                        elif name == 'patent_task_execution_duration_seconds_count':
                            print(f"Skipping histogram count metric {name} (not supported)")
                            skipped_count += 1
                            continue
                        elif name == 'patent_workflow_duration_seconds_count':
                            print(f"Skipping histogram count metric {name} (not supported)")
                            skipped_count += 1
                            continue
                        else:
                            print(f"Unknown counter metric {name}, skipping")
                            skipped_count += 1
                            continue
                        
                        # Only increment if the saved value is higher than current
                        if value > current_value:
                            for _ in range(int(value) - int(current_value)):
                                counter.inc()
                            restored_count += 1
                            print(f"Restored counter {name} {labels}: {current_value} -> {value}")
                    
                    # Restore gauges by setting
                    elif (name.endswith('_rate') or name.endswith('_usage_bytes') or 
                          name.endswith('_entries_total') or name.endswith('_remaining') or 
                          name.endswith('_reset_time') or name == 'patent_workflow_success_rate'):
                        if name == 'patent_workflow_success_rate':
                            gauge = WORKFLOW_SUCCESS_RATE.labels(**labels)
                        else:
                            print(f"Unknown gauge metric {name}, skipping")
                            skipped_count += 1
                            continue
                        
                        gauge.set(value)
                        restored_count += 1
                        print(f"Restored gauge {name} {labels}: {current_value} -> {value}")
                    
                    # Skip histogram sum metrics (cannot restore properly)
                    elif name.endswith('_sum'):
                        print(f"Skipping histogram sum metric {name} (not supported)")
                        skipped_count += 1
                        continue
                    
                    # Skip histogram bucket metrics (cannot restore properly)
                    elif name.endswith('_bucket'):
                        print(f"Skipping histogram bucket metric {name} (not supported)")
                        skipped_count += 1
                        continue
                    
                    # Skip other metrics
                    else:
                        print(f"Skipping unknown metric {name} (type not supported)")
                        skipped_count += 1
                        continue
                        
                except Exception as e:
                    print(f"Failed to restore metric {name} {labels}: {e}")
                    skipped_count += 1
            
            print(f"Restored {restored_count} metrics, skipped {skipped_count} metrics from persistence file.")
            
        except Exception as e:
            print(f"Failed to restore metrics: {e}")
            import traceback
            traceback.print_exc()
    
    def save_metrics_periodically(self, interval_seconds: int = 60):
        """Save metrics periodically in a background thread."""
        import threading
        
        def save_loop():
            while True:
                time.sleep(interval_seconds)
                self._save_metrics()
        
        save_thread = threading.Thread(target=save_loop, daemon=True)
        save_thread.start()
        print(f"Started periodic metrics saving every {interval_seconds} seconds")
    
    def track_agent_execution(self, agent_name: str, duration: float, success: bool, 
                            error_type: Optional[str] = None):
        """Track agent execution metrics."""
        status = "success" if success else "failure"
        
        # Record execution time
        AGENT_EXECUTION_TIME.labels(agent_name=agent_name, status=status).observe(duration)
        
        # Increment execution counter
        print(f"INCREMENTING AGENT COUNTER: {agent_name}, status: {status}")
        AGENT_EXECUTIONS_TOTAL.labels(agent_name=agent_name, status=status).inc()
        print(f"AGENT COUNTER VALUE AFTER INCREMENT: {AGENT_EXECUTIONS_TOTAL.labels(agent_name=agent_name, status=status)._value.get()}")
        
        # Track errors if any
        if not success and error_type:
            AGENT_ERRORS_TOTAL.labels(agent_name=agent_name, error_type=error_type).inc()
    
    def track_task_execution(self, task_name: str, duration: float, success: bool):
        """Track task execution metrics."""
        status = "success" if success else "failure"
        
        # Record execution time
        TASK_EXECUTION_TIME.labels(task_name=task_name, status=status).observe(duration)
        
        # Increment execution counter
        TASK_EXECUTIONS_TOTAL.labels(task_name=task_name, status=status).inc()
    
    def track_workflow(self, workflow_id: str, duration: float, success: bool):
        """Track workflow metrics."""
        status = "success" if success else "failure"
        
        # Record workflow duration
        WORKFLOW_DURATION.labels(workflow_id=workflow_id, status=status).observe(duration)
        
        # Update success rate
        success_rate = 1.0 if success else 0.0
        WORKFLOW_SUCCESS_RATE.labels(workflow_id=workflow_id).set(success_rate)
    
    def track_memory_usage(self, memory_type: str, usage_bytes: int, entries_count: int):
        """Track memory usage metrics."""
        # MEMORY_USAGE_BYTES.labels(memory_type=memory_type).set(usage_bytes) # Removed as per edit hint
        # MEMORY_ENTRIES_TOTAL.labels(memory_type=memory_type).set(entries_count) # Removed as per edit hint
        pass # Removed as per edit hint
    
    def get_metrics(self) -> str:
        """Get current metrics in Prometheus format."""
        return generate_latest()
    
    def shutdown(self):
        """Save metrics before shutdown."""
        print("Saving metrics before shutdown...")
        self._save_metrics()
        print("Metrics saved successfully")

# Global metrics instance
metrics = PrometheusMetrics()

# Start periodic metrics saving
metrics.save_metrics_periodically(interval_seconds=30)  # Save every 30 seconds

# Decorators for easy metric tracking
def track_agent_metrics(agent_name: str):
    """Decorator to track agent execution metrics."""
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
                duration = time.time() - start_time
                metrics.track_agent_execution(agent_name, duration, success, error_type)
        
        return wrapper
    return decorator

def track_task_metrics(task_name: str):
    """Decorator to track task execution metrics."""
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
                duration = time.time() - start_time
                metrics.track_task_execution(task_name, duration, success)
        
        return wrapper
    return decorator 