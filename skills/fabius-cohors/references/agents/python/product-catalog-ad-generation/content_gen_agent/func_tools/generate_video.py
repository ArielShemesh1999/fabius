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
"""Generates video clips from images using Google's Vertex AI services."""

import asyncio
import logging
import os
import re
from collections.abc import Coroutine
from dataclasses import dataclass

from google import genai
from google.adk.tools import ToolContext
from google.api_core import exceptions as api_exceptions
from google.api_core import operation
from google.cloud import storage
from google.genai.types import GenerateVideosConfig
from google.genai.types import Image as GenImage

from content_gen_agent.utils.images import load_image_resource

# --- Configuration ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

VIDEO_MODEL = "veo-3.1-generate-001"
GCS_TEMPLATE_IMAGE_FOLDER = "template_images/"
ALLOWED_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg")
VIDEO_ASPECT_RATIO = "9:16"
VIDEO_FPS = 24
MIN_VID_LENGTH = 4
MEDIAN_VID_LENGTH = 6
MAX_VID_LENGTH = 8


@dataclass
class VideoGenerationInput:
    """Input parameters for video generation."""

    video_query: str
    input_image: GenImage
    image_identifier: str
    duration: int


def _get_gcs_files(folder_prefix: str) -> list[str]:
    """Fetches all image files from a specified GCS folder.

    Args:
        folder_prefix (str): The GCS folder to search for images.

    Returns:
        A list of GCS URIs for the found images.
    """
    project_id = os.getenv("GCP_PROJECT")
    if not project_id:
        logging.error("GCP_PROJECT environment variable not set.")
        return []

    bucket_name = f"{project_id}-contentgen-static"
    try:
        storage_client = storage.Client()
        blobs = storage_client.list_blobs(bucket_name, prefix=folder_prefix)
        return [
            f"gs://{bucket_name}/{blob.name}"
            for blob in blobs
            if blob.name.lower().endswith(ALLOWED_IMAGE_EXTENSIONS)
        ]
    except api_exceptions.GoogleAPICallError as e:
        logging.error("Failed to fetch files from GCS: %s", e, exc_info=True)
        return []


async def _monitor_video_operation(
    operation: operation.Operation,
    image_identifier: str,
    vertex_client: genai.Client,
) -> tuple[GenImage | None, str | None]:
    """Monitors a video generation operation until completion.

    Args:
        operation (operation.Operation): The video operation to monitor.
        image_identifier (str): An identifier for the image being processed.
        vertex_client (genai.Client): The Vertex AI client.

    Returns:
        A tuple containing the generated video object and an error message.
    """
    logging.info(
        "Submitted video generation request for image %s. Operation: %s",
        image_identifier,
        operation.name,
    )
    while not operation.done:
        await asyncio.sleep(15)
        operation = vertex_client.operations.get(operation)
        logging.info(
            "Operation status for %s: %s - Done: %s",
            image_identifier,
            operation.name,
            operation.done,
        )

    if operation.error:
        error_message = operation.error.get("message", str(operation.error))
        logging.error(
            "Operation for %s failed with error: %s",
            image_identifier,
            error_message,
        )
        return None, error_message
    if not (operation.result and hasattr(operation.result, "generated_videos")):
        logging.warning(
            "No generated videos found in the response for %s.",
            image_identifier,
        )
        return None, "No videos found in the response."
    return operation.result.generated_videos[0], None


def _round_to_nearest_veo_duration(duration: int) -> int:
    """Rounds the desired duration to the nearest supported VEO duration.

    Args:
        duration (int): The desired duration of the video in seconds.
    """
    if duration <= MIN_VID_LENGTH:
        return MIN_VID_LENGTH
    if duration <= MEDIAN_VID_LENGTH:
        return MEDIAN_VID_LENGTH
    return MAX_VID_LENGTH


# pylint: disable=too-many-arguments
async def _generate_single_video(
    video_input: VideoGenerationInput,
    tool_context: ToolContext,
    vertex_client: genai.Client,
) -> tuple[dict[str, str] | None, str | None]:
    """Generates a single video from a given image and prompt.

    Args:
        video_input (VideoGenerationInput): Input params for video generation.
        tool_context (ToolContext): The context for artifact management.
        vertex_client (genai.Client): The Vertex AI client.

    Returns:
        A tuple containing the video result and an error message.
    """
    try:
        request = {
            "model": VIDEO_MODEL,
            "source": {
                "prompt": video_input.video_query,
                "image": video_input.input_image,
            },
            "config": GenerateVideosConfig(
                aspect_ratio=VIDEO_ASPECT_RATIO,
                generate_audio=False,
                number_of_videos=1,
                duration_seconds=_round_to_nearest_veo_duration(
                    video_input.duration
                ),
                fps=VIDEO_FPS,
                person_generation="allow_all",
                enhance_prompt=True,
            ),
        }
        operation = vertex_client.models.generate_videos(**request)
        video, error = await _monitor_video_operation(
            operation, video_input.image_identifier, vertex_client
        )

        if error or not (video and video.video and video.video.video_bytes):
            return None, error or "Generated video has no content."

        filename = f"{video_input.image_identifier}.mp4"
        await tool_context.save_artifact(
            filename,
            genai.types.Part.from_bytes(
                data=video.video.video_bytes, mime_type="video/mp4"
            ),
        )
        return {"name": filename}, None
    except (api_exceptions.Aborted, ValueError) as e:
        logging.error(
            "Error in _generate_single_video for %s: %s",
            video_input.image_identifier,
            e,
            exc_info=True,
        )
        return None, str(e)


def _initialize_vertex_client() -> genai.Client:
    """Initializes and returns the Vertex AI client.

    Raises:
        ValueError: If GCP_PROJECT or GCP_LOCATION are not set.
    """
    project_id = os.getenv("GCP_PROJECT")
    location = os.getenv("GCP_LOCATION")
    if not project_id or not location:
        raise ValueError("GCP_PROJECT or GCP_LOCATION not set.")
    return genai.Client(vertexai=True, project=project_id, location=location)


def _get_image_sources(
    scene_numbers: list[int] | None, num_images: int
) -> list[tuple[str, str]]:
    """Determines the image sources based on scene numbers or total count."""
    if scene_numbers:
        image_filenames = [f"{i}_.png" for i in scene_numbers]
    else:
        image_filenames = [f"{i}_.png" for i in range(num_images)]

    image_sources = image_filenames
    if not image_sources:
        image_sources = _get_gcs_files(GCS_TEMPLATE_IMAGE_FOLDER)
    return image_sources


async def _process_video_source(
    source_path: str,
    video_query: str,
    tool_context: ToolContext,
    *,
    is_last_image: bool,
    logo_prompt_present: bool,
) -> tuple[VideoGenerationInput | None, dict[str, str] | None]:
    """Loads image and prepares video generation input."""
    try:
        image_bytes, identifier, mime_type = await load_image_resource(
            source_path, tool_context
        )
        if not image_bytes:
            return None, {"source": source_path, "reason": "Failed image load"}

        duration = 6 if logo_prompt_present and is_last_image else 4
        video_input = VideoGenerationInput(
            video_query=video_query,
            input_image=GenImage(image_bytes=image_bytes, mime_type=mime_type),
            image_identifier=identifier,
            duration=duration,
        )
        return video_input, None
    except (FileNotFoundError, api_exceptions.GoogleAPICallError) as e:
        return None, {"source": source_path, "reason": str(e)}


async def _create_video_tasks(
    image_sources: list[str],
    video_queries: list[str],
    tool_context: ToolContext,
    vertex_client: genai.Client,
    logo_prompt_present: bool,
) -> tuple[list[Coroutine], list[str], list[dict[str, str]]]:
    """Creates video generation tasks for the given images.

    Returns:
        A tuple containing a list of video generation coroutines, a list of
        the sources for each task, and a list of videos that failed to process.
    """
    tasks = []
    task_sources = []
    failed_videos = []

    for i, source_path in enumerate(image_sources):
        if i >= len(video_queries):
            break

        video_input, failure = await _process_video_source(
            source_path,
            video_queries[i],
            tool_context,
            is_last_image=i == len(image_sources) - 1,
            logo_prompt_present=logo_prompt_present,
        )

        if failure:
            failed_videos.append(failure)
        elif video_input:
            tasks.append(
                _generate_single_video(
                    video_input=video_input,
                    tool_context=tool_context,
                    vertex_client=vertex_client,
                )
            )
            task_sources.append(source_path)

    return tasks, task_sources, failed_videos


def _process_results(
    results: list[tuple[dict[str, str] | None, str | None]],
    task_sources: list[str],
    failed_videos: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Processes the results of video generation tasks."""
    successful_videos = []
    for i, (res, error) in enumerate(results):
        if res:
            successful_videos.append(res)
        else:
            failed_videos.append(
                {
                    "source": task_sources[i],
                    "reason": error or "Generation failed",
                }
            )

    successful_videos.sort(
        key=lambda v: (
            int(re.match(r"(\d+)", v["name"]).group(1))
            if re.match(r"(\d+)", v["name"])
            else -1
        )
    )

    return successful_videos, failed_videos


async def generate_video(
    video_queries: list[str],
    tool_context: ToolContext,
    num_images: int,
    scene_numbers: list[int] | None = None,
    logo_prompt_present: bool = True,
) -> dict[str, str | list[dict[str, str]]]:
    """Generates videos in parallel from a list of prompts and images.

    Args:
        video_queries (List[str]): A list of prompts for video generation.
            - Each video query should only describe a 4 second scene, so
              describe a quick scene with only one setting.
            - Be VERY descriptive in what movements and camera angles you
              expect and what should not move in the scene. Describe who/what
              is causing the movement.
            - It will use the image as a starting point. Be clear about how
              the scene transitions and keep it on theme.
            - Character names won't be understood here, use pronouns +
              descriptions to detail actions.
            - Make sure to mention that there should be no text or logos added
              to the video, except for the logo video where you should ensure
              the logo is always present for the entire duration of the video.
            - Explicitly ground each of your prompts to follow the laws of
              physics.
        tool_context (ToolContext): The context for artifact management.
        num_images (int): The total number of images available.
        scene_numbers (Optional[List[int]]): A list of specific 0-indexed scene
            numbers to generate videos for. If None, generates for all images.
            Must be in ascending order. Defaults to None.
        logo_prompt_present (bool): If true, the logo scene number must be
            included in scene_numbers. Defaults to True.

    Returns:
        A dictionary containing the status of the generation, a detail message,
        a list of successfully generated videos, and a list of failures.
    """
    image_sources = _get_image_sources(scene_numbers, num_images)
    vertex_client = _initialize_vertex_client()

    tasks, task_sources, failed_videos = await _create_video_tasks(
        image_sources,
        video_queries,
        tool_context,
        vertex_client,
        logo_prompt_present,
    )

    successful_videos = []
    if tasks:
        results = await asyncio.gather(*tasks)
        successful_videos, failed_videos = _process_results(
            results, task_sources, failed_videos
        )

    return {
        "status": "success" if successful_videos else "failed",
        "detail": f"Generated {len(successful_videos)} video(s).",
        "videos": successful_videos,
        "failed_videos": failed_videos,
    }
