"""
This module provides utility functions for interacting with the Google Cloud Dataflow API.
It includes functions for listing, getting details of, and canceling Dataflow jobs.
"""

import logging
from http import HTTPStatus

from google.auth import default
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- Configuration and API Client Setup ---
logger = logging.getLogger("plumber-agent")
try:
    credentials, _ = default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    dataflow_service = build("dataflow", "v1b3", credentials=credentials)
except Exception as e:
    logger.error("An error occurred: %s", e, exc_info=True)
    raise RuntimeError(
        f"Failed to initialize Google API clients. Error: {e}"
    ) from e


# ===== Dataflow Job and Template Management Tools =====


def list_dataflow_jobs(
    project_id: str, location: str | None = None, status: str | None = None
) -> dict[str, str]:
    """
    Lists up to 30 of the most recent Google Cloud Dataflow jobs for a given project.

    By default, jobs from all regions are listed. Optionally, jobs can be
    filtered by a specific region (location) and/or job status.

    Args:
        project_id (str): The Google Cloud project ID where the Dataflow jobs
            are running.
        location (Optional[str], optional): The region to filter jobs by
            (e.g. 'us-central1'). If not specified or None, jobs from all
            regions are included.
        status (Optional[str], optional): Filter jobs by their current status.
            Allowed values are 'UNKNOWN', 'ALL', 'TERMINATED', 'ACTIVE'. If not
            specified, no status filtering is applied.

    Returns:
        dict: A dictionary with one of the following keys:
            - On success:
                {
                    "status": "success",
                    "report": str  # Human-readable summary of jobs found or none found.
                }
            - On API error:
                {
                    "status": "error",
                    "error_message": str  # Description of the API error.
                }
    """
    search_location = location or "-"
    print(f"INFO: Listing jobs in location: '{search_location}'")

    try:
        request = (
            dataflow_service.projects()  # pylint: disable=no-member
            .locations()
            .jobs()
            .list(projectId=project_id, location=search_location)
        )
        response = request.execute()
        jobs = response.get("jobs", [])

        if status:
            jobs = [
                job
                for job in jobs
                if job.get("currentState", "").lower()
                == f"job_state_{status.lower()}"
            ]

        search_scope = (
            "in all regions"
            if search_location == "-"
            else f"in location '{search_location}'"
        )

        if not jobs:
            return {
                "status": "success",
                "report": f"No Dataflow jobs found {search_scope}.",
            }

        # Sort jobs by createTime in descending order and take the top 30
        jobs.sort(key=lambda x: x["createTime"], reverse=True)
        jobs = jobs[:30]

        report = f"Found {len(jobs)} jobs {search_scope}:\n"
        for job in jobs:
            report += f"- Job Name: {job['name']} (ID: {job['id']})\n"
        return {"status": "success", "report": report}
    except HttpError as e:
        logger.error("An error occurred: %s", e, exc_info=True)
        return {
            "status": "error",
            "error_message": (
                f"API Error listing jobs: {e.reason} (Code: {e.status_code})"
            ),
        }


def get_dataflow_job_details(
    project_id: str, job_id: str, location: str
) -> dict[str, str]:
    """
    Retrieves detailed information and metrics for a specific Google Cloud
    Dataflow job.

    The job's location must be provided to retrieve the details. Use the
    `list_dataflow_jobs` function to find the correct location for a job if
    unknown.

    Args:
        project_id (str): The ID of the Google Cloud project containing the
            Dataflow job.
        job_id (str): The unique identifier of the Dataflow job.
        location (str): The regional location where the job is running
            (e.g., 'us-central1').

    Returns:
        dict: A dictionary containing either the job details and metrics report
              on success, or an error message on failure. The dictionary has
              the following keys:
            - On success:
                {
                    "status": "success",
                    "report": str  # Human-readable formatted job details and metrics.
                }
            - On job not found (HTTP 404):
                {
                    "status": "error",
                    "error_message": str  # Explanation that job was not found in given location.
                }
            - On other API errors:
                {
                    "status": "error",
                    "error_message": str  # Description of the API error and status code.
                }

    """
    try:
        job = (
            dataflow_service.projects()  # pylint: disable=no-member
            .locations()
            .jobs()
            .get(projectId=project_id, location=location, jobId=job_id)
            .execute()
        )
        report = (
            f"Job Details:\n"
            f"  ID: {job['id']}\n"
            f"  Name: {job['name']}\n"
            f"  State: {job['currentState']}\n"
            f"  Location: {job.get('location', 'N/A')}\n"
            f"  Type: {job.get('type', 'N/A')}\n"
            f"  Created: {job['createTime']}\n"
        )

        metrics = (
            dataflow_service.projects()  # pylint: disable=no-member
            .locations()
            .jobs()
            .getMetrics(projectId=project_id, location=location, jobId=job_id)
            .execute()
        )
        report += "\nJob Metrics:\n"
        for metric in metrics.get("metrics", []):
            report += (
                f"- {metric['name']['name']}: {metric.get('scalar', 'N/A')}\n"
            )

        return {
            "status": "success",
            "report": report or "No metrics available for this job.",
        }
    except HttpError as e:
        logger.error("An error occurred: %s", e, exc_info=True)
        if e.status_code == HTTPStatus.NOT_FOUND:
            error_message = (
                f"Job with ID '{job_id}' not found in location '{location}'. "
                "Please verify the job ID and its location. You can use 'list_dataflow_jobs' "
                "to find the correct location for all jobs."
            )
            return {
                "status": "error",
                "error_message": error_message,
            }
        return {
            "status": "error",
            "error_message": (f"API Error: {e.reason} (Code: {e.status_code})"),
        }


def cancel_dataflow_job(
    project_id: str, job_id: str, location: str
) -> dict[str, str]:
    """
    Cancels a running Google Cloud Dataflow job.

    The job's location must be provided to correctly identify and cancel the job.

    Args:
        project_id (str): The ID of the Google Cloud project containing the
            Dataflow job.
        job_id (str): The unique identifier of the Dataflow job to be cancelled.
        location (str): The regional location where the job is running
            (e.g., 'us-central1').

    Returns:
        dict: A dictionary indicating success or failure of the cancellation
              request with keys:
            - On success:
                {
                    "status": "success",
                    "report": str  # Confirmation message that cancellation was requested.
                }
            - On job not found (HTTP 404):
                {
                    "status": "error",
                "error_message": str  # Explanation that job was not found in the given location.
                }
            - On invalid cancellation attempt (e.g., job already terminal):
                {
                    "status": "error",
                "error_message": str  # Explanation that job cannot be cancelled due to its state.
                }
            - On other API or unexpected errors:
                {
                    "status": "error",
                    "error_message": str  # Error message describing the failure.
                }
    """
    print(
        f"INFO: Attempting to send cancellation request for job '{job_id}' in location "
        f"'{location}'..."
    )
    try:
        dataflow_service.projects().locations().jobs().update(  # pylint: disable=no-member
            projectId=project_id,
            location=location,
            jobId=job_id,
            body={"requestedState": "JOB_STATE_CANCELLED"},
        ).execute()
        return {
            "status": "success",
            "report": f"Job {job_id} cancellation request sent.",
        }
    except HttpError as e:
        logger.error("An error occurred: %s", e, exc_info=True)
        if e.status_code == HTTPStatus.NOT_FOUND:
            error_message = (
                f"Job with ID '{job_id}' not found in location '{location}'. "
                "Please verify the job ID and its location. Use "
                "'list_dataflow_jobs()' to confirm."
            )
            return {
                "status": "error",
                "error_message": error_message,
            }
        if (
            e.status_code == HTTPStatus.BAD_REQUEST
            and "immutable" in e.reason.lower()
        ):
            error_message = (
                f"Job '{job_id}' in '{location}' is already in a terminal "
                "state and cannot be cancelled."
            )
            return {
                "status": "error",
                "error_message": error_message,
            }
        return {
            "status": "error",
            "error_message": (
                f"API Error cancelling job: {e.reason} (Code: {e.status_code})"
            ),
        }
