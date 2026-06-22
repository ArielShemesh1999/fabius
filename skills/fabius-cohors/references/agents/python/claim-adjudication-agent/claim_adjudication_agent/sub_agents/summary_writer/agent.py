import os

from google.adk.agents import LlmAgent

from ...tools.tools import before_model_callback
from .prompt import SUMMARY_WRITER_AGENT_PROMPT

GEMINI_FLASH = os.getenv("GEMINI_FLASH", "gemini-2.5-flash")

claim_summary_agent = LlmAgent(
    name="claim_summary_agent",
    model=GEMINI_FLASH,
    description=(
        "Synthesizes admissibility findings and financial adjudication data into a "
        "structured, comprehensive health claim summary report."
    ),
    instruction=SUMMARY_WRITER_AGENT_PROMPT,
    output_key="claim_summary_agent_output",
    before_model_callback=before_model_callback,
)
