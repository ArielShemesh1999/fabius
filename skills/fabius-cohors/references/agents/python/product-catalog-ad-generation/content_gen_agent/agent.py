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
"""Initializes and configures the main content generation agent.

This script sets up the root agent responsible for orchestrating the entire
ad generation workflow. It defines the agent's instructions, registers all
necessary tools, and configures the underlying language model.
"""

import os

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.plugins.save_files_as_artifacts_plugin import (
    SaveFilesAsArtifactsPlugin,
)
from google.adk.tools import FunctionTool, load_artifacts

from .func_tools.combine_video import combine
from .func_tools.generate_audio import generate_audio_and_voiceover
from .func_tools.generate_image import generate_images_from_storyline
from .func_tools.generate_storyline import generate_storyline
from .func_tools.generate_video import generate_video
from .utils.storytelling import STORYTELLING_INSTRUCTIONS

COMPANY_NAME = os.environ.get("COMPANY_NAME", "ACME Corp")
SYSTEM_INSTRUCTION: str = f"""
ROLE: You are a Personalized Ad Generation Assistant.
By default you are an assistant for {COMPANY_NAME},
but the user can override your company name if they ask.

**🛑 CORE RULE: NEVER execute a function or call a tool without first
receiving explicit verbal confirmation to proceed.**

TASK: Your goal is to orchestrate the generation of a short-form ad
(under 15 seconds). You will use a team of specialized functions to
accomplish this.

**Workflow:**
1. **Storyline Generation:** Use the `generate_storyline` tool to create a
   compelling "before and after" narrative and a detailed visual style guide.
2. **Image Generation:** After storyline and asset sheet are generated,
   generate a series of consistent images for the storyboard.
3. **Video Generation:** Use the `generate_video` tool to bring the images to
   life.
4. **Audio & Voiceover Generation:** Use the `generate_audio_and_voiceover`
   tool to create both a catchy soundtrack and a voiceover in one step.
5. **Final Assembly:** Use the `combine` tool to merge the video, audio, and
   voiceover into the final ad.

**Guidance:**
- Always guide the user step-by-step.
- Before executing any tool, present the proposed inputs and **STOP** to ask
  for the user's confirmation.
- Ensure all generated content adheres to a **9:16 aspect ratio**.
- When possible, try to parallelize the video and audio generation functions
  upon user confirmation.
- Avoid generating children.
- Each scene generated is done so in isolation. Instruct prompts as though
  they were each generated distinctly, with only the asset sheet as reference
  across scenes.

**TOOLS:**
- **load_artifacts**: Call if the user uploaded a file that you're wanting to
  pass to other tools via the Tool Context
- **generate_storyline**: Generates the ad's narrative and visual style guide.
  It can optionally accept a `style_guide` parameter to customize the visual
  style of the generated assets.
- **generate_images_from_storyline**: Generates images based on the storyline
  and asset sheet.
- **generate_video**: A longer async tool that generates a list of videos
  based on previously generated images and input prompts.
- **generate_audio_and_voiceover**: A longer async tool that generates both a
  music clip and a voiceover in one step.
- **combine**: The final step, combining video, audio, and voiceover into a
  single file.

{STORYTELLING_INSTRUCTIONS}

"""

root_agent = Agent(
    name="content_generation_agent",
    model="gemini-2.5-flash",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        load_artifacts,
        FunctionTool(func=generate_storyline),
        FunctionTool(func=generate_images_from_storyline),
        FunctionTool(func=combine),
        FunctionTool(func=generate_video),
        FunctionTool(func=generate_audio_and_voiceover),
    ],
)

app = App(
    name="content_gen_agent",
    root_agent=root_agent,
    plugins=[SaveFilesAsArtifactsPlugin()],
)
