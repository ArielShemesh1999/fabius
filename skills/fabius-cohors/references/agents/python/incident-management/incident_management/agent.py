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
# limitations under the License

from google.adk.agents import Agent

from .snow_connector_tool import snow_connector_tool

root_agent = Agent(
    name="snow_agent",
    description="ServiceNow agent that allows you to manage and create Incidents",
    instruction="Help the user with getting, listing and creating ServiceNow incidents, leverage the tools you have access to",
    tools=[snow_connector_tool],
    model="gemini-2.5-pro",
)
