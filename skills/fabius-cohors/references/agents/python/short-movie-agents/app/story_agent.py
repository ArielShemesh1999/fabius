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

import logging

from app.utils.utils import load_prompt_from_file

try:
    from google.adk.agents import Agent
except ImportError:
    from adk.agents import Agent

# --- Story Agent ---
story_agent = None

try:
    MODEL = "gemini-2.5-flash"
    DESCRIPTION = (
        "An agent that generates a short, engaging campfire story for scouts."
    )
    story_agent = Agent(
        model=MODEL,
        name="story_agent",
        description=load_prompt_from_file("story_agent_desc.txt"),
        instruction=load_prompt_from_file("story_agent.txt"),
        output_key="story",
    )
    logging.info(
        f"✅ Agent '{story_agent.name}' created using model '{MODEL}'."
    )
except Exception as e:
    logging.error(
        f"❌ Could not create Story agent. Check API Key ({MODEL}). Error: {e}"
    )
