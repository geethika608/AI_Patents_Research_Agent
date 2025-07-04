from typing import Any, Dict, List
from datetime import datetime


def validate_research_area(research_area: str) -> bool:
    """
    Validate that the research area is not empty and has reasonable length.
    """
    if not research_area or not research_area.strip():
        return False
    
    if len(research_area.strip()) < 3:
        return False
    
    if len(research_area.strip()) > 500:
        return False
    
    return True


def validate_patent_data(patent_data: Dict[str, Any]) -> bool:
    """
    Validate patent data structure.
    """
    required_fields = ['title', 'summary', 'year', 'assignee']
    
    for field in required_fields:
        if field not in patent_data:
            return False
        
        if not patent_data[field]:
            return False
    
    # Validate year
    try:
        year = int(patent_data['year'])
        if year < 1900 or year > datetime.now().year + 1:
            return False
    except (ValueError, TypeError):
        return False
    
    return True


def validate_trend_data(trend_data: Dict[str, Any]) -> bool:
    """
    Validate trend analysis data structure.
    """
    required_fields = ['topics', 'keywords', 'innovation_clusters']
    
    for field in required_fields:
        if field not in trend_data:
            return False
        
        if not isinstance(trend_data[field], list):
            return False
    
    return True 