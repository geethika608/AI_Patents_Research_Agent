# Patent Research AI Agent Evaluation System

This document describes the evaluation system for the Patent Research AI Agent, which uses MLflow's LLM-as-a-Judge framework with OpenAI models to evaluate the quality of research outputs and push metrics to both Grafana and MLflow dashboards.

## Overview

The evaluation system provides automated quality assessment of patent research outputs using AI-powered metrics. It evaluates outputs across multiple dimensions and provides both real-time monitoring through Grafana and detailed tracking through MLflow.

## Features

- **AI-Powered Evaluation**: Uses OpenAI GPT-4 to evaluate research outputs
- **Multi-Dimensional Metrics**: Evaluates relevance, completeness, accuracy, clarity, and innovation
- **Real-Time Monitoring**: Metrics pushed to Grafana dashboard
- **Detailed Tracking**: Complete evaluation history in MLflow
- **Prometheus Integration**: Metrics available for Prometheus scraping
- **Automated Workflow**: Integrated into the main research workflow

## Evaluation Metrics

The system evaluates research outputs across five key dimensions:

### 1. Relevance Score (0-10)
- **Purpose**: Measures how well the output addresses the user's query
- **Criteria**: 
  - Direct answer to the question
  - Relevance of patents/trends to research area
  - Usefulness for user's needs

### 2. Completeness Score (0-10)
- **Purpose**: Measures the comprehensiveness of research coverage
- **Criteria**:
  - Multiple relevant patent categories
  - Sufficient examples/cases
  - Recent and historical patents
  - Comprehensive trends and insights

### 3. Accuracy Score (0-10)
- **Purpose**: Measures the reliability of information
- **Criteria**:
  - Consistent patent numbers and dates
  - Matching descriptions and titles
  - Plausible technical information
  - Well-supported trends and insights

### 4. Clarity Score (0-10)
- **Purpose**: Measures readability and understandability
- **Criteria**:
  - Clear and professional language
  - Well-organized information
  - Appropriate technical explanations
  - Logical structure

### 5. Innovation Score (0-10)
- **Purpose**: Measures insightfulness and innovation
- **Criteria**:
  - Emerging trend identification
  - Novel connections between patents
  - Strategic insights
  - Forward-looking analysis

## Architecture

```
User Query → CrewAI Workflow → Research Output → Evaluation System
                                                    ↓
                                    ┌─────────────────────────────┐
                                    │    MLflow Evaluation       │
                                    │  (LLM-as-a-Judge with      │
                                    │   OpenAI GPT-4)            │
                                    └─────────────────────────────┘
                                                    ↓
                                    ┌─────────────────────────────┐
                                    │    Metrics Distribution    │
                                    └─────────────────────────────┘
                                                    ↓
                        ┌─────────────────────────┬─────────────────────────┐
                        │     Grafana Dashboard   │    MLflow Dashboard     │
                        │   (Real-time metrics)   │  (Detailed tracking)    │
                        └─────────────────────────┴─────────────────────────┘
```

## Setup and Configuration

### Prerequisites

1. **OpenAI API Key**: Required for evaluation metrics
2. **MLflow**: For experiment tracking
3. **Prometheus**: For metrics collection
4. **Grafana**: For dashboard visualization

### Environment Variables

```bash
export OPENAI_API_KEY="your-openai-api-key"
export MLFLOW_TRACKING_URI="http://localhost:5000"  # Optional
```

### Dependencies

The evaluation system requires the following additional dependencies:

```toml
mlflow>=2.8.0
openai>=1.0.0
numpy>=1.21.0
```

## Usage

### Automatic Evaluation

The evaluation system is automatically integrated into the main research workflow. When you run a patent research query, the system will:

1. Execute the research workflow
2. Collect agent outputs
3. Evaluate the final result
4. Push metrics to Grafana and MLflow
5. Display evaluation results in the chat interface

### Manual Evaluation

You can also run evaluations manually:

```python
import asyncio
from patent_researcher_agent.utils.evaluation import evaluator

# Run evaluation
evaluation = await evaluator.evaluate_workflow(
    workflow_id="your_workflow_id",
    user_input="Find patents related to AI in healthcare",
    agent_outputs={
        "fetcher_agent": "Found 5 patents...",
        "analyzer_agent": "Analysis shows...",
        "reporter_agent": "Generated report..."
    },
    final_output="Complete research report..."
)

print(f"Overall Score: {evaluation.overall_score:.2f}/10")
```

## Dashboards

### Grafana Dashboard

The evaluation metrics are available in a dedicated Grafana dashboard at:
- **URL**: `http://localhost:3000/d/patent-evaluation/patent-research-evaluation-dashboard`
- **Features**:
  - Overall evaluation score over time
  - Individual metric scores
  - Evaluation duration tracking
  - Total evaluations by metric
  - Average scores

### MLflow Dashboard

Detailed evaluation data is tracked in MLflow:
- **URL**: `http://localhost:5000`
- **Experiment**: `PatentResearchEvaluation`
- **Features**:
  - Complete evaluation history
  - Individual metric scores and explanations
  - Workflow metadata
  - Evaluation artifacts

## Prometheus Metrics

The following Prometheus metrics are available:

```prometheus
# Overall evaluation score
patent_overall_evaluation_score{workflow_id="..."}

# Individual metric scores
patent_evaluation_score{workflow_id="...", metric_name="relevance_score"}
patent_evaluation_score{workflow_id="...", metric_name="completeness_score"}
patent_evaluation_score{workflow_id="...", metric_name="accuracy_score"}
patent_evaluation_score{workflow_id="...", metric_name="clarity_score"}
patent_evaluation_score{workflow_id="...", metric_name="innovation_score"}

# Evaluation duration
patent_evaluation_duration_seconds{workflow_id="..."}

# Total evaluations
patent_evaluations_total{metric_name="..."}
```

## Configuration

### Customizing Evaluation Metrics

You can customize the evaluation metrics by modifying the `_define_evaluation_metrics()` method in `PatentResearchEvaluator`:

```python
# Example: Adding a new metric
custom_metric = make_genai_metric(
    name="custom_score",
    grading_prompt="Your custom evaluation prompt...",
    examples=[EvaluationExample(input="...", output="...", score=8)],
    model="openai/gpt-4",
    parameters={"temperature": 0.1},
    aggregations=["mean", "variance"],
    greater_is_better=True
)
```

### Adjusting Weights

The overall score is calculated as a weighted average. You can adjust weights in the `_calculate_overall_score()` method:

```python
weights = {
    "relevance": 0.25,      # 25% weight
    "completeness": 0.20,   # 20% weight
    "accuracy": 0.25,       # 25% weight
    "clarity": 0.15,        # 15% weight
    "innovation": 0.15      # 15% weight
}
```

## Monitoring and Alerts

### Performance Monitoring

The system tracks evaluation performance:
- Average evaluation time
- Success/failure rates
- API usage and costs

### Quality Thresholds

You can set quality thresholds for automated alerts:
- Minimum overall score: 7.0/10
- Minimum relevance score: 8.0/10
- Maximum evaluation time: 30 seconds

### Error Handling

The evaluation system includes robust error handling:
- Graceful degradation if evaluation fails
- Fallback to basic metrics
- Detailed error logging

## Best Practices

### For High-Quality Evaluations

1. **Clear User Queries**: Specific, well-defined research topics
2. **Comprehensive Outputs**: Detailed reports with multiple sections
3. **Accurate Information**: Verified patent data and descriptions
4. **Structured Format**: Well-organized markdown output
5. **Insightful Analysis**: Beyond basic listing to strategic insights

### For Monitoring

1. **Regular Dashboard Review**: Check Grafana dashboard daily
2. **MLflow Experiment Tracking**: Monitor evaluation trends
3. **Performance Optimization**: Track evaluation times and costs
4. **Quality Improvement**: Use evaluation feedback to improve agents

## Troubleshooting

### Common Issues

1. **OpenAI API Errors**
   - Check API key configuration
   - Verify API quota and limits
   - Check network connectivity

2. **MLflow Connection Issues**
   - Verify MLflow server is running
   - Check tracking URI configuration
   - Ensure proper permissions

3. **Prometheus Metrics Not Appearing**
   - Verify metrics server is running on port 8000
   - Check Prometheus configuration
   - Ensure proper scraping intervals

### Debug Mode

Enable debug logging for detailed evaluation information:

```python
import logging
logging.getLogger("patent_researcher_agent.utils.evaluation").setLevel(logging.DEBUG)
```

## Future Enhancements

Planned improvements to the evaluation system:

1. **Multi-Model Support**: Support for different evaluation models
2. **Custom Metrics**: User-defined evaluation criteria
3. **Batch Evaluation**: Evaluate multiple outputs simultaneously
4. **Comparative Analysis**: Compare outputs across different workflows
5. **Automated Optimization**: Use evaluation feedback to improve agent performance

## Support

For issues and questions about the evaluation system:

1. Check the troubleshooting section above
2. Review the evaluation logs
3. Check logs for detailed error information
4. Verify all dependencies are properly installed 