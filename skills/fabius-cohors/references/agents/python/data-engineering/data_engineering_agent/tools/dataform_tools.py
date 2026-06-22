# Copyright 2025 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This module provides a set of tools for interacting with Google Cloud Dataform.

It includes functionality for generating Dataform SQLX code, identifying files
within LLM-generated output, uploading and compiling those files in Dataform,
and attempting to automatically fix compilation errors using an LLM.
"""

from typing import Any

from google.api_core.exceptions import GoogleAPIError
from google.cloud import dataform_v1

from ..config import config

DATAFORM_CLIENT = dataform_v1.DataformClient()


def get_workspace_path() -> str:
    """Get the workspace path using configuration."""
    return DATAFORM_CLIENT.workspace_path(
        config.project_id,
        config.location,
        config.repository_name,
        config.workspace_name,
    )


def write_file_to_dataform(file_content: str, file_path: str) -> str:
    """Upload a file to Dataform.

    Args:
        file_content (str): The content of the file to upload.
        file_path (str): The fully qualified path of the file to upload.

    Returns:
        str: Result of the upload operation.
    """
    workspace_path = get_workspace_path()
    print(f"Uploading file: {file_path}")
    try:
        request = dataform_v1.WriteFileRequest(
            workspace=workspace_path,
            path=file_path,
            contents=file_content.encode("utf-8"),
        )
        DATAFORM_CLIENT.write_file(request=request)
        print(f"File Uploaded: {file_path}")
        return f"File Uploaded: {file_path}"
    except GoogleAPIError as e:
        error_msg = f"Error uploading file '{file_path}': {e}"
        print(error_msg)
        return error_msg


def delete_file_from_dataform(file_path: str) -> str:
    """Delete a file from Dataform.

    Args:
        file_path (str): The fully qualified path of the file to delete.

    Returns:
        str: Result of the deletion operation.
    """
    workspace_path = get_workspace_path()
    request = dataform_v1.RemoveFileRequest(
        workspace=workspace_path,
        path=file_path,
    )
    try:
        DATAFORM_CLIENT.remove_file(request=request)
        print(f"File Deleted: {file_path}")
        return f"File Deleted: {file_path}"
    except GoogleAPIError as e:
        error_msg = f"Error deleting file '{file_path}': {e}"
        print(error_msg)
        return error_msg


def compile_dataform(compile_only: bool = False) -> dict[str, Any]:
    """Compile Dataform pipeline and get overview of the pipeline DAG.

    Args:
        compile_only (bool): If True, only compile without execution.

    Returns:
        Dict[str, Any]: Compilation results including status and pipeline DAG.
    """
    try:
        repository_path = DATAFORM_CLIENT.repository_path(
            config.project_id, config.location, config.repository_name
        )
        workspace_path = get_workspace_path()

        print("Compiling...")
        compilation_result = dataform_v1.CompilationResult()
        compilation_result.git_commitish = "main"
        compilation_result.workspace = workspace_path

        request = dataform_v1.CreateCompilationResultRequest(
            parent=repository_path, compilation_result=compilation_result
        )

        compilation_results = DATAFORM_CLIENT.create_compilation_result(
            request=request
        )

        if compilation_results.compilation_errors:
            print("Compilation errors found!")
            return {
                "status": "error",
                "error_message": str(compilation_results.compilation_errors),
            }

        request = dataform_v1.QueryCompilationResultActionsRequest(
            name=compilation_results.name,
        )

        actions = DATAFORM_CLIENT.query_compilation_result_actions(
            request=request
        ).compilation_result_actions

        if compile_only:
            return {
                "status": "success",
                "message": "Compilation successful (compile-only mode)",
                "pipeline_dag": str(actions),
            }

        # Execute the workflow if not in compile-only mode
        workflow_invocation = dataform_v1.WorkflowInvocation()
        workflow_invocation.compilation_result = compilation_results.name

        request = dataform_v1.CreateWorkflowInvocationRequest(
            parent=repository_path, workflow_invocation=workflow_invocation
        )

        workflow_invocation = DATAFORM_CLIENT.create_workflow_invocation(
            request=request
        )

        return {
            "status": "success",
            "message": "Compilation and execution successful",
            "pipeline_dag": str(actions),
            "workflow_invocation_id": workflow_invocation.name,
        }

    except GoogleAPIError as e:
        error_msg = f"Error in Dataform operation: {e}"
        print(error_msg)
        return {"status": "error", "error_message": error_msg}


def read_file_from_dataform(file_path: str) -> str:
    """Read a file from Dataform.

    Args:
        file_path (str): The fully qualified path of the file to read.

    Returns:
        str: The content of the file.
    """
    workspace_path = get_workspace_path()
    print(f"Reading file: {file_path}")
    try:
        request = dataform_v1.ReadFileRequest(
            workspace=workspace_path,
            path=file_path,
        )
        response = DATAFORM_CLIENT.read_file(request=request)
        print(f"File Read: {file_path}")
        return response.file_contents.decode("utf-8")
    except GoogleAPIError as e:
        error_msg = f"Error reading file '{file_path}': {e}"
        print(error_msg)
        return error_msg


def search_files_in_dataform(pattern: str | None = None) -> list[str]:
    """Search for files in Dataform.

    Args:
        pattern (Optional[str]): Optional pattern to filter files.

    Returns:
        List[str]: A list of file names matching the pattern.
    """
    workspace_path = get_workspace_path()
    try:
        request = dataform_v1.SearchFilesRequest(
            workspace=workspace_path,
        )
        response = DATAFORM_CLIENT.search_files(request=request)
        all_files = [page.file.path for page in response if page.file]

        if pattern:
            all_files = [f for f in all_files if pattern in f]

        print(f"Files found: {all_files}")
        return all_files
    except GoogleAPIError as e:
        print(f"Error searching files: {e}")
        return []


def get_dataform_execution_logs(workflow_invocation_id: str) -> dict[str, Any]:
    """Use this function to get execution logs for a Dataform workflow invocation.

    Args:
        workflow_invocation_id (str): The full ID of the workflow invocation.
          (e.g.,
          projects/PROJECT_ID/locations/LOCATION/repositories/REPOSITORY_NAME/workflowInvocations/WORKFLOW_INVOCATION_ID)

    Returns:
        Dict[str, Any]: A dictionary containing the status and actions of the
        workflow invocation.
                        "status": "success" or "error"
                        "actions": A list of actions with their details (name,
                        status, logs/errors).
                        "error_message": Present if the overall status is "error".
    """
    try:
        request = dataform_v1.QueryWorkflowInvocationActionsRequest(
            name=workflow_invocation_id,
        )
        actions_response = DATAFORM_CLIENT.query_workflow_invocation_actions(
            request=request
        )

        actions_details = []
        for action in actions_response.workflow_invocation_actions:
            action_detail = {
                "name": action.target.name,
                "status": (
                    dataform_v1.WorkflowInvocationAction.State(
                        action.state
                    ).name
                ),
            }
            if (
                action.state
                == dataform_v1.WorkflowInvocationAction.State.FAILED
            ):
                action_detail["error_message"] = action.failure_reason
            if (
                action.canonical_target.name
            ):  # Check if canonical_target has name
                action_detail["canonical_target_name"] = (
                    action.canonical_target.name
                )
            if action.bigquery_action:  # Check if bigquery_action exists
                action_detail["job_id"] = action.bigquery_action.job_id

            # Potentially, logs could be found in different fields depending on the action type
            # For now, focusing on BigQuery action job ID, which can be used to fetch logs from BigQuery directly.
            # Also, failure_reason provides some error information.
            actions_details.append(action_detail)

        # Determine overall status
        # The WorkflowInvocation itself has a state. We might need to fetch the WorkflowInvocation object
        # using get_workflow_invocation to get the overall status.
        # For now, let's assume if any action failed, the invocation is considered failed for logging purposes.
        overall_status = "success"
        for ad in actions_details:
            if ad["status"] == "FAILED":
                overall_status = "error"
                break

        if overall_status == "error":
            return {
                "status": "error",
                "error_message": (
                    "One or more actions failed in workflow invocation"
                    f" {workflow_invocation_id}. See actions for details."
                ),
                "actions": actions_details,
            }

        return {"status": "success", "actions": actions_details}

    except GoogleAPIError as e:
        print(
            f"Error getting execution logs for '{workflow_invocation_id}': {e}"
        )
        return {
            "status": "error",
            "error_message": (
                f"Error getting execution logs for '{workflow_invocation_id}': {e}"
            ),
        }


def execute_dataform_workflow(
    workflow_name: str, params: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Execute a Dataform workflow with optional parameters.

    Args:
        workflow_name (str): The name of the workflow to execute.
        params (Optional[Dict[str, Any]]): Optional parameters for the workflow
          execution.

    Returns:
        Dict[str, Any]: Execution results including status and workflow invocation
        ID.
    """
    try:
        repository_path = DATAFORM_CLIENT.repository_path(
            config.project_id, config.location, config.repository_name
        )

        # Create workflow invocation
        workflow_invocation = dataform_v1.WorkflowInvocation()
        workflow_invocation.workflow_config = workflow_name

        # Add parameters if provided
        if params:
            workflow_invocation.invocation_config = (
                dataform_v1.InvocationConfig(parameters=params)
            )

        request = dataform_v1.CreateWorkflowInvocationRequest(
            parent=repository_path, workflow_invocation=workflow_invocation
        )

        # Execute the workflow
        workflow_invocation = DATAFORM_CLIENT.create_workflow_invocation(
            request=request
        )

        return {
            "status": "success",
            "message": "Workflow execution started",
            "workflow_invocation_id": workflow_invocation.name,
            "workflow_name": workflow_name,
            "parameters": params,
        }

    except GoogleAPIError as e:
        error_msg = f"Error executing workflow '{workflow_name}': {e}"
        print(error_msg)
        return {"status": "error", "error_message": error_msg}


def get_dataform_repo_link() -> dict[str, str]:
    """Generate the GCP console link for the Dataform repository.

    Returns:
        Dict[str, str]: Dictionary containing the repository link and additional
        information.
    """
    try:
        # Construct the GCP console URL for the Dataform repository
        base_url = "https://console.cloud.google.com"
        repo_path = f"/bigquery/dataform/locations/{config.location}/repositories/{config.repository_name}/workspaces/{config.workspace_name}"

        repo_url = f"{base_url}{repo_path}"

        return {
            "status": "success",
            "repository_url": repo_url,
            "repository_name": config.repository_name,
            "project_id": config.project_id,
            "location": config.location,
            "workspace_name": config.workspace_name,
        }
    except Exception as e:
        error_msg = f"Error generating repository link: {e}"
        print(error_msg)
        return {"status": "error", "error_message": error_msg}
