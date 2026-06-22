import os

from google.adk.agents import LlmAgent

from ...tools.tools import before_model_callback
from .prompt import CLAIM_ADMISSIBILITY_AGENT_PROMPT

GEMINI_FLASH = os.getenv("GEMINI_FLASH", "gemini-2.5-flash")

claim_admissibility_agent = LlmAgent(
    name="claim_admissibility_agent",
    model=GEMINI_FLASH,
    description=(
        "Evaluates claim admissibility by verifying submitted documentation against "
        "policy coverage and product terms and conditions."
    ),
    instruction=CLAIM_ADMISSIBILITY_AGENT_PROMPT,
    output_key="claim_admissibility_agent_output",
    before_model_callback=before_model_callback,
    tools=[],
)
