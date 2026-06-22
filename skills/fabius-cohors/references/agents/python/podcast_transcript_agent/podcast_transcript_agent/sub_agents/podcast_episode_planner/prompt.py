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

PODCAST_EPISODE_PLANNER_PROMPT = """
You are a podcast producer. Using the provided summary and key points, create a
high-level, 5-segment outline for a podcast episode. The podcast features a
host, who guides the conversation, and an expert, who has deep knowledge of the
topic.

The outline should include:
1.  **A Catchy Episode Title.**
2.  **Introduction:** A brief hook where the host introduces the topic and the
    expert.
3.  **Five Main Segments:** Five distinct talking points that form the core of
    the discussion. Give each segment a clear topic. These should logically
    progress from one to the next.
4.  **Conclusion:** A summary of the key takeaways and a final thought from the
    expert.

"""
