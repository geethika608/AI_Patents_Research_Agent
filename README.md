# Patent Research AI Agent

This is the refactored version of the Patent Research AI Agent with improved modularity and scalability. The refactored structure maintains all existing functionality while providing better organization and extensibility.

## 🏗️ Architecture

### Modular Structure

```
patent_researcher_agent_refactored/
├── src/patent_researcher_agent/
│   ├── core/                    # Core business logic
│   │   ├── models/             # Pydantic models (self-sufficient)
│   │   └── tools/              # Custom tools
│   ├── ui/                     # UI components
│   │   ├── components/         # Reusable UI components
│   │   └── themes/             # UI themes
│   ├── utils/                  # Utility functions
│   ├── config/                 # Configuration
│   ├── crew.py                 # Main crew with agents/tasks
│   ├── main.py                 # Entry point
│   └── launch_chat.py          # Chat launcher
├── tests/                      # Test suite
├── docs/                       # Documentation
├── scripts/                    # Utility scripts
├── docker/                     # Docker configuration
├── deployment/                 # Deployment configs
├── monitoring/                 # Monitoring & logging
└── data/                       # Data storage
```

## 🚀 Key Improvements

### 1. **Modular Design**
- **Separation of Concerns**: Each component has a single responsibility
- **Reusable Components**: Models and tools can be easily reused
- **Clear Dependencies**: Explicit import structure

### 2. **Scalability**
- **Easy Extension**: Add new agents, tasks, or tools without modifying existing code
- **Plugin Architecture**: Modular components can be swapped or extended
- **Self-Sufficient Models**: Pydantic models handle validation and data structure
- **CrewAI Integration**: Uses CrewAI's built-in YAML config handling

### 3. **Maintainability**
- **Clear Structure**: Intuitive folder organization
- **Testability**: Each module can be tested independently
- **Documentation**: Comprehensive documentation structure

### 4. **Development Experience**
- **Hot Reloading**: Development-friendly structure
- **Debugging**: Clear module boundaries
- **Build Automation**: Makefile for common tasks

### 5. **Production Ready**
- **Health Monitoring**: Automated health checks and monitoring
- **Rate Limiting**: Configurable API rate limiting
- **Structured Logging**: Production-ready logging with structlog
- **Error Handling**: Comprehensive error handling and validation
- **Testing**: Unit and integration tests with coverage
- **Enhanced Monitoring**: Real-time performance tracking and metrics
- **Circuit Breakers**: Fault tolerance for external APIs
- **Retry Logic**: Exponential backoff for transient failures
- **Monitoring Dashboard**: Real-time observability interface

## 📦 Installation

```bash
# Clone the repository
git clone <repository-url>
cd patent_researcher_agent_refactored

# Install dependencies
pip install -e .

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

## 🏃‍♂️ Usage

### Running the Application

```bash
# Method 1: Using the main script
python src/patent_researcher_agent/main.py

# Method 2: Using the chat launcher
python src/patent_researcher_agent/launch_chat.py

# Method 3: Using Makefile
make chat
```

### Development Commands

```bash
# Setup development environment
make setup

# Run tests
make test

# Format code
make format

# Lint code
make lint

# Clean up
make clean

# Health check
make health-check

# Create backup
make backup

# Monitoring commands
make monitoring              # Run monitoring check
make monitoring-continuous   # Start continuous monitoring
make monitoring-export       # Export metrics
make dashboard               # Launch monitoring dashboard
```

### Docker Deployment

```bash
# Build and run with Docker Compose
cd docker
docker-compose up --build

# Or build and run manually
docker build -t patent-researcher-agent .
docker run -p 7860:7860 patent-researcher-agent
```

## 📊 Monitoring

The application includes comprehensive monitoring capabilities with multiple setup options:

### Option 1: Local Monitoring (Recommended for Development)

```bash
# Setup local monitoring (no Docker required)
./scripts/setup_local_monitoring.sh

# View logs
python scripts/view_logs.py

# Start simple metrics server
python monitoring/simple_metrics_server.py

# Access metrics in browser
# http://localhost:8000/metrics
```

### Option 2: Full Monitoring with Prometheus & Grafana

```bash
# Install Docker Desktop first (if not installed)
# Visit: https://docs.docker.com/desktop/install/mac-install/

# Setup full monitoring stack
./scripts/setup_monitoring.sh

# Access monitoring dashboards:
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000 (admin/admin)
```

### Monitoring Features

- **Real-time Metrics**: Agent execution times, success rates, error counts
- **Structured Logging**: JSON-formatted logs with rotation
- **Performance Tracking**: MLflow integration for experiment tracking
- **Health Checks**: Automated system health monitoring
- **Event Listeners**: CrewAI event-driven monitoring
- **Error Tracking**: Comprehensive error handling and reporting

### Available Metrics

- `agent_execution_duration_seconds`
- `agent_execution_success_total`
- `agent_execution_error_total`
- `task_execution_duration_seconds`
- `crew_execution_duration_seconds`
- `api_request_duration_seconds`
- `rate_limit_hits_total`

## 🔧 Configuration

Create a `.env` file based on `.env.example`:

```bash
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
SERPER_API_KEY=your_serper_api_key_here

# Application Settings
DEBUG=True
LOG_LEVEL=INFO

# Rate Limiting
MAX_RESEARCH_REQUESTS=5
RESEARCH_TIME_WINDOW=300
```

### Agent Configuration

Modify `src/patent_researcher_agent/config/agents.yaml` to customize agent behavior.

### Task Configuration

Modify `src/patent_researcher_agent/config/tasks.yaml` to customize task definitions.

## 🧪 Testing

The refactored structure includes a comprehensive test suite:

```bash
# Run all tests
make test

# Run specific test categories
make test-unit
make test-integration

# Run with coverage
pytest tests/ -v --cov=src/patent_researcher_agent --cov-report=html
```

## 📚 Documentation

- **User Guide**: `docs/user_guide/README.md`
- **Production Guide**: `docs/PRODUCTION.md`
- **Architecture**: `docs/architecture/README.md`
- **Developer Guide**: `docs/developer_guide/README.md`
- **Main Docs**: `docs/README.md`

## 🔄 Migration from Original

The refactored version maintains 100% compatibility with the original:

- **Same Functionality**: All features work exactly as before
- **Same API**: No changes to external interfaces
- **Same Configuration**: Uses the same YAML configs
- **Same UI**: Identical Gradio interface

### Key Differences

1. **Better Organization**: Code is now organized into logical modules
2. **Improved Maintainability**: Easier to understand and modify
3. **Enhanced Extensibility**: Simple to add new features
4. **Better Testing**: Modular structure enables comprehensive testing
5. **Self-Sufficient Models**: Pydantic models handle validation without additional service layer
6. **CrewAI Integration**: Uses CrewAI's built-in YAML config handling for agents and tasks
7. **Production Ready**: Comprehensive logging, validation, error handling, and real-time monitoring

## 🚀 Future Enhancements

The refactored structure enables easy addition of:

- **New Agents**: Add specialized research agents
- **New Tasks**: Implement additional analysis tasks
- **Custom Tools**: Create domain-specific tools
- **API Layer**: Add REST API endpoints
- **Web UI**: Expand beyond Gradio interface
- **Microservices**: Split into separate services

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the documentation in `docs/`
- Review the production guide
- Open an issue on GitHub 