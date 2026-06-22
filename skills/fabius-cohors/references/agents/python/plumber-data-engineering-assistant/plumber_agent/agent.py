"""Core agent module for orchestrating sub-agents."""

from google.adk.agents import Agent
from google.genai import types

from .constants import MODEL
from .prompts import AGENT_INSTRUCTIONS

# Import root_agents from each subagent.
from .sub_agents.dataflow_agent.agent import root_agent as dataflow_agent
from .sub_agents.dataproc_agent.agent import root_agent as dataproc_agent
from .sub_agents.dataproc_template_agent.agent import (
    root_agent as dataproc_template_agent,
)
from .sub_agents.dbt_agent.agent import root_agent as dbt_agent
from .sub_agents.github_agent.agent import root_agent as github_agent
from .sub_agents.monitoring_agent.agent import root_agent as monitoring_agent

root_agent = Agent(
    name="plumber_agent",
    model=MODEL,
    description=(
        "A main orchestrator that intelligently routes user requests to "
        "specialized sub-agents. It delegates tasks across key domains: data "
        "processing (Dataflow, Dataproc clusters & templates), data "
        "transformation (**dbt**), code & file management "
        "(GitHub, GCS), and cloud observability (Monitoring logs & metrics)."
    ),
    instruction=AGENT_INSTRUCTIONS,
    sub_agents=[
        dataflow_agent,
        dataproc_agent,
        dataproc_template_agent,
        dbt_agent,
        github_agent,
        monitoring_agent,
    ],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
        ]
    ),
)
