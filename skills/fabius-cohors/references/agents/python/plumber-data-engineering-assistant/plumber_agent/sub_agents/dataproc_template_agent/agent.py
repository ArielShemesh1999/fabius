"""Module for Dataproc template agent configuration."""

import warnings

from google.adk.agents import Agent
from google.genai import types

from .constants import MODEL
from .prompts import AGENT_INSTRUCTION
from .tools.dataproc_template_tools import (
    get_dataproc_template,
    get_transformation_sql,
    run_dataproc_template,
)

warnings.filterwarnings("ignore")

root_agent = Agent(
    name="dataproc_template_agent",
    model=MODEL,
    description=(
        "Agent to look for relevant dataproc template based on user query"
        "and submit dataproc template job"
    ),
    instruction=(AGENT_INSTRUCTION),
    tools=[
        get_dataproc_template,
        run_dataproc_template,
        get_transformation_sql,
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
