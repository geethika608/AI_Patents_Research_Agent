#!/usr/bin/env python
"""
Production monitoring script for the Patent Research AI Agent.
Provides real-time monitoring, alerting, and metrics export.
"""

import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import requests

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from patent_researcher_agent.utils.monitoring import monitor
from patent_researcher_agent.utils.error_handling import error_handler
from patent_researcher_agent.utils.health_check import HealthChecker
from patent_researcher_agent.utils.logger import setup_logger

logger = setup_logger(__name__)


class ProductionMonitor:
    """Production monitoring and alerting system."""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.logger = logger
        self.health_checker = HealthChecker()
        self.alert_thresholds = {
            "error_rate": 0.1,  # 10% error rate
            "response_time": 30.0,  # 30 seconds
            "memory_usage": 0.8,  # 80% memory usage
            "disk_usage": 0.9,  # 90% disk usage
        }
        self.alert_history = []
    
    def check_system_health(self) -> dict:
        """Comprehensive system health check."""
        try:
            # Get monitoring metrics
            monitoring_health = monitor.get_system_health()
            
            # Get error statistics
            error_stats = error_handler.get_error_stats()
            
            # Get health check results
            health_status = self.health_checker.full_health_check()
            
            # Calculate performance metrics
            agent_metrics = monitor.export_metrics()
            
            # Aggregate metrics
            total_requests = sum(
                metrics["total_executions"] 
                for metrics in agent_metrics["agent_metrics"].values()
            )
            
            total_errors = sum(
                metrics["failed_executions"] 
                for metrics in agent_metrics["agent_metrics"].values()
            )
            
            error_rate = (total_errors / total_requests) if total_requests > 0 else 0
            
            avg_response_time = sum(
                metrics["avg_duration"] 
                for metrics in agent_metrics["agent_metrics"].values()
            ) / len(agent_metrics["agent_metrics"]) if agent_metrics["agent_metrics"] else 0
            
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "healthy",
                "checks": {
                    "monitoring": monitoring_health["status"],
                    "health_check": health_status["overall_status"],
                    "error_rate": "healthy" if error_rate < self.alert_thresholds["error_rate"] else "critical",
                    "response_time": "healthy" if avg_response_time < self.alert_thresholds["response_time"] else "warning"
                },
                "metrics": {
                    "total_requests": total_requests,
                    "total_errors": total_errors,
                    "error_rate": error_rate,
                    "avg_response_time": avg_response_time,
                    "active_workflows": len(agent_metrics["workflow_metrics"])
                },
                "circuit_breakers": error_stats["circuit_breakers"],
                "error_distribution": error_stats["error_counts"]
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "error",
                "error": str(e)
            }
    
    def check_alerts(self, health_data: dict) -> list:
        """Check for alert conditions."""
        alerts = []
        
        try:
            # Check error rate
            error_rate = health_data.get("metrics", {}).get("error_rate", 0)
            if error_rate > self.alert_thresholds["error_rate"]:
                alerts.append({
                    "level": "critical",
                    "message": f"High error rate: {error_rate:.2%}",
                    "timestamp": datetime.now().isoformat(),
                    "metric": "error_rate",
                    "value": error_rate,
                    "threshold": self.alert_thresholds["error_rate"]
                })
            
            # Check response time
            avg_response_time = health_data.get("metrics", {}).get("avg_response_time", 0)
            if avg_response_time > self.alert_thresholds["response_time"]:
                alerts.append({
                    "level": "warning",
                    "message": f"Slow response time: {avg_response_time:.2f}s",
                    "timestamp": datetime.now().isoformat(),
                    "metric": "response_time",
                    "value": avg_response_time,
                    "threshold": self.alert_thresholds["response_time"]
                })
            
            # Check circuit breakers
            circuit_breakers = health_data.get("circuit_breakers", {})
            for name, status in circuit_breakers.items():
                if status.get("state") == "open":
                    alerts.append({
                        "level": "critical",
                        "message": f"Circuit breaker '{name}' is OPEN",
                        "timestamp": datetime.now().isoformat(),
                        "metric": "circuit_breaker",
                        "value": name,
                        "threshold": "closed"
                    })
            
            # Check overall status
            if health_data.get("overall_status") != "healthy":
                alerts.append({
                    "level": "critical",
                    "message": f"System status: {health_data.get('overall_status')}",
                    "timestamp": datetime.now().isoformat(),
                    "metric": "system_status",
                    "value": health_data.get("overall_status"),
                    "threshold": "healthy"
                })
            
        except Exception as e:
            self.logger.error(f"Alert check failed: {e}")
            alerts.append({
                "level": "critical",
                "message": f"Alert check failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "metric": "alert_check",
                "value": "failed",
                "threshold": "success"
            })
        
        return alerts
    
    def send_alert(self, alert: dict, webhook_url: str = None):
        """Send alert notification."""
        try:
            # Log alert
            self.logger.warning(f"Alert: {alert['level'].upper()} - {alert['message']}",
                              alert=alert)
            
            # Store in history
            self.alert_history.append(alert)
            
            # Send webhook if configured
            if webhook_url:
                self._send_webhook(alert, webhook_url)
            
            # Print to console
            print(f"[{alert['level'].upper()}] {alert['message']}")
            
        except Exception as e:
            self.logger.error(f"Failed to send alert: {e}")
    
    def _send_webhook(self, alert: dict, webhook_url: str):
        """Send alert to webhook endpoint."""
        try:
            payload = {
                "text": f"[{alert['level'].upper()}] Patent Research AI Agent Alert",
                "attachments": [{
                    "color": "danger" if alert["level"] == "critical" else "warning",
                    "fields": [
                        {"title": "Message", "value": alert["message"], "short": False},
                        {"title": "Metric", "value": alert["metric"], "short": True},
                        {"title": "Value", "value": str(alert["value"]), "short": True},
                        {"title": "Threshold", "value": str(alert["threshold"]), "short": True},
                        {"title": "Timestamp", "value": alert["timestamp"], "short": True}
                    ]
                }]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
        except Exception as e:
            self.logger.error(f"Webhook send failed: {e}")
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        try:
            health_data = self.check_system_health()
            
            if format == "json":
                return json.dumps(health_data, indent=2, default=str)
            elif format == "prometheus":
                return self._format_prometheus(health_data)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            self.logger.error(f"Metrics export failed: {e}")
            return json.dumps({"error": str(e)}, indent=2)
    
    def _format_prometheus(self, health_data: dict) -> str:
        """Format metrics for Prometheus."""
        lines = []
        
        # System status
        status = 1 if health_data.get("overall_status") == "healthy" else 0
        lines.append(f'patent_agent_system_status {status}')
        
        # Metrics
        metrics = health_data.get("metrics", {})
        lines.append(f'patent_agent_total_requests {metrics.get("total_requests", 0)}')
        lines.append(f'patent_agent_total_errors {metrics.get("total_errors", 0)}')
        lines.append(f'patent_agent_error_rate {metrics.get("error_rate", 0)}')
        lines.append(f'patent_agent_avg_response_time {metrics.get("avg_response_time", 0)}')
        lines.append(f'patent_agent_active_workflows {metrics.get("active_workflows", 0)}')
        
        # Circuit breakers
        for name, status in health_data.get("circuit_breakers", {}).items():
            state_value = 1 if status.get("state") == "open" else 0
            lines.append(f'patent_agent_circuit_breaker_state{{name="{name}"}} {state_value}')
        
        return "\n".join(lines)
    
    def run_continuous_monitoring(self, interval: int = 60, webhook_url: str = None):
        """Run continuous monitoring with alerting."""
        self.logger.info(f"Starting continuous monitoring (interval: {interval}s)")
        
        try:
            while True:
                # Check system health
                health_data = self.check_system_health()
                
                # Check for alerts
                alerts = self.check_alerts(health_data)
                
                # Send alerts
                for alert in alerts:
                    self.send_alert(alert, webhook_url)
                
                # Log status
                self.logger.info(f"Monitoring check completed: {health_data.get('overall_status')}")
                
                # Wait for next check
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.logger.info("Continuous monitoring stopped")
        except Exception as e:
            self.logger.error(f"Continuous monitoring failed: {e}")
            raise


def main():
    """Main monitoring script."""
    parser = argparse.ArgumentParser(description="Patent Research AI Agent Monitoring")
    parser.add_argument("--check", action="store_true", help="Run single health check")
    parser.add_argument("--continuous", action="store_true", help="Run continuous monitoring")
    parser.add_argument("--interval", type=int, default=60, help="Monitoring interval in seconds")
    parser.add_argument("--export", choices=["json", "prometheus"], help="Export metrics")
    parser.add_argument("--webhook", help="Webhook URL for alerts")
    parser.add_argument("--output", help="Output file for metrics")
    
    args = parser.parse_args()
    
    monitor_system = ProductionMonitor()
    
    try:
        if args.check:
            # Single health check
            health_data = monitor_system.check_system_health()
            alerts = monitor_system.check_alerts(health_data)
            
            print(json.dumps(health_data, indent=2, default=str))
            
            if alerts:
                print("\nAlerts:")
                for alert in alerts:
                    print(f"[{alert['level'].upper()}] {alert['message']}")
            
            # Exit with appropriate code
            if health_data.get("overall_status") == "healthy":
                sys.exit(0)
            else:
                sys.exit(1)
        
        elif args.continuous:
            # Continuous monitoring
            monitor_system.run_continuous_monitoring(args.interval, args.webhook)
        
        elif args.export:
            # Export metrics
            metrics = monitor_system.export_metrics(args.export)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(metrics)
                print(f"Metrics exported to {args.output}")
            else:
                print(metrics)
        
        else:
            # Default: single health check
            health_data = monitor_system.check_system_health()
            print(json.dumps(health_data, indent=2, default=str))
    
    except Exception as e:
        logger.error(f"Monitoring script failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 