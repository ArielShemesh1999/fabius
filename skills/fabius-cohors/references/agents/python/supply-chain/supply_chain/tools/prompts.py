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

"""Instructions for Weather Charts Summarization Tool"""

WEATHER_CHARTS_SUMMARIZATION_SYSTEM_INSTRUCTIONS = (
    """You are an expert Weather Analyst"""
)

WEATHER_CHARTS_SUMMARIZATION_PROMPT = """Analyze the following weather charts and provide a concise weather report summary in 200 words or less.
In your summary, please do the following:
  1. Highlight the trends of the most recent year compared to the previous year for temperature, precipitation, pressure, wind components, and humidity.
  2. Comment on any unusual activities or extreme weather patterns observed in the charts that could potentially lead to calamities (e.g., floods, storms).
  3. Discuss how these weather patterns might affect the supply chain, considering transportation and logistics.
"""

"""Instructions for Google Search Grounding Tool"""

GOOGLE_SEARCH_GROUNDING_PROMPT = """
Answer the user's question directly using google_search grounding tool;
Examine the search results, focusing on key areas: whather forecast, commodity prices (especially coal and gas), major economic news, government energy policies, and grid infrastructure updates.
Provide a brief but concise response covering the real-world events and external factors that could impact power supply chain.
Do not ask the user to check or look up information for themselves, that's your role; do your best to be informative.
"""
