# PatentResearcherAgent Crew

Welcome to the PatentResearcherAgent Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/patent_researcher_agent/config/agents.yaml` to define your agents
- Modify `src/patent_researcher_agent/config/tasks.yaml` to define your tasks
- Modify `src/patent_researcher_agent/crew.py` to add your own logic, tools and specific args
- Modify `src/patent_researcher_agent/main.py` to add custom inputs for your agents and tasks

## Running the Project

### Command Line Interface

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the patent_researcher_agent Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

### Chat Interface

For an interactive experience, you can use the Gradio chat interface:

```bash
# Method 1: Using the launcher script
python launch_chat.py

# Method 2: Using the main script with --chat flag
python src/patent_researcher_agent/main.py --chat

# Method 3: Using uv run (if installed)
uv run chat
```

The chat interface will be available at `http://localhost:7860` and provides:

- **Interactive Chat**: Ask questions about any research area or technology
- **Real-time Processing**: See the AI agents working in real-time
- **Structured Results**: Get formatted responses with summaries, recommendations, and patent information
- **Example Queries**: Built-in examples to get you started
- **Clear Interface**: Easy-to-use chat interface with clear visual feedback

**Example queries you can try:**
- "ECG monitoring systems for remote patient care"
- "Machine learning algorithms for drug discovery"
- "Renewable energy storage solutions"
- "Quantum computing applications in cryptography"
- "IoT sensors for smart agriculture"

## Understanding Your Crew

The patent_researcher_agent Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the PatentResearcherAgent Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
