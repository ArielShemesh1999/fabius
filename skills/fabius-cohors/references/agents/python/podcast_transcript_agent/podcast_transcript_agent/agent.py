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

from google.adk.agents import SequentialAgent

from .sub_agents.podcast_episode_planner import podcast_episode_planner_agent
from .sub_agents.podcast_topics import podcast_topics_agent
from .sub_agents.podcast_transcript_writer import (
    podcast_transcript_writer_agent,
)

podcast_transcript_agent = SequentialAgent(
    name="podcast_transcript_agent",
    description="Executes a sequence of podcast generation steps",
    sub_agents=[
        podcast_topics_agent,
        podcast_episode_planner_agent,
        podcast_transcript_writer_agent,
    ],
)

root_agent = podcast_transcript_agent
