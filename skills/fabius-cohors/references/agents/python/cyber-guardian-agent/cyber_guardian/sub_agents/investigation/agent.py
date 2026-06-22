import os

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from ...tools import investigationQueryTool
from .prompt import agent_instructions

investigation_agent = Agent(
    model=os.getenv("MODEL_ID", "gemini-2.5-flash"),
    name="investigation_agent",
    description="Performs incident investigation using internal DBs and sandboxes",
    instruction=agent_instructions,
    tools=[FunctionTool(investigationQueryTool)],
    output_key="investigation_agent_output",
)
