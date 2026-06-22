"""Module for managing Dataproc workflow templates."""

import logging
from typing import Any

from google.api_core.exceptions import GoogleAPICallError
from google.cloud.dataproc_v1 import WorkflowTemplateServiceClient
from google.cloud.dataproc_v1.types import (
    ClusterConfig,
    ClusterSelector,
    DiskConfig,
    GceClusterConfig,
    InstanceGroupConfig,
    ManagedCluster,
    OrderedJob,
    PySparkJob,
    SoftwareConfig,
    SparkJob,
    WorkflowTemplate,
    WorkflowTemplatePlacement,
)

logger = logging.getLogger("plumber-agent")


def get_workflow_template_client(region: str) -> WorkflowTemplateServiceClient:
    """
    Creates a Dataproc WorkflowTemplateServiceClient for a specific region.

    Args:
        region: The GCP region for the client.

    Returns:
        A WorkflowTemplateServiceClient instance.
    """
    return WorkflowTemplateServiceClient(
        client_options={"api_endpoint": f"{region}-dataproc.googleapis.com:443"}
    )


def create_workflow_template(
    project_id: str,
    region: str,
    template_id: str,
    jobs: list[dict[str, Any]],
    cluster_config: dict[str, Any],
) -> dict[str, Any]:
    """
    Creates a Dataproc workflow template.

    Args:
        project_id: The GCP project ID.
        region: The GCP region for the workflow template.
        template_id: The ID for the workflow template.
        jobs: A list of jobs to include in the workflow.
        managed_cluster_config: Configuration for a managed cluster.
        cluster_selector_labels: Labels for selecting an existing cluster.

    Returns:
        A dictionary with the status of the workflow template creation.
    """
    if not jobs:
        error_msg = "The 'jobs' list cannot be empty."
        logger.error(
            "Workflow template creation failed for '%s': %s",
            template_id,
            error_msg,
        )
        return {"status": "error", "message": error_msg}

    managed_cluster_config = cluster_config.get("managed_cluster_config")
    cluster_selector_labels = cluster_config.get("cluster_selector_labels")

    if not (managed_cluster_config or cluster_selector_labels):
        error_msg = "You must specify either 'managed_cluster_config' or 'cluster_selector_labels'."
        logger.error(
            "Workflow template creation failed for '%s': %s",
            template_id,
            error_msg,
        )
        return {
            "status": "error",
            "message": error_msg,
        }

    if managed_cluster_config and cluster_selector_labels:
        error_msg = (
            "'managed_cluster_config' and 'cluster_selector_labels' are "
            "mutually exclusive. Please provide only one."
        )
        logger.error(
            "Workflow template creation failed for '%s': %s",
            template_id,
            error_msg,
        )
        return {
            "status": "error",
            "message": error_msg,
        }

    workflow_template_client = get_workflow_template_client(region)

    parent = f"projects/{project_id}/regions/{region}"
    template = WorkflowTemplate()
    template.id = template_id

    placement_config = WorkflowTemplatePlacement()
    if managed_cluster_config:
        placement_config.managed_cluster = ManagedCluster(
            cluster_name=managed_cluster_config.get("cluster_name_prefix"),
            config=ClusterConfig(
                gce_cluster_config=GceClusterConfig(
                    service_account=managed_cluster_config.get(
                        "service_account"
                    ),
                    subnetwork_uri=managed_cluster_config.get("subnet_uri"),
                    zone_uri=managed_cluster_config.get("zone"),
                ),
                master_config=InstanceGroupConfig(
                    num_instances=1,
                    machine_type_uri=managed_cluster_config.get(
                        "master_machine_type"
                    ),
                    disk_config=DiskConfig(
                        boot_disk_size_gb=managed_cluster_config.get(
                            "master_disk_size_gb"
                        )
                    ),
                ),
                worker_config=InstanceGroupConfig(
                    num_instances=managed_cluster_config.get("num_workers"),
                    machine_type_uri=managed_cluster_config.get(
                        "worker_machine_type"
                    ),
                    disk_config=(
                        DiskConfig(
                            boot_disk_size_gb=managed_cluster_config.get(
                                "worker_disk_size_gb"
                            )
                        )
                        if managed_cluster_config.get("worker_disk_size_gb")
                        else None
                    ),
                ),
                software_config=SoftwareConfig(
                    image_version=managed_cluster_config.get("image_version"),
                ),
            ),
        )
    elif cluster_selector_labels:
        placement_config.cluster_selector = ClusterSelector(
            cluster_labels=cluster_selector_labels
        )

    template.placement = placement_config

    template_jobs = []
    if jobs:
        for job_data in jobs:
            job_obj = OrderedJob(
                step_id=job_data.get("step_id", ""),
                prerequisite_step_ids=job_data.get("prerequisite_step_ids", []),
            )

            if "pyspark_job" in job_data:
                job_obj.pyspark_job = PySparkJob(
                    main_python_file_uri=job_data["pyspark_job"].get(
                        "main_python_file_uri"
                    ),
                    args=job_data["pyspark_job"].get("args", []),
                    python_file_uris=job_data["pyspark_job"].get(
                        "python_file_uris", []
                    ),
                    jar_file_uris=job_data["pyspark_job"].get(
                        "jar_file_uris", []
                    ),
                    properties=job_data["pyspark_job"].get("properties", {}),
                )
            elif "spark_job" in job_data:
                job_obj.spark_job = SparkJob(
                    main_class=job_data["spark_job"].get("main_class"),
                    main_jar_file_uri=job_data["spark_job"].get(
                        "main_jar_file_uri"
                    ),
                    args=job_data["spark_job"].get("args", []),
                    jar_file_uris=job_data["spark_job"].get(
                        "jar_file_uris", []
                    ),
                    properties=job_data["spark_job"].get("properties", {}),
                )

            template_jobs.append(job_obj)

        template.jobs = template_jobs
    try:
        workflow_template_client.create_workflow_template(
            parent=parent, template=template
        )
        return {
            "status": "success",
            "message": f"Workflow template '{template_id}' created successfully.",
            "template_id": template_id,
        }
    except GoogleAPICallError as apierror:
        logger.error(
            "Google API Call Error while creating workflow template '%s': %s",
            template_id,
            str(apierror),
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": f"Failed to create workflow template: {apierror!s}",
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "An unexpected error occurred while creating workflow template '%s': %s",
            template_id,
            str(e),
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": f"An unexpected error occurred: {e!s}",
        }


def list_workflow_templates(project_id: str, region: str) -> dict[str, Any]:
    """
    Lists all Dataproc workflow templates in a region.

    Args:
        project_id: The GCP project ID.
        region: The GCP region to list workflow templates from.

    Returns:
        A dictionary containing a list of workflow templates.
    """
    try:
        workflow_template_client = get_workflow_template_client(region)

        parent = f"projects/{project_id}/regions/{region}"
        templates = workflow_template_client.list_workflow_templates(
            parent=parent
        )

        template_list = []
        for template in templates:
            template_list.append(
                {
                    "name": template.name,
                    "id": template.id,
                    "create_time": template.create_time,
                }
            )

        return {"status": "success", "templates": template_list}

    except GoogleAPICallError as apierror:
        logger.error(
            "Google API Call Error while listing workflow templates in %s: %s",
            region,
            apierror.message,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": f"Failed to list workflow templates: {apierror.message}",
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "An unexpected error occurred while listing workflow templates in %s: %s",
            region,
            str(e),
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": f"An unexpected error occurred: {e!s}",
        }
