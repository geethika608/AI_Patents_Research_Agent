"""
Metrics persistence for Prometheus metrics across server restarts.
"""

import json
import os
import time
from typing import Dict, Any, Optional
from pathlib import Path

class MetricsPersistence:
    """Handles saving and restoring Prometheus metrics across restarts."""
    
    def __init__(self, persistence_file: str = "metrics_persistence.json"):
        self.persistence_file = Path(persistence_file)
        self.metrics_dir = Path("monitoring/metrics")
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        self.persistence_file = self.metrics_dir / persistence_file
        
    def save_metrics(self, metrics_data: Dict[str, Any]) -> bool:
        """Save current metrics to file."""
        try:
            # Add timestamp for when metrics were saved
            save_data = {
                "timestamp": time.time(),
                "metrics": metrics_data
            }
            
            with open(self.persistence_file, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            print(f"Metrics saved to {self.persistence_file}")
            return True
        except Exception as e:
            print(f"Failed to save metrics: {e}")
            return False
    
    def load_metrics(self) -> Optional[Dict[str, Any]]:
        """Load metrics from file."""
        try:
            if not self.persistence_file.exists():
                print(f"No metrics persistence file found at {self.persistence_file}")
                return None
            
            with open(self.persistence_file, 'r') as f:
                data = json.load(f)
            
            print(f"Metrics loaded from {self.persistence_file}")
            return data.get("metrics", {})
        except Exception as e:
            print(f"Failed to load metrics: {e}")
            return None
    
    def get_metrics_age(self) -> Optional[float]:
        """Get the age of the saved metrics in seconds."""
        try:
            if not self.persistence_file.exists():
                return None
            
            with open(self.persistence_file, 'r') as f:
                data = json.load(f)
            
            saved_timestamp = data.get("timestamp", 0)
            return time.time() - saved_timestamp
        except Exception:
            return None
    
    def should_restore_metrics(self, max_age_hours: int = 24) -> bool:
        """Check if metrics should be restored based on age."""
        age = self.get_metrics_age()
        if age is None:
            return False
        
        max_age_seconds = max_age_hours * 3600
        return age < max_age_seconds 