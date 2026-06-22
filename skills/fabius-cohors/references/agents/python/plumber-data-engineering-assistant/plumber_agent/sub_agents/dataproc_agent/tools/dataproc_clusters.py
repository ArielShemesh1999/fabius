"""Module for managing Dataproc clusters."""

import logging
from typing import Any

from google.api_core.exceptions import GoogleAPICallError, NotFound
from google.cloud import dataproc
from google.cloud.dataproc_v1 import ClusterControllerClient
from google.cloud.dataproc_v1.types import (
    Cluster,
    ClusterConfig,
    DiskConfig,
    GceClusterConfig,
    InstanceGroupConfig,
)

logger = logging.getLogger("plumber-agent")


def get_cluster_client(region: str) -> ClusterControllerClient:
    """
    Creates a Dataproc ClusterControllerClient for a specific region.

    Args:
        region: The GCP region for the client.

    Returns:
        A ClusterControllerClient instance.
    """
    return ClusterControllerClient(
        client_options={"api_endpoint": f"{region}-dataproc.googleapis.com:443"}
    )


def create_cluster(
    project_id: str,
    region: str,
    cluster_name: str,
    cluster_config: dict,
) -> dict[str, Any]:
    """
    Creates a Dataproc cluster.

    Args:
        project_id: The GCP project ID.
        region: The GCP region for the cluster.
        cluster_name: The name of the cluster.
        cluster_config: A dictionary containing the cluster configuration.

    Returns:
        A dictionary with the status of the cluster creation.
    """
    try:
        # Create a client with the endpoint set to the desired cluster region.
        cluster_client = get_cluster_client(region)

        # Define the configuration for the master node
        master_config = InstanceGroupConfig(
            num_instances=cluster_config.get("num_instances_master"),
            machine_type_uri=cluster_config.get("machine_type_master"),
            disk_config=DiskConfig(
                boot_disk_size_gb=cluster_config.get("boot_disk_size_master")
            ),
        )

        # Define the configuration for the worker nodes
        worker_config = InstanceGroupConfig(
            num_instances=cluster_config.get("num_instances_worker"),
            machine_type_uri=cluster_config.get("machine_type_worker"),
            disk_config=DiskConfig(
                boot_disk_size_gb=cluster_config.get("boot_disk_size_worker")
            ),
        )

        # Define the GCE (Compute Engine) configuration for the cluster
        gce_cluster_config = GceClusterConfig(
            service_account_scopes=[
                "https://www.googleapis.com/auth/cloud-platform"
            ],
        )

        # Define software configuration, including pip packages
        software_properties = {}
        if cluster_config.get("pip_packages_to_install"):
            software_properties["dataproc:pip.packages"] = ",".join(
                cluster_config.get("pip_packages_to_install")
            )

        software_config = dataproc.SoftwareConfig(
            image_version="2.1-debian11", properties=software_properties
        )

        # If a JAR GCS path is provided, add it to the initialization actions
        initialization_actions = []
        if cluster_config.get("initialization_action_script_path"):
            init_action = Cluster.InitializationAction(
                executable_file=cluster_config.get(
                    "initialization_action_script_path"
                )
            )
            initialization_actions.append(init_action)

            # Pass JAR GCS path as metadata to the initialization script
            if cluster_config.get("jar_files_gcs_path"):
                if not gce_cluster_config.metadata:
                    gce_cluster_config.metadata = {}
                gce_cluster_config.metadata["JAR_GCS_PATH"] = (
                    cluster_config.get("jar_files_gcs_path")
                )

        # Construct the full cluster configuration using the imported types
        cluster = Cluster(
            project_id=project_id,
            cluster_name=cluster_name,
            labels={"submitted_from": "plumber"},
            config=ClusterConfig(
                gce_cluster_config=gce_cluster_config,
                master_config=master_config,
                worker_config=worker_config,
                software_config=software_config,
                initialization_actions=(
                    initialization_actions if initialization_actions else None
                ),
            ),
        )

        # Create the cluster.
        cluster_client.create_cluster(
            request={
                "project_id": project_id,
                "region": region,
                "cluster": cluster,
            }
        )

        # Output a success message.
        return {
            "status": "success",
            "report": (
                f"Dataproc cluster '{cluster_name}' created successfully in "
                f"region '{region}' It might take a few more minutes for all "
                "services to be fully ready."
            ),
        }

    except GoogleAPICallError as apierror:
        logger.error(
            "Google API Call Error during cluster creation of '%s': %s",
            cluster_name,
            apierror.message,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": f"Failed to create Dataproc cluster: {apierror.message}",
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "An unexpected error occurred during cluster creation of '%s': %s",
            cluster_name,
            e,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"An unexpected error occurred during cluster creation: {e!s}"
            ),
        }


def cluster_exists_or_not(
    project_id: str, region: str, cluster_name: str
) -> dict[str, Any]:
    """
    Checks if a Dataproc cluster exists.

    Args:
        project_id: The GCP project ID.
        region: The GCP region of the cluster.
        cluster_name: The name of the cluster.

    Returns:
        A dictionary indicating whether the cluster exists.
    """
    try:
        # Create a client for the ClusterController API
        cluster_client = get_cluster_client(region)

        # Attempt to fetch the cluster details
        cluster_client.get_cluster(
            project_id=project_id, region=region, cluster_name=cluster_name
        )

        # If no exception is raised, the cluster exists
        return {
            "status": "success",
            "exists": True,
            "message": f"Cluster '{cluster_name}' exists in region '{region}'.",
        }

    except NotFound:
        return {
            "status": "success",
            "exists": False,
            "message": (
                f"Cluster '{cluster_name}' does not exist in region '{region}'."
            ),
        }

    except GoogleAPICallError as apierror:
        logger.error(
            "Google API Call Error while checking cluster existence for '%s': %s",
            cluster_name,
            apierror.message,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": f"Failed to check cluster existence: {apierror.message}",
        }

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "An unexpected error occurred while checking cluster existence for '%s': %s",
            cluster_name,
            e,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"An unexpected error occurred while checking cluster existence: {e!s}"
            ),
        }


def list_clusters(project_id: str, region: str) -> dict[str, Any]:
    """
    Lists all Dataproc clusters in a region.

    Args:
        project_id: The GCP project ID.
        region: The GCP region to list clusters from.

    Returns:
        A dictionary containing a list of clusters.
    """
    try:
        cluster_client = get_cluster_client(region)

        clusters = cluster_client.list_clusters(
            project_id=project_id, region=region
        )

        # Prepare the response
        cluster_list = []
        for cluster in clusters:
            cluster_list.append(
                {
                    "name": cluster.cluster_name,
                    "status": cluster.status.state.name,
                    "create_time": cluster.status.detail,
                }
            )

        return {"status": "success", "clusters": cluster_list}

    except GoogleAPICallError as apierror:
        logger.error(
            "Google API Call Error while listing clusters in %s: %s",
            region,
            apierror.message,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": f"Failed to list Dataproc clusters: {apierror.message}",
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "An unexpected error occurred while listing clusters in %s: %s",
            region,
            e,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"An unexpected error occurred while listing clusters: {e!s}"
            ),
        }


def start_stop_cluster(
    project_id: str, region: str, cluster_name: str, action: str
) -> dict[str, Any]:
    """
    Starts or stops a Dataproc cluster.

    Args:
        project_id: The GCP project ID.
        region: The GCP region of the cluster.
        cluster_name: The name of the cluster.
        action: The action to perform ('start' or 'stop').

    Returns:
        A dictionary with the status of the action.
    """
    try:
        # Create a client for the ClusterController API
        cluster_client = get_cluster_client(region)

        if action.lower() == "start":
            # Start the cluster
            operation = cluster_client.start_cluster(
                request={
                    "project_id": project_id,
                    "region": region,
                    "cluster_name": cluster_name,
                }
            )
            operation.result()
            return {
                "status": "success",
                "report": (
                    f"Cluster '{cluster_name}' started successfully in region '{region}'."
                ),
            }

        if action.lower() == "stop":
            # Stop the cluster
            operation = cluster_client.stop_cluster(
                request={
                    "project_id": project_id,
                    "region": region,
                    "cluster_name": cluster_name,
                }
            )
            operation.result()
            return {
                "status": "success",
                "report": (
                    f"Cluster '{cluster_name}' stopped successfully in region '{region}'."
                ),
            }

        raise Exception("Invalid action. Use 'start' or 'stop'.")  # pylint: disable=broad-exception-raised

    except GoogleAPICallError as apierror:
        logger.error(
            "Google API Call Error while trying to '%s' cluster '%s': %s",
            action,
            cluster_name,
            apierror.message,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": f"Failed to {action} cluster: {apierror.message}",
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "An unexpected error occurred while trying to '%s' cluster '%s': %s",
            action,
            cluster_name,
            e,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"An unexpected error occurred while trying to {action} the cluster: {e!s}"
            ),
        }


def update_cluster(
    project_id: str,
    region: str,
    cluster_name: str,
    # num_workers: int | None = None
    num_workers: int | None = None,
) -> dict[str, Any]:
    """
    Updates a Dataproc cluster.

    Args:
        project_id: The GCP project ID.
        region: The GCP region of the cluster.
        cluster_name: The name of the cluster.
        num_workers: The new number of worker instances.

    Returns:
        A dictionary with the status of the update and cluster details.
    """
    try:
        if num_workers is None:
            return {
                "status": "Success",
                "report": (
                    f"No changes made to cluster '{cluster_name}' in region "
                    f"'{region}', as no worker configuration was provided."
                ),
            }
        # Create a client for the ClusterController API
        cluster_client = get_cluster_client(region)

        # Fetch the current cluster configuration
        cluster = cluster_client.get_cluster(
            project_id=project_id, region=region, cluster_name=cluster_name
        )

        current_num_workers = cluster.config.worker_config.num_instances
        if num_workers == current_num_workers:
            return {
                "status": "Success",
                "report": (
                    f"No changes made to cluster '{cluster_name}' in region "
                    f"'{region}', as the number of workers is already set to "
                    f"{num_workers}."
                ),
            }

        # Update worker configurations if specified
        update_mask_paths = []
        if num_workers is not None:
            cluster.config.worker_config.num_instances = num_workers
            update_mask_paths.append("config.worker_config.num_instances")

        # Submit the update request
        operation = cluster_client.update_cluster(
            request={
                "project_id": project_id,
                "region": region,
                "cluster_name": cluster_name,
                "cluster": cluster,
                "update_mask": {"paths": update_mask_paths},
            }
        )

        # Wait for the operation to complete
        updated_cluster = operation.result()

        # Extract relevant details from the updated cluster
        cluster_details = {
            "cluster_name": updated_cluster.cluster_name,
            "status": updated_cluster.status.state.name,
            "config": {
                "worker_config": {
                    "num_instances": (
                        updated_cluster.config.worker_config.num_instances
                    ),
                    "machine_type_uri": (
                        updated_cluster.config.worker_config.machine_type_uri
                    ),
                    "disk_config": {
                        "boot_disk_size_gb": (
                            updated_cluster.config.worker_config.disk_config.boot_disk_size_gb
                        )
                    },
                }
            },
        }

        return {
            "status": "success",
            "report": (
                f"Cluster '{cluster_name}' updated successfully in region '{region}'."
            ),
            "details": cluster_details,
        }

    except GoogleAPICallError as apierror:
        logger.error(
            "Google API Call Error while updating cluster '%s': %s",
            cluster_name,
            apierror.message,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": f"Failed to update cluster: {apierror.message}",
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "An unexpected error occurred during cluster update for '%s': %s",
            cluster_name,
            e,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"An unexpected error occurred during cluster update: {e!s}"
            ),
        }


def get_cluster_details(
    project_id: str, region: str, cluster_name: str
) -> dict[str, Any]:
    """
    Gets the details of a Dataproc cluster.

    Args:
        project_id: The GCP project ID.
        region: The GCP region of the cluster.
        cluster_name: The name of the cluster.

    Returns:
        A dictionary with the cluster details.
    """
    try:
        # Create a client for the ClusterController API
        cluster_client = get_cluster_client(region)

        # Fetch the cluster details
        cluster = cluster_client.get_cluster(
            project_id=project_id, region=region, cluster_name=cluster_name
        )

        # Extract relevant details
        cluster_details = {
            "cluster_name": cluster.cluster_name,
            "status": cluster.status.state.name,
            "status_detail": cluster.status.detail,
            "create_time": cluster.cluster_uuid,
            "labels": dict(cluster.labels),
            "config": {
                "master_config": {
                    "machine_type_uri": (
                        cluster.config.master_config.machine_type_uri
                    ),
                    "disk_config": {
                        "boot_disk_size_gb": (
                            cluster.config.master_config.disk_config.boot_disk_size_gb
                        )
                    },
                },
                "worker_config": {
                    "num_instances": (
                        cluster.config.worker_config.num_instances
                    ),
                    "machine_type_uri": (
                        cluster.config.worker_config.machine_type_uri
                    ),
                    "disk_config": {
                        "boot_disk_size_gb": (
                            cluster.config.worker_config.disk_config.boot_disk_size_gb
                        )
                    },
                },
            },
        }

        return {"status": "success", "details": cluster_details}

    except GoogleAPICallError as apierror:
        logger.error(
            "Google API Call Error while fetching details for cluster '%s': %s",
            cluster_name,
            apierror.message,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": f"Failed to fetch cluster details: {apierror.message}",
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "An unexpected error occurred while fetching details for cluster '%s': %s",
            cluster_name,
            e,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"An unexpected error occurred while fetching cluster details: {e!s}"
            ),
        }


def delete_cluster(
    project_id: str, region: str, cluster_name: str
) -> dict[str, Any]:
    """
    Deletes a Dataproc cluster.

    Args:
        project_id: The GCP project ID.
        region: The GCP region of the cluster.
        cluster_name: The name of the cluster to delete.

    Returns:
        A dictionary with the status of the deletion.
    """
    try:
        # Create a client for the ClusterController API
        cluster_client = get_cluster_client(region)

        # Delete the cluster
        operation = cluster_client.delete_cluster(
            request={
                "project_id": project_id,
                "region": region,
                "cluster_name": cluster_name,
            }
        )
        operation.result()

        return {
            "status": "success",
            "report": (
                f"Cluster '{cluster_name}' deleted successfully in region '{region}'."
            ),
        }

    except GoogleAPICallError as apierror:
        logger.error(
            "Google API Call Error while deleting cluster '%s': %s",
            cluster_name,
            apierror.message,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": f"Failed to delete cluster: {apierror.message}",
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "An unexpected error occurred while deleting cluster '%s': %s",
            cluster_name,
            e,
            exc_info=True,
        )
        return {
            "status": "error",
            "error_message": (
                f"An unexpected error occurred while deleting the cluster: {e!s}"
            ),
        }
