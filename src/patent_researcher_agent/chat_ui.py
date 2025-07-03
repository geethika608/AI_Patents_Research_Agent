#!/usr/bin/env python
"""
Gradio Chat UI for Patent Research Agent
"""

import gradio as gr
from datetime import datetime
from patent_researcher_agent.crew import PatentInnovationCrew


def run(query: str):
    inputs = {
        'research_area': query,
        "current_date": str(datetime.now())
    }
    
    # Show loading message
    yield "🔄 Processing your research request... This may take a few minutes."
    
    # Run the crew
    result = PatentInnovationCrew().crew().kickoff(inputs=inputs)
    
    # Return the final result
    yield result.raw

def create_chat_interface():
    """
    Create and return the Gradio chat interface.
    """    
    
    with gr.Blocks(theme=gr.themes.Default(primary_hue="sky", secondary_hue="gray", neutral_hue="slate")) as interface:
       gr.Markdown("# 🔬 Patent Research AI Agent")
       gr.Markdown("Enter a research topic to analyze patents and get insights.")
       
       query_textbox = gr.Textbox(
               label="Research Topic", 
               placeholder="e.g., ECG monitoring systems, AI in healthcare...",
           )
       run_button = gr.Button("🔍 Research", variant="primary")
       
       report = gr.Markdown(label="Research Report")
    
       run_button.click(fn=run, inputs=query_textbox, outputs=report, show_progress=True)
       query_textbox.submit(fn=run, inputs=query_textbox, outputs=report, show_progress=True)
        
    
    return interface


def launch_chat():
    """
    Launch the chat interface.
    """
    interface = create_chat_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )


if __name__ == "__main__":
    launch_chat() 