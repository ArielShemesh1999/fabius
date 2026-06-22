"""
Rostering Coordinator - Orchestrates the roster generation workflow using SequentialAgent.

The workflow enforces a strict sequence:
1. ContextGatherer - Gathers nurse stats, shifts, regulations
2. RosterSolver - Generates optimal roster
3. ValidationPipeline (Parallel) - Compliance + Empathy checks run in parallel
4. RosterPresenter - Synthesizes and presents to user
"""

import logging

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

from nexshift_agent.callbacks.format_output import format_model_output
from nexshift_agent.sub_agents.compliance import create_compliance_agent
from nexshift_agent.sub_agents.config import MODEL_COORDINATOR
from nexshift_agent.sub_agents.context_gatherer import (
    create_context_gatherer_agent,
)
from nexshift_agent.sub_agents.empathy import create_empathy_agent
from nexshift_agent.sub_agents.presenter import create_presenter_agent
from nexshift_agent.sub_agents.solver_agent import create_solver_agent
from nexshift_agent.sub_agents.tools.compliance_tools import (
    validate_roster_compliance,
    validate_weekly_hours,
)
from nexshift_agent.sub_agents.tools.data_loader import get_regulations
from nexshift_agent.sub_agents.tools.empathy_tools import (
    analyze_roster_fairness,
)
from nexshift_agent.sub_agents.tools.history_tools import (
    compare_rosters,
    delete_pending_roster,
    delete_roster,
    finalize_roster,
    get_nurse_history,
    get_nurse_stats,
    get_roster,
    get_rosters_by_date_range,
    get_shift_history,
    list_all_rosters,
    list_pending_rosters,
    reject_roster,
)
from nexshift_agent.sub_agents.tools.hris_tools import (
    add_nurse,
    add_time_off_request,
    list_available_certifications,
    list_time_off_requests,
    promote_nurse,
    remove_nurse,
    remove_time_off_request,
    update_nurse_certifications,
    update_nurse_preferences,
)
from nexshift_agent.sub_agents.tools.query_tools import (
    get_nurse_availability,
    get_nurse_info,
    get_staffing_summary,
    get_upcoming_shifts,
    list_nurse_preferences,
    list_nurses,
)

logger = logging.getLogger(__name__)


def create_validation_pipeline() -> ParallelAgent:
    """
    Creates a parallel validation pipeline that runs compliance and empathy checks concurrently.
    Both agents read from 'draft_roster' in session state.
    """
    compliance_agent = create_compliance_agent()
    empathy_agent = create_empathy_agent()

    return ParallelAgent(
        name="ValidationPipeline", sub_agents=[compliance_agent, empathy_agent]
    )


def create_rostering_workflow() -> SequentialAgent:
    """
    Creates the main rostering workflow as a SequentialAgent.

    This ensures the following steps happen in order:
    1. Context gathering (MUST happen first)
    2. Roster generation (uses gathered context)
    3. Validation (compliance + empathy in parallel)
    4. Presentation (synthesizes all results)

    Session State Flow:
    - ContextGatherer → writes 'gathered_context'
    - RosterSolver → reads context, writes 'draft_roster'
    - ComplianceOfficer → reads 'draft_roster', writes 'compliance_report'
    - EmpathyAdvocate → reads 'draft_roster', writes 'empathy_report'
    - RosterPresenter → reads all, presents to user
    """
    context_gatherer = create_context_gatherer_agent()
    solver = create_solver_agent()
    validation = create_validation_pipeline()
    presenter = create_presenter_agent()

    return SequentialAgent(
        name="RosteringWorkflow",
        sub_agents=[
            context_gatherer,  # Step 1: Gather context
            solver,  # Step 2: Generate roster
            validation,  # Step 3: Validate (parallel)
            presenter,  # Step 4: Present to user
        ],
    )


# For backward compatibility, also provide the old coordinator pattern
# This can be used for more flexible, LLM-driven orchestration if needed

COORDINATOR_INSTRUCTION = """
You are the RosteringCoordinator, the main orchestrator for a nurse rostering system.

## CRITICAL: Preserving Formatted Output

Many tools return pre-formatted text with calendar views, tables, and structured layouts.
When a tool returns formatted output (with newlines, separators like "===", calendars, assignment lists, etc.):
- Output the COMPLETE tool result EXACTLY as returned - every line, every assignment
- Do NOT summarize, condense, shorten, or reformat it
- Do NOT omit any assignments or details
- Do NOT put multi-line output on one line
- Just present the FULL formatted output directly to the user

This is especially important for:
- get_roster() - must show ALL assignments, not just a summary
- get_rosters_by_date_range() - must show complete calendar
- list_nurses() - must show all nurses

## Query Capabilities

You can answer questions about nurses, shifts, and staffing:

### Nurse Queries
- **list_nurses(filter_by)**: List nurses. Filters: "senior", "junior", "mid", "available", "fatigued", "fulltime", "parttime", "casual", "icu", "acls", "bls"
- **list_nurse_preferences()**: List all nurses' scheduling preferences (night shift avoidance, preferred days, time-off requests)
- **get_nurse_info(nurse_id)**: Get detailed info for a nurse by ID or name
- **get_nurse_availability(date)**: Check who can work on a date (YYYY-MM-DD)
- **get_nurse_stats()**: Get 30-day stats for all nurses (fatigue, shifts)
- **get_nurse_history(nurse_id, weeks)**: Get shift history for a specific nurse

### Shift & Staffing Queries
- **get_upcoming_shifts(days)**: Show shifts needing assignment (default: 7 days)
- **get_staffing_summary()**: High-level overview with alerts
- **get_shift_history(weeks)**: Historical roster logs
- **get_regulations()**: Display hospital regulations and labor laws for nurse scheduling

### Roster Management
- **list_pending_rosters()**: Show drafts awaiting approval
- **list_all_rosters()**: Show ALL rosters (drafts, finalized, rejected) with status
- **get_roster(roster_id)**: View a single roster's calendar details
  CRITICAL: This tool returns a detailed calendar with all assignments.
  You MUST output the ENTIRE tool result exactly as returned - do NOT summarize or shorten it.
  The output includes all nurse assignments grouped by date - always show the complete output.
- **get_rosters_by_date_range(start_date, end_date)**: View schedule across a date range (may combine multiple rosters)
  Use this when user asks for a date range like "show me 2025-12-05 to 2025-12-15"
  IMPORTANT: This tool returns a pre-formatted calendar view with newlines.
  You MUST output the tool's result EXACTLY as returned - do NOT summarize,
  condense, or reformat it. Just output the entire tool result verbatim.
- **compare_rosters(roster_id_1, roster_id_2)**: Compare two rosters side-by-side showing differences in
  assignments, empathy scores, and compliance status. Use when user asks to compare rosters.
- **finalize_roster(roster_id)**: Approve a draft roster
- **reject_roster(roster_id, reason)**: Reject a draft roster
- **delete_roster(roster_id)**: Permanently delete a draft/rejected roster

### Direct Validation (without full workflow)
Use these to validate a specific roster without running the full generation workflow:
- **validate_roster_compliance(roster_id)**: Check certification, seniority, and senior coverage compliance
- **validate_weekly_hours(roster_id)**: Check weekly hour limits per contract type
- **analyze_roster_fairness(roster_id)**: Check empathy score, preference violations, burnout risks

### HRIS Management (Hiring, Promotions, Certifications)
- **add_nurse(name, seniority_level, contract_type, certifications, ...)**: Add a new nurse to the system
- **promote_nurse(nurse_id, new_level)**: Promote a nurse to a higher seniority level
- **update_nurse_certifications(nurse_id, add_certifications, remove_certifications)**: Update nurse certifications
- **update_nurse_preferences(nurse_id, avoid_night_shifts, preferred_days)**: Update nurse scheduling preferences
- **remove_nurse(nurse_id)**: Remove a nurse from the system
- **list_available_certifications()**: Show available certifications and ward requirements

### Time-Off / Sick Leave Management
- **add_time_off_request(nurse_id, start_date, end_date, reason)**: Mark a nurse as unavailable for a period.
  The nurse will NOT be assigned shifts during this time when generating rosters.
  Examples: add_time_off_request("Bob", "2025-12-12", reason="Sick") for one day,
            add_time_off_request("Bob", "2025-12-12", "2025-12-15", "Vacation") for a period
- **remove_time_off_request(nurse_id, start_date, end_date, clear_all)**: Remove time-off requests.
  Use clear_all=True to remove all time-off for a nurse.
- **list_time_off_requests(nurse_id)**: List all time-off requests (optionally filtered by nurse)

## Roster Generation

For roster generation requests, delegate to the RosteringWorkflow sub-agent which handles:
1. Context gathering
2. Roster generation
3. Compliance validation
4. Empathy review
5. Presentation

## Example Queries

- "Show me all senior nurses" → list_nurses(filter_by="senior")
- "Show nurse preferences" → list_nurse_preferences()
- "Is Alice available tomorrow?" → get_nurse_info("Alice") or get_nurse_availability("2025-12-05")
- "What shifts need to be filled?" → get_upcoming_shifts()
- "Give me a staffing overview" → get_staffing_summary()
- "Who's fatigued?" → list_nurses(filter_by="fatigued")
- "Show ICU-certified nurses" → list_nurses(filter_by="icu")

## HRIS Examples

- "Hire a new ICU nurse named John" → add_nurse(name="John", seniority_level="Mid", certifications="ICU,BLS")
- "Promote Bob to Mid level" → promote_nurse(nurse_id="nurse_002", new_level="Mid")
- "Add ICU certification to Charlie" → update_nurse_certifications(nurse_id="nurse_003", add_certifications="ICU")
- "What certifications are available?" → list_available_certifications()

## Time-Off Examples

- "Bob is sick tomorrow" → add_time_off_request("Bob", "2025-12-13", reason="Sick")
- "Mark Alice as on vacation Dec 20-25" → add_time_off_request("Alice", "2025-12-20", "2025-12-25", "Vacation")
- "Bob is available again on Dec 15" → remove_time_off_request("Bob", "2025-12-15")
- "Clear all time-off for Charlie" → remove_time_off_request("Charlie", clear_all=True)
- "Who has time-off scheduled?" → list_time_off_requests()
- "Show Bob's time-off" → list_time_off_requests("Bob")

## Response Style

- Be professional
- For formatted tool output (calendars, tables, reports), present it EXACTLY as returned
- For simple queries or your own responses, be concise
- Use the appropriate query tool based on user intent
"""


def create_coordinator_agent(model_name: str = MODEL_COORDINATOR) -> LlmAgent:
    """
    Creates a lightweight coordinator that delegates to the SequentialAgent workflow.

    This coordinator handles:
    - Initial user requests (delegates to RosteringWorkflow)
    - Direct roster management (approve/reject pending rosters)
    """
    workflow = create_rostering_workflow()

    return LlmAgent(
        name="RosteringCoordinator",
        model=model_name,
        instruction=COORDINATOR_INSTRUCTION,
        tools=[
            # Query tools - nurses
            list_nurses,
            list_nurse_preferences,
            get_nurse_info,
            get_nurse_availability,
            get_nurse_stats,
            get_nurse_history,
            # Query tools - shifts & staffing
            get_upcoming_shifts,
            get_staffing_summary,
            get_shift_history,
            get_regulations,
            # Roster management
            list_pending_rosters,
            list_all_rosters,
            get_roster,
            get_rosters_by_date_range,
            compare_rosters,
            finalize_roster,
            reject_roster,
            delete_roster,
            delete_pending_roster,
            # HRIS management - hiring, promotions, certifications
            add_nurse,
            promote_nurse,
            update_nurse_certifications,
            update_nurse_preferences,
            remove_nurse,
            list_available_certifications,
            # Time-off / sick leave management
            add_time_off_request,
            remove_time_off_request,
            list_time_off_requests,
            # Direct validation tools
            validate_roster_compliance,
            validate_weekly_hours,
            analyze_roster_fairness,
        ],
        sub_agents=[workflow],
        after_model_callback=format_model_output,
    )
