# Human-in-the-Loop (HITL) Workflow Agent

This sample demonstrates a workflow that incorporates human-in-the-loop, where the agent can pause and ask for user input before continuing.

## 1. Architecture

The architecture of this sample is a `WorkflowAgent` that acts as an interactive concierge to create an itinerary.

- **`initial_prompt`**: A Python function that starts the workflow by showing an introductory message and asking for user input.
- **`concierge_agent`**: An `LlmAgent` that takes the user's input and generates a list of activities.
- **`get_user_feedback`**: A Python function that shows the generated itinerary and asks the user for feedback.
- **`process_feedback`**: A Python function that takes the user's feedback and sends it back to the `concierge_agent`.

The workflow is defined with a loop, allowing the user to iteratively refine the itinerary:

```python
edges=[
    (
        "START", 
        initial_prompt, 
        concierge_agent, 
        get_user_feedback, 
        process_feedback
    ),
    (process_feedback, concierge_agent)
]
```

## 2. Feature: Human-in-the-Loop

This sample showcases the Human-in-the-Loop (HITL) capability of `WorkflowAgent`. The `RequestInput` event is used to pause the workflow and request input from the user.

- **`RequestInput`**: This event is yielded by a function node to send a message to the user and wait for a response.

This feature is essential for building interactive applications where user feedback or decisions are required to drive the workflow. The sample demonstrates a conversational loop where the agent and user can go back and forth to achieve a desired outcome.

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
adk deploy workflows-HITL/agent.py:root_agent --display-name "Interactive Concierge Agent"
```

After deployment, you can interact with the agent through the provided endpoint. The agent will prompt you for input and guide you through creating an itinerary.
