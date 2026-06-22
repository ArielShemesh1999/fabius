"""
After-model callback to format coordinator output for chat display.
"""

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.genai import types

from nexshift_agent.sub_agents.utils.output_formatter import OutputFormatter


def format_model_output(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> LlmResponse | None:
    """
    Format the LLM's response for chat display.

    Detects data patterns in the response and applies appropriate
    markdown formatting (tables, sections, calendar views, etc.)

    Args:
        callback_context: Context with agent_name, session state, etc.
        llm_response: The LLM's response containing content

    Returns:
        None: Use original response (no changes needed)
        LlmResponse: Replace with formatted response
    """
    if not llm_response or not llm_response.content:
        return None

    content = llm_response.content
    if not content.parts:
        return None

    # Get the text content from all parts
    original_text = ""
    for part in content.parts:
        if hasattr(part, "text") and part.text:
            original_text += part.text

    if not original_text:
        return None

    # Format the output
    formatter = OutputFormatter()
    formatted_text = formatter.format(original_text)

    # If no changes, return None to use original
    if formatted_text == original_text:
        return None

    # Create new content with formatted text
    new_content = types.Content(
        role=content.role, parts=[types.Part(text=formatted_text)]
    )

    # Return new LlmResponse with formatted content
    return LlmResponse(
        content=new_content,
        grounding_metadata=llm_response.grounding_metadata,
        usage_metadata=llm_response.usage_metadata,
        finish_reason=llm_response.finish_reason,
        model_version=llm_response.model_version,
    )
