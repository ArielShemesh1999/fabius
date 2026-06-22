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

from google.adk import Agent
from google.genai import types

from .prompt import DATA_ANALYST_INSTRUCTION
from .tools.tools import store_pdf

data_analyst = Agent(
    model="gemini-2.5-flash",
    name="data_analyst",
    description="""Agent that analyzes the details on user insurance policy and
   medical necessity for a pre-authorization request and creates a report on
   the same.""",
    instruction=DATA_ANALYST_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(temperature=0.2),
    tools=[store_pdf],
)
