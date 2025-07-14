"""
Metrics persistence for Prometheus metrics across server restarts.

This module provides functionality to save and restore Prometheus metrics
between application restarts, ensuring metric continuity and historical data preservation.
"""

import json
import os
import time
from typing import Dict, Any, Optional
from pathlib import Path

class MetricsPersistence:
    """
    Handles saving and restoring Prometheus metrics across application restarts.
    
    This class manages the persistence of metrics data to JSON files,
    allowing metrics to survive application crashes and restarts.
    It also provides age-based filtering to prevent restoration of stale metrics.
    """
    
    def __init__(self, persistence_file: str = "metrics_persistence.json"):
        """
        Initialize the metrics persistence manager.
        
        Args:
            persistence_file (str): Name of the JSON file to store metrics (default: "metrics_persistence.json")
        """
        self.persistence_file = Path(persistence_file)
        # Create monitoring/metrics directory structure
        self.metrics_dir = Path("monitoring/metrics")
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        # Set full path to persistence file
        self.persistence_file = self.metrics_dir / persistence_file
    
    def save_metrics(self, metrics_data: Dict[str, Any]) -> bool:
        """
        Save current metrics to persistence file.
        
        This method saves metrics data along with a timestamp to a JSON file.
        The timestamp is used later to determine if metrics are too old to restore.
        
        Args:
            metrics_data (Dict[str, Any]): Dictionary containing metrics data to save
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            # Create save data with timestamp for age tracking
            save_data = {
                "timestamp": time.time(),  # Current Unix timestamp
                "metrics": metrics_data    # Actual metrics data
            }
            
            # Write to JSON file with pretty formatting
            with open(self.persistence_file, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Failed to save metrics: {e}")
            return False
    
    def load_metrics(self) -> Optional[Dict[str, Any]]:
        """
        Load metrics from persistence file.
        
        This method reads the metrics data from the JSON file.
        If the file doesn't exist or is corrupted, it returns None.
        
        Returns:
            Optional[Dict[str, Any]]: Metrics data if successful, None otherwise
        """
        try:
            # Check if persistence file exists
            if not self.persistence_file.exists():
                return None
            
            # Read and parse JSON file
            with open(self.persistence_file, 'r') as f:
                data = json.load(f)
            
            # Extract metrics data (return empty dict if not found)
            return data.get("metrics", {})
        except Exception as e:
            print(f"Failed to load metrics: {e}")
            return None
    
    def get_metrics_age(self) -> Optional[float]:
        """
        Get the age of the saved metrics in seconds.
        
        This method calculates how old the saved metrics are by comparing
        the saved timestamp with the current time.
        
        Returns:
            Optional[float]: Age in seconds if successful, None if file doesn't exist or is corrupted
        """
        try:
            # Check if persistence file exists
            if not self.persistence_file.exists():
                return None
            
            # Read timestamp from file
            with open(self.persistence_file, 'r') as f:
                data = json.load(f)
            
            # Calculate age: current time - saved timestamp
            saved_timestamp = data.get("timestamp", 0)
            return time.time() - saved_timestamp
        except Exception:
            return None
    
    def should_restore_metrics(self, max_age_hours: int = 24) -> bool:
        """
        Check if metrics should be restored based on their age.
        
        Prevents restoration of old metrics that might be irrelevant or corrupted.
        
        Args:
            max_age_hours (int): Maximum age in hours before metrics are considered stale (default: 24)
            
        Returns:
            bool: True if metrics should be restored, False if they're too old or don't exist
        """
        age = self.get_metrics_age()
        if age is None:
            return False
        
        # Convert hours to seconds and compare
        max_age_seconds = max_age_hours * 3600
        return age < max_age_seconds 