"""
This module provides tools for interacting with Google Cloud Dataflow.
"""

import logging
from datetime import datetime, timedelta

from google.api_core import exceptions as google_exceptions
from google.cloud import logging_v2

from .utils import _process_log_iterator

logger = logging.getLogger("plumber-agent")


def get_dataflow_job_logs_with_id(
    project_id: str, job_id: str, _limit: int = 10
) -> dict[str, str]:
    """
    Fetches log entries for a specific Dataflow job using its ID from Google Cloud Logging.

    This function retrieves log entries from Google Cloud Logging that are associated
    with a particular Google Cloud Dataflow job, identified by its unique `job_id`.
    It aims to provide insights into the job's execution, status, and any potential issues.
    By default, it fetches up to 10 of the most recent log entries.

    Args:
        project_id (str, required): The Google Cloud project ID. from which logs are to be fetched.
        job_id (str, required): The unique identifier of the Dataflow job
            for which the logs are to be fetched. This argument is required
            to filter the logs specifically for a given job.
        _limit (int, optional): The maximum number of log entries to fetch. The function
            will retrieve up to this many entries, Defaults to 10.

    Returns:
        dict: A dictionary containing the status of the operation and the retrieved logs.
            The dictionary will have the following structure:
                - "status" (str): "success" if logs were fetched successfully, or "error"
                    if an error occurred.
                - "report" (str): A human-readable message detailing the outcome.
                    If successful, it includes a summary and a list of the fetched log entries.
                    If no logs are found for the given job ID, it indicates that.
                - "message" (str, optional): Only present if "status" is "error", providing
                details about the error that occurred.

    Note: [IMPORTANT]
        - Don't call this tool until you have job_id
            - example job_id : 2025-07-11_02_51_43-12657112666808971216
    """

    logger.info(
        "datetime.now() - timedelta(days=90): %s",
        (datetime.now() - timedelta(days=90)).isoformat(),
    )

    filter_string = (
        f'resource.type="dataflow_step" AND '
        f'resource.labels.job_id="{job_id}" AND '
        f'timestamp >= "{(datetime.now() - timedelta(days=90)).isoformat()}Z"'
    )

    try:
        client = logging_v2.Client(project=project_id)
        project_path = f"projects/{project_id}"
        iterator = client.list_entries(
            resource_names=[project_path],
            filter_=filter_string,
            max_results=_limit,
        )

        collected_logs = _process_log_iterator(iterator, _limit)

        return {
            "status": "success",
            "report": (
                f"Fetched log entries of Job ID: {job_id}:\n"
                + "\n".join(collected_logs)
            ),
        }

    except StopIteration as err:
        logger.error("An error occurred: %s", err, exc_info=True)
        return {
            "status": "success",
            "report": "No job log entry found with given ID.",
        }
    except google_exceptions.GoogleAPIError as err:
        logger.error(
            "A Google Cloud API error occurred: %s", err, exc_info=True
        )
        return {
            "status": "error",
            "message": f"Failed to get job with given id due to API error: {err}",
        }
    except Exception as err:  # pylint: disable=broad-exception-caught
        logger.error("An unexpected error occurred: %s", err, exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to get job with given id due to unexpected error: {err}",
        }
