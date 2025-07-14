from pydantic import BaseModel, Field
from typing import List


class TrendSummary(BaseModel):
    """
    Summary of insights derived from a collection of patents during trend analysis.
    """
    topics: List[str] = Field(description="Emerging topics or technical domains")
    keywords: List[str] = Field(description="Important keywords showing recent growth")
    innovation_clusters: List[str] = Field(description="Clusters of related inventions")
