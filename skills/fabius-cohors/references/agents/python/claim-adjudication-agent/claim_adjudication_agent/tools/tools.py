import logging
import os
import traceback
from typing import Any

from dotenv import load_dotenv
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.cloud import logging as cloud_logging
from google.cloud import storage
from google.genai import types

# --- Logging Configuration ---
client = cloud_logging.Client()
client.setup_logging(log_level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

CLAIM_DOCUMENTS_BUCKET = os.environ.get(
    "CLAIM_DOCUMENTS_BUCKET", "agentspace-demo-ds-bucket-proj-genai-1729"
)
CLAIM_DOCUMENTS_BUCKET_FOLDER = os.getenv(
    "CLAIM_DOCUMENTS_BUCKET_FOLDER", "health_claim_documents"
)

logger.info(f"CLAIM_DOCUMENTS_BUCKET: {CLAIM_DOCUMENTS_BUCKET}")
logger.info(f"CLAIM_DOCUMENTS_BUCKET_FOLDER: {CLAIM_DOCUMENTS_BUCKET_FOLDER}")

storage_client = storage.Client()


async def before_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> LlmResponse | None:
    """Inspects/modifies the LLM request or skips the call."""
    agent_name = callback_context.agent_name
    logger.info(
        f"[Callback: before_model_callback] Before model call for agent: {agent_name}"
    )

    try:
        active_case_id = callback_context.state.get("active_case_id")
        if not active_case_id:
            logger.error(
                "[Callback: before_model_callback] No 'active_case_id' found in state."
            )
            logger.info("[Callback: before_model_callback] Proceeding with LLM call.")
            return None

        logger.info(
            f"[Callback: before_model_callback] Found active case: {active_case_id}"
        )

        document_list = callback_context.state.get(active_case_id)
        if (
            not document_list
            or not isinstance(document_list, list)
            or len(document_list) == 0
        ):
            logger.error(
                f"[Callback: before_model_callback] No document list found for key: {active_case_id}"
            )
            logger.info("[Callback: before_model_callback] Proceeding with LLM call.")
            return None

        logger.info(
            f"[Callback: before_model_callback] Found {len(document_list)} "
            f"documents for attachment."
        )

        if not llm_request.contents or llm_request.contents[-1].role != "user":
            logger.error(
                "[Callback: before_model_callback] No user message found in request to append files to."
            )
            logger.info("[Callback: before_model_callback] Proceeding with LLM call.")
            return None

        user_message_parts = llm_request.contents[-1].parts

        for doc in document_list:
            gcs_path = doc.get("gcs_path")
            mime_type = doc.get("mime_type")

            if not gcs_path or not mime_type:
                logger.error(
                    f"[Callback] Skipping document with missing path/mime: {doc.get('name', 'UNKNOWN')}"
                )
                continue

            # Check for duplicates using any()
            is_duplicate = any(
                hasattr(part, "file_data")
                and part.file_data
                and part.file_data.file_uri == gcs_path
                for part in user_message_parts
            )

            if is_duplicate:
                logger.error(
                    f"[Callback] Skipping duplicate attachment: {gcs_path}"
                )
                continue

            logger.info(
                f"[Callback] Attaching file: {gcs_path} (MIME: {mime_type})"
            )
            file_part = types.Part.from_uri(
                file_uri=gcs_path, mime_type=mime_type
            )
            user_message_parts.append(file_part)

    except Exception as e:
        logger.exception(
            f"[Callback: before_model_callback] ERROR attaching files from state: {e}"
        )
        traceback.print_exc()

    logger.info("[Callback: before_model_callback] Proceeding with LLM call.")
    return None


async def after_tool_callback(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: ToolContext,
    tool_response: dict,
) -> dict | None:
    """Inspects/modifies the tool result after execution."""
    agent_name = tool_context.agent_name
    tool_name = tool.name
    logger.info(
        f"[Callback: after_tool_callback] After tool call for tool "
        f"'{tool_name}' in agent '{agent_name}'"
    )
    logger.info(f"[Callback: after_tool_callback] Args used: {args}")
    logger.info(
        f"[Callback: after_tool_callback] Original tool_response: {tool_response}"
    )

    if tool_name != "get_claims_details":
        logger.info(
            "[Callback: after_tool_callback] Tool name is not 'get_claims_details', "
            "returning original response."
        )
        return tool_response

    try:
        case_id = args.get("claim_id")

        if case_id and isinstance(tool_response, list):
            # 3. Save the entire list (the tool_response) to state
            tool_context.state[case_id] = tool_response
            logger.info(
                f"[Callback: after_tool_callback] Saved extracted data to state "
                f"with key: '{case_id}'"
            )

            # 4. Set the active case
            tool_context.state["active_case_id"] = case_id
            logger.info(
                f"[Callback: after_tool_callback] Set 'active_case_id' to: '{case_id}'"
            )

            # Log the current state
            current_state = tool_context.state.to_dict()
            logger.info(
                f"[Callback: after_tool_callback] Current State is now: {current_state}"
            )

        elif not case_id:
            logger.info(
                "[Callback: after_tool_callback] ERROR: Could not find "
                "'claim_id' in args."
            )

        elif not isinstance(tool_response, list):
            logger.info(
                f"[Callback: after_tool_callback] ERROR: Tool response was not a list. "
                f"Got: {type(tool_response)}"
            )

    except Exception as e:
        logger.info(
            f"[Callback: after_tool_callback] ERROR saving tool response to state: {e}"
        )

    logger.info(
        "[Callback: after_tool_callback] Passing original tool response through."
    )
    return None


def get_claims_details(
    claim_id: str, tool_context: ToolContext
) -> list[dict[str, str]]:
    logger.info(
        f">>> Tool: 'get_claims_details' called for Claim ID '{claim_id}'"
    )

    results: list[dict[str, str]] = []
    prefix = f"{CLAIM_DOCUMENTS_BUCKET_FOLDER}/{claim_id}/"

    try:
        bucket = storage_client.bucket(CLAIM_DOCUMENTS_BUCKET)
        blobs = bucket.list_blobs(prefix=prefix)

        logger.info(
            f"Scanning GCS bucket '{CLAIM_DOCUMENTS_BUCKET}' for prefix '{prefix}'"
        )

        for blob in blobs:
            if blob.name.endswith("/"):
                continue

            file_name = os.path.basename(blob.name)

            try:
                # 1. Determine file type from extension
                _, ext = os.path.splitext(file_name)
                ext = ext.lower()

                mime_type = "unknown"
                if ext in [".pdf"]:
                    mime_type = "application/pdf"
                elif ext in [".png"]:
                    mime_type = "image/png"
                elif ext in [".jpg", ".jpeg"]:
                    mime_type = "image/jpeg"
                elif ext in [".gif"]:
                    mime_type = "image/gif"
                elif ext in [".mp3"]:
                    mime_type = "audio/mp3"
                elif ext in [".json"]:
                    mime_type = "text/plain"
                elif ext in [".txt"]:
                    mime_type = "text/plain"
                else:
                    continue

                results.append(
                    {
                        "name": file_name,
                        "description": f"File for claim {claim_id}",
                        "mime_type": mime_type,
                        "gcs_path": f"gs://{CLAIM_DOCUMENTS_BUCKET}/{blob.name}",
                    }
                )
                logger.info(f"Successfully processed and found: {file_name}")

            except Exception as e:
                logger.error(f"Failed to process file {file_name}: {e}")

    except Exception as e:
        logger.exception(f"Failed to list blobs for claim {claim_id}: {e}")
        return []

    return results
