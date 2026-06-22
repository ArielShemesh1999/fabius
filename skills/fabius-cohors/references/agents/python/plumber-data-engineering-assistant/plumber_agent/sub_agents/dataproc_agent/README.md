# Dataproc Agent

AI-powered agent for managing and orchestrating Google Cloud Dataproc clusters and jobs using Google's Agent Development Kit (ADK).

## Tools Overview

| Tool | Purpose |
|------|---------|
| [`create_cluster`](tools/dataproc_clusters.py) | Create a new Dataproc cluster. |
| [`list_clusters`](tools/dataproc_clusters.py) | List all Dataproc clusters in a project. |
| [`update_cluster`](tools/dataproc_clusters.py) | Update the configuration of an existing Dataproc cluster. |
| [`start_stop_cluster`](tools/dataproc_clusters.py) | Start or stop a Dataproc cluster. |
| [`get_cluster_details`](tools/dataproc_clusters.py) | Get detailed information about a specific Dataproc cluster. |
| [`delete_cluster`](tools/dataproc_clusters.py) | Delete a Dataproc cluster. |
| [`cluster_exists_or_not`](tools/dataproc_clusters.py) | Check if a Dataproc cluster exists. |
| [`submit_pyspark_job`](tools/dataproc_jobs.py) | Submit a PySpark job to a Dataproc cluster. |
| [`submit_scala_job`](tools/dataproc_jobs.py) | Submit a Scala or Java job to a Dataproc cluster. |
| [`check_job_status`](tools/dataproc_jobs.py) | Check the status of a Dataproc job. |
| [`list_dataproc_jobs`](tools/dataproc_jobs.py) | List all Dataproc jobs in a project. |
| [`list_dataproc_jobs_by_type`](tools/dataproc_jobs.py) | List Dataproc jobs filtered by type (e.g., PySpark, Hadoop). |
| [`list_dataproc_jobs_by_cluster`](tools/dataproc_jobs.py) | List all jobs associated with a specific Dataproc cluster. |
| [`delete_dataproc_job`](tools/dataproc_jobs.py) | Delete a Dataproc job. |
| [`check_dataproc_job_exists`](tools/dataproc_jobs.py) | Check if a specific Dataproc job exists. |
| [`create_workflow_template`](tools/dataproc_workflow.py) | Create a new Dataproc workflow template. |
| [`list_workflow_templates`](tools/dataproc_workflow.py) | List all Dataproc workflow templates in a project. |
| [`create_dataproc_serverless_batch`](tools/dataproc_batches.py) | Create a new Dataproc Serverless batch workload. |
| [`check_dataproc_serverless_status`](tools/dataproc_batches.py) | Check the status of a Dataproc Serverless batch workload. |
| [`list_dataproc_serverless_batches`](tools/dataproc_batches.py) | List all Dataproc Serverless batch workloads. |
| [`list_dataproc_serverless_batches_by_state`](tools/dataproc_batches.py) | List Dataproc Serverless batch workloads filtered by state. |
| [`delete_dataproc_serverless_batch`](tools/dataproc_batches.py) | Delete a Dataproc Serverless batch workload. |

## Key Features

- 🖥️ Cluster Management
- 🚀 Job Submission and Management
- 📄 Workflow Templates
- 💨 Serverless Batches
- 🤖 AI-powered with Google ADK

## Security

- Keep `.env` file private
- Use minimal permissions for service accounts

## Support

- [Google ADK Docs](https://developers.google.com/adk)
- [Google Cloud Dataproc Docs](https://cloud.google.com/dataproc/docs)
