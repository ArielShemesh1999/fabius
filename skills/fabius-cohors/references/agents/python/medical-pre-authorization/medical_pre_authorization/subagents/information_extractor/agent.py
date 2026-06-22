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
from google.genai import types

from .prompt import INFORMATION_EXTRACTOR_INSTRUCTION
from .tools.tools import (
    extract_medical_details,
    extract_policy_information,
    extract_treatment_name,
)

information_extractor = Agent(
    model="gemini-2.5-flash",
    name="information_extractor",
    description="""Agent that extracts the details on user insurance policy and
   medical necessity for a pre-authorization request from documents provided
   by the user.""",
    instruction=INFORMATION_EXTRACTOR_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(temperature=0.2),
    tools=[
        extract_treatment_name,
        extract_policy_information,
        extract_medical_details,
    ],
)
