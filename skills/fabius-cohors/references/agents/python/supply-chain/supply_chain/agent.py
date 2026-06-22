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

"""Agent module for the supply chain agent."""

import logging

from google.adk.agents import LlmAgent
from google.adk.planners import BuiltInPlanner
from google.adk.tools import FunctionTool
from google.adk.tools.agent_tool import AgentTool
from google.genai import types

from . import prompts
from .config import config
from .sub_agents.chart_generator.agent import chart_generator_agent
from .sub_agents.demand_sense.agent import demand_sense_agent
from .sub_agents.market_pulse.agent import market_pulse_agent
from .sub_agents.ops_insight.agent import ops_insight_agent
from .sub_agents.weather_report.agent import weather_report_agent
from .tools.date_time import get_current_date_time

# Configure logging for debug purposes
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

root_agent = LlmAgent(
    model=config.model_name,
    name="SupplyChainAgent",
    instruction=prompts.ROOT_AGENT_PROMPT,
    generate_content_config=types.GenerateContentConfig(
        temperature=config.temperature,
        top_p=config.top_p,
    ),
    planner=BuiltInPlanner(thinking_config=config.thinking_config),
    tools=[
        AgentTool(agent=demand_sense_agent),
        AgentTool(agent=ops_insight_agent),
        AgentTool(agent=market_pulse_agent),
        AgentTool(agent=chart_generator_agent),
        AgentTool(agent=weather_report_agent),
        FunctionTool(func=get_current_date_time),
    ],
)
