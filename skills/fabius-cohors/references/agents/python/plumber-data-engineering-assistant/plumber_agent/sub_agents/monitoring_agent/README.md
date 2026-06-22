# Monitoring Agent

AI-powered agent for monitoring Google Cloud resources and retrieving logs using Google's Agent Development Kit (ADK).

## Tools Overview

| Tool | Purpose |
|------|---------|
| [`get_cpu_utilization`](tools/utils.py) | Get the CPU utilization for a resource. |
| [`get_latest_10_logs`](tools/utils.py) | Retrieve the 10 most recent logs. |
| [`get_latest_error`](tools/utils.py) | Get the most recent error log. |
| [`get_logs`](tools/utils.py) | Retrieve logs based on a query. |
| [`get_latest_resource_based_logs`](tools/utils.py) | Get the latest logs for a specific resource. |
| [`get_dataflow_job_logs_with_id`](tools/dataflow.py) | Get logs for a specific Dataflow job by ID. |
| [`get_dataproc_logs_with_id`](tools/dataproc.py) | Get logs for a specific Dataproc job by ID. |
| [`get_dataproc_logs_with_name`](tools/dataproc.py) | Get logs for a specific Dataproc job by name. |

## Key Features

- 📈 Monitor Google Cloud resources
- 📄 Retrieve logs
- 🤖 AI-powered with Google ADK

## Security

- Keep `.env` file private
- Use minimal permissions for service accounts

## Support

- [Google ADK Docs](https://developers.google.com/adk)
- [Google Cloud Monitoring Docs](https://cloud.google.com/monitoring/docs)
