# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Ops Insight Agent: gets power consumption and generation information using BQ NL2SQL"""

import warnings

from google.adk.agents import LlmAgent
from google.adk.planners import BuiltInPlanner
from google.adk.tools import FunctionTool
from google.genai import types

from ...config import config
from ...tools.execute_sql import execute_sql_query, load_table_schema
from . import prompts

warnings.filterwarnings("ignore", category=UserWarning)

ops_insight_agent = LlmAgent(
    model=config.model_name,
    name="OpsInsightAgent",
    description="Gather the current power consumption and generation information by quering the BQ database based on the user question.",
    instruction=prompts.OPS_INSIGHT_AGENT_PROMPT.format(
        schema=load_table_schema()
    ),
    generate_content_config=types.GenerateContentConfig(
        temperature=config.temperature,
        top_p=config.top_p,
    ),
    planner=BuiltInPlanner(thinking_config=config.thinking_config),
    tools=[FunctionTool(func=execute_sql_query)],
    output_key="ops_insight_report",
)
