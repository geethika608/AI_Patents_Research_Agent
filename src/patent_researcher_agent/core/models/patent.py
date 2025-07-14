from pydantic import BaseModel, Field
from typing import List


class PatentEntry(BaseModel):
    """
    Represents a summarized patent record retrieved in the fetch phase.
    """
    title: str = Field(description="Title of the patent")
    summary: str = Field(description="Detailed self-contained summary of the patent")
    year: int = Field(ge=1900, description="Year the patent was filed or published")
    assignee: str = Field(description="Organization or entity assigned the patent")


class PatentEntryList(BaseModel):
    """
    Wrapper for a list of patent entries.
    """
    patents: List[PatentEntry] = Field(description="List of patent entries") 