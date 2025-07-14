import os
import time
import requests
from typing import Dict, Any
from .logger import setup_logger

from .workflow_tracker import get_workflow_status

logger = setup_logger(__name__)


class HealthChecker:
    """Health check utility for production monitoring."""
    
    def __init__(self):
        self.logger = logger
    
    def check_environment(self) -> Dict[str, Any]:
        """Check environment variables and configuration."""
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "checks": {}
        }
        
        # Check required environment variables
        required_vars = ["OPENAI_API_KEY"]
        for var in required_vars:
            if os.getenv(var):
                health_status["checks"][f"env_{var}"] = "ok"
            else:
                health_status["checks"][f"env_{var}"] = "error"
                health_status["status"] = "unhealthy"
        
        # Check optional environment variables
        optional_vars = ["SERPER_API_KEY", "DEBUG", "LOG_LEVEL"]
        for var in optional_vars:
            health_status["checks"][f"env_{var}"] = "ok" if os.getenv(var) else "warning"
        
        return health_status
    
    def check_directories(self) -> Dict[str, Any]:
        """Check if required directories exist and are writable."""
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "checks": {}
        }
        
        required_dirs = ["./memory", "./output", "./knowledge"]
        for dir_path in required_dirs:
            try:
                if os.path.exists(dir_path) and os.access(dir_path, os.W_OK):
                    health_status["checks"][f"dir_{dir_path}"] = "ok"
                else:
                    health_status["checks"][f"dir_{dir_path}"] = "error"
                    health_status["status"] = "unhealthy"
            except Exception as e:
                health_status["checks"][f"dir_{dir_path}"] = "error"
                health_status["status"] = "unhealthy"
                self.logger.error(f"Directory check failed for {dir_path}: {e}")
        
        return health_status
    
    def check_external_services(self) -> Dict[str, Any]:
        """Check external service connectivity."""
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "checks": {}
        }
        
        # Check MLflow server
        try:
            response = requests.get("http://localhost:5000/health", timeout=5)
            if response.status_code == 200:
                health_status["checks"]["mlflow"] = "ok"
            else:
                health_status["checks"]["mlflow"] = "warning"
        except requests.RequestException:
            health_status["checks"]["mlflow"] = "warning"  # MLflow is optional
        
        return health_status
    
    def full_health_check(self) -> Dict[str, Any]:
        """Perform a full health check."""
        self.logger.info("Performing full health check")
        
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "overall_status": "healthy",
            "checks": {}
        }
        
        # Run all health checks
        env_check = self.check_environment()
        dir_check = self.check_directories()
        service_check = self.check_external_services()
        

        
        # Check workflow tracker
        try:
            workflow_status = get_workflow_status()
            health_status["checks"]["workflow_tracker"] = "ok"
            health_status["checks"]["active_workflows_count"] = workflow_status["workflow_count"]
            health_status["checks"]["active_workflows"] = workflow_status["active_workflows"]
        except Exception as e:
            health_status["checks"]["workflow_tracker"] = "error"
            self.logger.error(f"Workflow tracker check failed: {e}")
        
        # Combine results
        health_status["checks"].update(env_check["checks"])
        health_status["checks"].update(dir_check["checks"])
        health_status["checks"].update(service_check["checks"])
        
        # Determine overall status
        if any(check == "error" for check in health_status["checks"].values()):
            health_status["overall_status"] = "unhealthy"
        elif any(check == "warning" for check in health_status["checks"].values()):
            health_status["overall_status"] = "degraded"
        
        self.logger.info(f"Health check completed: {health_status['overall_status']}")
        return health_status 