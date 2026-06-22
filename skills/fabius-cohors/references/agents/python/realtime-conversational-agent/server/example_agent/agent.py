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

from google.adk.agents import Agent
from google.genai.types import GenerateContentConfig

from .prompts import AGENT_INSTRUCTION

genai_config = GenerateContentConfig(temperature=0.5)

root_agent = Agent(
    name="example_agent",
    model="gemini-live-2.5-flash-native-audio",
    description="A helpful AI assistant.",
    instruction=AGENT_INSTRUCTION,
)
