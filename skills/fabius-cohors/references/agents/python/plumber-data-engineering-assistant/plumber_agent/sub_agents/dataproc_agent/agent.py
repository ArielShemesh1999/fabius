"""
Defines the main Dataproc Agent instance, configuring its model, instructions,
and all available Dataproc-specific tools.
"""

from google.adk.agents import Agent

from .constants import MODEL
from .prompts import AGENT_INSTRUCTIONS
from .tools.dataproc_batches import (
    check_dataproc_serverless_status,
    create_dataproc_serverless_batch,
    delete_dataproc_serverless_batch,
    list_dataproc_serverless_batches,
    list_dataproc_serverless_batches_by_state,
)
from .tools.dataproc_clusters import (
    cluster_exists_or_not,
    create_cluster,
    delete_cluster,
    get_cluster_details,
    list_clusters,
    start_stop_cluster,
    update_cluster,
)
from .tools.dataproc_jobs import (
    check_dataproc_job_exists,
    check_job_status,
    delete_dataproc_job,
    list_dataproc_jobs,
    list_dataproc_jobs_by_cluster,
    list_dataproc_jobs_by_type,
    submit_pyspark_job,
    submit_scala_job,
)
from .tools.dataproc_workflow import (
    create_workflow_template,
    list_workflow_templates,
)

root_agent = Agent(
    name="dataproc_agent",
    model=MODEL,
    description=(
        "An agent that is a Google Cloud automation engineer, specializing in Dataproc."
    ),
    instruction=(AGENT_INSTRUCTIONS),
    tools=[
        create_cluster,
        list_clusters,
        update_cluster,
        start_stop_cluster,
        get_cluster_details,
        delete_cluster,
        cluster_exists_or_not,
        submit_pyspark_job,
        submit_scala_job,
        check_job_status,
        list_dataproc_jobs,
        list_dataproc_jobs_by_type,
        list_dataproc_jobs_by_cluster,
        delete_dataproc_job,
        check_dataproc_job_exists,
        create_workflow_template,
        list_workflow_templates,
        create_dataproc_serverless_batch,
        check_dataproc_serverless_status,
        list_dataproc_serverless_batches,
        list_dataproc_serverless_batches_by_state,
        delete_dataproc_serverless_batch,
    ],
)
