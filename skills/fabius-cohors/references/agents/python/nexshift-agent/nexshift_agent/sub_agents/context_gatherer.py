"""
Context Gatherer Agent - First step in the roster generation workflow.
Gathers all necessary context (nurse stats, shifts, regulations) before roster generation.
"""

from google.adk.agents import LlmAgent

from nexshift_agent.sub_agents.config import MODEL_CONTEXT_GATHERER
from nexshift_agent.sub_agents.tools.data_loader import (
    get_available_nurses,
    get_regulations,
    get_shifts_to_fill,
)
from nexshift_agent.sub_agents.tools.history_tools import (
    get_nurse_stats,
    get_shift_history,
)

CONTEXT_GATHERER_INSTRUCTION = """
You are a Context Gatherer for a nurse rostering system.
Your job is to collect information before roster generation by calling tools.

## CRITICAL: NEVER WRITE CODE

You must ONLY use the provided tools. NEVER write Python, JavaScript, or any code.
If you find yourself writing "import", "def", or code - STOP and use the tools instead.

## Your Tools

Call these tools to gather context:

1. **get_nurse_stats()** - Get fatigue levels and shift counts
2. **get_available_nurses()** - Get nurse profiles and preferences
3. **get_shifts_to_fill()** - Get shifts needing assignment

## Your Task

1. Call all three tools above
2. Summarize the results in plain text (no code)

## Output Format

After calling the tools, provide a summary like:

CONTEXT SUMMARY

SCHEDULING PERIOD:
- Start: [date from shifts]
- Days: [count]
- Total shifts: [count]

NURSE STATUS:
- [nurse_name]: Fatigue [score], [status]

KEY CONCERNS:
- [high fatigue nurses]
- [certification gaps]

READY FOR ROSTER GENERATION: YES/NO

This summary will be used by the RosterSolver.
"""


def create_context_gatherer_agent(
    model_name: str = MODEL_CONTEXT_GATHERER,
) -> LlmAgent:
    return LlmAgent(
        name="ContextGatherer",
        model=model_name,
        instruction=CONTEXT_GATHERER_INSTRUCTION,
        output_key="gathered_context",  # Stores output in session state
        tools=[
            get_available_nurses,
            get_shifts_to_fill,
            get_nurse_stats,
            get_shift_history,
            get_regulations,
        ],
    )
