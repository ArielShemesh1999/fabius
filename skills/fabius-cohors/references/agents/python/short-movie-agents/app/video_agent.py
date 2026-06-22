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
import os
import re
import time

from google import genai
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from google.genai import types

from .utils.utils import load_prompt_from_file

# Set logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Configuration constants
MODEL = "gemini-2.5-flash"
VIDEO_MODEL = "veo-3.1-generate-001"
VIDEO_MODEL_LOCATION = "us-central1"
DESCRIPTION = "Agent responsible for creating videos based on a screenplay and storyboards"
ASPECT_RATIO = "16:9"

client = genai.Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=VIDEO_MODEL_LOCATION,
)


# Video generate tool
def video_generate(
    prompt: str,
    scene_number: int,
    image_link: str,
    screenplay: str,
    tool_context: ToolContext,
) -> list[str]:
    """
    Generate video based on the passed prompt and storyboard image.

    Args:
        prompt (str): A text prompt describing the video that should be generated and returned by the tool.
        scene_number (int): Scene number
        image_link (str): Link to the image stored in GCS bucket
        screenplay (str): Screenplay for the scene
        tool_context (): ToolContext needed by the tool

    Returns:
        str: Link to the video stored in GCS bucket.
    """
    try:
        # Get session_id for the GCS_PATH
        session_id = tool_context._invocation_context.session.id
        bucket_name = os.getenv("GOOGLE_CLOUD_BUCKET_NAME")
        GCS_PATH = f"gs://{bucket_name}/{session_id}"
        AUTHORIZED_URI = "https://storage.mtls.cloud.google.com/"

        # Extract dialogue from screenplay
        dialogue = "\n".join(
            re.findall(r"^\w+\s*\(.+\)\s*$", screenplay, re.MULTILINE)
        )
        dialogue += "\n".join(
            re.findall(r"^\s{2,}.+$", screenplay, re.MULTILINE)
        )

        if dialogue:
            prompt += f"\n\nAudio:\n{dialogue}"

        # Actual video generation
        logger.info(
            f"Generating video for prompt '{prompt}' and image '{image_link}'"
        )

        operation = client.models.generate_videos(
            model=VIDEO_MODEL,
            prompt=prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio=ASPECT_RATIO,
                output_gcs_uri=f"{GCS_PATH}/scene_{scene_number}",
                number_of_videos=1,
                duration_seconds=8,
                person_generation="allow_adult",
            ),
        )

        while not operation.done:
            time.sleep(15)
            operation = client.operations.get(operation)
            logger.info(f"Video generation operation: {operation}")

        if operation.response:
            logger.info(
                f"Generated {len(operation.result.generated_videos)} video(s) for prompt: {prompt}"
            )
            return [
                video.video.uri.replace("gs://", AUTHORIZED_URI)
                for video in operation.result.generated_videos
            ]
        else:
            logger.info(f"Generated no (0) video for prompt: {prompt}")
            return []  # Return an empty list if no video
    except Exception as e:
        logger.error(f"Error generating a video for {prompt}: {e}")
        return []


# --- Video Agent ---
video_agent = None
try:
    video_agent = Agent(
        # Using a potentially different/cheaper model for a simple task
        model=MODEL,
        name="video_agent",
        description=(DESCRIPTION),
        instruction=load_prompt_from_file("video_agent.txt"),
        output_key="video",
        tools=[video_generate],
    )
    logger.info(f"✅ Agent '{video_agent.name}' created using model '{MODEL}'.")
except Exception as e:
    logger.error(
        f"❌ Could not create Storyboard agent. Check API Key ({MODEL}). Error: {e}"
    )
