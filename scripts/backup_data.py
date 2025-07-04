#!/usr/bin/env python
"""
Data backup script for production data management.
"""

import shutil
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from patent_researcher_agent.utils.logger import setup_logger

logger = setup_logger(__name__)


def backup_data():
    """Backup important data directories."""
    logger.info("Starting data backup")
    
    # Define backup directories
    backup_dirs = ["memory", "output", "knowledge", "mlartifacts"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = Path(f"backups/backup_{timestamp}")
    
    try:
        # Create backup directory
        backup_root.mkdir(parents=True, exist_ok=True)
        
        for dir_name in backup_dirs:
            source_dir = Path(dir_name)
            if source_dir.exists():
                dest_dir = backup_root / dir_name
                logger.info(f"Backing up {dir_name} to {dest_dir}")
                shutil.copytree(source_dir, dest_dir)
            else:
                logger.warning(f"Directory {dir_name} does not exist, skipping")
        
        logger.info(f"Backup completed successfully: {backup_root}")
        return str(backup_root)
        
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        raise


def cleanup_old_backups(keep_days: int = 7):
    """Clean up old backup directories."""
    logger.info(f"Cleaning up backups older than {keep_days} days")
    
    backup_root = Path("backups")
    if not backup_root.exists():
        return
    
    cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 3600)
    
    for backup_dir in backup_root.iterdir():
        if backup_dir.is_dir() and backup_dir.name.startswith("backup_"):
            if backup_dir.stat().st_mtime < cutoff_time:
                logger.info(f"Removing old backup: {backup_dir}")
                shutil.rmtree(backup_dir)


def main():
    """Main backup function."""
    try:
        # Create backup
        backup_path = backup_data()
        print(f"✅ Backup completed: {backup_path}")
        
        # Clean up old backups
        cleanup_old_backups()
        print("✅ Old backups cleaned up")
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 