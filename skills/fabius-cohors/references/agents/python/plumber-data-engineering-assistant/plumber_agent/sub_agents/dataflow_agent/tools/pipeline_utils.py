"""
Utilities for creating, running, and managing Apache Beam pipelines on Google Cloud Dataflow.
"""

import asyncio
import json
import logging
import os
import re
import subprocess
import sys
import uuid

import vertexai
from google.api_core import exceptions
from google.cloud import storage
from vertexai.generative_models import GenerativeModel

from ..constants import MODEL
from ..prompts import (
    DATAFLOW_CODE_REVIEWER_EXPERT_PROMPT,
    STTM_PARSING_INSTRUCTIONS_BEAM_TRANSFORMATIONS,
)

logger = logging.getLogger("plumber-agent")


def _sanitize_job_name(name: str) -> str:
    """
    Sanitizes a string to conform to Google Cloud Dataflow job name requirements.
    """
    sanitized = name.lower()
    sanitized = re.sub(r"[^a-z0-9-]", "-", sanitized)
    sanitized = re.sub(r"-+", "-", sanitized)
    sanitized = sanitized.strip("-")
    if not sanitized:
        return f"job-{uuid.uuid4().hex[:8]}"
    if not sanitized[0].isalpha():
        sanitized = "job-" + sanitized
    if not sanitized[-1].isalnum():
        sanitized = sanitized[:-1]
    return sanitized[:63]


def generate_beam_transformations_from_sttm(gcs_path: str) -> str:
    """
    Generates Apache Beam transformation logic from an STTM CSV file.
    """
    logger.info("Generating Beam transformations from STTM file: %s", gcs_path)
    try:
        storage_client = storage.Client()
        bucket_name, blob_name = gcs_path.replace("gs://", "").split("/", 1)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        if not blob.exists():
            raise FileNotFoundError(f"Object not found at GCS path: {gcs_path}")

        file_content = blob.download_as_text()

        vertexai.init(
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION"),
        )
        model = GenerativeModel(MODEL)
        response = model.generate_content(
            [STTM_PARSING_INSTRUCTIONS_BEAM_TRANSFORMATIONS, file_content]
        )

        output_code = (
            response.text.replace("```python", "").replace("```", "").strip()
        )
        logger.info("Successfully generated Beam transformations.")
        return output_code

    except (FileNotFoundError, ValueError, exceptions.GoogleAPICallError) as e:
        logger.error(
            "An error occurred while generating Beam transformations from STTM: %s",
            e,
            exc_info=True,
        )
        return ""


async def create_pipeline_from_scratch(
    project_id: str,
    region: str,
    gcs_bucket_path: str,
    job_name: str,
    pipeline_code: str,
    pipeline_args: dict[str, str],
    pipeline_type: str,
) -> str:
    """
    Generates and executes a Python Apache Beam pipeline on Google Cloud Dataflow.
    """
    logger.info("Creating Dataflow %s pipeline from scratch...", pipeline_type)
    if pipeline_type not in ["batch", "streaming"]:
        logger.error("Invalid pipeline type specified.")
        return json.dumps(
            {
                "status": "error",
                "error_message": "Invalid pipeline type. Please choose 'batch' or 'streaming'.",
            }
        )

    if pipeline_type == "streaming":
        pipeline_args["streaming"] = "true"

    logger.info("Reviewing Dataflow code...")
    reviewed_code = review_dataflow_code(pipeline_code)
    logger.info("Dataflow code review complete.")

    return await generate_and_run_beam_pipeline(
        project_id,
        region,
        gcs_bucket_path,
        job_name,
        reviewed_code,
        pipeline_args,
        pipeline_type,
    )


async def generate_and_run_beam_pipeline(
    project_id: str,
    region: str,
    gcs_bucket_path: str,
    job_name: str,
    pipeline_code: str,
    pipeline_args: dict[str, str],
    pipeline_type: str,
) -> str:
    """
    Generates, executes, and archives a Python Apache Beam pipeline.
    """
    if not all([project_id, region, gcs_bucket_path]):
        return json.dumps(
            {
                "status": "error",
                "error_message": "project_id, region, and gcs_bucket_path are required.",
            }
        )

    if not gcs_bucket_path.startswith("gs://"):
        return json.dumps(
            {
                "status": "error",
                "error_message": "gcs_bucket_path must start with 'gs://'.",
            }
        )

    base_path = os.path.join("plumber", "agent", "agents", "dataflow_agent")
    os.makedirs(base_path, exist_ok=True)
    temp_filename = os.path.join(base_path, f"temp_pipeline_{uuid.uuid4()}.py")
    sanitized_job_name = _sanitize_job_name(job_name)
    logger.info("Sanitized job name: %s", sanitized_job_name)

    full_args = {
        "runner": "DataflowRunner",
        "project": project_id,
        "region": region,
        "job_name": sanitized_job_name,
        "temp_location": os.path.join(gcs_bucket_path, "temp"),
        "staging_location": os.path.join(gcs_bucket_path, "staging"),
        "labels": json.dumps({"source": "plumber"}),
        **pipeline_args,
    }

    try:
        with open(temp_filename, "w", encoding="utf-8") as f:
            f.write(pipeline_code)

        command = [sys.executable, temp_filename]
        for key, value in full_args.items():
            command.append(f"--{key}")
            command.append(str(value))

        logger.info("Executing command: %s", " ".join(command))
        output = ""
        job_id_match = None

        if pipeline_type == "streaming":
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            if process.stdout is not None:
                async for line_bytes in process.stdout:
                    line = line_bytes.decode("utf-8", errors="ignore")
                    output += line
                    print(line, end="")
                    match = re.search(
                        r"(\d{4}-\d{2}-\d{2}_\d{2}_\d{2}_\d{2}-\d+)", line
                    )
                    if match:
                        job_id_match = match
                        print(
                            f"\n--- INFO: Found Dataflow Job ID: {job_id_match.group(1)}. "
                            "Terminating script watcher. ---"
                        )
                        break

            if process.returncode is None:
                try:
                    process.terminate()
                    await asyncio.wait_for(process.wait(), timeout=10)
                except TimeoutError:
                    print(
                        "--- WARNING: Subprocess did not terminate gracefully, killing it. ---"
                    )
                    process.kill()
                except ProcessLookupError:
                    pass

            if not job_id_match:
                stdout, stderr = await process.communicate()
                output += stdout.decode("utf-8", errors="ignore")
                if stderr:
                    output += stderr.decode("utf-8", errors="ignore")
                raise subprocess.CalledProcessError(
                    process.returncode or 1, command, output=output
                )
        else:  # Batch
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            output = stdout.decode("utf-8", errors="ignore") + stderr.decode(
                "utf-8", errors="ignore"
            )
            if process.returncode != 0:
                raise subprocess.CalledProcessError(
                    process.returncode or 1, command, output=output
                )
        job_id_match = re.search(
            r"jobId: '(\d{4}-\d{2}-\d{2}_\d{2}_\d{2}_\d{2}-\d+)'", output
        )

        if not job_id_match:
            job_id_match = re.search(
                r"(?P<id>\d{4}-\d{2}-\d{2}_\d{2}_\d{2}_\d{2}-\d+)", output
            )

        if not job_id_match:
            return json.dumps(
                {
                    "status": "error",
                    "error_message": "Job launched, but could not find Job ID in output. "
                    f"Full output:\n{output}",
                }
            )

        job_details = {"name": sanitized_job_name}
        id_match = re.search(r"id: '([^']*)'", output)
        client_request_id_match = re.search(
            r"clientRequestId: '([^']*)'", output
        )
        create_time_match = re.search(r"createTime: '([^']*)'", output)

        job_id = job_id_match.group(1) if job_id_match else "unknown"
        job_details["id"] = job_id
        if id_match:
            if client_request_id_match:
                job_details["clientRequestId"] = client_request_id_match.group(
                    1
                )
            if create_time_match:
                job_details["createTime"] = create_time_match.group(1)

        logger.info(
            "Dataflow job details: %s", json.dumps(job_details, indent=2)
        )
        gcs_path, gcs_error = None, None
        try:
            storage_client = storage.Client(project=project_id)
            bucket_name, *path_parts = gcs_bucket_path.replace(
                "gs://", ""
            ).split("/")
            base_prefix = "/".join(filter(None, path_parts))
            script_filename = f"{sanitized_job_name}-{uuid.uuid4().hex[:8]}.py"
            gcs_path_str = os.path.join(
                base_prefix, "generated_pipelines", script_filename
            )

            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(gcs_path_str)
            blob.upload_from_string(pipeline_code, content_type="text/x-python")
            gcs_path = f"gs://{bucket_name}/{gcs_path_str}"
        except exceptions.GoogleAPICallError as e:
            gcs_error = e

        logger.info(
            "Successfully launched Dataflow job '%s'.", sanitized_job_name
        )
        report_lines = [
            f"Successfully launched Dataflow job '{sanitized_job_name}'."
        ]
        report_lines.append("Job Details:")
        for key, value in sorted(job_details.items()):
            report_lines.append(f"  {key}: {value}")

        status = "success"
        if gcs_path:
            report_lines.append(
                f"\nThe pipeline script was saved to {gcs_path}"
            )
        if gcs_error:
            status = "success_with_warning"
            report_lines.append(
                f"\nWARNING: Failed to save the script to GCS. Error: {gcs_error}"
            )

        final_report = {
            "status": status,
            "report": "\n".join(report_lines),
            "job_id": job_id,
            "gcs_script_path": gcs_path,
        }
        print(json.dumps(final_report, indent=2))
        return json.dumps(final_report)

    except subprocess.CalledProcessError as e:
        logger.error("An error occurred: %s", e, exc_info=True)
        return json.dumps(
            {
                "status": "error",
                "error_message": f"Failed to execute pipeline script.\n--- ERROR ---\n{e.output}",
            }
        )
    except (OSError, ValueError) as e:
        logger.error("An error occurred: %s", e, exc_info=True)
        return json.dumps(
            {"status": "error", "error_message": f"Unexpected error: {e!s}"}
        )
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)


def review_dataflow_code(code: str) -> str:
    """
    Reviews a Dataflow pipeline script using a generative model.
    """
    logger.info("Starting Dataflow code review...")
    try:
        vertexai.init(
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION"),
        )
        model = GenerativeModel(MODEL)
        response = model.generate_content(
            [DATAFLOW_CODE_REVIEWER_EXPERT_PROMPT, code]
        )
        reviewed_code = (
            response.text.replace("```python", "").replace("```", "").strip()
        )
        logger.info("Dataflow code review complete.")
        return reviewed_code
    except (ValueError, RuntimeError) as e:
        logger.error(
            "An error occurred while reviewing the Dataflow code: %s",
            e,
            exc_info=True,
        )
        return code
