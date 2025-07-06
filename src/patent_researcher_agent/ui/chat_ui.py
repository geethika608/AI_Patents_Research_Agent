#!/usr/bin/env python
"""
Gradio Chat UI for Patent Research Agent
"""

import gradio as gr
from datetime import datetime
from patent_researcher_agent.crew import PatentInnovationCrew
from ..utils.logger import setup_logger
from ..utils.validators import validate_research_area

# Setup logger
logger = setup_logger(__name__)


def run(query: str):
    """
    Run the patent research with validation, monitoring, error handling, and evaluation.
    """
    logger.info(f"Starting patent research for query: {query}")
    
    # Validate input
    if not validate_research_area(query):
        logger.warning(f"Invalid research area: {query}")
        yield "❌ Please provide a valid research topic (3-500 characters)."
        return
    
    inputs = {
        'research_area': query,
        "current_date": str(datetime.now())
    }
    
    logger.info(f"Processing research request with inputs: {inputs}")
        
    
    crew_obj = PatentInnovationCrew()
    workflow_id = None
    agent_outputs = {}
    try:
        # Start workflow monitoring
        workflow_id = crew_obj.start_workflow(query)
        logger.info(f"Workflow started: {workflow_id}")
        
        # Execute the entire crew workflow
        crew_instance = crew_obj.crew()
        result = crew_instance.kickoff(inputs)
        
        # Get execution summary from event listener if available
        execution_summary = None
        try:
            from ..crew import global_event_listener
            if global_event_listener:
                execution_summary = global_event_listener.get_execution_summary()
                logger.info(f"Execution summary captured from event listener - workflow_id={workflow_id}, summary={execution_summary}")
                
                # Log summary statistics if available
                if execution_summary and "summary" in execution_summary:
                    summary = execution_summary["summary"]
                    logger.info(f"Workflow execution summary - workflow_id={workflow_id}, agent_success_rate={summary.get('agent_success_rate', 0)}, task_success_rate={summary.get('task_success_rate', 0)}, total_agent_executions={summary.get('total_agent_executions', 0)}, total_task_executions={summary.get('total_task_executions', 0)}")
        except Exception as e:
            logger.warning(f"Could not get execution summary: {e}")
        
        crew_obj.end_workflow(success=True)
        logger.info("Crew execution completed successfully")
        
        # Process and validate the result
        final_result = process_result(result)

        yield final_result
        
        # Perform evaluation
        try:
            import asyncio
            from ..utils.evaluation import evaluator
            
            # Extract agent outputs from execution summary if available
            if execution_summary and "agent_executions" in execution_summary:
                agent_executions = execution_summary["agent_executions"]
                if isinstance(agent_executions, dict):
                    # If agent_executions is a dict, iterate through its values
                    for agent_exec in agent_executions.values():
                        if isinstance(agent_exec, dict):
                            agent_name = agent_exec.get("agent_name", "unknown")
                            output = agent_exec.get("result", "")
                            agent_outputs[agent_name] = output
                elif isinstance(agent_executions, list):
                    # If agent_executions is a list, iterate directly
                    for agent_exec in agent_executions:
                        if isinstance(agent_exec, dict):
                            agent_name = agent_exec.get("agent_name", "unknown")
                            output = agent_exec.get("result", "")
                            agent_outputs[agent_name] = output
            
            # Run evaluation asynchronously
            evaluation = asyncio.run(evaluator.evaluate_workflow(
                workflow_id=workflow_id,
                user_input=query,
                agent_outputs=agent_outputs,
                final_output=final_result
            ))
            
            logger.info(f"Evaluation completed for workflow {workflow_id} - Overall score: {evaluation.overall_score:.2f}")
            
        except Exception as eval_error:
            logger.error(f"Evaluation failed for workflow {workflow_id}: {str(eval_error)}")
            # Continue without evaluation if it fails
        
        
        
    except Exception as e:
        logger.error(f"Error during crew execution: {str(e)}")
        if workflow_id:
            crew_obj.end_workflow(success=False, error_message=str(e))
        yield f"❌ An error occurred during processing: {str(e)}"
    finally:
        # Ensure workflow cleanup happens even if there's an exception
        if 'workflow_id' in locals() and workflow_id:
            try:
                from ..utils.workflow_tracker import unregister_workflow
                unregister_workflow(workflow_id)
                logger.info(f"Unregistered workflow in finally block: {workflow_id}")
            except Exception as cleanup_error:
                logger.warning(f"Error during workflow cleanup: {cleanup_error}")


def process_result(result):
    """
    Process and validate the result to ensure it's properly formatted for Gradio.
    """
    try:
        # Handle different result types
        if result is None:
            return "❌ No result received from the research process."
        
        # Extract the actual result content
        if hasattr(result, 'raw'):
            content = result.raw
        elif hasattr(result, 'result'):
            content = result.result
        elif hasattr(result, 'output'):
            content = result.output
        else:
            content = str(result)
        
        # Ensure content is a string
        if not isinstance(content, str):
            content = str(content)
        
        # Validate markdown content
        if not content.strip():
            return "❌ Empty result received from the research process."
        
        # Basic markdown validation and cleanup
        content = cleanup_markdown(content)
        
        # Add a header if not present
        if not content.startswith('#'):
            content = f"# Research Report\n\n{content}"
        
        logger.info(f"Processed result successfully, length: {len(content)}")
        return content
        
    except Exception as e:
        logger.error(f"Error processing result: {str(e)}")
        return f"❌ Error processing the research result: {str(e)}"


def cleanup_markdown(content):
    """
    Clean up and validate markdown content for Gradio display.
    """
    try:
        # Remove any null characters or invalid unicode
        content = content.replace('\x00', '')
        
        # Ensure proper line breaks
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # Fix common markdown issues
        content = content.replace('```\n\n', '```\n')
        content = content.replace('\n\n```', '\n```')
        
        # Ensure proper spacing around headers
        content = content.replace('\n#', '\n\n#')
        content = content.replace('\n##', '\n\n##')
        content = content.replace('\n###', '\n\n###')
        
        # Remove excessive blank lines
        while '\n\n\n' in content:
            content = content.replace('\n\n\n', '\n\n')
        
        return content.strip()
        
    except Exception as e:
        logger.error(f"Error cleaning markdown: {str(e)}")
        return content


def create_chat_interface():
    """
    Create and return the Gradio chat interface.
    """    
    logger.info("Creating Gradio chat interface")
    
    with gr.Blocks(
        theme=gr.themes.Default(primary_hue="sky", secondary_hue="gray", neutral_hue="slate"),
        title="Patent Research AI Agent",
        css="""
        .markdown-body {
            max-height: 70vh;
            overflow-y: auto;
            padding: 20px;
            border: 1px solid #e1e5e9;
            border-radius: 8px;
            background-color: #ffffff;
        }
        """
    ) as interface:
       gr.Markdown("# 🔬 Patent Research AI Agent")
       gr.Markdown("Enter a research topic to analyze patents and get insights.")
       
       query_textbox = gr.Textbox(
               label="Research Topic", 
               placeholder="e.g., ECG monitoring systems, AI in healthcare...",
               lines=2,
               max_lines=3
           )
       run_button = gr.Button("🔍 Research", variant="primary", size="lg")
       
       with gr.Row():
            report = gr.Markdown(
               label="Research Report",
               elem_classes=["markdown-body"],
               show_label=True
            )
    
       # Event handlers
       run_button.click(
           fn=run, 
           inputs=query_textbox, 
           outputs=report, 
           show_progress=True,
           api_name="research"
       )
       query_textbox.submit(
           fn=run, 
           inputs=query_textbox, 
           outputs=report, 
           show_progress=True
       )
        
    logger.info("Gradio interface created successfully")
    return interface


def launch_chat():
    """
    Launch the chat interface.
    """
    logger.info("Launching chat interface")
    interface = create_chat_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True,
        show_error=True,
        quiet=False,
        inbrowser=True
    )


if __name__ == "__main__":
    launch_chat() 