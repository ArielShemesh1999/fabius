"""
Main definition for the DBT agent.
This module initializes the root 'dbt_agent' with its instructions,
model, and associated tools for SQL generation and project deployment.
"""

import warnings

from google.adk.agents import Agent
from google.genai import types

# UTILITY IMPORTS
from .constants import MODEL
from .prompts import AGENT_INSTRUCTIONS
from .tools.dbt_model_sql_generator import generate_dbt_model_sql

# TOOL IMPORTS
from .tools.dbt_project_deployment import deploy_dbt_project
from .tools.dbt_project_runner import run_dbt_project

warnings.filterwarnings("ignore")

root_agent = Agent(
    name="dbt_agent",
    model=MODEL,
    description=(
        "Agent to convert source to target mapping image/csv file to corresponding dbt sql model"
    ),
    instruction=(AGENT_INSTRUCTIONS),
    tools=[generate_dbt_model_sql, deploy_dbt_project, run_dbt_project],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
        ]
    ),
)
