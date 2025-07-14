# Logging System

The Patent Research AI Agent uses a comprehensive logging system that captures all activities, errors, and performance metrics.

## Log Files Location

All logs are stored in the `./logs/` directory with the following structure:

```
logs/
├── patent_researcher_YYYYMMDD.log          # All logs (INFO and above)
├── patent_researcher_errors_YYYYMMDD.log   # Error logs only
└── patent_researcher_debug_YYYYMMDD.json   # Debug logs in JSON format
```

## Log File Types

### 1. Main Log File (`patent_researcher_YYYYMMDD.log`)
- **Content**: All log messages (INFO, WARNING, ERROR)
- **Format**: Human-readable text format
- **Size Limit**: 10MB with rotation (keeps 5 backup files)
- **Example**:
```
2024-01-15 10:30:15 - patent_researcher_agent.crew - INFO - Creating patent innovation crew
2024-01-15 10:30:16 - patent_researcher_agent.ui.chat_ui - INFO - Starting patent research for query: AI in healthcare
```

### 2. Error Log File (`patent_researcher_errors_YYYYMMDD.log`)
- **Content**: Only ERROR level messages
- **Format**: Human-readable with stack traces
- **Size Limit**: 5MB with rotation (keeps 3 backup files)
- **Example**:
```
2024-01-15 10:30:20 - patent_researcher_agent.crew - ERROR - Agent execution failed: fetcher_agent
src/patent_researcher_agent/crew.py:45
```

### 3. Debug Log File (`patent_researcher_debug_YYYYMMDD.json`)
- **Content**: All log messages including DEBUG
- **Format**: Structured JSON for analysis
- **Size Limit**: 20MB with rotation (keeps 3 backup files)
- **Example**:
```json
{
  "timestamp": "2024-01-15T10:30:15.123456Z",
  "level": "info",
  "logger": "patent_researcher_agent.crew",
  "event": "Creating patent innovation crew",
  "workflow_id": "abc123"
}
```

## Viewing Logs

### Using the Log Viewer Script

The project includes a utility script to view and analyze logs:

```bash
# List all available log files
python scripts/view_logs.py list

# View the last 50 lines of a log file
python scripts/view_logs.py view --file patent_researcher_20240115.log

# View the last 100 lines
python scripts/view_logs.py view --file patent_researcher_20240115.log --lines 100

# Follow a log file in real-time (like tail -f)
python scripts/view_logs.py view --file patent_researcher_20240115.log --follow

# Search for specific terms
python scripts/view_logs.py search --term "ERROR"

# Search in a specific file
python scripts/view_logs.py search --term "fetcher_agent" --file patent_researcher_20240115.log

# Analyze log statistics
python scripts/view_logs.py analyze

# Analyze a specific file
python scripts/view_logs.py analyze --file patent_researcher_20240115.log
```

### Using Standard Unix Tools

You can also use standard Unix tools to view logs:

```bash
# View last 50 lines
tail -n 50 logs/patent_researcher_20240115.log

# Follow logs in real-time
tail -f logs/patent_researcher_20240115.log

# Search for errors
grep "ERROR" logs/patent_researcher_20240115.log

# Search for specific agent
grep "fetcher_agent" logs/patent_researcher_20240115.log

# Count total lines
wc -l logs/patent_researcher_20240115.log
```

## Log Levels

The system uses the following log levels:

- **DEBUG**: Detailed information for debugging
- **INFO**: General information about application flow
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failed operations

## What Gets Logged

### Agent Execution
- Agent creation and initialization
- Agent execution start/end
- Agent errors and failures
- Performance metrics (duration, success rate)

### Task Execution
- Task creation and assignment
- Task execution start/end
- Task results and validation
- Task errors and failures

### Workflow Management
- Workflow start/end
- Workflow success/failure
- User input processing
- Output generation

### System Operations
- Configuration loading
- Memory operations
- API calls and responses
- Error handling

### Monitoring Metrics
- Performance thresholds
- Error rates
- Token usage
- MLflow integration

## Log Rotation

Log files automatically rotate when they reach their size limits:

- **Main logs**: 10MB → 5 backup files
- **Error logs**: 5MB → 3 backup files  
- **Debug logs**: 20MB → 3 backup files

Old log files are automatically compressed and archived.

## Integration with MLflow

All important metrics are also logged to MLflow for:

- Performance analysis
- Error tracking
- Workflow comparison
- Historical trends

## Troubleshooting

### No Logs Appearing
1. Check if the `./logs/` directory exists
2. Verify the application has write permissions
3. Check if the application is actually running

### Log Files Too Large
1. Logs automatically rotate when they reach size limits
2. You can manually delete old log files
3. Adjust rotation settings in `logger.py` if needed

### Missing Information
1. Check debug logs for detailed information
2. Verify log level settings
3. Check if specific components are logging properly

## Best Practices

1. **Monitor Error Logs**: Regularly check error logs for issues
2. **Use Log Analysis**: Use the analysis tool to identify patterns
3. **Archive Old Logs**: Move old logs to long-term storage
4. **Set Up Alerts**: Monitor error rates and performance metrics
5. **Regular Cleanup**: Remove very old log files to save space 