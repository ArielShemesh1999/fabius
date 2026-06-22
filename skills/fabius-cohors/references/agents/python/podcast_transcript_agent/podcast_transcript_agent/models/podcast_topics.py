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


class Topic(BaseModel):
    """A model for a podcast topic, which includes a title, description, and key facts."""

    topic_name: str
    description: str
    key_facts: list[str]


class PodcastTopics(BaseModel):
    """A model for the main topic and sub-topics of a podcast episode."""

    main_topic: str
    sub_topics: list[Topic]
