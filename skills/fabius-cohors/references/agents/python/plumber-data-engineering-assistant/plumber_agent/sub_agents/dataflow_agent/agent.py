"""Dataflow agent."""

from google.adk.agents import Agent

from .constants import MODEL
from .prompts import AGENT_INSTRUCTION
from .tools.dataflow_management_utils import (
    cancel_dataflow_job,
    get_dataflow_job_details,
    list_dataflow_jobs,
)
from .tools.dataflow_template_tools import (
    get_dataflow_template,
    submit_dataflow_template,
)
from .tools.pipeline_utils import (
    create_pipeline_from_scratch,
    generate_beam_transformations_from_sttm,
    review_dataflow_code,
)

# Create the unified agent instance with all tools
root_agent = Agent(
    name="dataflow_agent",
    model=MODEL,  # A powerful model is needed to follow these detailed instructions
    description=(
        "A powerful agent that can create, deploy, and manage Google Cloud"
        " Dataflow jobs, and find, customize, and build Dataflow templates."
    ),
    instruction=AGENT_INSTRUCTION,
    tools=[
        # Core execution tool
        create_pipeline_from_scratch,
        generate_beam_transformations_from_sttm,
        review_dataflow_code,
        # Job Management tools
        list_dataflow_jobs,
        get_dataflow_job_details,
        cancel_dataflow_job,
        # Template tools
        get_dataflow_template,
        submit_dataflow_template,
    ],
)
