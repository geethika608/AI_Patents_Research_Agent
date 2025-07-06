# Docker Guide - Patent Research AI Agent

This guide provides instructions for running the Patent Research AI Agent using Docker.

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API Key (required)
- Serper API Key (optional, for enhanced search)

## Quick Start

### 1. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Create .env file
cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key_here
SERPER_API_KEY=your_serper_api_key_here
EOF
```

### 2. Build and Run

```bash
# Navigate to the project directory
cd patent_researcher_agent

# Build and run with Docker Compose
docker-compose -f docker/docker-compose.yml up --build
```

### 3. Access the Application

- **Main Application**: http://localhost:7860
- **MLflow Dashboard**: http://localhost:5000

## How Package Management Works in Docker

The Dockerfile uses the project's package manager to:

1. **Install Package Manager**: Installs the required package manager
2. **Create Virtual Environment**: Creates a virtual environment directory
3. **Install Dependencies**: Installs the project and its dependencies
4. **Activate Environment**: Sets up the virtual environment in the container

## Detailed Setup Options

### Option A: Basic Application Only

```bash
# Build and run the main application
docker-compose -f docker/docker-compose.yml up --build -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f
```

### Option B: Application with Full Monitoring

```bash
# Run the main application
docker-compose -f docker/docker-compose.yml up --build -d

# Run monitoring stack (Prometheus + Grafana)
docker-compose -f docker-compose.monitoring.yml up -d
```

### Option C: Manual Docker Commands

```bash
# Build the image
docker build -f docker/Dockerfile -t patent-researcher-agent .

# Run the container
docker run -d \
  --name patent-agent \
  -p 7860:7860 \
  -e OPENAI_API_KEY=your_key \
  -e SERPER_API_KEY=your_key \
  -v $(pwd)/memory:/app/memory \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/knowledge:/app/knowledge \
  -v $(pwd)/logs:/app/logs \
  patent-researcher-agent
```

## Development

### Local Development (without Docker)

If you want to develop locally:

```bash
# Install uv locally
pip install uv

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Run the application
python src/patent_researcher_agent/launch_chat.py
```

### Development with Docker

For development with live code changes:

```bash
# Run with volume mounting for live code changes
docker run -d \
  --name patent-agent-dev \
  -p 7860:7860 \
  -e OPENAI_API_KEY=your_key \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/memory:/app/memory \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/logs:/app/logs \
  patent-researcher-agent
```

## Package Management Commands in Docker

You can execute package management commands inside the running container:

```bash
# Access the container shell
docker exec -it patent-researcher-agent /bin/bash

# Inside the container, you can use uv commands:
uv pip list                    # List installed packages
uv pip install new-package     # Install new package
uv pip uninstall package       # Uninstall package
uv pip freeze                  # Show requirements
```

## Monitoring Setup

### Full Monitoring Stack

```bash
# Start all services including monitoring
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.monitoring.yml up -d
```

### Access Monitoring Dashboards

- **Grafana**: http://localhost:3000
  - Username: `admin`
  - Password: `admin`
- **Prometheus**: http://localhost:9090

## Troubleshooting

### Common Issues

#### 1. Virtual Environment Issues

If you encounter virtual environment problems:

```bash
# Check if virtual environment is created
docker exec patent-researcher-agent ls -la /app/.venv

# Recreate virtual environment
docker exec patent-researcher-agent bash -c "cd /app && rm -rf .venv && uv venv && . .venv/bin/activate && uv pip install -e ."
```

#### 2. Dependency Installation Issues

```bash
# Check installed packages
docker exec patent-researcher-agent uv pip list

# Reinstall dependencies
docker exec patent-researcher-agent bash -c "cd /app && . .venv/bin/activate && uv pip install -e . --force-reinstall"
```

#### 3. Port Already in Use

```bash
# Check what's using port 7860
lsof -i :7860

# Use a different port
docker run -p 7861:7860 patent-researcher-agent
```

#### 4. API Key Issues

```bash
# Check environment variables
docker exec patent-researcher-agent env | grep API_KEY

# Restart with correct keys
docker-compose down
docker-compose up --build
```

#### 5. Permission Issues

```bash
# Fix volume permissions
sudo chown -R $USER:$USER memory output knowledge logs
```

### Useful Docker Commands

```bash
# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# View container logs
docker logs -f patent-researcher-agent

# Execute commands in running container
docker exec -it patent-researcher-agent /bin/bash

# Stop and remove containers
docker-compose down

# Remove all containers and images
docker system prune -a
```

## Production Deployment

For production deployment with UV:

```bash
# Build production image
docker build -f docker/Dockerfile -t patent-researcher-agent:latest .

# Run with production settings
docker run -d \
  --name patent-agent-prod \
  -p 7860:7860 \
  -e OPENAI_API_KEY=your_production_key \
  -e LOG_LEVEL=INFO \
  -e DEBUG=false \
  -v /path/to/production/data:/app/memory \
  -v /path/to/production/output:/app/output \
  --restart unless-stopped \
  patent-researcher-agent:latest
```

## Health Checks

```bash
# Check if containers are running
docker ps

# Run health check
docker exec patent-researcher-agent python scripts/health_check.py

# Check application status
curl http://localhost:7860

# Check package environment
docker exec patent-researcher-agent uv pip list
```

## Stopping the Application

```bash
# Stop all services
docker-compose -f docker/docker-compose.yml down
docker-compose -f docker-compose.monitoring.yml down

# Or stop everything at once
docker-compose -f docker/docker-compose.yml -f docker-compose.monitoring.yml down
```

## File Structure

The Docker setup with UV creates the following structure:

```
patent_researcher_agent/
├── .venv/           # UV virtual environment (inside container)
├── memory/          # Persistent memory storage
├── output/          # Generated outputs
├── knowledge/       # Knowledge base
├── logs/           # Application logs
├── mlartifacts/    # MLflow artifacts
└── mlruns/         # MLflow runs
```

## Environment Variables

Available environment variables:

- `OPENAI_API_KEY`: Required OpenAI API key
- `SERPER_API_KEY`: Optional Serper API key
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `DEBUG`: Enable debug mode (true/false)
- `VIRTUAL_ENV`: UV virtual environment path (set automatically)
- `PATH`: Includes UV virtual environment bin directory

## Package Management Benefits

Using the project's package manager in Docker provides:

1. **Fast Installation**: UV is significantly faster than pip
2. **Reliable Dependencies**: Better dependency resolution
3. **Virtual Environment**: Isolated Python environment
4. **Lock File**: Reproducible builds with `uv.lock`
5. **Modern Tooling**: Latest Python packaging standards

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review container logs: `docker logs patent-researcher-agent`
3. Verify environment variables are set correctly
4. Check package manager installation: `docker exec patent-researcher-agent uv --version`
5. Ensure Docker and Docker Compose are up to date 