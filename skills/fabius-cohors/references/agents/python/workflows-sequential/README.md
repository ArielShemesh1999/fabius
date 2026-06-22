# Sequential Workflow Agent

This sample demonstrates a simple, sequential workflow where agents and functions are executed in a linear order.

## 1. Architecture

The architecture of this sample is a `WorkflowAgent` that defines a single, non-branching execution path.

- **`city_generator_agent`**: An `LlmAgent` that starts the workflow by generating a random city.
- **`lookup_time_function`**: A Python function that takes the city from the previous step, looks up the current time for that city, and yields the time information.
- **`city_report_agent`**: A final `LlmAgent` that takes the city and time, and formats a sentence to be returned to the user.

The sequence is defined in the `edges` of the `WorkflowAgent`:

```python
edges=[
    (START, city_generator_agent, lookup_time_function, city_report_agent)
]
```

This creates a chain where the output of one node is passed as the input to the next.

## 2. Feature: Sequential Execution

This sample showcases the basic sequential execution capabilities of a `WorkflowAgent`. It's the simplest form of a workflow, where you can define a specific, ordered series of tasks. This is useful when you have a process that needs to run in a controlled, step-by-step manner without any complex routing or conditional logic.

## 3. Deployment Guide

To deploy this workflow agent, you can use the `adk deploy` command.

### Prerequisites

Ensure you have authenticated with Google Cloud:
```sh
gcloud auth application-default login
```

Your GCP `project` and `location` should be set in a `.env` file in the root of this project.

### Deployment Command

```sh
adk deploy workflow-sequential/agent.py:root_agent --display-name "Sequential City Time Agent"
```

After deployment, you can interact with the agent through the provided endpoint.
