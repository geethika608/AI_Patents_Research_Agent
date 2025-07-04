#!/usr/bin/env python
"""
Health check script for production monitoring.
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from patent_researcher_agent.utils.health_check import HealthChecker


def main():
    """Run health check and output results."""
    checker = HealthChecker()
    health_status = checker.full_health_check()
    
    # Output as JSON for monitoring systems
    print(json.dumps(health_status, indent=2))
    
    # Exit with appropriate code
    if health_status["overall_status"] == "healthy":
        sys.exit(0)
    elif health_status["overall_status"] == "degraded":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main() 