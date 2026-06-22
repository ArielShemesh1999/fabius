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

from google.adk.agents import Agent

from .utils.utils import load_prompt_from_file

# Set logging
logger = logging.getLogger(__name__)

# Configuration constants
MODEL = "gemini-2.5-flash"
DESCRIPTION = "Agent responsible for writing a screenplay based on a story"

# --- Screenplay Agent ---
screenplay_agent = None
try:
    screenplay_agent = Agent(
        # Using a potentially different/cheaper model for a simple task
        model=MODEL,
        name="screenplay_agent",
        description=(DESCRIPTION),
        instruction=load_prompt_from_file("screenplay_agent.txt"),
        output_key="screenplay",
    )
    logger.info(
        f"✅ Agent '{screenplay_agent.name}' created using model '{MODEL}'."
    )
except Exception as e:
    logger.error(
        f"❌ Could not create Screenplay agent. Check API Key ({MODEL}). Error: {e}"
    )
