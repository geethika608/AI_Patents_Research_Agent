import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# Set test environment
os.environ["TESTING"] = "true"
os.environ["OPENAI_API_KEY"] = "test_key"
os.environ["SERPER_API_KEY"] = "test_key"


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def mock_crew():
    """Mock crew for testing."""
    with patch('patent_researcher_agent.crew.PatentInnovationCrew') as mock:
        crew_instance = Mock()
        mock.return_value.crew.return_value = crew_instance
        yield mock


@pytest.fixture
def sample_patent_data():
    """Sample patent data for testing."""
    return {
        "title": "Test Patent",
        "summary": "This is a detailed summary of the test patent",
        "year": 2023,
        "assignee": "Test Corp",
    }


@pytest.fixture
def sample_trend_data():
    """Sample trend data for testing."""
    return {
        "topics": ["AI", "Healthcare"],
        "keywords": ["machine learning", "diagnosis"],
        "innovation_clusters": ["AI in Healthcare"],
    }
