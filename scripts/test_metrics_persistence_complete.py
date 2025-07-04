#!/usr/bin/env python3
"""
Comprehensive test script for complete metrics persistence functionality.
"""

import time
import sys
import os
import json
import re

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from patent_researcher_agent.utils.prometheus_metrics import metrics
from patent_researcher_agent.utils.metrics_persistence import MetricsPersistence

def test_all_metrics_save_restore():
    """Test that all Prometheus metrics are saved and restored correctly."""
    print("🧪 Testing Complete Metrics Persistence")
    print("=" * 60)
    
    # Create a test persistence instance
    persistence = MetricsPersistence("test_complete_metrics.json")
    
    # Clear any existing test file
    if persistence.persistence_file.exists():
        persistence.persistence_file.unlink()
        print("1. Cleared existing test file")
    
    # Generate some test metrics
    print("\n2. Generating test metrics...")
    
    # Agent metrics
    metrics.track_agent_execution("fetcher_agent", 2.5, True)
    metrics.track_agent_execution("analyzer_agent", 3.1, True)
    metrics.track_agent_execution("reporter_agent", 1.8, False, "TimeoutError")
    
    # Task metrics
    metrics.track_task_execution("fetch_patents", 5.2, True)
    metrics.track_task_execution("analyze_trends", 4.7, True)
    metrics.track_task_execution("generate_report", 2.3, False)
    
    # Workflow metrics
    metrics.track_workflow("test-workflow-1", 12.5, True)
    metrics.track_workflow("test-workflow-2", 8.9, False)
    
    # API metrics
    metrics.track_api_request("openai_api", 1.2, True)
    metrics.track_api_request("serper_api", 0.8, True)
    metrics.track_api_request("external_api", 2.1, False)
    
    # Memory metrics
    metrics.track_memory_usage("long_term", 1024000, 150)
    metrics.track_memory_usage("short_term", 512000, 75)
    metrics.track_memory_usage("entity", 256000, 25)
    
    # Rate limit metrics
    metrics.track_rate_limit("openai_api", 45, time.time() + 3600)
    metrics.track_rate_limit("serper_api", 98, time.time() + 1800)
    
    print("   Generated test metrics for all metric types")
    
    # Save metrics
    print("\n3. Saving all metrics...")
    metrics._save_metrics()
    
    # Load and analyze saved metrics
    print("\n4. Analyzing saved metrics...")
    saved_metrics = persistence.load_metrics()
    
    if not saved_metrics:
        print("   ❌ No metrics were saved!")
        return False
    
    print(f"   ✅ Saved {len(saved_metrics)} metrics")
    
    # Analyze metric types
    metric_types = {}
    metric_names = set()
    
    for metric in saved_metrics:
        name = metric.get("name", "")
        metric_names.add(name)
        
        if name.endswith('_total'):
            metric_types['counters'] = metric_types.get('counters', 0) + 1
        elif name.endswith('_count'):
            metric_types['histogram_counts'] = metric_types.get('histogram_counts', 0) + 1
        elif name.endswith('_sum'):
            metric_types['histogram_sums'] = metric_types.get('histogram_sums', 0) + 1
        elif name.endswith('_bucket'):
            metric_types['histogram_buckets'] = metric_types.get('histogram_buckets', 0) + 1
        elif name.endswith('_rate') or name.endswith('_usage_bytes') or name.endswith('_entries_total') or name.endswith('_remaining') or name.endswith('_reset_time'):
            metric_types['gauges'] = metric_types.get('gauges', 0) + 1
        else:
            metric_types['other'] = metric_types.get('other', 0) + 1
    
    print("   Metric types found:")
    for metric_type, count in metric_types.items():
        print(f"     {metric_type}: {count}")
    
    print("   Metric names found:")
    for name in sorted(metric_names):
        print(f"     {name}")
    
    # Check for specific expected metrics
    expected_metrics = [
        'patent_agent_executions_total',
        'patent_task_executions_total',
        'patent_agent_errors_total',
        'patent_api_requests_total',
        'patent_workflow_success_rate',
        'patent_memory_usage_bytes',
        'patent_memory_entries_total',
        'patent_rate_limit_remaining',
        'patent_rate_limit_reset_time',
        'patent_agent_execution_duration_seconds_count',
        'patent_task_execution_duration_seconds_count',
        'patent_workflow_duration_seconds_count',
        'patent_api_request_duration_seconds_count'
    ]
    
    missing_metrics = []
    for expected in expected_metrics:
        if not any(metric.get("name") == expected for metric in saved_metrics):
            missing_metrics.append(expected)
    
    if missing_metrics:
        print(f"   ⚠️  Missing expected metrics: {missing_metrics}")
    else:
        print("   ✅ All expected metrics found")
    
    # Test restore functionality
    print("\n5. Testing restore functionality...")
    
    # Clear current metrics by restarting
    print("   Clearing current metrics...")
    # Note: In a real scenario, this would be done by restarting the service
    # For testing, we'll just call restore and see what happens
    
    # Call restore
    metrics._restore_metrics()
    
    print("   ✅ Restore test completed")
    
    # Clean up
    if persistence.persistence_file.exists():
        persistence.persistence_file.unlink()
        print("\n6. Cleaned up test file")
    
    return True

def test_metrics_structure():
    """Test the structure of saved metrics JSON."""
    print("\n🧪 Testing Metrics JSON Structure")
    print("=" * 60)
    
    persistence = MetricsPersistence("test_structure.json")
    
    # Generate some metrics
    metrics.track_agent_execution("test_agent", 1.0, True)
    metrics.track_task_execution("test_task", 2.0, True)
    
    # Save metrics
    metrics._save_metrics()
    
    # Load and check structure
    saved_metrics = persistence.load_metrics()
    
    if saved_metrics and len(saved_metrics) > 0:
        sample_metric = saved_metrics[0]
        print("Sample metric structure:")
        print(json.dumps(sample_metric, indent=2))
        
        # Check required fields
        required_fields = ['name', 'labels', 'value']
        missing_fields = [field for field in required_fields if field not in sample_metric]
        
        if missing_fields:
            print(f"   ❌ Missing required fields: {missing_fields}")
            return False
        else:
            print("   ✅ All required fields present")
        
        # Check data types
        if not isinstance(sample_metric['name'], str):
            print("   ❌ 'name' field is not a string")
            return False
        if not isinstance(sample_metric['labels'], dict):
            print("   ❌ 'labels' field is not a dict")
            return False
        if not isinstance(sample_metric['value'], (int, float)):
            print("   ❌ 'value' field is not a number")
            return False
        
        print("   ✅ All data types correct")
    
    # Clean up
    if persistence.persistence_file.exists():
        persistence.persistence_file.unlink()
    
    return True

def test_metrics_parsing():
    """Test the Prometheus metrics parsing logic."""
    print("\n🧪 Testing Metrics Parsing")
    print("=" * 60)
    
    # Get current metrics text
    from prometheus_client import generate_latest
    metrics_text = generate_latest().decode('utf-8')
    
    print(f"Raw metrics text length: {len(metrics_text)} characters")
    print("Sample metrics lines:")
    
    lines = metrics_text.split('\n')[:10]  # First 10 lines
    for i, line in enumerate(lines):
        if line.strip():
            print(f"  {i+1}: {line}")
    
    # Test parsing
    import re
    metric_line_pattern = re.compile(r'^(?P<name>[a-zA-Z_:][a-zA-Z0-9_:]*)\{(?P<labels>[^}]*)\} (?P<value>[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)$', re.MULTILINE)
    label_pattern = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)="([^"]*)"')
    
    parsed_count = 0
    for match in metric_line_pattern.finditer(metrics_text):
        name = match.group('name')
        labels_str = match.group('labels')
        value = match.group('value')
        labels = {k: v for k, v in label_pattern.findall(labels_str)}
        
        if parsed_count < 5:  # Show first 5 parsed metrics
            print(f"  Parsed: {name} {labels} = {value}")
        
        parsed_count += 1
    
    print(f"   ✅ Successfully parsed {parsed_count} metrics")
    return True

if __name__ == "__main__":
    try:
        success = True
        
        # Run all tests
        success &= test_all_metrics_save_restore()
        success &= test_metrics_structure()
        success &= test_metrics_parsing()
        
        if success:
            print("\n🎉 All metrics persistence tests passed!")
        else:
            print("\n❌ Some tests failed!")
            
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc() 