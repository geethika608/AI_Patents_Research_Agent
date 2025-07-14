import pytest
import os
from unittest.mock import patch
from patent_researcher_agent.utils.validators import validate_research_area, validate_patent_data, validate_trend_data
from patent_researcher_agent.utils.helpers import validate_required_env_vars, ensure_directory_exists


class TestValidators:
    """Test validation functions."""
    
    def test_validate_research_area_valid(self):
        """Test valid research area."""
        assert validate_research_area("AI in healthcare") == True
        assert validate_research_area("Machine learning algorithms") == True
    
    def test_validate_research_area_invalid(self):
        """Test invalid research area."""
        assert validate_research_area("") == False
        assert validate_research_area("ab") == False  # Too short
        assert validate_research_area("x" * 501) == False  # Too long
    
    def test_validate_patent_data_valid(self, sample_patent_data):
        """Test valid patent data."""
        assert validate_patent_data(sample_patent_data) == True
    
    def test_validate_patent_data_invalid(self):
        """Test invalid patent data."""
        invalid_data = {
            "title": "",  # Empty title
            "abstract": "Test",
            "summary": "Test",
            "year": 2023,
            "inventors": "Test",
            "assignee": "Test",
            "classification": "Test"
        }
        assert validate_patent_data(invalid_data) == False
    
    def test_validate_trend_data_valid(self, sample_trend_data):
        """Test valid trend data."""
        assert validate_trend_data(sample_trend_data) == True
    
    def test_validate_trend_data_invalid(self):
        """Test invalid trend data."""
        invalid_data = {
            "topics": "not a list",  # Should be list
            "keywords": [],
            "innovation_clusters": [],
        }
        assert validate_trend_data(invalid_data) == False


class TestHelpers:
    """Test helper functions."""
    
    def test_validate_required_env_vars_success(self):
        """Test successful environment validation."""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            validate_required_env_vars(["TEST_VAR"])  # Should not raise
    
    def test_validate_required_env_vars_missing(self):
        """Test missing environment variable."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                validate_required_env_vars(["MISSING_VAR"])
    
    def test_ensure_directory_exists(self, temp_dir):
        """Test directory creation."""
        new_dir = temp_dir / "test_dir"
        ensure_directory_exists(str(new_dir))
        assert new_dir.exists()
        assert new_dir.is_dir() 