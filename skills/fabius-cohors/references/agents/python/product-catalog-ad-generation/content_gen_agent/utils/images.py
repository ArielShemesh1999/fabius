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
"""Utility functions for handling images."""

import logging
import os

from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types

# --- Configuration ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

IMAGE_MIME_TYPE = "image/png"


async def _load_gcs_image(
    gcs_uri: str, storage_client: storage.Client
) -> types.Part | None:
    """Loads an image from GCS and returns it as a Part object.

    Args:
        gcs_uri: The GCS URI of the image. Does not start with "gs://"
        storage_client: The GCS storage client.

    Returns:
        A Part object containing the image data, or None on failure.
    """
    try:
        bucket_name, blob_name = gcs_uri.split("/", 1)
        blob = storage_client.bucket(bucket_name).blob(blob_name)
        image_bytes = blob.download_as_bytes()
        return types.Part.from_bytes(
            data=image_bytes, mime_type=IMAGE_MIME_TYPE
        )
    except Exception as e:
        logging.error(f"Failed to load image from '{gcs_uri}': {e}")
        return None


async def ensure_image_artifact(
    image_filename: str,
    tool_context: ToolContext,
) -> str | None:
    """Ensures the image artifact exists, creating it if necessary from GCS.

    If an `image_filename` is provided that starts with "gs://", it will be
    downloaded from GCS and saved as an artifact. Otherwise, it's assumed to be
    an existing artifact.

    Args:
        image_filename (str): The filename of an existing image artifact or a
          GCS URI.
        tool_context (ToolContext): The context used to load and save artifacts

    Returns:
        The filename of the image artifact, or None on failure.
    """
    if image_filename.startswith("gs://"):
        try:
            storage_client = storage.Client()
            gcs_uri = image_filename.replace("gs://", "")
            image_part = await _load_gcs_image(gcs_uri, storage_client)
            if image_part:
                artifact_filename = gcs_uri.split("/")[-1]
                await tool_context.save_artifact(artifact_filename, image_part)
                logging.info(
                    "Saved image from GCS URI '%s' as artifact '%s'",
                    gcs_uri,
                    artifact_filename,
                )
                return artifact_filename
            else:
                raise ValueError("Failed to load image from GCS.")
        except Exception as e:
            logging.warning(
                "Failed to process GCS URI '%s': %s. Will try to load as artifact.",
                image_filename,
                e,
                exc_info=True,
            )
            # Fall through to try loading as an artifact
            image_filename = image_filename.split("/")[-1]

    try:
        logging.info(
            "Using provided image filename: %s, context has: %s",
            image_filename,
            await tool_context.list_artifacts(),
        )
        # Verify the artifact exists by trying to load it.
        await tool_context.load_artifact(image_filename)
        logging.info("Using existing image artifact: %s", image_filename)
        return image_filename
    except Exception as e:
        logging.warning(
            "Could not load provided artifact '%s': %s.",
            image_filename,
            e,
        )
        return None


async def load_image_resource(
    source_path: str,
    tool_context: "ToolContext",
) -> tuple[bytes | None, str, str]:
    """Loads image bytes from either a GCS path or a tool artifact.

    Args:
        source_path (str): The path to the image.  Must start with gs://
          if GCS URI.
        tool_context (ToolContext): The context for artifact management.

    Returns:
        A tuple with the image bytes, identifier, and MIME type.
    """
    identifier = os.path.basename(source_path).split(".")[0]
    mime_suffix = "jpeg" if source_path.lower().endswith(".jpg") else "png"

    if source_path.startswith("gs://"):
        gcs_uri = source_path.replace("gs://", "")
        _bucket_name, _blob_name = gcs_uri.split("/", 1)
        storage_client = storage.Client()
        image_bytes = _load_gcs_image(gcs_uri, storage_client)
    else:
        artifact = await tool_context.load_artifact(source_path)
        image_bytes = (
            artifact.inline_data.data
            if artifact and artifact.inline_data
            else None
        )

    return image_bytes, identifier, f"image/{mime_suffix}"
