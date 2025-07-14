"""
Evaluation module for Patent Research AI Agent using OpenAI.

This module provides comprehensive evaluation capabilities for patent research outputs
using OpenAI's GPT models. It evaluates the quality, relevance, accuracy, and strategic
value of patent research analyses across multiple dimensions.
"""

import os
import time
import json
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

from openai import OpenAI
import numpy as np

from .logger import setup_logger
from .prometheus_metrics import metrics

logger = setup_logger(__name__)

# =============================================================================
# EVALUATION DATA STRUCTURES
# =============================================================================

@dataclass
class EvaluationResult:
    """
    Result of an individual evaluation metric.
    
    This dataclass stores the results of evaluating a single aspect
    of a patent research output (e.g., relevance, accuracy, clarity).
    
    Attributes:
        metric_name (str): Name of the evaluation metric (e.g., 'relevance', 'accuracy')
        score (float): Numerical score from 0-10 for this metric
        explanation (str): Detailed explanation of the scoring rationale
        confidence (float): Confidence level in the evaluation (0-1, default: 1.0)
        metadata (Dict[str, Any]): Additional metadata about the evaluation
    """
    metric_name: str
    score: float
    explanation: str
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowEvaluation:
    """
    Complete evaluation of a workflow execution.
    
    This dataclass stores the comprehensive evaluation results for an entire
    patent research workflow, including all individual metric scores and
    overall performance metrics.
    
    Attributes:
        workflow_id (str): Unique identifier for the workflow
        timestamp (datetime): When the evaluation was performed
        user_input (str): Original user query that triggered the workflow
        agent_outputs (Dict[str, str]): Outputs from individual agents in the workflow
        final_output (str): Final consolidated output from the workflow
        evaluation_results (Dict[str, EvaluationResult]): Results for each evaluation metric
        overall_score (float): Weighted average of all metric scores
        evaluation_duration (float): Time taken to perform the evaluation
        metadata (Dict[str, Any]): Additional metadata about the workflow evaluation
    """
    workflow_id: str
    timestamp: datetime
    user_input: str
    agent_outputs: Dict[str, str]
    final_output: str
    evaluation_results: Dict[str, EvaluationResult]
    overall_score: float
    evaluation_duration: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class PatentResearchEvaluator:
    """
    Evaluator for Patent Research AI Agent using OpenAI.
    
    This class provides comprehensive evaluation capabilities for patent research outputs
    using OpenAI's GPT models. It evaluates outputs across multiple dimensions including
    relevance, completeness, accuracy, clarity, and innovation value.
    
    The evaluator uses carefully crafted prompts to ensure consistent and reliable
    evaluation of patent research quality, providing both numerical scores and
    detailed explanations for each evaluation metric.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the patent research evaluator.
        
        Args:
            openai_api_key (Optional[str]): OpenAI API key. If not provided, 
                                          will use OPENAI_API_KEY environment variable.
        """
        self.logger = logger
        # Initialize OpenAI client for evaluation requests
        self.openai_client = OpenAI(api_key=openai_api_key or os.getenv("OPENAI_API_KEY"))
        
        # Define evaluation metrics and prompts
        self.metrics = self._define_evaluation_metrics()
        
        # Performance tracking for monitoring evaluation efficiency
        self.evaluation_count = 0
        self.avg_evaluation_time = 0.0
        
    def _define_evaluation_metrics(self) -> Dict[str, Any]:
        """
        Define evaluation metrics and their corresponding prompts.
        
        Sets up the evaluation framework with prompts for each evaluation dimension.
        The prompts are designed to provide consistent and reliable evaluations
        of patent research outputs.
        
        Returns:
            Dict[str, Any]: Dictionary containing evaluation metric definitions
        """
        metrics_dict = {}
        
        # Define evaluation prompts for each metric
        self.evaluation_prompts = {
            "relevance": """You are evaluating the relevance of a patent research analysis to the user's query.

User Query: {user_input}

Patent Research Analysis: {output}

Rate the relevance from 0 to 10, where:
- 0: Completely irrelevant, doesn't address the query at all
- 5: Somewhat relevant, addresses part of the query with basic information
- 10: Highly relevant, directly and comprehensively addresses the query with detailed analysis

Consider:
- Does the analysis directly answer the user's research question?
- Are the patents and trends specifically related to the query topic?
- Does it provide actionable insights for the requested technology area?
- Is the information directly applicable to the user's research needs?

Provide only a number between 0 and 10 as your response.""",
            
            "completeness": """You are evaluating the comprehensiveness of a patent research analysis.

User Query: {user_input}

Patent Research Analysis: {output}

Rate the completeness from 0 to 10, where:
- 0: Very incomplete, missing most important aspects of patent analysis
- 5: Moderately complete, covers some key areas but lacks depth
- 10: Highly complete, comprehensive coverage with detailed insights

Consider:
- Does it include specific patent numbers and detailed descriptions?
- Are there multiple patent categories or technology areas covered?
- Does it provide both technical details and strategic insights?
- Are there sufficient examples and supporting evidence?
- Does it include recent patents and current trends?
- Are there actionable recommendations or strategic guidance?

Provide only a number between 0 and 10 as your response.""",
            
            "accuracy": """You are evaluating the accuracy and reliability of patent research information.

Patent Research Analysis: {output}

Rate the accuracy from 0 to 10, where:
- 0: Highly inaccurate, contains false or misleading patent information
- 5: Moderately accurate, some reliable information with potential errors
- 10: Highly accurate, all patent information appears reliable and well-researched

Consider:
- Are patent numbers in correct format (e.g., US20230077899A1, WO2023178317A1)?
- Do the patent descriptions match the actual technology areas?
- Is the technical information technically plausible and current?
- Are the trends and insights supported by the patent evidence?
- Are the strategic recommendations based on solid patent analysis?
- Is the information consistent throughout the analysis?

Provide only a number between 0 and 10 as your response.""",
            
            "clarity": """You are evaluating the clarity and professional presentation of a patent research analysis.

Patent Research Analysis: {output}

Rate the clarity from 0 to 10, where:
- 0: Very unclear, poorly organized, difficult to understand
- 5: Moderately clear, some parts are understandable but needs improvement
- 10: Very clear, well-structured, professional, and easy to follow

Consider:
- Is the language clear, professional, and appropriate for business/technical audience?
- Is the information well-organized with logical structure (summary, details, recommendations)?
- Are technical terms explained appropriately for the target audience?
- Is the structure logical with clear sections and flow?
- Are patent references clearly cited and easy to follow?
- Is the analysis presented in a way that supports decision-making?

Provide only a number between 0 and 10 as your response.""",
            
            "innovation": """You are evaluating the insightfulness and strategic value of patent research analysis.

Patent Research Analysis: {output}

Rate the innovation from 0 to 10, where:
- 0: No insights, just basic listing of patents without analysis
- 5: Some insights, basic trend analysis with limited strategic value
- 10: Highly innovative, deep insights with strategic recommendations and forward-looking analysis

Consider:
- Does it identify emerging technology trends and innovation patterns?
- Are there novel connections between different patents or technology areas?
- Does it provide strategic insights for investment or R&D decisions?
- Are there forward-looking predictions or market positioning analysis?
- Does it offer actionable strategic recommendations?
- Does it identify competitive advantages or market opportunities?
- Is there analysis of technology evolution and future directions?

Provide only a number between 0 and 10 as your response."""
        }
        
        return metrics_dict
    
    async def evaluate_workflow(self, 
                              workflow_id: str,
                              user_input: str,
                              agent_outputs: Dict[str, str],
                              final_output: str) -> WorkflowEvaluation:
        """
        Evaluate a complete workflow execution using OpenAI.
        
        This method performs comprehensive evaluation of a patent research workflow
        by assessing the final output across multiple quality dimensions. It uses
        OpenAI's GPT models to provide consistent, reliable evaluations with detailed
        explanations for each metric.
        
        Args:
            workflow_id (str): Unique identifier for the workflow being evaluated
            user_input (str): Original user query that triggered the workflow
            agent_outputs (Dict[str, str]): Outputs from individual agents in the workflow
            final_output (str): Final consolidated output from the workflow
            
        Returns:
            WorkflowEvaluation: Complete evaluation results including all metric scores
                               and overall performance assessment
        """
        start_time = time.time()
        self.logger.info(f"Starting evaluation for workflow: {workflow_id}")
        
        try:
            # Prepare evaluation data
            user_input_str = str(user_input) if user_input is not None else ""
            final_output_str = str(final_output) if final_output is not None else ""
            
            # Initialize results dictionary
            evaluation_results = {}
            
            # Evaluate each metric using OpenAI
            for metric_name, prompt_template in self.evaluation_prompts.items():
                try:
                    # Format the prompt with the appropriate variables
                    if metric_name in ["relevance", "completeness"]:
                        # These metrics need both user_input and output
                        prompt = prompt_template.format(
                            user_input=user_input_str,
                            output=final_output_str
                        )
                    else:
                        # These metrics only need output
                        prompt = prompt_template.format(output=final_output_str)
                    
                    # Call OpenAI API
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are an expert evaluator. Provide only a number between 0 and 10 as your response."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.1,
                        max_tokens=10
                    )
                    
                    # Extract the score from the response
                    score_text = response.choices[0].message.content.strip()
                    try:
                        score = float(score_text)
                        # Ensure score is between 0 and 10
                        score = max(0.0, min(10.0, score))
                        explanation = f"OpenAI evaluation score: {score}"
                    except ValueError:
                        self.logger.warning(f"Could not parse score '{score_text}' for {metric_name}, using default")
                        score = 5.0
                        explanation = f"Default evaluation score (parsing failed: {score_text})"
                    
                    evaluation_results[metric_name] = EvaluationResult(
                        metric_name=metric_name,
                        score=score,
                        explanation=explanation,
                        confidence=1.0,
                        metadata={
                            "workflow_id": workflow_id,
                            "metric_version": "1.0"
                        }
                    )
                    
                except Exception as e:
                    self.logger.warning(f"Failed to evaluate {metric_name}: {str(e)}")
                    evaluation_results[metric_name] = EvaluationResult(
                        metric_name=metric_name,
                        score=5.0,
                        explanation=f"Default evaluation score (evaluation failed: {str(e)})",
                        confidence=1.0,
                        metadata={
                            "workflow_id": workflow_id,
                            "metric_version": "1.0"
                        }
                    )
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(evaluation_results)
            
            # Create evaluation object
            evaluation = WorkflowEvaluation(
                workflow_id=workflow_id,
                timestamp=datetime.now(),
                user_input=user_input_str,
                agent_outputs=agent_outputs,
                final_output=final_output_str,
                evaluation_results=evaluation_results,
                overall_score=overall_score,
                evaluation_duration=time.time() - start_time,
                metadata={
                    "evaluator_version": "1.0",
                    "openai_model": "gpt-4"
                }
            )
            
            # Track metrics
            self._track_evaluation_metrics(evaluation)
            
            # Save evaluation results
            await self._save_evaluation_results(evaluation)
            
            self.logger.info(f"Evaluation completed for workflow: {workflow_id}, overall score: {overall_score:.2f}")
            return evaluation
            
        except Exception as e:
            self.logger.error(f"Evaluation failed for workflow {workflow_id}: {str(e)}")
            # Return a default evaluation with error information
            return WorkflowEvaluation(
                workflow_id=workflow_id,
                timestamp=datetime.now(),
                user_input=str(user_input) if user_input is not None else "",
                agent_outputs=agent_outputs,
                final_output=str(final_output) if final_output is not None else "",
                evaluation_results={},
                overall_score=0.0,
                evaluation_duration=time.time() - start_time,
                metadata={
                    "error": str(e),
                    "evaluator_version": "1.0"
                }
            )
    

    
    def _calculate_overall_score(self, evaluation_results: Dict[str, EvaluationResult]) -> float:
        """Calculate overall score as weighted average of individual metrics."""
        weights = {
            "relevance": 0.25,
            "completeness": 0.20,
            "accuracy": 0.25,
            "clarity": 0.15,
            "innovation": 0.15
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for metric_name, result in evaluation_results.items():
            weight = weights.get(metric_name, 0.1)
            total_score += result.score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _track_evaluation_metrics(self, evaluation: WorkflowEvaluation):
        """Track evaluation metrics for monitoring."""
        try:
            # Track overall evaluation score and duration
            metrics.track_evaluation_score(
                workflow_id=evaluation.workflow_id,
                overall_score=evaluation.overall_score,
                evaluation_duration=evaluation.evaluation_duration
            )
            
            # Track individual metric scores
            for metric_name, result in evaluation.evaluation_results.items():
                metrics.track_metric_score(
                    workflow_id=evaluation.workflow_id,
                    metric_name=metric_name,
                    score=result.score
                )
            
            # Update internal tracking
            self.evaluation_count += 1
            self.avg_evaluation_time = (
                (self.avg_evaluation_time * (self.evaluation_count - 1) + evaluation.evaluation_duration) 
                / self.evaluation_count
            )
            
        except Exception as e:
            self.logger.warning(f"Failed to track evaluation metrics: {str(e)}")
    
    async def _save_evaluation_results(self, evaluation: WorkflowEvaluation):
        """Save evaluation results using existing Prometheus metrics persistence."""
        try:
            # The evaluation results are already being tracked in Prometheus metrics
            # via the _track_evaluation_metrics method, which calls:
            # - metrics.track_evaluation_score() for overall score and duration
            # - metrics.track_metric_score() for individual metric scores
            
            # The Prometheus metrics are automatically persisted to metrics_persistence.json
            # by the PrometheusMetrics class, so no additional persistence is needed here.
            
            self.logger.info(f"Evaluation results tracked in Prometheus metrics for workflow: {evaluation.workflow_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to track evaluation results: {str(e)}")
    
    def get_evaluation_summary(self) -> Dict[str, Any]:
        """Get summary of evaluation statistics."""
        return {
            "total_evaluations": self.evaluation_count,
            "avg_evaluation_time": self.avg_evaluation_time,
            "evaluation_metrics": list(self.metrics.keys()),
            "timestamp": datetime.now().isoformat(),
            "note": "Evaluation metrics are persisted via Prometheus metrics_persistence.json"
        }

# Global evaluator instance
evaluator = PatentResearchEvaluator() 