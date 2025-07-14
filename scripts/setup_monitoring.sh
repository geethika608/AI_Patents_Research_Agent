#!/bin/bash

# Setup script for Prometheus and Grafana monitoring

echo "🚀 Setting up Prometheus and Grafana monitoring..."

# Create necessary directories
mkdir -p monitoring/grafana/provisioning/datasources
mkdir -p monitoring/grafana/provisioning/dashboards
mkdir -p monitoring/grafana/dashboards

# Install prometheus_client if not already installed
uv add prometheus-client

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not available in PATH"
    echo ""
    echo "📋 To install Docker on macOS:"
    echo "   1. Visit https://docs.docker.com/desktop/install/mac-install/"
    echo "   2. Download and install Docker Desktop for Mac"
    echo "   3. Start Docker Desktop"
    echo "   4. Run this script again"
    echo ""
    echo "🔧 Alternative: Use local monitoring without Docker"
    echo "   Your application will still collect metrics and log them"
    echo "   You can view logs using: python scripts/view_logs.py"
    echo ""
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running"
    echo "   Please start Docker Desktop and try again"
    exit 1
fi

# Start Prometheus and Grafana using Docker Compose
echo "📊 Starting Prometheus and Grafana..."
docker compose -f docker-compose.monitoring.yml up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
docker compose -f docker-compose.monitoring.yml ps

echo ""
echo "✅ Monitoring setup complete!"
echo ""
echo "📊 Access URLs:"
echo "   Prometheus: http://localhost:9090"
echo "   Grafana:    http://localhost:3000 (admin/admin)"
echo ""
echo "🔧 Your application metrics will be available at:"
echo "   http://localhost:8000/metrics"
echo ""
echo "📈 To view the dashboard in Grafana:"
echo "   1. Go to http://localhost:3000"
echo "   2. Login with admin/admin"
echo "   3. Import the dashboard from monitoring/grafana/dashboards/"
echo ""
echo "🛑 To stop monitoring:"
echo "   docker compose -f docker-compose.monitoring.yml down" 