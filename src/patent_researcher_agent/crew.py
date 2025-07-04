# crew_refactored.py

import mlflow
import os
import uuid
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage

# Import our modular components
from .core.models import PatentEntryList, TrendSummary
from .utils.logger import setup_logger
from .utils.validators import validate_research_area
from .utils.helpers import ensure_directory_exists, validate_required_env_vars
from .utils.prometheus_metrics import metrics
from .utils.error_handling import error_handler, AgentExecutionError, TaskExecutionError, WorkflowExecutionError
from .core.listeners import MonitoringEventListener
from .utils.workflow_tracker import register_workflow, unregister_workflow, is_workflow_active, workflow_tracker

# Create a global event listener instance that will be registered automatically
# This follows the CrewAI documentation pattern for event listener registration
global_event_listener = None

load_dotenv()

# Setup logger
logger = setup_logger(__name__)

# Configure MLflow for remote tracking
try:
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("CrewAI")
    mlflow.crewai.autolog()
    logger.info("MLflow remote tracking configured successfully")
except Exception as e:
    logger.warning(f"Failed to configure MLflow remote tracking: {e}")
    # Fallback to local tracking
    mlflow.set_tracking_uri("file:./mlruns")
    mlflow.set_experiment("CrewAI")
    mlflow.crewai.autolog()
    logger.info("MLflow local tracking configured as fallback")

# Validate required environment variables
validate_required_env_vars(["OPENAI_API_KEY"])


@CrewBase
class PatentInnovationCrew:
    """Crew for patent-based innovation prediction with open-source tools."""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # Memory configuration - Optimized for performance
    long_term_memory = LongTermMemory(
        storage=LTMSQLiteStorage(db_path="./memory/long_term.db")
    )
    short_term_memory = ShortTermMemory(
        storage=RAGStorage(
            embedder_config={
                "provider": "openai",
                "config": {"model": "text-embedding-3-small"}
            },
            type="short_term",
            path="./memory/short_term"
        )
    )
    entity_memory = EntityMemory(
        storage=RAGStorage(
            embedder_config={
                "provider": "openai",
                "config": {"model": "text-embedding-3-small"}
            },
            type="entity",
            path="./memory/entity"
        )
    )
    
    def __init__(self):
        """Initialize crew with monitoring and error handling."""
        self.workflow_id = None
        self.user_input = None
        
        # Metrics tracking handled by Prometheus monitoring
        

        
        logger.info("PatentInnovationCrew initialized with Prometheus monitoring")
    
    def start_workflow(self, user_input: str) -> str:
        """Start a new workflow with monitoring."""
        # Unregister any existing workflow first
        if hasattr(self, 'workflow_id') and self.workflow_id:
            unregister_workflow(self.workflow_id)
            logger.info(f"Unregistered previous workflow: {self.workflow_id}")
        
        self.workflow_id = str(uuid.uuid4())
        self.user_input = user_input
        
        logger.info(f"Workflow started: {self.workflow_id}")
        
        return self.workflow_id
    
    def end_workflow(self, success: bool, error_message: str = None):
        """End workflow with monitoring."""
        global global_event_listener
        
        if self.workflow_id:
            logger.info(f"Workflow ended: {self.workflow_id}, success: {success}")
            
            # Clean up the event listener for this workflow
            if global_event_listener and global_event_listener.workflow_id == self.workflow_id:
                global_event_listener.cleanup()
                global_event_listener = None
                logger.info(f"Cleaned up event listener for workflow: {self.workflow_id}")
            
            # Unregister from global workflow tracker
            unregister_workflow(self.workflow_id)
    


    @agent
    def fetcher_agent(self) -> Agent:
        logger.info("Creating fetcher agent")
        return Agent(
            config=self.agents_config['fetcher_agent'],
            tools=[SerperDevTool()],
        )

    @agent
    def analyzer_agent(self) -> Agent:
        logger.info("Creating analyzer agent")
        return Agent(
            config=self.agents_config['analyzer_agent'],
        )

    @agent
    def reporter_agent(self) -> Agent:
        logger.info("Creating reporter agent")
        return Agent(
            config=self.agents_config['reporter_agent'],
        )

    @task
    def fetch_patents(self) -> Task:
        logger.info("Creating fetch patents task")
        return Task(
            config=self.tasks_config['fetch_patents'],
            output_pydantic=PatentEntryList,
        )

    @task
    def analyze_trends(self) -> Task:
        logger.info("Creating analyze trends task")
        return Task(
            config=self.tasks_config['analyze_innovation'],
            output_pydantic=TrendSummary,
        )

    @task
    def generate_report(self) -> Task:
        logger.info("Creating generate report task")
        return Task(
            config=self.tasks_config['generate_report'],
        )

    @crew
    def crew(self) -> Crew:
        logger.info("Creating patent innovation crew")
        
        crew_kwargs = {
            "agents": self.agents,
            "tasks": self.tasks,
            "process": Process.sequential,
            "memory": True,
            "long_term_memory": self.long_term_memory,
            "short_term_memory": self.short_term_memory,
            "entity_memory": self.entity_memory,
            "embedder": {
               "provider": "openai",
               "config": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "model": "text-embedding-3-small"
               }
            },
            "verbose": True,
        }
        
        crew_instance = Crew(**crew_kwargs)
        
        # Create monitoring event listener if workflow_id is available
        global global_event_listener
        if self.workflow_id:
            try:
                # Check if this workflow is already active
                if is_workflow_active(self.workflow_id):
                    logger.info(f"Workflow {self.workflow_id} is already active, reusing existing listener")
                    global_event_listener = workflow_tracker.get_workflow_listener(self.workflow_id)
                else:
                    # Clear any existing listener first
                    if global_event_listener is not None:
                        logger.info(f"Clearing existing event listener for workflow: {global_event_listener.workflow_id}")
                        global_event_listener = None
                    
                    # Create new listener
                    global_event_listener = MonitoringEventListener(self.workflow_id)
                    
                    # Register with global workflow tracker
                    register_workflow(self.workflow_id, global_event_listener)
                    
                    logger.info(f"Prometheus monitoring event listener created for workflow: {self.workflow_id}")
            except Exception as e:
                logger.warning(f"Failed to create monitoring event listener: {e}")
        else:
            logger.info("Monitoring event listener not created (no workflow_id)")
        
        # Log the current state for debugging
        if global_event_listener:
            logger.info(f"Current event listener workflow_id: {global_event_listener.workflow_id}, listener_id: {global_event_listener.listener_id}")
        else:
            logger.info("No event listener available")
        
        return crew_instance 