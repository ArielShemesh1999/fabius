"""
This module provides utility functions for interacting with Google Cloud Monitoring and Logging.
"""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from google.api_core import exceptions as google_exceptions
from google.cloud import logging_v2, monitoring_v3

SEVERITIES_LIST = ["INFO", "DEFAULT", "WARNING", "NOTICE", "DEBUG", "ERROR"]


logger = logging.getLogger("plumber-agent")


def get_cpu_utilization(project_id: str) -> dict[str, Any]:
    """
    Connects to Google Cloud Monitoring and retrieves CPU utilization
    for all VM instances in the specified project over the last 5 minutes.

    This function queries Google Cloud Monitoring to obtain CPU utilization metrics
    for all virtual machine (VM) instances within the configured Google Cloud project.
    It fetches data for the last 5 minutes, aggregates it by instance ID and zone,
    and calculates the mean CPU utilization for each instance over 1-minute intervals.

    Args:
        project_id (str, required): The Google Cloud project ID. from which logs are to be fetched.

    Returns:
        dict[str, Any]: A dictionary containing the status of the operation and a report of
            CPU utilization data or an error message if the operation fails.
            The dictionary will have the following keys:
            - "status" (str): "success" if the data was fetched, or "error" on failure.
            - "report" (str): A detailed string containing the CPU utilization
                data for each instance (Instance ID, Zone, Timestamp, and Value)
                or a message indicating no data was found.
            - "message" (str, optional): Only present if "status" is "error",
                providing details about the specific error encountered.

    Note: [IMPORTANT]
        - Call only when user ask's about CPU utilization
    """
    try:
        util_client = monitoring_v3.MetricServiceClient()

        # The TimeInterval constructor accepts datetime objects directly
        interval = monitoring_v3.TimeInterval(
            end_time=datetime.now(UTC),
            start_time=datetime.now(UTC) - timedelta(minutes=5),
        )
        metric_filter = (
            'metric.type = "compute.googleapis.com/instance/cpu/utilization"'
        )

        # The Aggregation constructor accepts timedelta objects directly
        aggregation = monitoring_v3.Aggregation(
            alignment_period=timedelta(seconds=60),  # Use timedelta
            per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_MEAN,
            cross_series_reducer=monitoring_v3.Aggregation.Reducer.REDUCE_MEAN,
            group_by_fields=[
                "resource.label.instance_id",
                "resource.label.zone",
            ],
        )

        response = util_client.list_time_series(
            request={
                "name": f"projects/{project_id}",
                "filter": metric_filter,
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
                "aggregation": aggregation,
            }
        )

        cpu_data_report: list[str] = []
        for series in response.time_series:
            instance_id = series.resource.labels.get("instance_id", "N/A")
            zone = series.resource.labels.get("zone", "N/A")

            cpu_data_report.append(
                f"  Instance ID: {instance_id}, Zone: {zone}"
            )

            for point in series.points:
                value = point.value.double_value
                # Convert the returned protobuf Timestamp to a Python datetime
                # for cleaner, more consistent formatting in the report.
                timestamp_dt = point.interval.end_time
                cpu_data_report.append(
                    f"    Timestamp: {timestamp_dt}, Value: {value:.2f}%"
                )

        if not cpu_data_report:
            message = "No CPU utilization data found for the specified project and time range."
            return {"status": "success", "report": message}

        logger.info("Successfully fetched CPU utilization data.")
        return {
            "status": "success",
            "report": "CPU Utilization Data:\n" + "\n".join(cpu_data_report),
        }

    except google_exceptions.GoogleAPIError as e:
        logger.error("A Google Cloud API error occurred: %s", e, exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to get CPU utilization due to API error: {e}",
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("An unexpected error occurred: %s", e, exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to get CPU utilization due to unexpected error: {e}",
        }


def _process_log_iterator(iterator, _limit: int) -> list[str]:
    """
    Helper function to process a log iterator and collect log entries.
    """
    collected_logs = []
    log_count = 0
    for entry in iterator:
        log_count += 1
        logger.info("Entry - %s \n %s", log_count, entry)
        collected_logs.append(f"Entry {log_count}: {entry!s}")
        if log_count >= _limit:
            break
    return collected_logs


def get_latest_resource_based_logs(
    project_id: str, severity: str = "", resource: str = "", _limit: int = 10
) -> dict[str, str]:
    """
    Fetches log entries from Google Cloud Logging filtered by severity and resource type.

    This function retrieves the most recent log entries from Google Cloud Logging,
    allowing filters based on the log's severity level and the type of Google Cloud
    resource that generated the log. It is useful for quickly pinpointing logs
    of interest for specific services or error levels.

    Args:
        project_id (str, required): The Google Cloud project ID from which logs are to be fetched.
        severity (str, optional): Filters logs by their severity level (e.g., "ERROR",
                                "WARNING", "INFO", "DEBUG"). This string should directly
                                correspond to a valid Google Cloud Logging severity.
                                If an invalid or empty string is provided, the filter
                                defaults to `severity != ""`, which effectively includes
                                all severity levels. The supported severities are:
                                - 'severity = INFO'
                                - 'severity = DEFAULT'
                                - 'severity = WARNING'
                                - 'severity = NOTICE'
                                - 'severity = DEBUG'
                                - 'severity = ERROR'
                                - Defaults to '' (fetches all logs).
        resource (str, required): Filters logs by the resource type (e.g., "cloud_run_revision",
                                "cloud_dataproc_cluster", "gce_instance"). This string should
                                directly correspond to a valid Google Cloud resource type.
                                The supported resource types include:
                                - 'resource.type=cloud_dataproc_cluster'
                                - 'resource.type=dataflow_step'
                                - 'resource.type=gce_instance'
                                - 'resource.type=audited_resource'
                                - 'resource.type=project'
                                - 'resource.type=gce_firewall_rule'
                                - 'resource.type=gce_instance_group_manager'
                                - 'resource.type=gce_instance_template'
                                - 'resource.type=gce_instance_group'
                                - 'resource.type=gcs_bucket'
                                - 'resource.type=api'
                                - 'resource.type=pubsub_topic'
                                - 'resource.type=datapipelines.googleapis.com/Pipeline'
                                - 'resource.type=gce_subnetwork'
                                - 'resource.type=networking.googleapis.com/Location'
                                - 'resource.type=client_auth_config_brand'
                                - 'resource.type=service_account'
                                Defaults to an empty string.
        _limit (int, optional): The maximum number of log entries to retrieve. The function
                                will fetch up to this many entries, ordered by timestamp in
                                descending order (most recent first). Defaults to 10.

    Returns:
        dict[str, str]: A dictionary containing the status of the operation and the retrieved logs.
            The dictionary will have the following structure:
            - "status" (str): "success" if logs were fetched successfully, or "error"
            if an error occurred during the API call.
            - "report" (str): A human-readable message. If successful, it includes
            a summary and a list of the fetched log entries. If no logs are found
            matching the criteria, it indicates that.
            - "message" (str, optional): Only present if "status" is "error", providing
            details about the specific error.

    Note: [IMPORTANT]
        - make sure you have required fields before calling this tool.

    """

    client = logging_v2.Client(project=project_id)
    call_args = {
        "resource_names": [f"projects/{project_id}"],
        "order_by": "timestamp desc",
        "page_size": 5,
        "max_results": _limit,
        "filter_": (
            f'timestamp >= "{(datetime.now() - timedelta(days=90)).isoformat()}Z"'
        ),
    }

    full_filter = f"{resource}"

    for severity_exist in SEVERITIES_LIST:
        if severity is not None and severity.upper().find(severity_exist) != -1:
            full_filter += f" AND {severity}"
            break

    call_args["filter_"] = full_filter

    try:
        iterator = client.list_entries(**call_args)
        collected_logs = _process_log_iterator(iterator, _limit)
        log_count = len(collected_logs)

        if log_count == 0:
            logger.info("No log entries found matching the criteria.")
            return {
                "status": "success",
                "report": "No log entries found matching the criteria.",
            }

        logger.info("\nSuccessfully fetched %s log entries.", log_count)
        return {
            "status": "success",
            "report": "Fetched recent log entries:\n"
            + "\n".join(collected_logs),
        }

    except google_exceptions.GoogleAPIError as e:
        logger.error("A Google Cloud API error occurred: %s", e, exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to get latest resource based 10 logs due to API error: {e}",
        }
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("An unexpected error occurred: %s", e, exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to get latest resource based 10 logs due to unexpected error: {e}",
        }
