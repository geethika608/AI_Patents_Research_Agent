# Event Listeners Module

This module provides a modular event listener system for monitoring CrewAI execution events. The structure is designed to be maintainable and extensible, with separate listeners for different types of events.

## Structure

```
listeners/
├── __init__.py              # Main exports
├── base_listener.py         # Base class with common functionality
├── crew_listener.py         # Crew-level event monitoring
├── agent_listener.py        # Agent-level event monitoring
├── task_listener.py         # Task-level event monitoring
├── monitoring_listener.py   # Main listener that combines all others
└── README.md               # This documentation
```

## Components

### BaseMonitoringListener (`base_listener.py`)
Base class that provides common functionality for all listeners:
- Time tracking utilities
- Logging helpers
- MLflow integration helpers
- Execution data storage

### CrewListener (`crew_listener.py`)
Monitors crew-level events:
- `CrewKickoffStartedEvent`
- `CrewKickoffCompletedEvent`
- `CrewKickoffFailedEvent`

### AgentListener (`agent_listener.py`)
Monitors agent-level events:
- `AgentExecutionStartedEvent`
- `AgentExecutionCompletedEvent`
- `AgentExecutionFailedEvent`

### TaskListener (`task_listener.py`)
Monitors task-level events:
- `TaskExecutionStartedEvent`
- `TaskExecutionCompletedEvent`
- `TaskExecutionFailedEvent`

### MonitoringEventListener (`monitoring_listener.py`)
Main listener that combines all individual listeners and provides a unified interface.

## Usage

### Basic Usage
```python
from patent_researcher_agent.core.listeners import MonitoringEventListener
from patent_researcher_agent.utils.monitoring import monitor

# Create the listener
listener = MonitoringEventListener(monitor, "workflow-123")

# The listener will be automatically registered when imported
# according to CrewAI's event listener pattern
```

### Getting Execution Summary
```python
# Get comprehensive execution summary
summary = listener.get_execution_summary()

# Access specific data
crew_data = summary['crew_executions']
agent_data = summary['agent_executions']
task_data = summary['task_executions']
stats = summary['summary']

print(f"Agent success rate: {stats['agent_success_rate']}")
print(f"Task success rate: {stats['task_success_rate']}")
```

## Event Handler Structure

Each event handler follows this pattern:
1. **Start tracking**: Record start time and basic info
2. **Execute**: Monitor the actual execution
3. **End tracking**: Calculate duration and log results
4. **MLflow logging**: Record metrics and parameters
5. **Error handling**: Log errors if execution fails

## Benefits of Modular Structure

1. **Separation of Concerns**: Each listener handles specific event types
2. **Maintainability**: Easy to modify or extend individual listeners
3. **Testability**: Each listener can be tested independently
4. **Reusability**: Individual listeners can be used separately if needed
5. **Extensibility**: Easy to add new listeners for other event types

## Adding New Listeners

To add a new listener for different event types:

1. Create a new file (e.g., `tool_listener.py`)
2. Inherit from `BaseMonitoringListener`
3. Implement the `setup_listeners` method
4. Add the new listener to `MonitoringEventListener`
5. Update the `get_execution_summary` method if needed

Example:
```python
from .base_listener import BaseMonitoringListener
from crewai.utilities.events import ToolUsageStartedEvent

class ToolListener(BaseMonitoringListener):
    def setup_listeners(self, crewai_event_bus):
        @crewai_event_bus.on(ToolUsageStartedEvent)
        def on_tool_usage_started(source, event):
            # Handle tool usage events
            pass
```

## Integration with CrewAI

The listeners follow CrewAI's official event listener pattern:
- Use `setup_listeners` method with event bus decorators
- Register handlers using `@crewai_event_bus.on(EventType)`
- Follow the `source, event` parameter pattern
- Ensure listeners are imported to be automatically registered

## Testing

Run the test script to verify the modular structure:
```bash
python test_listeners.py
```

This will test:
- Import functionality
- Listener creation
- Execution summary generation
- Data structure validation 