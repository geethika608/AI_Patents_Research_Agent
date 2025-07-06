# Developer Guide - Patent Research AI Agent

Comprehensive developer documentation for the Patent Research AI Agent project.

## 🏗️ Project Overview

The Patent Research AI Agent is a modular, production-ready AI application built with:
- **CrewAI**: Multi-agent orchestration framework
- **Gradio**: Web-based user interface
- **Pydantic**: Data validation and settings management
- **structlog**: Structured logging
- **Docker**: Containerization and deployment

## 🚀 Quick Start for Developers

### Prerequisites
- Python 3.10-3.13
- Git
- Docker (optional, for containerized development)
- OpenAI API key

### Setup Development Environment

1. **Clone the repository**
```bash
git clone <repository-url>
cd patent_researcher_agent
```

2. **Install dependencies**
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Run the application**
```bash
# Development mode
python -m patent_researcher_agent.main

# Or using the script
python -m patent_researcher_agent.launch_chat
```

## 📁 Project Structure

```
patent_researcher_agent/
├── src/patent_researcher_agent/
│   ├── core/                    # Core business logic
│   │   ├── models/             # Pydantic data models
│   │   └── tools/              # CrewAI tools
│   ├── ui/                     # User interface
│   │   ├── components/         # Reusable UI components
│   │   └── themes/             # UI theming
│   ├── utils/                  # Utility functions
│   ├── config/                 # Configuration management
│   ├── crew.py                 # Main CrewAI crew
│   ├── main.py                 # Application entry point
│   └── launch_chat.py          # Chat interface launcher
├── tests/                      # Test suite
├── docs/                       # Documentation
├── scripts/                    # Utility scripts
├── docker/                     # Docker configuration
├── deployment/                 # Deployment configurations
└── monitoring/                 # Monitoring and logging
```

## 🔧 Development Workflow

### Code Style and Standards

#### Python Code Style
- **Formatter**: Black
- **Linter**: Ruff
- **Type Checking**: mypy
- **Import Sorting**: isort

#### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

#### Code Quality Commands
```bash
# Format code
make format

# Lint code
make lint

# Type check
make type-check

# Run all quality checks
make quality
```

### Testing

#### Running Tests
```bash
# Run all tests
make test

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Run with coverage
make test-coverage

# Run specific test file
pytest tests/unit/test_models.py
```

#### Test Structure
```
tests/
├── unit/                       # Unit tests
│   ├── test_models.py         # Model tests
│   ├── test_utils.py          # Utility tests
│   └── test_crew.py           # Crew tests
├── integration/                # Integration tests
├── fixtures/                   # Test fixtures
└── conftest.py                # Pytest configuration
```

#### Writing Tests
```python
import pytest
from patent_researcher_agent.core.models.patent import PatentEntry

def test_patent_entry_creation():
    """Test PatentEntry model creation and validation."""
    patent = PatentEntry(
        title="Test Patent",
        abstract="Test abstract",
        summary="Test summary",
        year=2023,
        inventors=["John Doe"],
        assignee="Test Corp",
        classification="A01B 1/00"
    )
    
    assert patent.title == "Test Patent"
    assert patent.year == 2023
    assert len(patent.inventors) == 1
```

### Debugging

#### Logging
The project uses structured logging with structlog:

```python
from patent_researcher_agent.utils.logger import get_logger

logger = get_logger(__name__)

def my_function():
    logger.info("Processing request", user_id="123", action="research")
    try:
        # Your code here
        logger.info("Request completed successfully")
    except Exception as e:
        logger.error("Request failed", error=str(e), exc_info=True)
```

#### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with debug output
python -m patent_researcher_agent.main --debug
```

## 🧩 Core Components

### Models (`core/models/`)

#### PatentEntry Model
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class PatentEntry(BaseModel):
    title: str = Field(..., description="Patent title")
    abstract: str = Field(..., description="Patent abstract")
    summary: str = Field(..., description="Detailed summary")
    year: int = Field(..., description="Patent year")
    inventors: List[str] = Field(default_factory=list)
    assignee: Optional[str] = None
    classification: Optional[str] = None
```

#### Adding New Models
1. Create new model file in `core/models/`
2. Define Pydantic model with proper validation
3. Add to `core/models/__init__.py`
4. Write unit tests
5. Update documentation

### CrewAI Integration (`crew.py`)

#### Agent Definition
```python
from crewai import Agent

def create_fetcher_agent():
    return Agent(
        role="Patent Research Specialist",
        goal="Find and analyze relevant patents",
        backstory="Expert in patent research and analysis",
        verbose=True,
        allow_delegation=False,
        tools=[search_tool, analyze_tool]
    )
```

#### Task Definition
```python
from crewai import Task

def create_fetch_task(agent, research_area):
    return Task(
        description=f"Search for patents related to {research_area}",
        agent=agent,
        expected_output="List of relevant patents with summaries",
        context=f"Research area: {research_area}"
    )
```

#### Adding New Agents/Tasks
1. Define agent in `crew.py`
2. Create corresponding task
3. Add to crew workflow
4. Update configuration if needed
5. Test integration

### UI Components (`ui/`)

#### Creating New Components
```python
import gradio as gr

def create_custom_component():
    """Create a custom Gradio component."""
    with gr.Box():
        gr.Markdown("## Custom Component")
        input_field = gr.Textbox(label="Input")
        output_field = gr.Textbox(label="Output")
        
    return input_field, output_field
```

#### UI Best Practices
- Use consistent styling
- Implement proper error handling
- Add loading states
- Provide user feedback
- Follow accessibility guidelines

### Utilities (`utils/`)

#### Adding New Utilities
1. Create utility function in appropriate file
2. Add proper type hints
3. Include docstrings
4. Write unit tests
5. Update imports if needed

#### Example Utility
```python
from typing import List, Dict, Any
import re

def validate_research_area(research_area: str) -> Dict[str, Any]:
    """
    Validate research area input.
    
    Args:
        research_area: The research area to validate
        
    Returns:
        Dict with validation result and any errors
    """
    errors = []
    
    if len(research_area) < 3:
        errors.append("Research area must be at least 3 characters")
    
    if len(research_area) > 500:
        errors.append("Research area must be less than 500 characters")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
```

## 🔧 Configuration Management

### Settings (`config/settings.py`)

#### Environment Variables
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    log_level: str = "INFO"
    max_research_requests: int = 5
    request_timeout: int = 300
    
    class Config:
        env_file = ".env"
```

#### Adding New Settings
1. Add field to Settings class
2. Set default value if needed
3. Add to environment file template
4. Update documentation
5. Test configuration loading

### YAML Configuration

#### Agents Configuration (`config/agents.yaml`)
```yaml
agents:
  fetcher:
    role: "Patent Research Specialist"
    goal: "Find and analyze relevant patents"
    backstory: "Expert in patent research and analysis"
    
  analyzer:
    role: "Patent Analyst"
    goal: "Analyze patent trends and patterns"
    backstory: "Specialist in trend analysis and market insights"
```

#### Tasks Configuration (`config/tasks.yaml`)
```yaml
tasks:
  fetch_patents:
    description: "Search for patents related to {research_area}"
    expected_output: "List of relevant patents with summaries"
    
  analyze_trends:
    description: "Analyze trends in the patent data"
    expected_output: "Trend analysis report with insights"
```

## 🧪 Testing Strategy

### Unit Testing
- **Models**: Test data validation and serialization
- **Utilities**: Test helper functions and validators
- **Configuration**: Test settings loading and validation

### Integration Testing
- **CrewAI Workflow**: Test complete agent workflow
- **UI Integration**: Test Gradio interface
- **API Integration**: Test external API calls

### Test Fixtures
```python
# tests/fixtures/patent_data.py
import pytest
from patent_researcher_agent.core.models.patent import PatentEntry

@pytest.fixture
def sample_patent():
    return PatentEntry(
        title="Test Patent",
        abstract="Test abstract",
        summary="Test summary",
        year=2023,
        inventors=["John Doe"],
        assignee="Test Corp"
    )

@pytest.fixture
def sample_patent_list(sample_patent):
    return [sample_patent]
```

### Mocking External Services
```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_openai_client():
    with patch("openai.OpenAI") as mock:
        mock.return_value.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Mock response"))]
        )
        yield mock
```

## 📊 Monitoring and Observability

### Health Checks
```python
from patent_researcher_agent.utils.health_check import HealthChecker

def check_system_health():
    checker = HealthChecker()
    status = checker.check_all()
    
    if not status["healthy"]:
        logger.error("System health check failed", issues=status["issues"])
        return False
    
    return True
```

### Metrics Collection
```python
import time
from functools import wraps

def track_metrics(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            logger.info("Function completed", 
                       function=func.__name__,
                       duration=duration,
                       success=True)
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error("Function failed",
                        function=func.__name__,
                        duration=duration,
                        error=str(e))
            raise
    return wrapper
```

## 🚀 Deployment

### Docker Development
```bash
# Build development image
docker build -f docker/Dockerfile.dev -t patent-agent-dev .

# Run development container
docker run -p 7860:7860 -e OPENAI_API_KEY=your_key patent-agent-dev
```

### Production Deployment
```bash
# Build production image
docker build -f docker/Dockerfile -t patent-agent-prod .

# Run with docker-compose
docker-compose up -d
```

### Environment Configuration
```bash
# Production environment
export ENVIRONMENT=production
export LOG_LEVEL=INFO
export MAX_WORKERS=4
export OPENAI_API_KEY=your_production_key
```

## 🔒 Security Considerations

### Input Validation
- Validate all user inputs
- Sanitize data before processing
- Implement rate limiting
- Log security events

### API Key Management
- Use environment variables for secrets
- Rotate keys regularly
- Monitor API usage
- Implement key validation

### Error Handling
```python
def safe_api_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error("API call failed", 
                        function=func.__name__,
                        error=str(e))
            # Don't expose internal errors to users
            raise ValueError("Service temporarily unavailable")
    return wrapper
```

## 📚 Documentation

### Code Documentation
- Use docstrings for all functions and classes
- Follow Google docstring format
- Include type hints
- Document exceptions and edge cases

### API Documentation
- Document all public interfaces
- Include usage examples
- Specify parameter types and constraints
- Document return values and errors

### Architecture Documentation
- Keep architecture docs up to date
- Document design decisions
- Include sequence diagrams for complex flows
- Maintain dependency graphs

## 🔄 Contributing

### Development Process
1. **Create feature branch** from main
2. **Implement changes** with tests
3. **Run quality checks** (linting, formatting, tests)
4. **Update documentation** as needed
5. **Create pull request** with description
6. **Code review** and approval
7. **Merge to main** after approval

### Commit Guidelines
```
feat: add new patent analysis feature
fix: resolve memory leak in crew processing
docs: update user guide with new features
test: add unit tests for validation utilities
refactor: improve error handling in UI
```

### Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes
```

## 🆘 Getting Help

### Resources
- **Documentation**: Check this guide and other docs
- **Code Comments**: Read inline documentation
- **Tests**: Review test cases for usage examples
- **Issues**: Check existing issues and discussions

### Support Channels
- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas
- **Code Review**: For implementation guidance
- **Team Chat**: For quick questions

### Debugging Tips
1. **Check logs** for error messages
2. **Use debug mode** for detailed output
3. **Test components** in isolation
4. **Verify configuration** is correct
5. **Check dependencies** are installed

---

This developer guide provides comprehensive information for developers working on the Patent Research AI Agent project. 