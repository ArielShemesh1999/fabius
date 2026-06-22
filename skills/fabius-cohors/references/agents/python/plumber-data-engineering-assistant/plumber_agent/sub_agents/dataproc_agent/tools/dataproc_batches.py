"""Module for managing Dataproc Serverless batches."""

import logging
from typing import Any

from google.api_core.exceptions import GoogleAPICallError
from google.cloud import dataproc_v1 as dataproc
from google.cloud.dataproc_v1 import BatchControllerClient
from google.cloud.dataproc_v1.types import (
    Batch,
    CreateBatchRequest,
    EnvironmentConfig,
    ExecutionConfig,
    PeripheralsConfig,
    PySparkBatch,
    RuntimeConfig,
    SparkBatch,
    SparkHistoryServerConfig,
)

logger = logging.getLogger("plumber-agent")


def get_batch_client(region: str) -> BatchControllerClient:
    """
    Creates a Dataproc BatchControllerClient for a specific region.

    Args:
        region: The GCP region for the client.

    Returns:
        A BatchControllerClient instance.
    """
    return BatchControllerClient(
        client_options={"api_endpoint": f"{region}-dataproc.googleapis.com:443"}
    )


def create_dataproc_serverless_batch(
    project_id: str,
    region: str,
    batch_id: str,
    job_type: str,
    job_details: dict[str, any],
) -> dict[str, Any]:
    """Creates a Dataproc Serverless batch job."""
    try:
        batch_client = get_batch_client(region)

        pyspark_batch_config = None
        spark_batch_config = None

        if job_type == "pyspark":
            pyspark_batch_config = PySparkBatch(
                main_python_file_uri=job_details.get("main_python_file_uri"),
                args=job_details.get("args", []),
            )
        elif job_type == "spark":
            spark_batch_config = SparkBatch(
                jar_file_uris=job_details.get("jar_file_uris"),
                main_class=job_details.get("main_class"),
                args=job_details.get("args", []),
            )

        runtime_config = RuntimeConfig(
            version=job_details.get("runtime_version", "1.1"),
            properties=job_details.get("properties", {}),
        )

        execution_config = None
        if job_details.get("service_account") or job_details.get("subnet_uri"):
            execution_config = ExecutionConfig(
                service_account=job_details.get("service_account"),
                subnetwork_uri=job_details.get("subnet_uri"),
            )

        environment_config = EnvironmentConfig()
        if execution_config:
            environment_config.execution_config = execution_config
        if job_details.get("spark_history_staging_dir"):
            environment_config.peripherals_config = PeripheralsConfig(
                spark_history_server_config=SparkHistoryServerConfig(
                    dataproc_staging_dir=job_details.get(
                        "spark_history_staging_dir"
                    )
                )
            )

        batch_labels = {"submitted_from": "plumber"}
        if job_details.get("labels"):
            batch_labels.update(job_details.get("labels"))

        batch = Batch(
            pyspark_batch=pyspark_batch_config,
            spark_batch=spark_batch_config,
            labels=batch_labels,
            environment_config=environment_config,
            runtime_config=runtime_config,
        )

        parent = f"projects/{project_id}/locations/{region}"
        request = CreateBatchRequest(
            parent=parent, batch_id=batch_id, batch=batch
        )

        batch_client.create_batch(request=request)

        return {
            "status": "success",
            "message": f"Batch {batch_id} created successfully.",
            "batch_id": batch_id,
        }

    except GoogleAPICallError as apierror:
        logger.error(
            "Google API Call Error during batch creation for %s: %s",
            batch_id,
            apierror.message,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": f"Failed to create Dataproc batch: {apierror.message}",
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "An unexpected error occurred during batch creation for %s: %s",
            batch_id,
            e,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"An unexpected error occurred during batch creation: {e!s}"
            ),
        }


def check_dataproc_serverless_status(
    project_id: str, region: str, batch_id: str
) -> dict[str, Any]:
    """
    Checks the status of a Dataproc Serverless batch job.

    Args:
        project_id: The GCP project ID.
        region: The GCP region of the batch job.
        batch_id: The ID of the batch job.

    Returns:
        A dictionary with the batch ID and its current state.
    """
    try:
        batch_client = get_batch_client(region)
        batch = batch_client.get_batch(
            name=f"projects/{project_id}/locations/{region}/batches/{batch_id}"
        )
        batch_state = batch.state
        return {
            "batch_id": batch_id,
            "state": dataproc.Batch.State(batch_state).name,
        }

    except GoogleAPICallError as apierror:
        logger.error(
            "Google API Call Error while checking status for %s: %s",
            batch_id,
            apierror.message,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"Failed to list Dataproc Serverless batches by state: {apierror.message}"
            ),
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "An unexpected error occurred while checking status for %s: %s",
            batch_id,
            e,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"An unexpected error occurred while checking batch status: {e!s}"
            ),
        }


def list_dataproc_serverless_batches(
    project_id: str, region: str
) -> list[dict[str, Any]]:
    """
    Lists all Dataproc Serverless batch jobs in a region.

    Args:
        project_id: The GCP project ID.
        region: The GCP region to list batches from.

    Returns:
        A list of dictionaries, each representing a batch job.
    """
    try:
        batch_client = get_batch_client(region)
        batches = batch_client.list_batches(
            parent=f"projects/{project_id}/locations/{region}"
        )
        all_batches = [
            {
                "batch_id": batch.name.split("/")[-1],
                "state": dataproc.Batch.State(batch.state).name,
                "create_time": batch.create_time,
            }
            for batch in batches
        ]
        return all_batches[:30]

    except GoogleAPICallError as apierror:
        logger.error(
            "Google API Call Error while listing all batches in %s: %s",
            region,
            apierror.message,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"Failed to check Dataproc Serverless batch status: {apierror.message}"
            ),
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "An unexpected error occurred while listing all batches in %s: %s",
            region,
            e,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"An unexpected error occurred while checking batch status: {e!s}"
            ),
        }


def list_dataproc_serverless_batches_by_state(
    project_id: str, region: str, state: str
) -> list[dict[str, Any]]:
    """
    Lists Dataproc Serverless batch jobs in a region filtered by state.

    Args:
        project_id: The GCP project ID.
        region: The GCP region to list batches from.
        state: The state to filter batches by (e.g., 'RUNNING', 'SUCCEEDED').

    Returns:
        A list of dictionaries, each representing a batch job in the specified state.
    """
    try:
        batch_client = get_batch_client(region)
        batches = batch_client.list_batches(
            parent=f"projects/{project_id}/locations/{region}"
        )
        filtered_batches = [
            {
                "batch_id": batch.name.split("/")[-1],
                "state": dataproc.Batch.State(batch.state).name,
                "create_time": batch.create_time,
            }
            for batch in batches
            if dataproc.Batch.State(batch.state).name == state
        ]
        return filtered_batches

    except GoogleAPICallError as apierror:
        logger.error(
            "Google API Call Error while listing batches by state '%s' in %s: %s",
            state,
            region,
            apierror.message,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"Failed to check Dataproc Serverless batch status: {apierror.message}"
            ),
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "An unexpected error occurred while listing batches by state '%s' in %s: %s",
            state,
            region,
            e,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"An unexpected error occurred while checking batch status: {e!s}"
            ),
        }


def delete_dataproc_serverless_batch(
    project_id: str, region: str, batch_id: str
) -> dict[str, Any]:
    """
    Deletes a Dataproc Serverless batch job.

    Args:
        project_id: The GCP project ID.
        region: The GCP region of the batch job.
        batch_id: The ID of the batch job to delete.

    Returns:
        A dictionary with the status of the deletion.
    """
    try:
        batch_client = get_batch_client(region)
        batch_client.delete_batch(
            name=f"projects/{project_id}/locations/{region}/batches/{batch_id}"
        )
        return {
            "status": "success",
            "message": f"Batch {batch_id} deleted successfully.",
        }

    except GoogleAPICallError as apierror:
        logger.error(
            "Google API Call Error while deleting batch %s: %s",
            batch_id,
            apierror.message,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"Failed to delete Dataproc Serverless batch: {apierror.message}"
            ),
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "An unexpected error occurred while deleting batch %s: %s",
            batch_id,
            e,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"An unexpected error occurred while deleting the batch: {e!s}"
            ),
        }
