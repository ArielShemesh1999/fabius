"""
Tools for interacting with and managing Google Cloud Dataflow templates.

This module includes functions for:
- Cloning and updating the Dataflow templates git repository.
- Finding and validating Dataflow templates based on user input.
- Customizing, building, and staging Dataflow templates.
- Submitting Dataflow jobs from templates.
"""

import json
import logging
import os
import subprocess

import git
import vertexai
from vertexai.generative_models import GenerativeModel

# Import everything from your other files
from ..constants import (
    DATAFLOW_TEMPLATE_GIT_URL,
    GIT_PATH,
    MODEL,
    TEMPLATE_MAPPING_PATH,
)
from ..prompts import (
    SEARCH_DATAFLOW_TEMPLATE_INSTRUCTION,
)

logger = logging.getLogger("plumber-agent")


def get_dataflow_template_repo() -> dict[str, str]:
    """
    Clones or updates the local DataflowTemplates git repository.

    If the repository already exists locally, it pulls the latest changes.
    Otherwise, it clones the repository.

    Returns:
        A dictionary with 'status' and 'repo_path' on success, or 'status'
        on error.
    """
    try:
        repo_path = f"./{GIT_PATH}/DataflowTemplates"
        if os.path.exists(repo_path):
            repo = git.Repo(repo_path)
            repo.remotes.origin.pull("main")
        else:
            git.Repo.clone_from(
                DATAFLOW_TEMPLATE_GIT_URL, to_path=repo_path, branch="main"
            )
        return {"status": "success", "repo_path": repo_path}
    except git.exc.GitCommandError as err:
        logger.error("An error occurred: %s", err, exc_info=True)
        return {"status": f"error - {err!s}"}


def validate_input_params(
    template_definition: dict[str, list[str]], user_inputs: dict[str, str]
) -> dict[str, str]:
    """
    Validates user input parameters against a template definition.

    Args:
        template_definition: Dictionary with 'required' and 'optional' params.
        user_inputs: Dictionary of user-provided parameters.

    Returns:
        A dictionary with validation result and a comment.
    """
    try:
        required_params = template_definition.get("required", [])
        optional_params = template_definition.get("optional", [])
        all_defined_params = required_params + optional_params
        user_param_keys = user_inputs.keys()

        invalid_params = list(set(user_param_keys) - set(all_defined_params))
        if invalid_params:
            return {
                "validation_result": "failed",
                "comment": (
                    f"Invalid param(s) passed: {invalid_params}. "
                    f"Valid params are: {all_defined_params}"
                ),
            }

        missing_required = list(set(required_params) - set(user_param_keys))
        if missing_required:
            return {
                "validation_result": "failed",
                "comment": f"Missing required param(s): {missing_required}",
            }

        return {"validation_result": "success", "comment": "Validation Passed"}
    except (TypeError, AttributeError) as err:
        logger.error("An error occurred: %s", err, exc_info=True)
        return {
            "validation_result": "failed",
            "comment": f"An unexpected error occurred during validation - {err!s}",
        }


def get_dataflow_template(user_prompt: str) -> str:
    """
    Retrieves a Dataflow template based on a user prompt.

    Args:
        user_prompt: A natural language description for a Dataflow template.

    Returns:
        The generated Dataflow template as text, or a JSON string with an
        error message.
    """
    try:
        get_dataflow_template_repo()
        vertexai.init(
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION"),
        )
        model = GenerativeModel(MODEL)
        with open(f"./{TEMPLATE_MAPPING_PATH}", encoding="utf-8") as json_file:
            template_mapping_dict = json.load(json_file)
        instruction = SEARCH_DATAFLOW_TEMPLATE_INSTRUCTION.format(
            task=user_prompt,
            template_mapping_json=json.dumps(template_mapping_dict),
        )
        response = model.generate_content(instruction)
        return response.text
    except (OSError, json.JSONDecodeError, ValueError) as err:
        logger.error("An error occurred: %s", err, exc_info=True)
        return json.dumps({"error": f"An unexpected error occurred: {err!s}"})


def _prepare_gcloud_command(
    job_name: str,
    gcp_config: dict[str, str],
    template_gcs_path: str,
    parameters_str: str,
    is_flex: bool,
) -> list[str]:
    """Helper to construct the gcloud command for submitting a job."""
    base_cmd = ["gcloud", "dataflow"]
    default_labels = "source=plumber"

    if is_flex:
        return [
            *base_cmd,
            "flex-template",
            "run",
            job_name,
            f"--project={gcp_config['project_id']}",
            f"--region={gcp_config['region']}",
            f"--template-file-gcs-location={template_gcs_path}",
            f"--parameters={parameters_str}",
            f"--additional-user-labels={default_labels}",
        ]

    return [
        *base_cmd,
        "jobs",
        "run",
        job_name,
        f"--project={gcp_config['project_id']}",
        f"--region={gcp_config['region']}",
        f"--gcs-location={template_gcs_path}",
        f"--parameters={parameters_str}",
        f"--staging-location={gcp_config['staging_location']}",
        f"--additional-user-labels={default_labels}",
    ]


def submit_dataflow_template(
    job_name: str,
    input_params: str,
    template_params: str,
    gcp_config: dict[str, str],
) -> dict[str, str]:
    """
    Submits a Dataflow job using a given template.
    """
    try:
        user_input_dict = json.loads(input_params)
        template_def = json.loads(template_params)
        template_def = (
            template_def[0]
            if isinstance(template_def, list) and template_def
            else template_def
        )

        if not isinstance(template_def, dict):
            return {
                "status": "failed",
                "comment": "Invalid template definition.",
            }

        template_gcs_path = template_def.get("template_gcs_path")
        if not template_gcs_path:
            return {
                "status": "failed",
                "comment": "Template GCS path not found.",
            }

        validation = validate_input_params(
            template_def.get("params", {}), user_input_dict
        )
        if validation["validation_result"] != "success":
            return {
                "status": "failed",
                "comment": f"Validation error: {validation['comment']}",
            }

        delimiter = "~"
        params_list = [
            f"{key}={value}" for key, value in user_input_dict.items()
        ]
        parameters_str = f"^{delimiter}^{delimiter.join(params_list)}"

        is_flex = (
            "/flex/" in template_gcs_path or template_def.get("type") == "FLEX"
        )
        run_cmd = _prepare_gcloud_command(
            job_name, gcp_config, template_gcs_path, parameters_str, is_flex
        )

        result = subprocess.run(
            run_cmd, capture_output=True, text=True, check=True
        )
        return {
            "status": "success",
            "stdout": result.stdout,
            "comment": "Job Submitted",
        }
    except (
        json.JSONDecodeError,
        subprocess.CalledProcessError,
        KeyError,
    ) as err:
        logger.error("An error occurred: %s", err, exc_info=True)
        return {"status": "failed", "comment": f"An error occurred: {err!s}"}
