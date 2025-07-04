#!/bin/bash

# Setup script for local monitoring (without Docker)

echo "🚀 Setting up local monitoring..."

# Create necessary directories
mkdir -p monitoring/logs
mkdir -p monitoring/metrics

# Install prometheus_client if not already installed
uv add prometheus-client

# Create a simple metrics endpoint script
cat > monitoring/simple_metrics_server.py << 'EOF'
#!/usr/bin/env python3
"""
Simple metrics server for local monitoring
"""
import http.server
import socketserver
import json
import os
from datetime import datetime
from pathlib import Path

class MetricsHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            
            # Read metrics from file if it exists
            metrics_file = Path("monitoring/metrics/current_metrics.json")
            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    metrics = json.load(f)
                
                # Format as Prometheus metrics
                response = []
                for metric_name, value in metrics.items():
                    response.append(f"# HELP {metric_name} {metric_name}")
                    response.append(f"# TYPE {metric_name} gauge")
                    response.append(f"{metric_name} {value}")
                
                self.wfile.write('\n'.join(response).encode())
            else:
                self.wfile.write(b"# No metrics available yet\n")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")

def run_server(port=8000):
    with socketserver.TCPServer(("", port), MetricsHandler) as httpd:
        print(f"📊 Metrics server running on http://localhost:{port}")
        print("   Access metrics at: http://localhost:8000/metrics")
        print("   Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Stopping metrics server...")

if __name__ == "__main__":
    run_server()
EOF

# Make the script executable
chmod +x monitoring/simple_metrics_server.py

echo ""
echo "✅ Local monitoring setup complete!"
echo ""
echo "📊 Your application will collect metrics and log them to:"
echo "   - Logs: monitoring/logs/"
echo "   - Metrics: monitoring/metrics/"
echo ""
echo "🔧 To view logs:"
echo "   python scripts/view_logs.py"
echo ""
echo "📈 To start a simple metrics server:"
echo "   python monitoring/simple_metrics_server.py"
echo ""
echo "📋 To view metrics in browser:"
echo "   http://localhost:8000/metrics"
echo ""
echo "💡 For full monitoring with Prometheus and Grafana:"
echo "   1. Install Docker Desktop"
echo "   2. Run: ./scripts/setup_monitoring.sh" 