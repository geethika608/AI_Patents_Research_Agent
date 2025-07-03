# crew.py

import mlflow

mlflow.crewai.autolog()

# Optional: Set a tracking URI and an experiment name if you have a tracking server
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("CrewAI")

import os
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
from pydantic import BaseModel, Field
from typing import List
# ------------------------
# Pydantic Models & Fields
# ------------------------

load_dotenv()

class PatentEntry(BaseModel):
    """
    Represents a summarized patent record retrieved in the fetch phase.
    """
    title: str = Field(description="Title of the patent")
    abstract: str = Field(description="Abstract of the patent")
    summary: str = Field(description="Detailed self-contained summary of the patent")
    year: int = Field(ge=1900, description="Year the patent was filed or published")
    inventors: str = Field(description="Comma-separated list of inventors")
    assignee: str = Field(description="Organization or entity assigned the patent")
    classification: str = Field(description="Patent classification code (e.g. CPC)")

class TrendSummary(BaseModel):
    """
    Summary of insights derived from a collection of patents during trend analysis.
    """
    topics: List[str] = Field(description="Emerging topics or technical domains")
    keywords: List[str] = Field(description="Important keywords showing recent growth")
    innovation_clusters: List[str] = Field(description="Clusters of related inventions")
    top_assignees: List[str] = Field(description="Organizations with the most activity")


class PatentEntryList(BaseModel):
    """
    Wrapper for a list of patent entries.
    """
    patents: List[PatentEntry] = Field(description="List of patent entries")

# ------------------------
# CrewAI Setup
# ------------------------

@CrewBase
class PatentInnovationCrew:
    """Crew for patent-based innovation prediction with open-source tools."""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'


    # Memory configuration
    long_term_memory = LongTermMemory(storage=LTMSQLiteStorage(db_path="./memory/long_term.db"))
    short_term_memory = ShortTermMemory(
        storage=RAGStorage(
            embedder_config={
                "provider": "openai",
                "config": {"model": "text-embedding-3-small"}
            },
            type="short_term",
            path="./memory/short_term")
    )
    entity_memory = EntityMemory(
        storage=RAGStorage(
            embedder_config={
                "provider": "openai",
                "config": {"model": "text-embedding-3-small"}
            },
            type="entity",
            path="./memory/entity")
    )

    @agent
    def fetcher_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['fetcher_agent'],
            tools=[SerperDevTool()],
            memory=True,
        )

    @agent
    def analyzer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['analyzer_agent'],
            tools=[SerperDevTool()],
            memory=True,
        )

    @agent
    def reporter_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['reporter_agent'],
        )


    @task
    def fetch_patents(self) -> Task:
        return Task(
            config=self.tasks_config['fetch_patents'],
            output_pydantic=PatentEntryList,
        )

    @task
    def analyze_trends(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_innovation'],
            output_pydantic=TrendSummary,
        )

    @task
    def generate_report(self) -> Task:
        return Task(
            config=self.tasks_config['generate_report'],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            memory=True,
            long_term_memory=self.long_term_memory,
            short_term_memory=self.short_term_memory,
            entity_memory=self.entity_memory,
            embedder={
               "provider": "openai",
               "config": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "model": "text-embedding-3-small"
               }
            },
            verbose=True,
        )
