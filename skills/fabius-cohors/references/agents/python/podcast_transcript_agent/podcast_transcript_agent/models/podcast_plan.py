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


from pydantic import BaseModel

from podcast_transcript_agent.models.podcast_transcript import PodcastSpeaker


class Segment(BaseModel):
    """A model for a 'main_segment', which includes a title."""

    title: str
    script_points: list[str]


class PodcastEpisodePlan(BaseModel):
    """Represents the entire episode, containing a title and a list of segments."""

    episode_title: str
    speakers: list[PodcastSpeaker]
    segments: list[Segment]
