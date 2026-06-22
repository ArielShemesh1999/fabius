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

"""This module provides a set of tools for interacting with Google Cloud Storage.

It includes functionalities for validating bucket and file existence, listing
files in buckets,
and reading files with various options (head, tail, or full content).
"""

from typing import Any

from google.cloud import storage

from ..config import config


def get_gcs_client() -> storage.Client:
    """Get a configured GCS client."""
    return storage.Client(project=config.project_id)


def validate_bucket_exists_tool(bucket_name: str) -> dict[str, Any]:
    """Validate if a GCS bucket exists.

    Args:
        bucket_name (str): The name of the bucket to validate.

    Returns:
        Dict[str, Any]: Dictionary containing validation results and bucket
        metadata if exists.
    """
    try:
        client = get_gcs_client()
        bucket = client.bucket(bucket_name)

        if bucket.exists():
            bucket.reload()  # Get fresh metadata
            return {
                "status": "success",
                "exists": True,
                "bucket_name": bucket_name,
                "metadata": {
                    "created": (
                        bucket.time_created.isoformat()
                        if bucket.time_created
                        else None
                    ),
                    "updated": bucket.updated.isoformat()
                    if bucket.updated
                    else None,
                    "location": bucket.location,
                    "storage_class": bucket.storage_class,
                    "labels": bucket.labels,
                },
            }
        else:
            return {
                "status": "success",
                "exists": False,
                "bucket_name": bucket_name,
            }

    except Exception as e:
        return {"status": "error", "error": str(e)}


def validate_file_exists_tool(
    bucket_name: str, file_path: str
) -> dict[str, Any]:
    """Validate if a file exists in a GCS bucket.

    Args:
        bucket_name (str): The name of the bucket.
        file_path (str): The path of the file within the bucket.

    Returns:
        Dict[str, Any]: Dictionary containing validation results and file metadata
        if exists.
    """
    try:
        client = get_gcs_client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_path)

        if blob.exists():
            blob.reload()  # Get fresh metadata
            return {
                "status": "success",
                "exists": True,
                "bucket_name": bucket_name,
                "file_path": file_path,
                "metadata": {
                    "size": blob.size,
                    "content_type": blob.content_type,
                    "created": (
                        blob.time_created.isoformat()
                        if blob.time_created
                        else None
                    ),
                    "updated": blob.updated.isoformat()
                    if blob.updated
                    else None,
                    "md5_hash": blob.md5_hash,
                    "generation": blob.generation,
                },
            }
        else:
            return {
                "status": "success",
                "exists": False,
                "bucket_name": bucket_name,
                "file_path": file_path,
            }

    except Exception as e:
        return {"status": "error", "error": str(e)}


def list_bucket_files_tool(
    bucket_name: str,
    prefix: str | None = None,
    delimiter: str | None = None,
    max_results: int | None = None,
) -> dict[str, Any]:
    """List files in a GCS bucket with optional filtering.

    Args:
        bucket_name (str): The name of the bucket.
        prefix (Optional[str]): Filter results to objects whose names begin with
          this prefix.
        delimiter (Optional[str]): Filter results to objects whose names don't
          contain the delimiter.
        max_results (Optional[int]): Maximum number of results to return.

    Returns:
        Dict[str, Any]: Dictionary containing list of files and their metadata.
    """
    try:
        client = get_gcs_client()
        bucket = client.bucket(bucket_name)

        # Build the list of blobs
        blobs = bucket.list_blobs(
            prefix=prefix, delimiter=delimiter, max_results=max_results
        )

        # Collect file information
        files = []
        prefixes = []

        for blob in blobs:
            if isinstance(blob, storage.Blob):
                files.append(
                    {
                        "name": blob.name,
                        "size": blob.size,
                        "content_type": blob.content_type,
                        "created": (
                            blob.time_created.isoformat()
                            if blob.time_created
                            else None
                        ),
                        "updated": blob.updated.isoformat()
                        if blob.updated
                        else None,
                    }
                )
            else:
                prefixes.append(blob)

        return {
            "status": "success",
            "bucket_name": bucket_name,
            "prefix": prefix,
            "delimiter": delimiter,
            "files": files,
            "prefixes": prefixes,
            "total_files": len(files),
            "total_prefixes": len(prefixes),
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}


def read_gcs_file_tool(
    bucket_name: str, file_path: str, mode: str = "full", num_lines: int = 10
) -> dict[str, Any]:
    """Read content from a GCS file with various options.

    Args:
        bucket_name (str): The name of the bucket.
        file_path (str): The path of the file within the bucket.
        mode (str): Reading mode - "head", "tail", or "full". Defaults to "full".
        num_lines (int): Number of lines to read for head/tail modes. Defaults to
          10.

    Returns:
        Dict[str, Any]: Dictionary containing file content and metadata.
    """
    try:
        client = get_gcs_client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_path)

        if not blob.exists():
            return {
                "status": "error",
                "error": f"File {file_path} does not exist in bucket {bucket_name}",
            }

        # Read the file content
        content = blob.download_as_text()
        lines = content.splitlines()

        # Process based on mode
        if mode == "head":
            result_lines = lines[:num_lines]
            position = "start"
        elif mode == "tail":
            result_lines = lines[-num_lines:]
            position = "end"
        else:  # full
            result_lines = lines
            position = "full"

        return {
            "status": "success",
            "bucket_name": bucket_name,
            "file_path": file_path,
            "mode": mode,
            "num_lines": len(result_lines),
            "position": position,
            "content": "\n".join(result_lines),
            "metadata": {
                "size": blob.size,
                "content_type": blob.content_type,
                "created": (
                    blob.time_created.isoformat() if blob.time_created else None
                ),
                "updated": blob.updated.isoformat() if blob.updated else None,
            },
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}
