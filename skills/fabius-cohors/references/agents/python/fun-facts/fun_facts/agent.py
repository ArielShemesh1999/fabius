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

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.tools import google_search

# Load environment variables from .env file
load_dotenv(override=True)

# --- Root Agent ---
root_agent = Agent(
    name="Facts",
    model="gemini-flash-latest",
    instruction="Provide the most mind-blowing, obscure, and wacky fun facts about the topic. Aim for maximum 'wow' factor with rare and surprising information.",
    description="An Agent to provide fun facts about a given topic.",
    tools=[google_search],
)


app = App(name="fun_facts", root_agent=root_agent)
