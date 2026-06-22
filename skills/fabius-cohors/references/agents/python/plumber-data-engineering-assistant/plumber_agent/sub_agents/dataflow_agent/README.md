# Dataflow Agent

AI-powered agent for managing and orchestrating Google Cloud Dataflow jobs using Google's Agent Development Kit (ADK).

## Tools Overview

| Tool | Purpose |
|------|---------|
| [`list_dataflow_jobs`](tools/dataflow_management_utils.py) | List all Dataflow jobs in a project. |
| [`get_dataflow_job_details`](tools/dataflow_management_utils.py) | Get detailed information about a specific Dataflow job. |
| [`cancel_dataflow_job`](tools/dataflow_management_utils.py) | Cancel a running Dataflow job. |
| [`create_pipeline_from_scratch`](tools/pipeline_utils.py) | Create a new Dataflow pipeline from scratch. |
| [`get_dataflow_template`](tools/dataflow_template_tools.py) | Retrieve a pre-defined Dataflow template. |
| [`submit_dataflow_template`](tools/dataflow_template_tools.py) | Submit a job using a Dataflow template. |

## Key Features

- 🚀 Manage and orchestrate Dataflow jobs
- 📄 Work with Dataflow templates
- ✨ Create a new Dataflow pipeline from scratch with transformations
- 🤖 AI-powered with Google ADK

## Security

- Keep `.env` file private
- Use minimal permissions for service accounts

## Support

- [Google ADK Docs](https://developers.google.com/adk)
- [Google Cloud Dataflow Docs](https://cloud.google.com/dataflow/docs)
