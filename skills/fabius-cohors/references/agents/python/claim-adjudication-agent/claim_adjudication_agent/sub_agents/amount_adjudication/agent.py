import os

from google.adk.agents import LlmAgent

from ...tools.tools import before_model_callback
from .prompt import AMOUNT_ADJUDICATION_AGENT_PROMPT

GEMINI_FLASH = os.getenv("GEMINI_FLASH", "gemini-2.5-flash")

amount_adjudication_agent = LlmAgent(
    name="amount_adjudication_agent",
    model=GEMINI_FLASH,
    description=(
        "Adjudicates claim amounts by analyzing hospital bills and invoices against "
        "policy terms, co-payments, deductibles."
    ),
    instruction=AMOUNT_ADJUDICATION_AGENT_PROMPT,
    output_key="amount_adjudication_agent_output",
    before_model_callback=before_model_callback,
    tools=[],
)
