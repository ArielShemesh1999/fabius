from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.workflow.parallel_worker import ParallelWorker
from src.prompts import (
    JOIN_AND_DISTILL_PROMPT,
)
from src.tools import execute_search

# The LlmAgent that will be run in parallel for each platform.
_research_worker_llm_agent = LlmAgent(
    # The name for the inner agent is not strictly necessary for the
    # workflow but can be useful for debugging.
    name="research_worker_llm_agent",
    model="gemini-2.5-flash",
    instruction="""Your sole task is to research the topic '{topic}' on a specific platform.
The platform you MUST use is provided as your input. Your entire input is the name of the platform.
DO NOT ask for the platform. Use the input you are given.
Execute a search on that platform for the topic and summarize the results.""",
    tools=[execute_search],
)

# A single, reusable worker agent that will be run in parallel for each platform.
research_worker_agent = ParallelWorker(_research_worker_llm_agent)


# The Synthesizer joins the results from the parallel workers into a final report.
distill_agent = LlmAgent(
    name="join_and_distill_agent",
    model="gemini-2.5-flash",
    instruction=JOIN_AND_DISTILL_PROMPT,
)
