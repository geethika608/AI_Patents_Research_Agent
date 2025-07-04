import pytest
from patent_researcher_agent.core.models import PatentEntry, PatentEntryList, TrendSummary


class TestPatentEntry:
    """Test PatentEntry model validation."""
    
    def test_valid_patent_entry(self, sample_patent_data):
        """Test creating a valid patent entry."""
        patent = PatentEntry(**sample_patent_data)
        assert patent.title == "Test Patent"
        assert patent.year == 2023
        assert patent.inventors == "John Doe, Jane Smith"
    
    def test_invalid_year(self):
        """Test validation of year field."""
        invalid_data = {
            "title": "Test",
            "abstract": "Test",
            "summary": "Test",
            "year": 1800,  # Too old
            "inventors": "Test",
            "assignee": "Test",
            "classification": "Test"
        }
        with pytest.raises(ValueError):
            PatentEntry(**invalid_data)
    
    def test_missing_required_field(self):
        """Test that missing required fields raise validation error."""
        incomplete_data = {
            "title": "Test",
            "abstract": "Test",
            "summary": "Test",
            "year": 2023,
            "inventors": "Test",
            # Missing assignee and classification
        }
        with pytest.raises(ValueError):
            PatentEntry(**incomplete_data)


class TestPatentEntryList:
    """Test PatentEntryList model."""
    
    def test_valid_patent_list(self, sample_patent_data):
        """Test creating a valid patent list."""
        patent = PatentEntry(**sample_patent_data)
        patent_list = PatentEntryList(patents=[patent])
        assert len(patent_list.patents) == 1
        assert patent_list.patents[0].title == "Test Patent"


class TestTrendSummary:
    """Test TrendSummary model validation."""
    
    def test_valid_trend_summary(self, sample_trend_data):
        """Test creating a valid trend summary."""
        trend = TrendSummary(**sample_trend_data)
        assert len(trend.topics) == 2
        assert "AI" in trend.topics
        assert len(trend.keywords) == 2
    
    def test_empty_lists(self):
        """Test that empty lists are valid."""
        empty_data = {
            "topics": [],
            "keywords": [],
            "innovation_clusters": [],
        }
        trend = TrendSummary(**empty_data)
        assert trend.topics == []
        assert trend.keywords == [] 