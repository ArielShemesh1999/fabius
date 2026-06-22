"""Health claim advisor: facilitate health insurance claim processing."""

import os

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.tools.function_tool import FunctionTool

from .prompt import CASHLESS_HEALTH_CLAIM_ADVISOR_WORKFLOW_PROMPT
from .sub_agents.amount_adjudication.agent import amount_adjudication_agent
from .sub_agents.claim_admissibility.agent import claim_admissibility_agent
from .sub_agents.summary_writer.agent import claim_summary_agent
from .tools.tools import after_tool_callback, get_claims_details

GEMINI_FLASH = os.getenv("GEMINI_FLASH", "gemini-2.5-flash")

claims_processing_core_agent = ParallelAgent(
    name="claims_processing_core_agent",
    description=(
        "Facilitates the concurrent execution of core claim evaluation modules, "
        "including admissibility verification and financial adjudication, to ensure "
        "efficient processing."
    ),
    sub_agents=[claim_admissibility_agent, amount_adjudication_agent],
)

claims_processing_flow_agent = SequentialAgent(
    name="claims_processing_flow_agent",
    description=(
        "Manages the sequential progression of claim processing, transitioning from "
        "core technical adjudication to final report synthesis and summary generation."
    ),
    sub_agents=[claims_processing_core_agent, claim_summary_agent],
)

cashless_health_claim_advisor_workflow = LlmAgent(
    name="cashless_health_claim_advisor_workflow",
    model=GEMINI_FLASH,
    description=(
        "The master orchestration agent responsible for the end-to-end management of "
        "the cashless health insurance claim lifecycle, streamlining document "
        "retrieval, verification, and adjudication."
    ),
    instruction=CASHLESS_HEALTH_CLAIM_ADVISOR_WORKFLOW_PROMPT,
    sub_agents=[claims_processing_flow_agent],
    tools=[FunctionTool(get_claims_details)],
    after_tool_callback=after_tool_callback,
)

root_agent = cashless_health_claim_advisor_workflow
