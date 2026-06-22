# Copyright 2025 Google LLC
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

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai import types

from .prompt import AGENT_INSTRUCTION
from .subagents.data_analyst import data_analyst
from .subagents.information_extractor import information_extractor

root_agent = Agent(
    model="gemini-2.5-flash",
    name="root_agent",
    description="""As a medical pre-authorization agent, you process user
   pre-auth request for a treatment.""",
    instruction=AGENT_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(temperature=0.2),
    tools=[
        AgentTool(agent=information_extractor),
        AgentTool(agent=data_analyst),
    ],
)
