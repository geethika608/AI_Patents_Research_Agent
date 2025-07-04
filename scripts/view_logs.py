#!/usr/bin/env python3
"""
Utility script to view and analyze logs from the Patent Research AI Agent.
"""

import os
import json
import argparse
from datetime import datetime
from pathlib import Path


def list_log_files():
    """List all available log files."""
    logs_dir = Path("./logs")
    if not logs_dir.exists():
        print("❌ Logs directory does not exist. Run the application first to generate logs.")
        return
    
    print("📁 Available log files:")
    print("-" * 50)
    
    for log_file in logs_dir.glob("*"):
        if log_file.is_file():
            stat = log_file.stat()
            size_mb = stat.st_size / (1024 * 1024)
            modified = datetime.fromtimestamp(stat.st_mtime)
            
            print(f"📄 {log_file.name}")
            print(f"   Size: {size_mb:.2f} MB")
            print(f"   Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Path: {log_file.absolute()}")
            print()


def view_log_file(filename, lines=50, follow=False):
    """View contents of a specific log file."""
    log_path = Path(f"./logs/{filename}")
    
    if not log_path.exists():
        print(f"❌ Log file {filename} not found.")
        return
    
    print(f"📖 Viewing log file: {filename}")
    print(f"📊 File size: {log_path.stat().st_size / (1024 * 1024):.2f} MB")
    print("-" * 80)
    
    try:
        with open(log_path, 'r') as f:
            if follow:
                # Follow the log file (like tail -f)
                print("🔄 Following log file (press Ctrl+C to stop)...")
                while True:
                    line = f.readline()
                    if line:
                        print(line.rstrip())
                    else:
                        import time
                        time.sleep(0.1)
            else:
                # Read last N lines
                all_lines = f.readlines()
                start_line = max(0, len(all_lines) - lines)
                
                for line in all_lines[start_line:]:
                    print(line.rstrip())
                    
    except KeyboardInterrupt:
        print("\n⏹️  Stopped following log file.")
    except Exception as e:
        print(f"❌ Error reading log file: {e}")


def search_logs(search_term, filename=None, case_sensitive=False):
    """Search for specific terms in log files."""
    logs_dir = Path("./logs")
    
    if not logs_dir.exists():
        print("❌ Logs directory does not exist.")
        return
    
    print(f"🔍 Searching for: '{search_term}'")
    if filename:
        print(f"📄 In file: {filename}")
    else:
        print("📄 In all log files")
    print("-" * 80)
    
    search_files = [logs_dir / filename] if filename else logs_dir.glob("*")
    
    for log_file in search_files:
        if not log_file.is_file():
            continue
            
        print(f"\n📄 Searching in: {log_file.name}")
        print("-" * 40)
        
        try:
            with open(log_file, 'r') as f:
                line_number = 0
                found_count = 0
                
                for line in f:
                    line_number += 1
                    search_line = line if case_sensitive else line.lower()
                    search_term_lower = search_term if case_sensitive else search_term.lower()
                    
                    if search_term_lower in search_line:
                        found_count += 1
                        print(f"Line {line_number}: {line.rstrip()}")
                        
                        if found_count >= 20:  # Limit results per file
                            print(f"... and {found_count - 20} more matches")
                            break
                            
        except Exception as e:
            print(f"❌ Error reading {log_file.name}: {e}")


def analyze_logs(filename=None):
    """Analyze log files for patterns and statistics."""
    logs_dir = Path("./logs")
    
    if not logs_dir.exists():
        print("❌ Logs directory does not exist.")
        return
    
    print("📊 Log Analysis")
    print("-" * 50)
    
    analyze_files = [logs_dir / filename] if filename else logs_dir.glob("*.log")
    
    for log_file in analyze_files:
        if not log_file.is_file():
            continue
            
        print(f"\n📄 Analyzing: {log_file.name}")
        print("-" * 30)
        
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                
                # Basic statistics
                total_lines = len(lines)
                error_lines = sum(1 for line in lines if 'ERROR' in line)
                warning_lines = sum(1 for line in lines if 'WARNING' in line)
                info_lines = sum(1 for line in lines if 'INFO' in line)
                
                print(f"Total lines: {total_lines}")
                print(f"Error lines: {error_lines}")
                print(f"Warning lines: {warning_lines}")
                print(f"Info lines: {info_lines}")
                
                # Find most common log sources
                sources = {}
                for line in lines:
                    if ' - ' in line:
                        parts = line.split(' - ')
                        if len(parts) >= 3:
                            source = parts[1]
                            sources[source] = sources.get(source, 0) + 1
                
                if sources:
                    print("\nTop log sources:")
                    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True)[:5]:
                        print(f"  {source}: {count} lines")
                
                # Find recent activity
                recent_lines = lines[-10:] if lines else []
                if recent_lines:
                    print("\nRecent activity:")
                    for line in recent_lines:
                        print(f"  {line.rstrip()}")
                        
        except Exception as e:
            print(f"❌ Error analyzing {log_file.name}: {e}")


def main():
    parser = argparse.ArgumentParser(description="View and analyze Patent Research AI Agent logs")
    parser.add_argument("action", choices=["list", "view", "search", "analyze"], 
                       help="Action to perform")
    parser.add_argument("--file", "-f", help="Specific log file to work with")
    parser.add_argument("--lines", "-n", type=int, default=50, 
                       help="Number of lines to show (default: 50)")
    parser.add_argument("--follow", "-F", action="store_true", 
                       help="Follow log file (like tail -f)")
    parser.add_argument("--term", "-t", help="Search term")
    parser.add_argument("--case-sensitive", "-c", action="store_true", 
                       help="Case sensitive search")
    
    args = parser.parse_args()
    
    if args.action == "list":
        list_log_files()
    elif args.action == "view":
        if not args.file:
            print("❌ Please specify a log file with --file")
            return
        view_log_file(args.file, args.lines, args.follow)
    elif args.action == "search":
        if not args.term:
            print("❌ Please specify a search term with --term")
            return
        search_logs(args.term, args.file, args.case_sensitive)
    elif args.action == "analyze":
        analyze_logs(args.file)


if __name__ == "__main__":
    main() 