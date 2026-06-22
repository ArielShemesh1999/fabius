"""
This module handles the deployment of dbt projects from Google Cloud Storage
to the local environment.
"""

import logging
import os

from ..constants import STORAGE_CLIENT

logger = logging.getLogger("plumber-agent")


def deploy_dbt_project(gcs_bucket_path: str) -> dict[str, str | None]:
    """
    Downloads a dbt project directory from a Google Cloud Storage (GCS) bucket
    and deploys it locally under a `dbt_projects/` directory.

    The function:
    - Validates the input GCS URL.
    - Extracts the bucket name and project directory path.
    - Lists all blobs/files under the project path in the bucket.
    - Downloads all files to a local directory structure mirroring the GCS structure.
    - Creates local directories as needed.

    Args:
        gcs_bucket_path (str): A GCS URL (starting with "gs://") pointing to the
          root of the dbt project folder.

    Returns:
        dict: A dictionary containing:
            - "deployment_status" (str): "success" or an error message.
            - "deployed_path" (str or None): Local path of the deployed project, or None on failure.
    """
    try:
        if not gcs_bucket_path.startswith("gs://"):
            return {
                "deployment_status": "Invalid gcs URL",
                "deployed_path": None,
            }

        bucket_name, project_name = gcs_bucket_path[5:].split("/", 1)

        bucket = STORAGE_CLIENT.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=project_name)

        # COMPUTING THE TARGET FOLDER
        target_folder = f"dbt_projects/{project_name}"

        # CREATING TARGET DIRECTORY IF NOT EXIST
        os.makedirs(target_folder, exist_ok=True)

        for blob in blobs:
            relative_path = os.path.relpath(blob.name, project_name)
            local_file_path = os.path.join(target_folder, relative_path)
            local_file_dir = os.path.dirname(local_file_path)

            # CREATE SUB-DIRECTORY IF NOT EXIST
            os.makedirs(local_file_dir, exist_ok=True)

            # DOWNLOAD THE FILE TO THE PATH
            if not blob.name.endswith("/"):
                blob.download_to_filename(local_file_path)
        return {
            "deployment_status": "success",
            "deployed_path": f"./dbt_projects/{project_name}",
        }
    except Exception as err:  # pylint: disable=broad-exception-caught
        logger.error("An error occurred: %s", err, exc_info=True)
        return {"deployment_status": f"error - {err!s}", "deployed_path": None}
