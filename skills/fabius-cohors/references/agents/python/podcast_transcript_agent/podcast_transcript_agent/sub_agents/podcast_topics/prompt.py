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

TOPIC_EXTRACTION_PROMPT = """
You are an expert research analyst. Your task is to analyze the provided
text and perform a detailed extraction of its key components for a podcast
scriptwriter. Do not invent information. All output must be based strictly
on the provided content.

Analyze the given research paper and identify
- The main topic of the content
- A summary of the content's central argument and conclusion.

Then, extract the 5 most important subtopics. Important guidelines for
subtopic selection:
- Avoid generic topics like 'Introduction', 'Background', or 'Conclusion'.
- Each subtopic should be suitable for an in-depth, discussion.

For each subtopic, extract the following:

1. A descriptive and enticing title.
2. A summary of the subtopic. Maximum of two paragraphs. If relevant, include
   any supporting evidence, specific examples, or data points mentioned in the
   text.
3. Key Statistics & Data. A list of the most impactful statistics, figures, or
   data points mentioned.

Provide your response in a JSON format that can be directly parsed.
"""
