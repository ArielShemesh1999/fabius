"""Module for managing Dataproc jobs."""

import datetime
import logging
import os
from typing import Any

from dotenv import load_dotenv
from google.api_core.exceptions import GoogleAPICallError
from google.cloud import dataproc_v1 as dataproc
from google.cloud.dataproc_v1 import JobControllerClient
from google.cloud.dataproc_v1.types import Job, JobPlacement, SparkJob

logger = logging.getLogger("plumber-agent")

load_dotenv()


def get_job_client(region: str) -> JobControllerClient:
    """
    Creates a Dataproc JobControllerClient for a specific region.

    Args:
        region: The GCP region for the client.

    Returns:
        A JobControllerClient instance.
    """
    return JobControllerClient(
        client_options={"api_endpoint": f"{region}-dataproc.googleapis.com:443"}
    )


def submit_pyspark_job(
    project_id: str,
    region: str,
    cluster_name: str,
    main_python_file_uri: str,
    # input_path: str | None = None,
    input_path: str | None = None,
) -> dict[str, Any]:
    """
    Submits a PySpark job to a Dataproc cluster.

    Args:
        project_id: The GCP project ID.
        region: The GCP region of the cluster.
        cluster_name: The name of the cluster to run the job on.
        main_python_file_uri: The GCS URI of the main Python file.
        input_path: The GCS URI of the input data (optional).

    Returns:
        A dictionary with the submission status and job ID.
    """
    try:
        job_client = get_job_client(region)

        # Define the output path for the job
        output_bucket_path = os.getenv("GCS_BUCKET_FOR_OUTPUT")
        current_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_path = f"gs://{output_bucket_path}/output/wordcount_results_{current_timestamp}"

        job_args = [output_path]
        if input_path is not None:
            job_args.insert(0, input_path)

        # Define the PySpark job configuration
        pyspark_job = dataproc.PySparkJob(
            main_python_file_uri=main_python_file_uri, args=job_args
        )

        # Define where the job should run
        placement = dataproc.JobPlacement(cluster_name=cluster_name)

        # Construct the full Job object
        job = dataproc.Job(
            placement=placement,
            pyspark_job=pyspark_job,
            labels={"submitted_from": "plumber"},
        )

        # Submit the job
        submitted_job = job_client.submit_job(
            project_id=project_id, region=region, job=job
        )

        job_id = submitted_job.reference.job_id
        return {"status": "submitted", "job_id": job_id}

    except GoogleAPICallError as apierror:
        logger.error(
            "Google API Call Error while submitting PySpark job to cluster '%s': %s",
            cluster_name,
            apierror.message,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": f"Failed to submit Dataproc job: {apierror.message}",
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "An unexpected error occurred during PySpark job submission: %s",
            e,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"An unexpected error occurred during job submission: {e!s}"
            ),
        }


def submit_scala_job(
    project_id: str, region: str, cluster_name: str, main_jar_file_uri: str
) -> dict[str, Any]:
    """
    Submits a Scala Spark job to a Dataproc cluster.

    Args:
        project_id: The GCP project ID.
        region: The GCP region of the cluster.
        cluster_name: The name of the cluster to run the job on.
        main_jar_file_uri: The GCS URI of the main JAR file.

    Returns:
        A dictionary with the submission status and job ID.
    """
    try:
        # Create a client for the JobController API
        job_client = get_job_client(region)

        # Define the Spark job configuration
        spark_job = SparkJob(main_jar_file_uri=main_jar_file_uri)

        # Define where the job should run (on your specified cluster)
        placement = JobPlacement(cluster_name=cluster_name)

        # Construct the full Job object
        job = Job(
            placement=placement,
            spark_job=spark_job,
            labels={"submitted_from": "plumber"},
        )

        # Submit the job
        submitted_job = job_client.submit_job(
            project_id=project_id, region=region, job=job
        )

        job_id = submitted_job.reference.job_id
        return {"status": "submitted", "job_id": job_id}

    except GoogleAPICallError as apierror:
        logger.error(
            "Google API Call Error while submitting Scala Spark job to cluster '%s': %s",
            cluster_name,
            apierror.message,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": f"Failed to submit Scala job: {apierror.message}",
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "An unexpected error occurred during Scala job submission: %s",
            e,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"An unexpected error occurred during Scala job submission: {e!s}"
            ),
        }


def check_job_status(
    project_id: str, region: str, job_id: str
) -> dict[str, Any]:
    """
    Checks the status of a Dataproc job.

    Args:
        project_id: The GCP project ID.
        region: The GCP region of the job.
        job_id: The ID of the job.

    Returns:
        A dictionary with the job ID and its current status.
    """
    try:
        job_client = get_job_client(region)

        job = job_client.get_job(
            project_id=project_id, region=region, job_id=job_id
        )
        job_state = job.status.state

        return {
            "job_id": job_id,
            "status": job_state.name,
        }

    except GoogleAPICallError as e:
        logger.error(
            "Google API Call Error while checking status for job ID '%s': %s",
            job_id,
            e.message,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": f"Failed to check job status: {e.message}",
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "An unexpected error occurred while checking status for job ID '%s': %s",
            job_id,
            e,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"An unexpected error occurred while checking job status: {e!s}"
            ),
        }


def list_dataproc_jobs(
    project_id: str,
    region: str,
) -> dict[str, Any]:
    """
    Lists all Dataproc jobs in a region.

    Args:
        project_id: The GCP project ID.
        region: The GCP region to list jobs from.

    Returns:
        A dictionary containing a list of jobs.
    """
    try:
        # Create a client for the JobController API
        job_client = get_job_client(region)

        jobs = job_client.list_jobs(project_id=project_id, region=region)

        job_list = []
        for job in jobs:
            job_info = {
                "job_id": job.reference.job_id,
                "status": job.status.state.name,
                "status_message": (
                    job.status.details
                    if job.status.details
                    else "No detailed message."
                ),
            }

            if job.pyspark_job:
                job_info["type"] = "PySpark"
            elif job.spark_job:
                job_info["type"] = "Spark"
            elif job.hadoop_job:
                job_info["type"] = "Hadoop"
            elif job.spark_sql_job:
                job_info["type"] = "Spark SQL"
            elif job.presto_job:
                job_info["type"] = "Presto"
            else:
                job_info["type"] = "Unknown"

            job_list.append(job_info)

        return {"status": "success", "jobs": job_list}

    except GoogleAPICallError as apierror:
        logger.error(
            "Google API Call Error while listing all jobs in %s: %s",
            region,
            apierror.message,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": f"Failed to list Dataproc jobs: {apierror.message}",
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "An unexpected error occurred while listing all jobs in %s: %s",
            region,
            e,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"An unexpected error occurred while listing jobs: {e!s}"
            ),
        }


def list_dataproc_jobs_by_type(
    project_id: str,
    region: str,
    job_type: str,
) -> dict[str, Any]:
    """
    Lists Dataproc jobs in a region filtered by job type.

    Args:
        project_id: The GCP project ID.
        region: The GCP region to list jobs from.
        job_type: The type of job to filter by (e.g., 'PySpark', 'Spark').

    Returns:
        A dictionary containing a list of filtered jobs.
    """
    normalized_job_type = job_type.lower().strip()

    try:
        # Create a client for the JobController API
        job_client = get_job_client(region)

        jobs = job_client.list_jobs(project_id=project_id, region=region)

        filtered_job_list = []
        for job in jobs:
            current_job_type = "Unknown"
            if job.pyspark_job:
                current_job_type = "PySpark"
            elif job.spark_job:
                current_job_type = "Spark"
            elif job.hadoop_job:
                current_job_type = "Hadoop"
            elif job.spark_sql_job:
                current_job_type = "Spark SQL"
            elif job.presto_job:
                current_job_type = "Presto"

            # Check if the current job's type matches the requested job_type
            if current_job_type.lower() == normalized_job_type:
                job_info = {
                    "job_id": job.reference.job_id,
                    "status": job.status.state.name,
                    "status_message": (
                        job.status.details
                        if job.status.details
                        else "No detailed message."
                    ),
                    "type": current_job_type,
                }
                filtered_job_list.append(job_info)

        return {"status": "success", "jobs": filtered_job_list}

    except GoogleAPICallError as apierror:
        logger.error(
            "Google API Call Error while listing jobs by type '%s' in %s: %s",
            job_type,
            region,
            apierror.message,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"Failed to list Dataproc jobs by type: {apierror.message}"
            ),
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "An unexpected error occurred while listing jobs by type '%s' in %s: %s",
            job_type,
            region,
            e,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"An unexpected error occurred while listing jobs by type: {e!s}"
            ),
        }


def list_dataproc_jobs_by_cluster(
    project_id: str,
    region: str,
    cluster_name: str,
) -> dict[str, Any]:
    """
    Lists Dataproc jobs in a region filtered by cluster name.

    Args:
        project_id: The GCP project ID.
        region: The GCP region to list jobs from.
        cluster_name: The name of the cluster to filter jobs by.

    Returns:
        A dictionary containing a list of filtered jobs.
    """
    try:
        job_client = get_job_client(region)

        jobs = job_client.list_jobs(project_id=project_id, region=region)

        filtered_job_list = []
        for job in jobs:
            if job.placement and job.placement.cluster_name == cluster_name:
                current_job_type = "Unknown"
                if job.pyspark_job:
                    current_job_type = "PySpark"
                elif job.spark_job:
                    current_job_type = "Spark"
                elif job.hadoop_job:
                    current_job_type = "Hadoop"
                elif job.spark_sql_job:
                    current_job_type = "Spark SQL"
                elif job.presto_job:
                    current_job_type = "Presto"

                job_info = {
                    "job_id": job.reference.job_id,
                    "status": job.status.state.name,
                    "status_message": (
                        job.status.details
                        if job.status.details
                        else "No detailed message."
                    ),
                    "type": current_job_type,
                    "cluster_name": job.placement.cluster_name,
                }
                filtered_job_list.append(job_info)

        return {"status": "success", "jobs": filtered_job_list}

    except GoogleAPICallError as apierror:
        logger.error(
            "Google API Call Error while listing jobs by cluster '%s' in %s: %s",
            cluster_name,
            region,
            apierror.message,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"Failed to list Dataproc jobs by cluster: {apierror.message}"
            ),
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "An unexpected error occurred while listing jobs by cluster '%s' in %s: %s",
            cluster_name,
            region,
            e,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"An unexpected error occurred while listing jobs by cluster: {e!s}"
            ),
        }


def delete_dataproc_job(
    project_id: str,
    region: str,
    job_id: str,
) -> dict[str, Any]:
    """
    Deletes a Dataproc job.

    Args:
        project_id: The GCP project ID.
        region: The GCP region of the job.
        job_id: The ID of the job to delete.

    Returns:
        A dictionary with the status of the deletion request.
    """
    try:
        job_client = get_job_client(region)

        job_client.delete_job(
            project_id=project_id, region=region, job_id=job_id
        )

        return {
            "status": "success",
            "message": (
                f"Delete request for job ID '{job_id}' sent successfully. "
                "The job should terminate shortly."
            ),
        }

    except GoogleAPICallError as apierror:
        logger.error(
            "Google API Call Error while deleting job ID '%s': %s",
            job_id,
            apierror.message,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"Failed to delete Dataproc job '{job_id}': {apierror.message}"
            ),
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "An unexpected error occurred while deleting job ID '%s': %s",
            job_id,
            e,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"An unexpected error occurred while deleting job '{job_id}': {e!s}"
            ),
        }


def check_dataproc_job_exists(
    project_id: str,
    region: str,
    job_id: str,
) -> dict[str, Any]:
    """
    Checks if a Dataproc job exists.

    Args:
        project_id: The GCP project ID.
        region: The GCP region of the job.
        job_id: The ID of the job.

    Returns:
        A dictionary indicating whether the job exists and its status.
    """
    try:
        # Create a client for the JobController API
        job_client = get_job_client(region)

        # Attempt to get the job
        job = job_client.get_job(
            project_id=project_id, region=region, job_id=job_id
        )

        return {
            "status": "success",
            "exists": True,
            "job_id": job_id,
            "message": (
                f"Job '{job_id}' exists and is in '{job.status.state.name}' state."
            ),
        }

    except GoogleAPICallError as apierror:
        logger.error(
            "Google API Call Error while checking existence of job ID '%s': %s",
            job_id,
            apierror.message,
            exc_info=True,
        )
        return {
            "status": "success",
            "exists": False,
            "job_id": job_id,
            "message": f"Job '{job_id}' does not exist.",
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "An unexpected error occurred while checking existence of job ID '%s': %s",
            job_id,
            e,
            exc_info=True,
        )
        return {
            "status": "error",
            "exists": None,
        }
