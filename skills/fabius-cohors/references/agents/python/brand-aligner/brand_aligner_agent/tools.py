# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import json
import os
from datetime import UTC, datetime
from typing import Any

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.sessions import Session
from google.adk.tools import ToolContext
from google.cloud import storage
from google.cloud.storage import Blob
from google.genai import types

from .auth import get_user_id
from .models import (
    Asset,
    AssetEvaluation,
    Category,
    Guideline,
    Severity,
)
from .services import EvalService, GuidelineService
from .utils import generate_radar_chart, logger

# --- Environment Variables ---
PROJECT_ID = os.getenv("PROJECT_ID", os.getenv("GOOGLE_CLOUD_PROJECT"))
LOCATION = os.getenv("LOCATION", os.getenv("GOOGLE_CLOUD_LOCATION"))
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")
GCS_BUCKET = os.getenv(
    "GCS_BUCKET_NAME",
    f"{os.getenv('GOOGLE_CLOUD_PROJECT')}-brandaligner-agent-assets",
)

guideline_service = GuidelineService(
    project_id=PROJECT_ID, location=LOCATION, model_name=MODEL_NAME
)
eval_service = EvalService(
    project_id=PROJECT_ID,
    location=LOCATION,
    model_name=MODEL_NAME,
    bucket_name=GCS_BUCKET,
)
storage_client = storage.Client()
bucket = storage_client.bucket(GCS_BUCKET)


# --- Tool Definitions ---
async def save_files_as_artifacts(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> LlmResponse | None:
    """Inspects the LLM request for user-uploaded files and saves them as artifacts."""
    agent_name = callback_context.agent_name
    invocation_id = callback_context.invocation_id

    logger.info("[Callback] Before model callback for agent: %s", agent_name)

    last_user_message = None
    if llm_request.contents and llm_request.contents[-1].role == "user":
        last_user_message = llm_request.contents[-1]

    if not last_user_message or not last_user_message.parts:
        return None

    for i, part in enumerate(last_user_message.parts):
        if isinstance(part, dict):
            part = types.Part.model_validate(part)  # noqa: PLW2901

        if part.inline_data is None:
            continue

        try:
            file_name = (
                part.inline_data.display_name or f"artifact_{invocation_id}_{i}"
            )
            logger.info(
                f"Saving artifact: {file_name}, type: {part.inline_data.mime_type}"
            )

            await callback_context.save_artifact(
                filename=file_name,
                artifact=part,
            )
            logger.info(f"Successfully saved artifact: {file_name}")

        except Exception as e:
            logger.error(f"Failed to save artifact for part {i}: {e}")
            continue

    return None


async def _append_to_session_state(
    key: str, value: Any, context: CallbackContext
) -> str:
    """Appends a value to a list in the session state."""
    if key not in context.state:
        context.state[key] = []
    if not isinstance(context.state[key], list):
        raise TypeError(f"State entry for key '{key}' is not a list.")

    # If the value is a Pydantic model, convert it to a dict for JSON serialization
    if hasattr(value, "model_dump"):
        value = value.model_dump()

    context.state[key].append(value)
    logger.info("Appended to state key %s", key)
    return f"Successfully appended to {key}."


async def save_plan_to_state_tool(
    guideline_files: list[str],
    asset_files: list[str],
    tool_context: ToolContext,
    additional_guidance: str = "",
) -> str:
    """Saves the evaluation plan to the session state."""
    tool_context.state["guideline_files"] = guideline_files
    tool_context.state["asset_files"] = asset_files
    tool_context.state["additional_guidance"] = additional_guidance
    logger.info(
        "Saved plan to state: %d guidelines, %d assets.",
        len(guideline_files),
        len(asset_files),
    )
    return "Plan saved successfully."


async def _upload_part_to_gcs(
    filename: str,
    part: types.Part,
    session: Session,
    user_id: str,
    file_name_suffix: str,
) -> None:
    """Uploads a file part to GCS."""
    if part.inline_data is None:
        return None

    try:
        file_name = (
            filename
            or part.inline_data.display_name
            or f"artifact_{file_name_suffix}"
        )
        logger.info(
            f"Uploading artifact to GCS: {file_name}, type: {part.inline_data.mime_type}"
        )

        # Upload to GCS
        destination_blob_name = (
            f"{session.app_name}/{user_id}/{user_id}/{file_name}"
        )
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(
            part.inline_data.data,
            content_type=part.inline_data.mime_type,
        )
        gcs_uri = blob.name
        logger.info(
            f"Successfully uploaded artifact to GCS: gs://{GCS_BUCKET}/{gcs_uri}"
        )

        # Remove processed guidelines if this was a new guideline file with the same name
        _, processed_guideline_blob = await _get_processed_guideline(gcs_uri)
        if processed_guideline_blob:
            logger.info(f"Deleting existing processed guideline for {gcs_uri}")
            processed_guideline_blob.delete()
    except Exception as e:
        logger.error(
            f"Failed to upload artifact with suffix {file_name_suffix} to GCS: {e}"
        )

    return None


async def _upload_artifact_to_gcs(
    user_id: str,
    filename: str,
    file_name_suffix: str,
    tool_context: ToolContext,
) -> None:
    """Saves an artifact to GCS by first retrieving its contents by name."""
    artifact = await tool_context.load_artifact(filename)
    logger.info("Retrieved artifact: %r", artifact)

    if isinstance(artifact, dict):
        logger.info("Parsed artifact to google.genai.types.Part.")
        artifact = types.Part.model_validate(artifact)

    await _upload_part_to_gcs(
        filename=filename,
        part=artifact,
        session=tool_context.session,
        user_id=user_id,
        file_name_suffix=file_name_suffix,
    )


async def save_artifacts_to_gcs_tool(tool_context: ToolContext) -> str:
    """Checks for in-session files (artifacts) and uploads them to GCS.
    This ensures that files from the current session are available in persistent storage.
    """
    logger.info("Checking for in-session artifacts to save to GCS.")
    try:
        artifacts = await tool_context.list_artifacts()

        if not artifacts:
            logger.info("No in-session artifacts found to save.")
            return "No new in-session files to save."

        logger.info(
            f"Found {len(artifacts)} in-session artifacts. Uploading to GCS..."
        )

        continue_processing, user_id = _get_user_id(tool_context)
        if not continue_processing:
            return user_id  # This is the pending auth message

        upload_tasks = []

        for i, artifact in enumerate(artifacts):
            logger.info(f"Uploading artifact: [{artifact}]...")
            upload_tasks.append(
                _upload_artifact_to_gcs(
                    user_id=user_id,
                    filename=artifact,
                    file_name_suffix=f"{tool_context.session.id}_{i}",
                    tool_context=tool_context,
                )
            )
        await asyncio.gather(*upload_tasks)
        return f"Successfully saved {len(artifacts)} in-session files to GCS."

    except Exception as e:
        logger.error(f"Error in _save_artifacts_to_gcs_tool: {e}")
        return "An error occurred while saving files to GCS."


async def search_user_files_tool(
    tool_context: ToolContext,
) -> dict[str, list[str]]:
    """Lists all available files for the current user."""
    continue_processing, user_id = _get_user_id(tool_context)
    if not continue_processing:
        return user_id  # This is the pending auth message

    prefix = f"{tool_context.session.app_name}/{user_id}/{user_id}/"
    logger.info("Searching for files in GCS with prefix: %s", prefix)
    blobs = storage_client.list_blobs(GCS_BUCKET, prefix=prefix, delimiter="/")
    files = [
        os.path.basename(blob.name)
        for blob in blobs
        if not blob.name.endswith("/")
        and not blob.name.startswith(f"{prefix}processed_guideline_")
        and not blob.name.startswith(f"{prefix}processed_rubrics_")
    ]
    logger.info("Found %d files in GCS.", len(files))
    return {"gcs_files": files}


async def _get_processed_guideline(
    gcs_uri: str,
) -> tuple[Guideline | None, Blob | None]:
    """Retrieves the latest processed guideline output for a given guideline gcs_uri.
    Returns the Guideline object if found, otherwise None.
    """
    file_name_ext = os.path.basename(gcs_uri)
    file_name, _ = os.path.splitext(file_name_ext)
    prefix_to_find = gcs_uri.replace(
        file_name_ext, f"processed_guideline_{file_name}"
    )
    blobs = storage_client.list_blobs(GCS_BUCKET, prefix=prefix_to_find)
    retrieved_blobs = list(blobs)

    if len(retrieved_blobs) == 0:
        logger.info("No processed guideline found for %s", gcs_uri)
        return (None, None)

    latest_blob = max(retrieved_blobs, key=lambda blob: blob.name)
    logger.info("Found latest processed guideline: %s", latest_blob.name)

    guideline_json = latest_blob.download_as_bytes()
    guideline_data = json.loads(guideline_json)
    return (Guideline.model_validate(guideline_data), latest_blob)


async def _process_single_guideline(
    user_id: str, gcs_uri: str, tool_context: ToolContext
) -> dict[str, Any]:
    """Helper to process one guideline file, checking for a pre-processed version first."""
    file_name_ext = os.path.basename(gcs_uri)
    file_name, _ = os.path.splitext(file_name_ext)
    logger.info(f"Processing guideline: {file_name_ext} from {gcs_uri}")
    was_preprocessed = False

    guideline, _ = await _get_processed_guideline(gcs_uri)

    if guideline:
        was_preprocessed = True
        logger.info(f"Found pre-processed version for {file_name_ext}.")
    else:
        logger.info(
            f"No pre-processed version found for {file_name_ext}. Processing from scratch."
        )
        blob = bucket.blob(gcs_uri)
        if not blob.exists():
            raise ValueError(f"File not found in GCS: {gcs_uri}")
        mime_type = blob.content_type

        logger.info(
            "Processing guideline file: %s with MIME type: %s",
            gcs_uri,
            mime_type,
        )

        gcs_guideline_file_uri = f"gs://{GCS_BUCKET}/{gcs_uri}"
        guideline_response = await guideline_service.extract_guideline_from_doc(
            file_uri=gcs_guideline_file_uri, mime_type=mime_type
        )
        guideline = Guideline(
            name=guideline_response.name,
            description=guideline_response.description,
            criteria=guideline_response.criteria,
            file_uri=gcs_guideline_file_uri,
        )

        timestamp = guideline_response.created_at.isoformat()
        processed_guideline_name = (
            f"processed_guideline_{file_name}_{timestamp}.json"
        )

        upload_blob = bucket.blob(
            f"{tool_context.session.app_name}/{user_id}/{user_id}/{processed_guideline_name}"
        )
        upload_blob.upload_from_string(
            data=guideline.model_dump_json(indent=2).encode("utf-8"),
            content_type="application/json",
        )
        logger.info(f"File uploaded to {upload_blob.name}.")

    await _append_to_session_state(
        "processed_guidelines", guideline, tool_context
    )
    return {
        "was_preprocessed": was_preprocessed,
        "guideline": guideline.model_dump(),
    }


def _format_guideline_string(guideline_obj: Guideline) -> str:
    """Helper to format a Guideline object into a Markdown table with severity breakdown."""
    headers = ["Severity", "Category", "Criterion Name", "Criterion Value"]
    table = [
        f"| {' | '.join(headers)} |",
        f"| {' | '.join(['---'] * len(headers))} |",
    ]

    blocker_count = 0
    warning_count = 0

    for criterion in guideline_obj.criteria:
        severity = criterion.severity
        if severity == Severity.BLOCKER:
            blocker_count += 1
        elif severity == Severity.WARNING:
            warning_count += 1

        severity_icon = "🛑 " if severity == Severity.BLOCKER else "⚠️ "
        row = [
            f"{severity_icon} {severity.value}",
            criterion.category,
            criterion.name,
            criterion.criterion_value,
        ]
        table.append(f"| {' | '.join(row)} |")

    total = blocker_count + warning_count
    stats = ["#### Severity Breakdown"]
    if total > 0:
        stats.append(f"BLOCKER Criteria: {blocker_count}/{total}")
        stats.append(f"WARNING Criteria: {warning_count}/{total}")
    else:
        stats.append("No criteria found.")

    return "\n\n".join(stats) + "\n\n" + "\n".join(table)


async def guideline_processor_tool(
    filename: str, tool_context: ToolContext
) -> str:
    """Processes a single guideline file from GCS and returns a formatted report."""
    continue_processing, user_id = _get_user_id(tool_context)
    if not continue_processing:
        return user_id  # This is the pending auth message

    gcs_uri = f"{tool_context.session.app_name}/{user_id}/{user_id}/{filename}"
    result = await _process_single_guideline(user_id, gcs_uri, tool_context)

    guideline_data = result["guideline"]
    guideline_obj = Guideline.model_validate(guideline_data)
    formatted_table = _format_guideline_string(guideline_obj)
    report = f"### Processed Guideline: {guideline_obj.name}\n{formatted_table}"

    return report


async def _evaluate_single_asset(
    tool_context: ToolContext,
    user_id: str,
    asset_uri: str,
    asset_name: str,
    asset_id: str,
    category: str,
    asset_prompt: str | None = "",
    video_reference_image_uris: list[str] | None = None,
) -> AssetEvaluation:
    """Helper to evaluate one asset from GCS against the processed guidelines."""
    logger.info(f"Evaluating asset: {asset_uri}")

    processed_guidelines = [
        Guideline.model_validate(g)
        for g in tool_context.state.get("processed_guidelines", [])
    ]
    additional_guidance = tool_context.state.get("additional_guidance", "")

    asset = Asset(
        asset_uri=f"gs://{GCS_BUCKET}/{asset_uri}",
        asset_name=asset_name,
        asset_id=asset_id,
        category=Category(category.upper()),
        asset_prompt=asset_prompt or "",
        video_reference_image_uris=[
            f"gs://{GCS_BUCKET}/{uri}" for uri in video_reference_image_uris
        ]
        or [],
    )

    logger.info(
        "Evaluating asset {%s} using guidelines {%s} and additional guidance {%s}",
        asset.model_dump_json(),
        "".join([g.model_dump_json() for g in processed_guidelines]),
        additional_guidance,
    )

    evaluation = await asyncio.to_thread(
        eval_service.evaluate_asset,
        asset=asset,
        guidelines=processed_guidelines,
        additional_guidance=additional_guidance,
        user_id=user_id,
        app_name=tool_context.session.app_name,
    )

    logger.info(
        "Received evaluation result for asset {%s}: %s",
        asset.asset_id,
        evaluation.model_dump_json(),
    )

    timestamp = datetime.now(UTC).isoformat()
    eval_report_name = f"eval_{asset.asset_id}_{timestamp}.json"
    upload_blob = bucket.blob(
        f"{tool_context.session.app_name}/{user_id}/{tool_context.session.id}/{eval_report_name}"
    )
    upload_blob.upload_from_string(
        data=evaluation.model_dump_json(indent=2).encode("utf-8"),
        content_type="application/json",
    )
    logger.info(f"File uploaded to {upload_blob.name}.")

    # Generate and save radar chart
    try:
        chart_bytes = await generate_radar_chart(evaluation)
        if chart_bytes:
            chart_filename = f"chart_{asset.asset_id}_{timestamp}.png"

            # 1. Upload to GCS (Persistence)
            chart_blob = bucket.blob(
                f"{tool_context.session.app_name}/{user_id}/{tool_context.session.id}/{chart_filename}"
            )
            chart_blob.upload_from_string(chart_bytes, content_type="image/png")
            logger.info(f"Chart uploaded to {chart_blob.name}")

            # 2. Save as Artifact (Context)
            chart_part = types.Part(
                inline_data=types.Blob(mime_type="image/png", data=chart_bytes)
            )
            await tool_context.save_artifact(
                filename=chart_filename, artifact=chart_part
            )
            logger.info(f"Chart saved as artifact: {chart_filename}")

    except Exception as e:
        logger.error(f"Failed to generate or save chart: {e}")

    await _append_to_session_state(
        "evaluation_results", evaluation, tool_context
    )
    return evaluation


def _format_evaluation_string(asset_evaluation: AssetEvaluation) -> str:
    """Helper to format an AssetEvaluation object into a Markdown table with summary stats."""
    headers = [
        "Guideline",
        "Category",
        "Criterion Name",
        "Question",
        "Verdict",
        "Justification",
    ]
    table = [
        f"| {' | '.join(headers)} |",
        f"| {' | '.join(['---'] * len(headers))} |",
    ]

    verdict_icons = {"yes": "✅", "no": "❌", "n/a": "➖"}  # noqa: RUF001

    total_checks = 0
    pass_count = 0
    fail_count = 0
    na_count = 0

    for gv in asset_evaluation.guideline_verdicts:
        guideline_id = gv.guideline_id
        for verdict in gv.verdicts:
            total_checks += 1
            v_lower = verdict.verdict.lower()
            if v_lower == "yes":
                pass_count += 1
            elif v_lower == "no":
                fail_count += 1
            else:
                na_count += 1

            v_str = f"{verdict_icons.get(v_lower, '')} {verdict.verdict}"

            # Use criterion name if available, otherwise fallback to ID
            c_display = (
                verdict.criterion_name
                if verdict.criterion_name
                else verdict.criterion_id
            )

            row = [
                guideline_id,
                verdict.category,
                c_display,
                verdict.question,
                v_str,
                verdict.justification,
            ]
            table.append(f"| {' | '.join([str(item) for item in row])} |")

    # Create Summary
    summary_lines = ["#### Evaluation Summary"]
    # Score
    # Adjust max_value if needed based on data.
    max_score = 1.0 if asset_evaluation.final_score <= 1.0 else 100.0

    # Format with rounded numbers and newlines
    summary_lines.append(
        f"Final Score: {asset_evaluation.final_score:.1f}/{max_score:.1f}"
    )

    # Pass/Fail stats
    if total_checks > 0:
        summary_lines.append(f"Passing Checks: {pass_count}/{total_checks}")
        summary_lines.append(f"Failing Checks: {fail_count}/{total_checks}")
        summary_lines.append(
            f"Not Applicable Checks: {na_count}/{total_checks}"
        )

    return "\n\n".join(summary_lines) + "\n\n" + "\n".join(table)


async def asset_evaluator_tool(
    tool_context: ToolContext,
    assets: list[dict[str, Any]],
) -> list[str]:
    """Evaluates multiple assets from GCS in parallel and returns formatted reports."""
    continue_processing, user_id = _get_user_id(tool_context)
    if not continue_processing:
        return user_id  # This is the pending auth message

    prefix = f"{tool_context.session.app_name}/{user_id}/{user_id}"

    tasks = [
        _evaluate_single_asset(
            tool_context=tool_context,
            user_id=user_id,
            asset_uri=f"{prefix}/{asset['asset_name']}",
            asset_name=asset["asset_name"],
            asset_id=asset["asset_id"],
            category=asset["category"],
            asset_prompt=asset.get("asset_prompt", ""),
            video_reference_image_uris=[
                f"{prefix}/{filename}"
                for filename in asset.get("video_reference_image_files", [])
            ],
        )
        for asset in assets
    ]
    results = await asyncio.gather(*tasks)

    formatted_reports = []
    for evaluation in results:
        formatted_table = _format_evaluation_string(evaluation)
        report = f"### Evaluation Result for Asset: {evaluation.asset_id}\n{formatted_table}"
        formatted_reports.append(report)

    return formatted_reports


def _get_user_id(tool_context: ToolContext) -> tuple[bool, str]:
    """Retrieves the user's id to use in the agent's operations, along with whether to continue processing or not."""
    user_id = get_user_id(tool_context)

    if isinstance(user_id, dict):
        logger.info("Pausing operation to await user authentication.")
        return False, user_id["message"]
    return True, user_id
