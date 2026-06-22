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


from google.adk.agents import LlmAgent
from google.genai import types

from ..config import config
from ..safety_rules import BANKING_AGENT_IDENTITY, BANKING_SAFETY_CONSTITUTION

system_prompt = f"""
    {BANKING_AGENT_IDENTITY}
    {BANKING_SAFETY_CONSTITUTION}
    When answering the user, adhere strictly to these protocols.
    """


def create() -> LlmAgent:
    return LlmAgent(
        name="target",
        model=config.target_model,
        instruction=system_prompt,
        generate_content_config=types.GenerateContentConfig(temperature=0.1),
    )
