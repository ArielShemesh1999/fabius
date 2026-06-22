"""
History tools for roster management.

Provides tools for:
- Reading shift history and nurse stats
- Saving and finalizing rosters
- Comparing rosters
"""

import json
import os
from datetime import datetime, timedelta

from nexshift_agent.sub_agents.config import (
    DAY_SHIFT_START_HOUR,
    DISPLAY_OVERLAP_DATES,
    EVENING_SHIFT_START_HOUR,
    FATIGUE_CONSECUTIVE_DIVISOR,
    FATIGUE_DISPLAY_HIGH,
    FATIGUE_DISPLAY_MODERATE,
    FATIGUE_REST_HOURS_DIVISOR,
    FATIGUE_WEEKLY_HOURS_DIVISOR,
    FATIGUE_WEIGHT_CONSECUTIVE,
    FATIGUE_WEIGHT_PATTERN,
    FATIGUE_WEIGHT_REST_GAP,
    FATIGUE_WEIGHT_WEEKLY_HOURS,
    NIGHT_SHIFT_START_HOUR,
    WEEKEND_WEEKDAY_START,
)
from nexshift_agent.sub_agents.tools.data_loader import (
    generate_shifts,
    load_nurses,
)
from nexshift_agent.sub_agents.tools.schedule_utils import (
    _load_json as _schedule_load_json,
)
from nexshift_agent.sub_agents.tools.schedule_utils import (
    get_next_unscheduled_date,
    get_scheduled_periods,
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data")
SHIFT_HISTORY_FILE = os.path.join(DATA_DIR, "shift_history.json")
NURSE_STATS_FILE = os.path.join(DATA_DIR, "nurse_stats.json")
ROSTERS_DIR = os.path.join(DATA_DIR, "rosters")


# =============================================================================
# Internal Helper Functions
# =============================================================================


def _load_json(filepath: str) -> dict:
    """Load JSON file, return empty dict if not found."""
    return _schedule_load_json(filepath)


def _save_json(filepath: str, data: dict) -> None:
    """Save data to JSON file."""
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)


def _get_shift_type(start_time: str) -> str:
    """Determine shift type based on start time."""
    try:
        hour = int(start_time.split(":", maxsplit=1)[0])
        if hour >= NIGHT_SHIFT_START_HOUR or hour < DAY_SHIFT_START_HOUR:
            return "night"
        elif hour >= DAY_SHIFT_START_HOUR and hour < EVENING_SHIFT_START_HOUR:
            return "day"
        else:
            return "evening"
    except (ValueError, IndexError):
        return "unknown"


def _is_weekend(date_str: str) -> bool:
    """Check if date is a weekend."""
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        return date.weekday() >= WEEKEND_WEEKDAY_START  # Saturday=5, Sunday=6
    except ValueError:
        return False


def _calculate_fatigue_score(stats: dict) -> float:
    """
    Calculate fatigue score based on nurse stats.
    0.0 = Fresh, 1.0 = Burnout risk
    """
    consecutive_factor = (
        min(
            stats.get("consecutive_shifts_current", 0)
            / FATIGUE_CONSECUTIVE_DIVISOR,
            1.0,
        )
        * FATIGUE_WEIGHT_CONSECUTIVE
    )
    weekend_factor = (
        min(
            stats.get("weekend_shifts_30d", 0) / FATIGUE_WEEKLY_HOURS_DIVISOR,
            1.0,
        )
        * FATIGUE_WEIGHT_WEEKLY_HOURS
    )
    night_factor = (
        min(stats.get("night_shifts_30d", 0) / FATIGUE_REST_HOURS_DIVISOR, 1.0)
        * FATIGUE_WEIGHT_REST_GAP
    )
    preference_factor = (
        1 - stats.get("preferences_honored_rate", 1.0)
    ) * FATIGUE_WEIGHT_PATTERN

    return round(
        consecutive_factor + weekend_factor + night_factor + preference_factor,
        2,
    )


# =============================================================================
# Scheduling Period Tools
# =============================================================================


def get_scheduling_status() -> str:
    """
    Returns a summary of scheduling status including scheduled periods
    and the next available date.

    Returns:
        Formatted string with scheduling status.
    """
    periods = get_scheduled_periods()
    next_date = get_next_unscheduled_date()

    result = "SCHEDULING STATUS\n" + "=" * 50 + "\n\n"

    if not periods:
        result += "No rosters scheduled yet.\n"
    else:
        result += "SCHEDULED PERIODS:\n" + "-" * 40 + "\n"

        finalized = [p for p in periods if p["status"] == "finalized"]
        drafts = [p for p in periods if p["status"] == "draft"]

        if finalized:
            result += "\n✅ Finalized:\n"
            for p in finalized:
                result += f"   {p['start']} to {p['end']} ({p['roster_id']})\n"

        if drafts:
            result += "\n📝 Drafts (pending approval):\n"
            for p in drafts:
                result += f"   {p['start']} to {p['end']} ({p['roster_id']})\n"

    result += "\n" + "=" * 50 + "\n"
    result += f"📅 Next unscheduled date: {next_date}\n"

    return result


# =============================================================================
# Read Tools (Phase 2)
# =============================================================================


def get_shift_history(weeks: int = 12) -> str:
    """
    Retrieves historical roster logs for the specified number of weeks.

    Args:
        weeks: Number of weeks of history to retrieve (default: 12)

    Returns:
        Formatted string with roster history including dates, assignments, and scores.
    """
    history = _load_json(SHIFT_HISTORY_FILE)
    logs = history.get("logs", [])

    if not logs:
        return "No roster history found. This appears to be a fresh system."

    # Filter by date
    cutoff_date = datetime.now() - timedelta(weeks=weeks)
    recent_logs = []

    for log in logs:
        try:
            generated_at = datetime.fromisoformat(log.get("generated_at", ""))
            if generated_at >= cutoff_date:
                recent_logs.append(log)
        except ValueError:
            continue

    if not recent_logs:
        return f"No roster history found in the last {weeks} weeks."

    # Format output
    result = f"ROSTER HISTORY (Last {weeks} weeks)\n" + "=" * 50 + "\n\n"

    for log in sorted(
        recent_logs, key=lambda x: x.get("generated_at", ""), reverse=True
    ):
        roster_id = log.get("roster_id") or log.get("id", "unknown")
        period = log.get("period", {})
        status = log.get("status", "unknown")
        metadata = log.get("metadata", {})

        result += f"📋 {roster_id}\n"
        result += f"   Period: {period.get('start', '?')} to {period.get('end', '?')}\n"
        result += f"   Status: {status.upper()}\n"
        result += f"   Compliance: {metadata.get('compliance_status', 'N/A')}\n"
        result += f"   Empathy Score: {metadata.get('empathy_score', 'N/A')}\n"
        result += f"   Assignments: {len(log.get('assignments', []))} shifts\n"

        if metadata.get("feedback"):
            result += f"   Feedback: {'; '.join(metadata['feedback'])}\n"

        result += "\n"

    result += f"Total rosters: {len(recent_logs)}\n"
    return result


def get_nurse_stats() -> str:
    """
    Retrieves cumulative statistics for all nurses.

    Returns:
        Formatted string with nurse stats including shift counts, fatigue scores,
        and preference satisfaction rates.
    """
    stats = _load_json(NURSE_STATS_FILE)

    if not stats or all(k.startswith("_") for k in stats.keys()):
        return "No nurse statistics found."

    result = "NURSE STATISTICS (30-day rolling)\n" + "=" * 50 + "\n\n"

    for nurse_id, nurse_stats in stats.items():
        if nurse_id.startswith("_"):  # Skip metadata
            continue

        name = nurse_stats.get("nurse_name", nurse_id)
        fatigue = nurse_stats.get("fatigue_score", 0)

        # Fatigue indicator
        if fatigue >= FATIGUE_DISPLAY_HIGH:
            fatigue_indicator = "🔴 HIGH RISK"
        elif fatigue >= FATIGUE_DISPLAY_MODERATE:
            fatigue_indicator = "🟡 Moderate"
        else:
            fatigue_indicator = "🟢 Good"

        result += f"📋 {name} ({nurse_id})\n"
        result += (
            f"   Total Shifts (30d): {nurse_stats.get('total_shifts_30d', 0)}\n"
        )
        result += (
            f"   Weekend Shifts: {nurse_stats.get('weekend_shifts_30d', 0)}\n"
        )
        result += f"   Night Shifts: {nurse_stats.get('night_shifts_30d', 0)}\n"
        result += f"   Consecutive Shifts: {nurse_stats.get('consecutive_shifts_current', 0)}\n"
        result += (
            f"   Last Shift: {nurse_stats.get('last_shift_date', 'N/A')}\n"
        )
        result += f"   Preferences Honored: {nurse_stats.get('preferences_honored_rate', 0) * 100:.0f}%\n"
        result += f"   Fatigue Score: {fatigue:.2f} {fatigue_indicator}\n"
        result += "\n"

    return result


def get_nurse_stats_json() -> str:
    """
    Retrieves nurse statistics as JSON for use with the solver.

    Returns:
        JSON string containing nurse stats keyed by nurse_id.
        Includes fatigue_score, shift counts, and other stats needed for
        fatigue-aware scheduling.
    """
    stats = _load_json(NURSE_STATS_FILE)

    # Filter out metadata keys
    nurse_only_stats = {k: v for k, v in stats.items() if not k.startswith("_")}

    return json.dumps(nurse_only_stats)


def get_roster_by_id(roster_id: str) -> str:
    """
    Retrieves a specific roster by its ID with full calendar view.

    Args:
        roster_id: The unique identifier for the roster (e.g., "roster_2025_week_48")

    Returns:
        Formatted string with full roster details including all assignments in calendar view.
    """
    # First check individual roster files
    roster_file = os.path.join(ROSTERS_DIR, f"{roster_id}.json")

    if os.path.exists(roster_file):
        roster = _load_json(roster_file)
    else:
        # Check in history logs
        history = _load_json(SHIFT_HISTORY_FILE)
        roster = None
        for log in history.get("logs", []):
            if log.get("roster_id") == roster_id or log.get("id") == roster_id:
                roster = log
                break

    if not roster:
        return f"Roster '{roster_id}' not found."

    nurses = {n.id: n for n in load_nurses()}

    # Determine start date for shift generation
    metadata = roster.get("metadata", {})
    period = roster.get("period", {})
    start_dt = None
    num_days = 7

    if period.get("start"):
        try:
            start_dt = datetime.strptime(period["start"], "%Y-%m-%d")
            if period.get("end"):
                end_dt = datetime.strptime(period["end"], "%Y-%m-%d")
                num_days = (end_dt - start_dt).days + 1
        except ValueError:
            pass

    # If no period, infer from generated_at date
    if not start_dt:
        generated_at = roster.get("generated_at") or metadata.get(
            "generated_at"
        )
        if generated_at:
            try:
                if "T" in str(generated_at):
                    start_dt = datetime.fromisoformat(
                        str(generated_at).split("T")[0]
                    )
                else:
                    start_dt = datetime.strptime(
                        str(generated_at).split(" ")[0], "%Y-%m-%d"
                    )
            except ValueError:
                pass

    if not start_dt:
        start_dt = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    # Generate shifts and build lookup map
    shifts = generate_shifts(start_date=start_dt, num_days=num_days)
    shifts_map = {s["id"]: s for s in shifts}

    # Calculate period
    end_dt = start_dt + timedelta(days=num_days - 1)

    # Format header
    result = f"ROSTER DETAILS: {roster_id}\n" + "=" * 60 + "\n\n"
    result += f"Period: {start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}\n"
    result += f"Status: {roster.get('status', 'unknown').upper()}\n"
    result += f"Generated: {roster.get('generated_at', 'N/A')}\n"

    if roster.get("finalized_at"):
        result += f"Finalized: {roster.get('finalized_at')}\n"
    if roster.get("rejected_at"):
        result += f"Rejected: {roster.get('rejected_at')}\n"
        result += f"Reason: {roster.get('rejection_reason', 'N/A')}\n"

    result += f"\nCompliance: {metadata.get('compliance_status', 'N/A')}\n"
    result += f"Empathy Score: {metadata.get('empathy_score', 'N/A')}\n"

    assignments = roster.get("assignments", [])
    result += f"Total Assignments: {len(assignments)}\n"

    if not assignments:
        result += "\nNo assignments found.\n"
        return result

    # Group assignments by date
    assignments_by_date = {}
    for a in assignments:
        shift_id = a.get("shift_id", "")
        nurse_id = a.get("nurse_id", "")
        shift_info = shifts_map.get(shift_id, {})
        date = shift_info.get("date", "Unknown")

        if date not in assignments_by_date:
            assignments_by_date[date] = []

        nurse = nurses.get(nurse_id)
        assignments_by_date[date].append(
            {
                "nurse_id": nurse_id,
                "nurse_name": nurse.name if nurse else nurse_id,
                "seniority": nurse.seniority_level if nurse else "?",
                "shift_id": shift_id,
                "ward": shift_info.get("ward", "?"),
                "start": shift_info.get("start", "?"),
                "end": shift_info.get("end", "?"),
                "day": shift_info.get("day", ""),
            }
        )

    # Calendar view output
    result += "\n" + "=" * 60 + "\n"
    result += "CALENDAR VIEW\n"
    result += "=" * 60 + "\n"

    for date in sorted(assignments_by_date.keys()):
        day_assignments = assignments_by_date[date]
        day_name = day_assignments[0].get("day", "") if day_assignments else ""
        is_weekend = day_name in ["Saturday", "Sunday"]
        weekend_marker = " [WEEKEND]" if is_weekend else ""

        result += f"\n📅 {date} ({day_name}){weekend_marker}\n"
        result += "-" * 50 + "\n"

        # Sort by start time
        for a in sorted(day_assignments, key=lambda x: x.get("start", "")):
            time_range = f"{a['start']}-{a['end']}"
            seniority_badge = {"Senior": "🔵", "Mid": "🟢", "Junior": "🟡"}.get(
                a["seniority"], "⚪"
            )
            result += f"  {time_range:14} | {a['ward']:10} | {seniority_badge} {a['nurse_name']:10} ({a['nurse_id']})\n"

    # Summary by nurse
    result += "\n" + "=" * 60 + "\n"
    result += "SUMMARY BY NURSE\n"
    result += "=" * 60 + "\n"

    nurse_summary = {}
    for _date, day_assignments in assignments_by_date.items():
        for a in day_assignments:
            nid = a["nurse_id"]
            if nid not in nurse_summary:
                nurse_summary[nid] = {
                    "name": a["nurse_name"],
                    "seniority": a["seniority"],
                    "shifts": 0,
                    "wards": set(),
                    "weekends": 0,
                    "nights": 0,
                }
            nurse_summary[nid]["shifts"] += 1
            nurse_summary[nid]["wards"].add(a["ward"])
            if a["day"] in ["Saturday", "Sunday"]:
                nurse_summary[nid]["weekends"] += 1
            if a["start"] >= "20:00" or a["start"] < "06:00":
                nurse_summary[nid]["nights"] += 1

    result += f"\n{'Nurse':<15} {'Level':<8} {'Shifts':>6} {'Wknd':>5} {'Night':>5} {'Wards'}\n"
    result += "-" * 60 + "\n"

    for nid in sorted(nurse_summary.keys()):
        s = nurse_summary[nid]
        wards = ", ".join(sorted(s["wards"]))
        result += f"{s['name']:<15} {s['seniority']:<8} {s['shifts']:>6} {s['weekends']:>5} {s['nights']:>5} {wards}\n"

    # Check for unassigned nurses
    assigned_nurses = set(nurse_summary.keys())
    all_nurses = set(nurses.keys())
    unassigned = all_nurses - assigned_nurses
    if unassigned:
        result += f"\n⚠️  Unassigned nurses: {', '.join(sorted(unassigned))}\n"

    return result


def get_nurse_history(nurse_id: str, weeks: int = 12) -> str:
    """
    Retrieves shift history for a specific nurse.

    Args:
        nurse_id: The nurse's ID (e.g., "nurse_001")
        weeks: Number of weeks of history to retrieve (default: 12)

    Returns:
        Formatted string with the nurse's shift history and patterns.
    """
    history = _load_json(SHIFT_HISTORY_FILE)
    stats = _load_json(NURSE_STATS_FILE)

    nurse_stats = stats.get(nurse_id, {})
    nurse_name = nurse_stats.get("nurse_name", nurse_id)

    result = f"SHIFT HISTORY: {nurse_name} ({nurse_id})\n" + "=" * 50 + "\n\n"

    # Current stats
    result += "CURRENT STATS:\n"
    result += (
        f"   Total Shifts (30d): {nurse_stats.get('total_shifts_30d', 0)}\n"
    )
    result += f"   Weekend Shifts: {nurse_stats.get('weekend_shifts_30d', 0)}\n"
    result += f"   Night Shifts: {nurse_stats.get('night_shifts_30d', 0)}\n"
    result += f"   Fatigue Score: {nurse_stats.get('fatigue_score', 0):.2f}\n"
    result += "\n"

    # Historical shifts
    cutoff_date = datetime.now() - timedelta(weeks=weeks)
    nurse_shifts = []

    for log in history.get("logs", []):
        try:
            generated_at = datetime.fromisoformat(log.get("generated_at", ""))
            if generated_at < cutoff_date:
                continue
        except ValueError:
            continue

        for assignment in log.get("assignments", []):
            if assignment.get("nurse_id") == nurse_id:
                nurse_shifts.append(
                    {
                        "roster_id": log.get("roster_id"),
                        "date": assignment.get("date"),
                        "ward": assignment.get("ward"),
                        "shift_type": assignment.get("shift_type"),
                    }
                )

    if nurse_shifts:
        result += f"RECENT SHIFTS (Last {weeks} weeks):\n" + "-" * 40 + "\n"
        # Sort by date, handling None values
        for shift in sorted(
            nurse_shifts, key=lambda x: x.get("date") or "", reverse=True
        ):
            date_str = shift.get("date") or "?"
            weekend = "🅆" if date_str != "?" and _is_weekend(date_str) else " "
            result += f"   {date_str} {weekend} {shift.get('ward') or '?'} ({shift.get('shift_type') or '?'})\n"
        result += f"\nTotal shifts in period: {len(nurse_shifts)}\n"
    else:
        result += f"No shift history found for {nurse_name} in the last {weeks} weeks.\n"

    return result


def get_roster(roster_id: str) -> str:
    """
    Retrieves a roster by ID and returns it in a formatted view.

    Args:
        roster_id: The ID of the roster to retrieve

    Returns:
        Formatted string with roster details including assignments grouped by date.
    """
    roster_file = os.path.join(ROSTERS_DIR, f"{roster_id}.json")

    if not os.path.exists(roster_file):
        return f"Error: Roster '{roster_id}' not found."

    roster = _load_json(roster_file)

    # Build formatted output
    status = roster.get("status", "unknown").upper()
    period = roster.get("period", {})
    metadata = roster.get("metadata", {})
    assignments = roster.get("assignments", [])

    if not assignments:
        result = f"ROSTER: {roster_id}\n" + "=" * 50 + "\n\n"
        result += f"Status: {status}\n"
        result += f"Compliance: {metadata.get('compliance_status', 'N/A')}\n"
        result += f"Empathy Score: {metadata.get('empathy_score', 'N/A')}\n"
        result += "No assignments in this roster.\n"
        return result

    nurses = {n.id: n.name for n in load_nurses()}

    shifts_map = {}

    # Try to determine the start date for shift generation
    start_dt = None
    num_days = 7  # default

    if period.get("start"):
        try:
            start_dt = datetime.strptime(period["start"], "%Y-%m-%d")
            if period.get("end"):
                end_dt = datetime.strptime(period["end"], "%Y-%m-%d")
                num_days = (end_dt - start_dt).days + 1
        except ValueError:
            pass

    # If no period, try to infer from generated_at date
    if not start_dt:
        generated_at = roster.get("generated_at") or metadata.get(
            "generated_at"
        )
        if generated_at:
            try:
                # Handle both ISO format and space-separated format
                if "T" in str(generated_at):
                    start_dt = datetime.fromisoformat(
                        str(generated_at).split("T")[0]
                    )
                else:
                    start_dt = datetime.strptime(
                        str(generated_at).split(" ")[0], "%Y-%m-%d"
                    )
            except ValueError:
                pass

    # Fallback to today
    if not start_dt:
        start_dt = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    # Generate shifts and build map
    shifts = generate_shifts(start_date=start_dt, num_days=num_days)
    for s in shifts:
        shifts_map[s["id"]] = s

    # Calculate actual period from shifts
    end_dt = start_dt + timedelta(days=num_days - 1)
    result = f"ROSTER: {roster_id}\n" + "=" * 50 + "\n\n"
    result += f"Status: {status}\n"
    result += f"Period: {start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}\n"
    result += f"Compliance: {metadata.get('compliance_status', 'N/A')}\n"
    result += f"Empathy Score: {metadata.get('empathy_score', 'N/A')}\n"
    result += f"Total Assignments: {len(assignments)}\n\n"

    # Group assignments by date
    assignments_by_date = {}
    for a in assignments:
        shift_id = a.get("shift_id", "")
        nurse_id = a.get("nurse_id", "")

        shift_info = shifts_map.get(shift_id, {})
        date = shift_info.get("date", "Unknown")

        if date not in assignments_by_date:
            assignments_by_date[date] = []

        assignments_by_date[date].append(
            {
                "nurse_id": nurse_id,
                "nurse_name": nurses.get(nurse_id, nurse_id),
                "shift_id": shift_id,
                "ward": shift_info.get("ward", "?"),
                "time": f"{shift_info.get('start', '?')}-{shift_info.get('end', '?')}",
                "day": shift_info.get("day", ""),
            }
        )

    # Format output grouped by date
    result += "ASSIGNMENTS:\n" + "-" * 40 + "\n"
    for date in sorted(assignments_by_date.keys()):
        day_assignments = assignments_by_date[date]
        day_name = day_assignments[0].get("day", "") if day_assignments else ""
        result += f"\n📅 {date} ({day_name})\n"

        for a in sorted(day_assignments, key=lambda x: x.get("time", "")):
            result += f"   {a['time']} | {a['ward']:10} | {a['nurse_name']} ({a['nurse_id']})\n"

    return result


def get_rosters_by_date_range(start_date: str, end_date: str) -> str:
    """
    Retrieves all rosters within a date range and displays each roster separately.

    This tool finds all rosters that overlap with the requested period and
    displays each one with its own calendar view.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Each roster displayed separately with its own calendar view.
    """
    # Parse dates
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError as e:
        return f"Error: Invalid date format. Use YYYY-MM-DD. Details: {e}"

    if end_dt < start_dt:
        return "Error: end_date must be after start_date."

    # Find all rosters that overlap with the date range
    all_matching = []
    if os.path.exists(ROSTERS_DIR):
        for filename in os.listdir(ROSTERS_DIR):
            if filename.endswith(".json") and not filename.startswith("."):
                roster_path = os.path.join(ROSTERS_DIR, filename)
                roster = _load_json(roster_path)

                period = roster.get("period", {})
                roster_start = period.get("start")
                roster_end = period.get("end")

                if not roster_start or not roster_end:
                    continue

                try:
                    r_start = datetime.strptime(roster_start, "%Y-%m-%d")
                    r_end = datetime.strptime(roster_end, "%Y-%m-%d")
                except ValueError:
                    continue

                # Check if roster overlaps with requested range
                if r_start <= end_dt and r_end >= start_dt:
                    roster_id = roster.get("id") or filename.replace(
                        ".json", ""
                    )
                    all_matching.append(
                        {
                            "roster_id": roster_id,
                            "status": roster.get("status", "unknown"),
                            "period_start": roster_start,
                            "period_end": roster_end,
                            "generated_at": roster.get("generated_at", ""),
                        }
                    )

    # Filter: prefer finalized rosters, fall back to most recent draft per period
    matching_rosters = []
    periods_covered = set()

    # Sort by generated_at descending to get most recent first
    sorted_rosters = sorted(
        all_matching, key=lambda x: x["generated_at"], reverse=True
    )

    # First, add most recent finalized roster per period
    for r in sorted_rosters:
        if r["status"] == "finalized":
            period_key = (r["period_start"], r["period_end"])
            if period_key not in periods_covered:
                matching_rosters.append(r)
                periods_covered.add(period_key)

    # If no finalized rosters for a period, use most recent draft
    for r in sorted_rosters:
        if r["status"] == "draft":
            period_key = (r["period_start"], r["period_end"])
            if period_key not in periods_covered:
                matching_rosters.append(r)
                periods_covered.add(period_key)

    if not matching_rosters:
        return (
            f"No rosters found covering the period {start_date} to {end_date}."
        )

    # Sort rosters by period start
    matching_rosters.sort(key=lambda x: x["period_start"])

    # Build output - display each roster separately
    num_days = (end_dt - start_dt).days + 1
    result = "ROSTERS\n" + "=" * 60 + "\n\n"
    result += f"Period: {start_date} to {end_date} ({num_days} days)\n"
    result += f"Found {len(matching_rosters)} roster(s)\n\n"

    nurses = {n.id: n for n in load_nurses()}

    # Display each roster with calendar table
    for r in matching_rosters:
        roster_id = r["roster_id"]
        status = r["status"].upper()
        period_start = r["period_start"]
        period_end = r["period_end"]

        # Section header with roster ID
        result += f"{'─' * 60}\n"
        result += f"📋 {roster_id}\n"
        result += (
            f"   Status: {status} | Period: {period_start} to {period_end}\n"
        )
        result += f"{'─' * 60}\n\n"

        # Load roster data
        roster_file = os.path.join(ROSTERS_DIR, f"{roster_id}.json")
        if not os.path.exists(roster_file):
            result += "Roster file not found.\n\n"
            continue

        roster = _load_json(roster_file)
        assignments = roster.get("assignments", [])

        if not assignments:
            result += "No assignments in this roster.\n\n"
            continue

        # Generate shifts for this roster's period
        try:
            r_start = datetime.strptime(period_start, "%Y-%m-%d")
            r_end = datetime.strptime(period_end, "%Y-%m-%d")
            r_days = (r_end - r_start).days + 1
        except ValueError:
            result += "Invalid period dates.\n\n"
            continue

        shifts = generate_shifts(start_date=r_start, num_days=r_days)
        shifts_map = {s["id"]: s for s in shifts}

        # Build nurse schedule: {nurse_id: {date: ward-shift_type}}
        nurse_schedule = {}
        for a in assignments:
            nurse_id = a.get("nurse_id")
            shift_id = a.get("shift_id")
            shift_info = shifts_map.get(shift_id, {})

            if not shift_info:
                continue

            date = shift_info.get("date", "")
            ward = shift_info.get("ward", "?")[:3]
            start_time = shift_info.get("start", "")

            # Determine shift type
            try:
                hour = int(start_time.split(":")[0])
                if (
                    hour >= NIGHT_SHIFT_START_HOUR
                    or hour < DAY_SHIFT_START_HOUR
                ):
                    shift_type = "N"
                elif hour >= EVENING_SHIFT_START_HOUR:
                    shift_type = "E"
                else:
                    shift_type = "D"
            except (ValueError, IndexError):
                shift_type = "?"

            if nurse_id not in nurse_schedule:
                nurse_schedule[nurse_id] = {}

            cell_val = f"{ward}-{shift_type}"
            if date in nurse_schedule[nurse_id]:
                nurse_schedule[nurse_id][date] += " " + cell_val
            else:
                nurse_schedule[nurse_id][date] = cell_val

        # Build calendar table
        dates_in_roster = []
        for i in range(r_days):
            d = r_start + timedelta(days=i)
            dates_in_roster.append(d.strftime("%Y-%m-%d"))

        # Header row
        headers = ["Nurse"]
        for date_str in dates_in_roster:
            d = datetime.strptime(date_str, "%Y-%m-%d")
            day_abbr = d.strftime("%a")
            day_num = d.strftime("%d")
            headers.append(f"{day_abbr} {day_num}")
        headers.append("Total")

        result += "| " + " | ".join(headers) + " |\n"
        result += "|" + "|".join(["---"] * len(headers)) + "|\n"

        # Data rows
        for nurse_id in sorted(nurse_schedule.keys()):
            nurse = nurses.get(nurse_id)
            name = nurse.name if nurse else nurse_id
            row = [name]
            nurse_total = 0

            for date_str in dates_in_roster:
                cell = nurse_schedule.get(nurse_id, {}).get(date_str, "-")
                row.append(cell)
                if cell != "-":
                    nurse_total += len(cell.split(" "))

            row.append(str(nurse_total))
            result += "| " + " | ".join(row) + " |\n"

        result += "\n"

    result += "**Legend**: D=Day | E=Evening | N=Night | Ward abbreviations (ICU, Gen, Eme, etc.)\n"

    return result


# =============================================================================
# Write Tools (Phase 3)
# =============================================================================


def save_draft_roster(roster_json: str) -> str:
    """
    Saves a roster as a draft awaiting approval.

    Args:
        roster_json: JSON string containing the roster data with assignments

    Returns:
        Confirmation message with the roster ID.
    """
    try:
        roster = json.loads(roster_json)
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON - {e}"

    # Generate roster ID if not provided
    roster_id = roster.get("id")
    if not roster_id:
        week_num = datetime.now().isocalendar()[1]
        roster_id = f"roster_{datetime.now().year}_week_{week_num:02d}"
        roster["id"] = roster_id

    # Check if roster already exists (idempotent - prevent duplicate saves)
    roster_file = os.path.join(ROSTERS_DIR, f"{roster_id}.json")
    if os.path.exists(roster_file):
        existing = _load_json(roster_file)
        if existing.get("status") == "draft":
            assignment_count = len(existing.get("assignments", []))
            return f"✅ Draft roster already saved: {roster_id}\n   Assignments: {assignment_count}\n   Status: DRAFT (awaiting approval)\n   Use finalize_roster('{roster_id}') to approve."

    # Set metadata
    roster["status"] = "draft"
    roster["generated_at"] = datetime.now().isoformat()

    # Calculate period from shift_ids by looking up shift dates
    if "period" not in roster or not roster.get("period", {}).get("start"):
        # Infer start date from generated_at or roster metadata
        generated_at = roster.get("generated_at") or roster.get(
            "metadata", {}
        ).get("generated_at")
        start_dt = None
        if generated_at:
            try:
                if "T" in str(generated_at):
                    start_dt = datetime.fromisoformat(
                        str(generated_at).split("T")[0]
                    )
                else:
                    start_dt = datetime.strptime(
                        str(generated_at).split(" ")[0], "%Y-%m-%d"
                    )
            except ValueError:
                pass

        if not start_dt:
            start_dt = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )

        # Generate shifts to get the date mapping
        shifts = generate_shifts(start_date=start_dt, num_days=7)
        shift_dates = {s["id"]: s["date"] for s in shifts}

        # Extract dates from assignments using shift lookup
        dates = []
        for a in roster.get("assignments", []):
            shift_id = a.get("shift_id")
            if shift_id and shift_id in shift_dates:
                dates.append(shift_dates[shift_id])

        if dates:
            roster["period"] = {"start": min(dates), "end": max(dates)}

    # Save to rosters directory
    roster_file = os.path.join(ROSTERS_DIR, f"{roster_id}.json")
    _save_json(roster_file, roster)

    # Add to history log
    history = _load_json(SHIFT_HISTORY_FILE)
    if "logs" not in history:
        history["logs"] = []

    # Create history entry with roster_id field
    history_entry = roster.copy()
    history_entry["roster_id"] = roster_id

    # Remove existing draft with same ID
    history["logs"] = [
        entry
        for entry in history["logs"]
        if entry.get("roster_id") != roster_id
    ]
    history["logs"].append(history_entry)
    _save_json(SHIFT_HISTORY_FILE, history)

    assignment_count = len(roster.get("assignments", []))
    return f"✅ Draft roster saved: {roster_id}\n   Assignments: {assignment_count}\n   Status: DRAFT (awaiting approval)\n   Use finalize_roster('{roster_id}') to approve."


def _get_assignment_dates(roster: dict, rosters_dir: str) -> set:
    """
    Get all dates covered by assignments in a roster.
    Uses shift_id to look up dates from generated shifts.
    """
    period = roster.get("period", {})
    if not period.get("start"):
        return set()

    try:
        start_dt = datetime.strptime(period["start"], "%Y-%m-%d")
        end_dt = datetime.strptime(
            period.get("end", period["start"]), "%Y-%m-%d"
        )
        num_days = (end_dt - start_dt).days + 1
    except ValueError:
        return set()

    shifts = generate_shifts(start_date=start_dt, num_days=num_days)
    shifts_map = {s["id"]: s["date"] for s in shifts}

    dates = set()
    for a in roster.get("assignments", []):
        shift_id = a.get("shift_id")
        if shift_id and shift_id in shifts_map:
            dates.add(shifts_map[shift_id])

    return dates


def _remove_assignments_for_dates(roster: dict, dates_to_remove: set) -> list:
    """
    Remove assignments for specific dates from a roster.
    Returns the removed assignments.
    """
    period = roster.get("period", {})
    if not period.get("start"):
        return []

    try:
        start_dt = datetime.strptime(period["start"], "%Y-%m-%d")
        end_dt = datetime.strptime(
            period.get("end", period["start"]), "%Y-%m-%d"
        )
        num_days = (end_dt - start_dt).days + 1
    except ValueError:
        return []

    shifts = generate_shifts(start_date=start_dt, num_days=num_days)
    shifts_map = {s["id"]: s for s in shifts}

    removed = []
    kept = []

    for a in roster.get("assignments", []):
        shift_id = a.get("shift_id")
        shift_info = shifts_map.get(shift_id, {})
        shift_date = shift_info.get("date", "")

        if shift_date in dates_to_remove:
            # Add shift info to removed assignment for stats reversal
            a["date"] = shift_date
            a["shift_type"] = (
                "night"
                if shift_info.get("start", "").startswith(
                    ("20", "21", "22", "23", "00", "01", "02", "03", "04", "05")
                )
                else "day"
            )
            removed.append(a)
        else:
            kept.append(a)

    roster["assignments"] = kept
    return removed


def _reverse_nurse_stats(assignments: list, stats: dict) -> None:
    """
    Reverse nurse stats for removed assignments.
    Subtracts shift counts that were previously added.
    """
    for a in assignments:
        nurse_id = a.get("nurse_id")
        if not nurse_id or nurse_id not in stats:
            continue

        nurse_stats = stats[nurse_id]
        date = a.get("date", "")
        shift_type = a.get("shift_type", "")

        # Subtract counts (don't go below 0)
        nurse_stats["total_shifts_30d"] = max(
            0, nurse_stats.get("total_shifts_30d", 0) - 1
        )

        if _is_weekend(date):
            nurse_stats["weekend_shifts_30d"] = max(
                0, nurse_stats.get("weekend_shifts_30d", 0) - 1
            )

        if shift_type == "night":
            nurse_stats["night_shifts_30d"] = max(
                0, nurse_stats.get("night_shifts_30d", 0) - 1
            )

        # Recalculate fatigue
        nurse_stats["fatigue_score"] = _calculate_fatigue_score(nurse_stats)
        nurse_stats["updated_at"] = datetime.now().isoformat()


def finalize_roster(roster_id: str) -> str:
    """
    Finalizes a draft roster, updating nurse statistics.

    Handles overlapping rosters:
    - If overlap includes past/today dates: Block finalization
    - If overlap is only future dates: Overwrite those dates in existing roster

    Args:
        roster_id: The ID of the draft roster to finalize

    Returns:
        Confirmation message with updated nurse stats.
    """
    # Load roster
    roster_file = os.path.join(ROSTERS_DIR, f"{roster_id}.json")

    if os.path.exists(roster_file):
        roster = _load_json(roster_file)
    else:
        return f"Error: Roster '{roster_id}' not found."

    if roster.get("status") == "finalized":
        return f"Roster '{roster_id}' is already finalized."

    if roster.get("status") == "rejected":
        return f"Cannot finalize rejected roster '{roster_id}'."

    # Get the new roster's period
    new_period = roster.get("period", {})
    overwrite_messages = []

    if new_period.get("start") and new_period.get("end"):
        try:
            new_start = datetime.strptime(new_period["start"], "%Y-%m-%d")
            new_end = datetime.strptime(new_period["end"], "%Y-%m-%d")
            today = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            # Check all finalized rosters for overlap
            finalized_periods = get_scheduled_periods()
            stats = _load_json(NURSE_STATS_FILE)

            for p in finalized_periods:
                if p["status"] != "finalized":
                    continue
                if p["roster_id"] == roster_id:
                    continue

                try:
                    p_start = datetime.strptime(p["start"], "%Y-%m-%d")
                    p_end = datetime.strptime(p["end"], "%Y-%m-%d")
                except ValueError:
                    continue

                # Check if there's overlap
                if new_end < p_start or new_start > p_end:
                    continue  # No overlap

                # Calculate overlapping dates
                overlap_start = max(new_start, p_start)
                overlap_end = min(new_end, p_end)

                # Check if overlap includes past/today dates
                past_overlap_dates = []
                future_overlap_dates = []

                current = overlap_start
                while current <= overlap_end:
                    date_str = current.strftime("%Y-%m-%d")
                    if current <= today:
                        past_overlap_dates.append(date_str)
                    else:
                        future_overlap_dates.append(date_str)
                    current += timedelta(days=1)

                # Block if overlap includes past/today
                if past_overlap_dates:
                    past_dates_str = ", ".join(
                        past_overlap_dates[:DISPLAY_OVERLAP_DATES]
                    )
                    if len(past_overlap_dates) > DISPLAY_OVERLAP_DATES:
                        past_dates_str += (
                            f" ... ({len(past_overlap_dates)} dates total)"
                        )
                    return (
                        f"❌ Cannot finalize roster '{roster_id}'.\n\n"
                        f"Period {new_period['start']} to {new_period['end']} overlaps with "
                        f"PAST/CURRENT shifts in finalized roster '{p['roster_id']}':\n"
                        f"   Overlapping dates: {past_dates_str}\n\n"
                        f"These shifts have already occurred and cannot be overwritten."
                    )

                # Overwrite future dates
                if future_overlap_dates:
                    # Load the existing roster
                    existing_file = os.path.join(
                        ROSTERS_DIR, f"{p['roster_id']}.json"
                    )
                    if not os.path.exists(existing_file):
                        continue

                    existing_roster = _load_json(existing_file)

                    # Remove assignments for future overlap dates
                    removed = _remove_assignments_for_dates(
                        existing_roster, set(future_overlap_dates)
                    )

                    if removed:
                        # Reverse nurse stats for removed assignments
                        _reverse_nurse_stats(removed, stats)

                        # Update the existing roster's period
                        remaining_dates = _get_assignment_dates(
                            existing_roster, ROSTERS_DIR
                        )

                        if not remaining_dates:
                            # No assignments left - delete the roster
                            os.remove(existing_file)
                            # Remove from history
                            history = _load_json(SHIFT_HISTORY_FILE)
                            history["logs"] = [
                                entry
                                for entry in history.get("logs", [])
                                if entry.get("roster_id") != p["roster_id"]
                                and entry.get("id") != p["roster_id"]
                            ]
                            _save_json(SHIFT_HISTORY_FILE, history)
                            overwrite_messages.append(
                                f"   - Deleted '{p['roster_id']}' (all shifts overwritten)"
                            )
                        else:
                            # Update period to remaining dates
                            existing_roster["period"] = {
                                "start": min(remaining_dates),
                                "end": max(remaining_dates),
                            }
                            existing_roster["trimmed_at"] = (
                                datetime.now().isoformat()
                            )
                            existing_roster["trimmed_reason"] = (
                                f"Future shifts overwritten by {roster_id}"
                            )
                            _save_json(existing_file, existing_roster)

                            # Update history
                            history = _load_json(SHIFT_HISTORY_FILE)
                            for log in history.get("logs", []):
                                if (
                                    log.get("roster_id") == p["roster_id"]
                                    or log.get("id") == p["roster_id"]
                                ):
                                    log["period"] = existing_roster["period"]
                                    break
                            _save_json(SHIFT_HISTORY_FILE, history)

                            overwrite_messages.append(
                                f"   - Trimmed '{p['roster_id']}' to {existing_roster['period']['start']} - {existing_roster['period']['end']} "
                                f"({len(removed)} shifts removed)"
                            )

            # Save updated stats if any overwrites occurred
            if overwrite_messages:
                _save_json(NURSE_STATS_FILE, stats)

        except ValueError:
            pass  # If dates can't be parsed, skip overlap check

    # Update roster status
    roster["status"] = "finalized"
    roster["finalized_at"] = datetime.now().isoformat()
    _save_json(roster_file, roster)

    # Update nurse stats
    stats = _load_json(NURSE_STATS_FILE)
    updated_nurses = []

    for assignment in roster.get("assignments", []):
        nurse_id = assignment.get("nurse_id")
        if not nurse_id or nurse_id not in stats:
            continue

        nurse_stats = stats[nurse_id]
        date = assignment.get("date", "")
        shift_type = assignment.get("shift_type", "")

        # Update counts
        nurse_stats["total_shifts_30d"] = (
            nurse_stats.get("total_shifts_30d", 0) + 1
        )

        if _is_weekend(date):
            nurse_stats["weekend_shifts_30d"] = (
                nurse_stats.get("weekend_shifts_30d", 0) + 1
            )

        if shift_type == "night":
            nurse_stats["night_shifts_30d"] = (
                nurse_stats.get("night_shifts_30d", 0) + 1
            )

        # Update consecutive shifts
        last_date = nurse_stats.get("last_shift_date", "")
        if last_date:
            try:
                last = datetime.strptime(last_date, "%Y-%m-%d")
                current = datetime.strptime(date, "%Y-%m-%d")
                if (current - last).days == 1:
                    nurse_stats["consecutive_shifts_current"] = (
                        nurse_stats.get("consecutive_shifts_current", 0) + 1
                    )
                else:
                    nurse_stats["consecutive_shifts_current"] = 1
            except ValueError:
                pass

        nurse_stats["last_shift_date"] = date
        nurse_stats["updated_at"] = datetime.now().isoformat()

        # Recalculate fatigue
        nurse_stats["fatigue_score"] = _calculate_fatigue_score(nurse_stats)

        updated_nurses.append(nurse_stats.get("nurse_name", nurse_id))

    _save_json(NURSE_STATS_FILE, stats)

    # Update history log
    history = _load_json(SHIFT_HISTORY_FILE)
    for log in history.get("logs", []):
        if log.get("roster_id") == roster_id:
            log["status"] = "finalized"
            log["finalized_at"] = roster["finalized_at"]
            break
    _save_json(SHIFT_HISTORY_FILE, history)

    result = f"✅ Roster '{roster_id}' has been FINALIZED.\n\n"

    # Show overwrite info if any
    if overwrite_messages:
        result += "⚠️  Overlapping rosters updated:\n"
        for msg in overwrite_messages:
            result += f"{msg}\n"
        result += "\n"

    result += f"Updated stats for {len(updated_nurses)} nurses:\n"
    for name in updated_nurses:
        result += f"   - {name}\n"

    # Append the full roster view
    result += "\n" + "=" * 50 + "\n"
    result += get_roster(roster_id)

    return result


def reject_roster(roster_id: str, reason: str = "") -> str:
    """
    Rejects a draft roster with an optional reason.

    Args:
        roster_id: The ID of the draft roster to reject
        reason: Optional reason for rejection

    Returns:
        Confirmation message.
    """
    roster_file = os.path.join(ROSTERS_DIR, f"{roster_id}.json")

    if os.path.exists(roster_file):
        roster = _load_json(roster_file)
    else:
        return f"Error: Roster '{roster_id}' not found."

    if roster.get("status") == "finalized":
        return f"Cannot reject finalized roster '{roster_id}'."

    # Update roster status
    roster["status"] = "rejected"
    roster["rejected_at"] = datetime.now().isoformat()
    roster["rejection_reason"] = reason or "No reason provided"
    _save_json(roster_file, roster)

    # Update history log
    history = _load_json(SHIFT_HISTORY_FILE)
    for log in history.get("logs", []):
        if log.get("roster_id") == roster_id:
            log["status"] = "rejected"
            log["rejected_at"] = roster["rejected_at"]
            log["rejection_reason"] = roster["rejection_reason"]
            break
    _save_json(SHIFT_HISTORY_FILE, history)

    return f"❌ Roster '{roster_id}' has been REJECTED.\n   Reason: {roster['rejection_reason']}"


def list_pending_rosters() -> str:
    """
    Lists all draft rosters awaiting approval.

    Scans actual roster files in the rosters directory for accuracy.

    Returns:
        Formatted string with pending rosters.
    """
    drafts = []

    # Scan actual roster files for accuracy
    if os.path.exists(ROSTERS_DIR):
        for filename in os.listdir(ROSTERS_DIR):
            if filename.endswith(".json") and not filename.startswith("."):
                roster_path = os.path.join(ROSTERS_DIR, filename)
                roster = _load_json(roster_path)
                if roster.get("status") == "draft":
                    # Handle both 'id' and 'roster_id' keys
                    roster_id = (
                        roster.get("roster_id")
                        or roster.get("id")
                        or filename.replace(".json", "")
                    )
                    drafts.append({"roster_id": roster_id, "roster": roster})

    if not drafts:
        return "No pending rosters. All rosters have been processed."

    result = "PENDING ROSTERS (Awaiting Approval)\n" + "=" * 50 + "\n\n"

    for item in sorted(
        drafts, key=lambda x: x["roster"].get("generated_at", ""), reverse=True
    ):
        roster_id = item["roster_id"]
        roster = item["roster"]
        period = roster.get("period", {})
        metadata = roster.get("metadata", {})

        result += f"📋 {roster_id}\n"
        result += f"   Period: {period.get('start', '?')} to {period.get('end', '?')}\n"
        result += f"   Generated: {roster.get('generated_at', 'N/A')}\n"
        result += f"   Assignments: {len(roster.get('assignments', []))}\n"
        result += f"   Empathy Score: {metadata.get('empathy_score', 'N/A')}\n"
        result += "\n"

    result += f"Total pending: {len(drafts)}\n"
    result += "\nUse finalize_roster('<roster_id>') to approve, reject_roster('<roster_id>') to reject, or delete_roster('<roster_id>') to remove."

    return result


def delete_roster(roster_id: str) -> str:
    """
    Deletes a roster (draft or rejected) permanently.

    Args:
        roster_id: The ID of the roster to delete

    Returns:
        Confirmation message.
    """
    roster_file = os.path.join(ROSTERS_DIR, f"{roster_id}.json")

    # Check if roster exists
    if os.path.exists(roster_file):
        roster = _load_json(roster_file)
    else:
        return f"Error: Roster '{roster_id}' not found."

    # Only allow deletion of draft or rejected rosters
    status = roster.get("status", "unknown")
    if status == "finalized":
        return f"Cannot delete finalized roster '{roster_id}'. Finalized rosters are preserved for audit."

    if status not in ["draft", "rejected"]:
        return f"Cannot delete roster '{roster_id}' with status '{status}'."

    # Delete the roster file
    try:
        os.remove(roster_file)
    except OSError as e:
        return f"Error deleting roster file: {e}"

    # Remove from history log - handle both 'id' and 'roster_id' keys
    history = _load_json(SHIFT_HISTORY_FILE)
    original_count = len(history.get("logs", []))
    history["logs"] = [
        entry
        for entry in history.get("logs", [])
        if entry.get("roster_id") != roster_id and entry.get("id") != roster_id
    ]
    removed_count = original_count - len(history["logs"])
    _save_json(SHIFT_HISTORY_FILE, history)

    return f"Deleted roster '{roster_id}' (status: {status}).\n   Removed {removed_count} history entry(ies)."


# Alias for backwards compatibility
def delete_pending_roster(roster_id: str) -> str:
    """Alias for delete_roster. Deletes a draft or rejected roster."""
    return delete_roster(roster_id)


def list_all_rosters() -> str:
    """
    Lists ALL rosters in the rosters directory with their status.

    Scans actual roster files to show complete inventory including
    draft, finalized, and rejected rosters.

    Returns:
        Formatted string with all rosters grouped by status.
    """
    rosters_by_status = {
        "draft": [],
        "finalized": [],
        "rejected": [],
        "unknown": [],
    }

    if not os.path.exists(ROSTERS_DIR):
        return "No rosters directory found."

    for filename in os.listdir(ROSTERS_DIR):
        if filename.endswith(".json") and not filename.startswith("."):
            roster_path = os.path.join(ROSTERS_DIR, filename)
            roster = _load_json(roster_path)

            # Handle both 'id' and 'roster_id' keys
            roster_id = (
                roster.get("roster_id")
                or roster.get("id")
                or filename.replace(".json", "")
            )
            status = roster.get("status", "unknown")
            period = roster.get("period", {})
            metadata = roster.get("metadata", {})

            roster_info = {
                "roster_id": roster_id,
                "period_start": period.get("start", "?"),
                "period_end": period.get("end", "?"),
                "generated_at": roster.get("generated_at", "N/A"),
                "assignments": len(roster.get("assignments", [])),
                "empathy_score": metadata.get("empathy_score", "N/A"),
            }

            if status in rosters_by_status:
                rosters_by_status[status].append(roster_info)
            else:
                rosters_by_status["unknown"].append(roster_info)

    total = sum(len(v) for v in rosters_by_status.values())

    if total == 0:
        return "No rosters found in the rosters directory."

    result = "ALL ROSTERS\n" + "=" * 60 + "\n\n"

    # Draft rosters first
    if rosters_by_status["draft"]:
        result += (
            f"📝 DRAFT ({len(rosters_by_status['draft'])} pending approval)\n"
        )
        result += "-" * 50 + "\n"
        for r in sorted(
            rosters_by_status["draft"],
            key=lambda x: x["generated_at"],
            reverse=True,
        ):
            result += f"\n• {r['roster_id']}\t"
            result += f"  Period: {r['period_start']} to {r['period_end']}\n"
            result += f"  Assignments: {r['assignments']} | Generated: {r['generated_at'][:10] if len(str(r['generated_at'])) >= 10 else r['generated_at']}\n"  # noqa: PLR2004
        result += "\n"

    # Finalized rosters
    if rosters_by_status["finalized"]:
        result += f"✅ FINALIZED ({len(rosters_by_status['finalized'])})\n"
        result += "-" * 50 + "\n"
        for r in sorted(
            rosters_by_status["finalized"],
            key=lambda x: x["generated_at"],
            reverse=True,
        ):
            result += f"\n• {r['roster_id']}\t"
            result += f"  Period: {r['period_start']} to {r['period_end']}\n"
        result += "\n"

    # Rejected rosters
    if rosters_by_status["rejected"]:
        result += f"❌ REJECTED ({len(rosters_by_status['rejected'])})\n"
        result += "-" * 50 + "\n"
        for r in sorted(
            rosters_by_status["rejected"],
            key=lambda x: x["generated_at"],
            reverse=True,
        ):
            result += f"\n• {r['roster_id']}\t"
            result += f"  Period: {r['period_start']} to {r['period_end']}\n"
        result += "\n"

    # Unknown status
    if rosters_by_status["unknown"]:
        result += f"❓ UNKNOWN STATUS ({len(rosters_by_status['unknown'])})\n"
        result += "-" * 50 + "\n"
        for r in rosters_by_status["unknown"]:
            result += f"\n• {r['roster_id']}\n"
        result += "\n"

    result += "=" * 60 + "\n"
    result += f"Total: {total} roster(s)\n"
    result += "\nActions:\n"
    result += "  - finalize_roster('<id>') to approve a draft\n"
    result += "  - reject_roster('<id>') to reject a draft\n"
    result += "  - delete_roster('<id>') to remove draft/rejected\n"
    result += "  - get_roster('<id>') to view details\n"

    return result


# =============================================================================
# Analysis Tools (Phase 4)
# =============================================================================


def compare_rosters(roster_id_1: str, roster_id_2: str) -> str:
    """
    Compares two rosters side by side.

    Args:
        roster_id_1: First roster ID
        roster_id_2: Second roster ID

    Returns:
        Formatted comparison showing differences in assignments and scores.
    """
    # Load both rosters
    roster1 = None
    roster2 = None

    for rid, roster_var in [(roster_id_1, "roster1"), (roster_id_2, "roster2")]:
        roster_file = os.path.join(ROSTERS_DIR, f"{rid}.json")
        if os.path.exists(roster_file):
            if roster_var == "roster1":
                roster1 = _load_json(roster_file)
            else:
                roster2 = _load_json(roster_file)
        else:
            # Check history
            history = _load_json(SHIFT_HISTORY_FILE)
            for log in history.get("logs", []):
                if log.get("roster_id") == rid:
                    if roster_var == "roster1":
                        roster1 = log
                    else:
                        roster2 = log
                    break

    if not roster1:
        return f"Roster '{roster_id_1}' not found."
    if not roster2:
        return f"Roster '{roster_id_2}' not found."

    result = "ROSTER COMPARISON\n" + "=" * 50 + "\n"
    result += f"{roster_id_1} vs {roster_id_2}\n\n"

    # Compare metadata
    m1 = roster1.get("metadata", {})
    m2 = roster2.get("metadata", {})

    result += "SCORES:\n"
    result += f"   Empathy:    {m1.get('empathy_score', 'N/A'):>6} vs {m2.get('empathy_score', 'N/A'):>6}\n"
    result += f"   Compliance: {m1.get('compliance_status', 'N/A'):>6} vs {m2.get('compliance_status', 'N/A'):>6}\n\n"

    # Compare assignments per nurse
    def count_by_nurse(roster):
        counts = {}
        for a in roster.get("assignments", []):
            nid = a.get("nurse_id", "unknown")
            if nid not in counts:
                counts[nid] = {"total": 0, "weekend": 0, "night": 0}
            counts[nid]["total"] += 1
            if _is_weekend(a.get("date", "")):
                counts[nid]["weekend"] += 1
            if a.get("shift_type") == "night":
                counts[nid]["night"] += 1
        return counts

    c1 = count_by_nurse(roster1)
    c2 = count_by_nurse(roster2)

    all_nurses = set(c1.keys()) | set(c2.keys())

    result += "ASSIGNMENTS BY NURSE:\n"
    result += f"{'Nurse':<12} {'R1 Total':>8} {'R2 Total':>8} {'R1 Wknd':>8} {'R2 Wknd':>8}\n"
    result += "-" * 50 + "\n"

    for nurse in sorted(all_nurses):
        n1 = c1.get(nurse, {"total": 0, "weekend": 0})
        n2 = c2.get(nurse, {"total": 0, "weekend": 0})
        result += f"{nurse:<12} {n1['total']:>8} {n2['total']:>8} {n1['weekend']:>8} {n2['weekend']:>8}\n"

    return result


# =============================================================================
# Maintenance Tools (Phase 5)
# =============================================================================


def sync_history_with_files() -> str:
    """
    Synchronizes shift_history.json with actual roster files.
    Removes entries from history where the roster file no longer exists.

    Returns:
        Summary of cleanup actions taken.
    """
    history = _load_json(SHIFT_HISTORY_FILE)
    original_count = len(history.get("logs", []))
    removed = []

    # Filter out entries where roster file doesn't exist
    valid_logs = []
    for log in history.get("logs", []):
        roster_id = log.get("roster_id") or log.get("id")
        roster_file = os.path.join(ROSTERS_DIR, f"{roster_id}.json")

        if os.path.exists(roster_file):
            valid_logs.append(log)
        else:
            removed.append(roster_id)

    history["logs"] = valid_logs
    _save_json(SHIFT_HISTORY_FILE, history)

    result = "HISTORY SYNC COMPLETE\n" + "=" * 50 + "\n\n"
    result += f"Original entries: {original_count}\n"
    result += f"Valid entries: {len(valid_logs)}\n"
    result += f"Removed: {len(removed)}\n"

    if removed:
        result += "\nRemoved orphaned entries:\n"
        for rid in removed:
            result += f"   - {rid}\n"

    return result


def cleanup_old_history(weeks: int = 12) -> str:
    """
    Archives rosters older than the specified number of weeks and
    recalculates nurse stats based on remaining history.

    Args:
        weeks: Number of weeks to retain (default: 12)

    Returns:
        Summary of cleanup actions taken.
    """
    history = _load_json(SHIFT_HISTORY_FILE)
    cutoff_date = datetime.now() - timedelta(weeks=weeks)

    archived_count = 0
    kept_count = 0

    for log in history.get("logs", []):
        # Skip already archived
        if log.get("status") == "archived":
            continue

        # Check finalized_at or generated_at date
        date_str = log.get("finalized_at") or log.get("generated_at")
        if date_str:
            try:
                log_date = datetime.fromisoformat(date_str)
                if log_date < cutoff_date and log.get("status") == "finalized":
                    log["status"] = "archived"
                    log["archived_at"] = datetime.now().isoformat()
                    archived_count += 1
                else:
                    kept_count += 1
            except ValueError:
                kept_count += 1

    # Update history metadata
    if "metadata" not in history:
        history["metadata"] = {}
    history["metadata"]["last_cleanup"] = datetime.now().isoformat()

    _save_json(SHIFT_HISTORY_FILE, history)

    # Recalculate nurse stats
    recalc_result = recalculate_nurse_stats(days=30)

    result = "HISTORY CLEANUP COMPLETE\n" + "=" * 50 + "\n\n"
    result += f"Retention period: {weeks} weeks\n"
    result += f"Cutoff date: {cutoff_date.strftime('%Y-%m-%d')}\n\n"
    result += f"Rosters archived: {archived_count}\n"
    result += f"Rosters retained: {kept_count}\n\n"
    result += recalc_result

    return result


def recalculate_nurse_stats(days: int = 30) -> str:
    """
    Recalculates nurse statistics based on finalized rosters
    within the specified time window.

    Args:
        days: Number of days to include in calculation (default: 30)

    Returns:
        Summary of recalculated stats.
    """
    history = _load_json(SHIFT_HISTORY_FILE)
    stats = _load_json(NURSE_STATS_FILE)
    cutoff_date = datetime.now() - timedelta(days=days)

    # Initialize fresh counts for each nurse
    nurse_counts = {}
    for nurse_id in stats.keys():
        if nurse_id.startswith("_"):
            continue
        nurse_counts[nurse_id] = {
            "total": 0,
            "weekend": 0,
            "night": 0,
            "dates": [],
            "nurse_name": stats[nurse_id].get("nurse_name", nurse_id),
        }

    # Aggregate from finalized rosters within window
    for log in history.get("logs", []):
        if log.get("status") != "finalized":
            continue

        finalized_at = log.get("finalized_at")
        if not finalized_at:
            continue

        try:
            log_date = datetime.fromisoformat(finalized_at)
            if log_date < cutoff_date:
                continue
        except ValueError:
            continue

        for assignment in log.get("assignments", []):
            nurse_id = assignment.get("nurse_id")
            if nurse_id not in nurse_counts:
                continue

            nurse_counts[nurse_id]["total"] += 1
            nurse_counts[nurse_id]["dates"].append(assignment.get("date", ""))

            if _is_weekend(assignment.get("date", "")):
                nurse_counts[nurse_id]["weekend"] += 1

            if assignment.get("shift_type") == "night":
                nurse_counts[nurse_id]["night"] += 1

    # Update stats
    for nurse_id, counts in nurse_counts.items():
        if nurse_id not in stats:
            continue

        stats[nurse_id]["total_shifts_30d"] = counts["total"]
        stats[nurse_id]["weekend_shifts_30d"] = counts["weekend"]
        stats[nurse_id]["night_shifts_30d"] = counts["night"]

        # Calculate consecutive shifts from dates
        if counts["dates"]:
            sorted_dates = sorted(counts["dates"])
            last_date = sorted_dates[-1]
            stats[nurse_id]["last_shift_date"] = last_date

            # Count consecutive from most recent
            consecutive = 1
            for i in range(len(sorted_dates) - 1, 0, -1):
                try:
                    d1 = datetime.strptime(sorted_dates[i], "%Y-%m-%d")
                    d2 = datetime.strptime(sorted_dates[i - 1], "%Y-%m-%d")
                    if (d1 - d2).days == 1:
                        consecutive += 1
                    else:
                        break
                except ValueError:
                    break
            stats[nurse_id]["consecutive_shifts_current"] = consecutive

        # Recalculate fatigue
        stats[nurse_id]["fatigue_score"] = _calculate_fatigue_score(
            stats[nurse_id]
        )
        stats[nurse_id]["updated_at"] = datetime.now().isoformat()

    # Update metadata
    if "_metadata" not in stats:
        stats["_metadata"] = {}
    stats["_metadata"]["last_recalculated"] = datetime.now().isoformat()
    stats["_metadata"]["calculation_window_days"] = days

    _save_json(NURSE_STATS_FILE, stats)

    result = "NURSE STATS RECALCULATED\n"
    result += f"Window: Last {days} days\n\n"

    for nurse_id, counts in nurse_counts.items():
        name = counts["nurse_name"]
        fatigue = stats.get(nurse_id, {}).get("fatigue_score", 0)
        result += f"  {name}: {counts['total']} shifts, fatigue={fatigue:.2f}\n"

    return result
