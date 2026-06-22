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
"""Combines video clips, audio, and voiceovers into a final video."""

import datetime
import logging
import os
import tempfile
import time

from dotenv import load_dotenv
from google import genai
from google.adk.tools import ToolContext
from google.api_core import exceptions as api_exceptions
from google.cloud import storage
from moviepy import (
    AudioFileClip,
    CompositeAudioClip,
    VideoFileClip,
    concatenate_videoclips,
)

# --- Configuration ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()

VIDEO_CODEC = "libx264"
GCS_VIDEO_FOLDER = "videos"


def _get_storyline_schema(num_images: int) -> list[dict]:
    """Generates a storyline schema with a dynamic number of scenes.

    Args:
        num_images (int): The total number of images in the storyline.

    Returns:
        A list of dictionaries, where each dictionary defines a scene.
    """
    if num_images <= 0:
        return []

    schema = []
    if num_images > 1:
        schema.append(
            {"name": "before", "generate": True, "step": 0, "duration": 3}
        )

    for i in range(num_images - 2):
        schema.append(
            {
                "name": f"showcase_{i + 1}",
                "generate": True,
                "step": i + 1,
                "duration": 3,
            }
        )

    schema.append(
        {
            "name": "logo",
            "generate": True,
            "step": num_images - 1,
            "duration": 5,
        }
    )
    return schema


def _get_datetime_folder_path() -> str:
    """Generates a GCS folder path based on the current date and time.

    Returns:
        A path in the format 'videos/YYYY-MM-DD/HH-MM-SS/'.
    """
    now = datetime.datetime.now(datetime.UTC)
    date_folder = now.strftime("%Y-%m-%d")
    time_folder = now.strftime("%H-%M-%S")
    return f"{GCS_VIDEO_FOLDER}/{date_folder}/{time_folder}/"


def _upload_to_gcs(video_bytes: bytes, filename: str) -> str | None:
    """Uploads a video to Google Cloud Storage.

    Args:
        video_bytes (bytes): The video file bytes to upload.
        filename (str): The name of the video file.

    Returns:
        The GCS URI of the uploaded file, or None if the upload fails.
    """
    try:
        project_id = os.getenv("GCP_PROJECT")
        if not project_id:
            logging.error("GCP_PROJECT environment variable not set.")
            return None

        bucket_name = (
            os.getenv("GCS_BUCKET") or f"{project_id}-contentgen-static"
        )
        folder_path = _get_datetime_folder_path()
        blob_name = f"{folder_path}{filename}"

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(video_bytes, content_type="video/mp4")

        gcs_uri = f"gs://{bucket_name}/{blob_name}"
        logging.info("Uploaded combined video to GCS: %s", gcs_uri)
        return gcs_uri
    except (api_exceptions.GoogleAPICallError, OSError) as e:
        logging.error("Failed to upload video to GCS: %s", e, exc_info=True)
        return None


async def _load_single_clip(
    filename: str,
    tool_context: ToolContext,
    temp_dir: str,
    storyline: list[dict],
) -> tuple[VideoFileClip, str] | None:
    """Loads and processes a single video clip artifact."""
    try:
        artifact = await tool_context.load_artifact(filename)
        if not (
            artifact and artifact.inline_data and artifact.inline_data.data
        ):
            logging.warning("Could not load artifact data for %s.", filename)
            return None

        temp_path = os.path.join(temp_dir, os.path.basename(filename))
        with open(temp_path, "wb") as f:
            f.write(artifact.inline_data.data)

        clip = VideoFileClip(temp_path)
        clip_index_str = filename.split("_")[0]
        if clip_index_str.isdigit():
            clip_index = int(clip_index_str)
            if 0 <= clip_index < len(storyline):
                duration = storyline[clip_index]["duration"]
                if clip.duration > duration:
                    clip = clip.subclipped(0, duration)
        return clip, temp_path
    except (OSError, ValueError) as e:
        logging.error(
            "Failed to load/process video artifact '%s': %s",
            filename,
            e,
            exc_info=True,
        )
        return None


async def _load_and_process_video_clips(
    video_files: list[str],
    num_images: int,
    tool_context: ToolContext,
    temp_dir: str,
) -> tuple[list[VideoFileClip], list[str]]:
    """Loads video artifacts, processes them, and returns clips.

    Args:
        video_files (List[str]): A list of video artifact filenames.
        num_images (int): The number of images in the storyline.
        tool_context (ToolContext): The context for artifact management.
        temp_dir (str): The temporary directory to store video files.

    Returns:
        A tuple containing a list of VideoFileClip objects and their paths.
    """
    video_clips, temp_paths = [], []
    storyline = _get_storyline_schema(num_images)

    for filename in video_files:
        if not filename:
            logging.warning("Skipping video file with missing filename.")
            continue

        result = await _load_single_clip(
            filename, tool_context, temp_dir, storyline
        )
        if result:
            clip, temp_path = result
            video_clips.append(clip)
            temp_paths.append(temp_path)

    return video_clips, temp_paths


async def _load_and_process_audio_clips(
    audio_file: str,
    voiceover_file: str | None,
    final_duration: float,
    tool_context: ToolContext,
    temp_dir: str,
) -> CompositeAudioClip | None:
    """Loads and processes audio and voiceover files into a composite clip.

    Args:
        audio_file (str): The filename of the background audio artifact.
        voiceover_file (Optional[str]): The filename of the voiceover artifact.
        final_duration (float): The duration of the final video.
        tool_context (ToolContext): The context for artifact management.
        temp_dir (str): The temporary directory to store audio files.

    Returns:
        A CompositeAudioClip or None if no audio is loaded.
    """
    audio_clips = []
    try:
        # Background audio
        artifact = await tool_context.load_artifact(audio_file)
        if artifact and artifact.inline_data and artifact.inline_data.data:
            temp_path = os.path.join(temp_dir, os.path.basename(audio_file))
            with open(temp_path, "wb") as f:
                f.write(artifact.inline_data.data)
            audio_clips.append(AudioFileClip(temp_path))

        # Voiceover
        if voiceover_file:
            vo_artifact = await tool_context.load_artifact(voiceover_file)
            if (
                vo_artifact
                and vo_artifact.inline_data
                and vo_artifact.inline_data.data
            ):
                temp_path = os.path.join(
                    temp_dir, os.path.basename(voiceover_file)
                )
                with open(temp_path, "wb") as f:
                    f.write(vo_artifact.inline_data.data)
                vo_clip = AudioFileClip(temp_path)
                vo_start = max(0, final_duration - vo_clip.duration)
                audio_clips.append(vo_clip.with_start(vo_start))

        if audio_clips:
            return CompositeAudioClip(audio_clips).with_duration(final_duration)
    except (OSError, ValueError) as e:
        logging.error("Failed to load or process audio: %s", e, exc_info=True)
    return None


async def _combine_and_upload_video(
    video_clips: list[VideoFileClip],
    audio_file: str,
    voiceover_file: str | None,
    tool_context: ToolContext,
    temp_dir: str,
) -> dict[str, str] | None:
    """Combines video clips with audio and uploads the result."""
    try:
        final_clip = concatenate_videoclips(video_clips, method="compose")
        final_clip.audio = await _load_and_process_audio_clips(
            audio_file,
            voiceover_file,
            final_clip.duration,
            tool_context,
            temp_dir,
        )

        filename = f"combined_video_{int(time.time())}.mp4"
        output_path = os.path.join(temp_dir, filename)
        final_clip.write_videofile(output_path, codec=VIDEO_CODEC)

        with open(output_path, "rb") as f:
            video_bytes = f.read()

        gcs_uri = _upload_to_gcs(video_bytes, filename)
        await tool_context.save_artifact(
            filename,
            genai.types.Part.from_bytes(
                data=video_bytes, mime_type="video/mp4"
            ),
        )

        result = {"name": filename}
        if gcs_uri:
            result["gcs_uri"] = gcs_uri
        return result
    except (OSError, ValueError) as e:
        logging.error(
            "An error occurred during video combination: %s", e, exc_info=True
        )
        return None
    finally:
        for clip in video_clips:
            clip.close()


async def combine(
    video_files: list[str],
    audio_file: str,
    num_images: int,
    tool_context: ToolContext,
    voiceover_file: str | None = None,
) -> dict[str, str] | None:
    """Combines videos, audio, and voiceover into a single file.

    Args:
        video_files (List[str]): A list of video artifact filenames.
        audio_file (str): The filename of the background audio artifact.
        num_images (int): The number of images in the storyline.
        tool_context (ToolContext): The context for tool execution and
          artifact management.
        voiceover_file (Optional[str]): The filename of the voiceover artifact.
          Defaults to None.

    Returns:
        A dictionary with the combined video artifact name and GCS URI.
    """
    if not video_files:
        logging.warning("No video files provided to combine.")
        return None

    with tempfile.TemporaryDirectory() as temp_dir:
        video_clips, _ = await _load_and_process_video_clips(
            video_files, num_images, tool_context, temp_dir
        )
        if not video_clips:
            logging.error("No valid video clips could be loaded.")
            return None

        return await _combine_and_upload_video(
            video_clips, audio_file, voiceover_file, tool_context, temp_dir
        )
