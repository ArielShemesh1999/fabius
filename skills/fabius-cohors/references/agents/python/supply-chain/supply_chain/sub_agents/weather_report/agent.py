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

"""Weather Report Agent: provides weather info for a specific location and date"""

import warnings

from google.adk.agents import LlmAgent
from google.adk.planners import BuiltInPlanner
from google.genai import types

from ...config import config
from ...tools.analyse_weather_toolkit import WEATHER_REPORT_TOOLKIT
from . import prompts

warnings.filterwarnings("ignore", category=UserWarning)

weather_report_agent = LlmAgent(
    model=config.model_name,
    name="WeatherReportAgent",
    description="Gather weather info from past and forecast data for a specific location/address & date based on the user question.",
    instruction=prompts.WEATHER_REPORT_AGENT_PROMPT,
    generate_content_config=types.GenerateContentConfig(
        temperature=config.temperature,
        top_p=config.top_p,
    ),
    planner=BuiltInPlanner(thinking_config=config.thinking_config),
    tools=WEATHER_REPORT_TOOLKIT,
    output_key="weather_info_report",
)
