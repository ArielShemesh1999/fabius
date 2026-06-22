import json
import os
from datetime import datetime, timedelta

from nexshift_agent.models.domain import Nurse
from nexshift_agent.sub_agents.tools.schedule_utils import (
    check_period_overlap,
    get_next_unscheduled_date,
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data")


def load_nurses() -> list[Nurse]:
    """Loads nurse profiles from the mock HRIS database (internal use)."""
    hris_path = os.path.join(DATA_DIR, "mock_hris.json")
    with open(hris_path) as f:
        data = json.load(f)
    return [Nurse(**item) for item in data]


def load_regulations() -> str:
    """Loads regulatory text from the knowledge base."""
    regulations_path = os.path.join(
        DATA_DIR, "regulations", "hospital_rules.txt"
    )
    try:
        with open(regulations_path) as f:
            return f.read()
    except FileNotFoundError:
        return "Error: Regulations file not found at " + regulations_path


def load_shift_history(nurse_id: str) -> str:
    """Loads historical shift data for a specific nurse."""
    # Mock implementation
    return f"History for {nurse_id}: Last shift was 2 days ago. Worked 3 weekends last month."


# ============================================================================
# ADK Tool Functions (return strings for LLM agents)
# ============================================================================


def get_available_nurses() -> str:
    """
    Retrieves all available nurses from the HRIS database.
    Returns a formatted string with nurse details including certifications,
    seniority level, and preferences.
    """
    nurses = load_nurses()
    result = "AVAILABLE NURSES:\n" + "=" * 50 + "\n\n"

    for n in nurses:
        result += f"📋 {n.name} (ID: {n.id})\n"
        result += f"   Seniority: {n.seniority_level}\n"
        result += f"   Contract: {n.contract_type}\n"
        result += f"   Certifications: {', '.join(n.certifications)}\n"
        result += "   Preferences:\n"
        result += (
            f"     - Avoid night shifts: {n.preferences.avoid_night_shifts}\n"
        )
        result += f"     - Preferred days: {', '.join(n.preferences.preferred_days) or 'None'}\n"
        if n.preferences.adhoc_requests:
            result += f"     - Special requests: {', '.join(n.preferences.adhoc_requests)}\n"
        result += "   History:\n"
        result += f"     - Consecutive shifts: {n.history_summary.consecutive_shifts}\n"
        result += f"     - Weekend shifts last month: {n.history_summary.weekend_shifts_last_month}\n"
        result += "\n"

    return result


def generate_shifts(
    start_date: datetime | None = None, num_days: int = 7
) -> list:
    """
    Generates mock shifts for the scheduling period.

    Args:
        start_date: Starting date for shifts (defaults to today)
        num_days: Number of days to generate shifts for (default: 7)

    Returns:
        List of shift dictionaries
    """
    if start_date is None:
        start_date = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    # Shift templates for different wards
    # ICU & Emergency: 24/7 coverage with 3 x 8-hour shifts
    # General: Weekdays only, day shift (08:00-16:00)
    shift_templates = [
        # ICU - 24/7 coverage (3 shifts per day)
        {
            "ward": "ICU",
            "start": "00:00",
            "end": "08:00",
            "certs": ["ICU"],
            "level": "Mid",
            "all_week": True,
        },
        {
            "ward": "ICU",
            "start": "08:00",
            "end": "16:00",
            "certs": ["ICU"],
            "level": "Mid",
            "all_week": True,
        },
        {
            "ward": "ICU",
            "start": "16:00",
            "end": "00:00",
            "certs": ["ICU"],
            "level": "Mid",
            "all_week": True,
        },
        # Emergency - 24/7 coverage (3 shifts per day)
        {
            "ward": "Emergency",
            "start": "00:00",
            "end": "08:00",
            "certs": ["ACLS", "BLS"],
            "level": "Mid",
            "all_week": True,
        },
        {
            "ward": "Emergency",
            "start": "08:00",
            "end": "16:00",
            "certs": ["ACLS", "BLS"],
            "level": "Mid",
            "all_week": True,
        },
        {
            "ward": "Emergency",
            "start": "16:00",
            "end": "00:00",
            "certs": ["ACLS", "BLS"],
            "level": "Mid",
            "all_week": True,
        },
        # General - Weekdays only, day shift
        {
            "ward": "General",
            "start": "08:00",
            "end": "16:00",
            "certs": ["BLS"],
            "level": "Junior",
            "all_week": False,
        },
    ]

    shifts = []
    shift_counter = 1

    for day_offset in range(num_days):
        current_date = start_date + timedelta(days=day_offset)
        day_name = current_date.strftime("%A")
        is_weekend = day_name in ["Saturday", "Sunday"]

        for template in shift_templates:
            # Skip non-24/7 wards on weekends
            if is_weekend and not template.get("all_week", True):
                continue

            shifts.append(
                {
                    "id": f"shift_{shift_counter:03d}",
                    "ward": template["ward"],
                    "date": current_date.strftime("%Y-%m-%d"),
                    "day": day_name,
                    "start": template["start"],
                    "end": template["end"],
                    "required_certs": template["certs"],
                    "min_level": template["level"],
                }
            )
            shift_counter += 1

    return shifts


def get_shifts_to_fill(start_date: str = "", num_days: int = 7) -> str:
    """
    Retrieves the shifts that need to be filled for the scheduling period.
    Automatically uses the next unscheduled date if no start_date is provided.
    Warns if the requested period overlaps with existing rosters.

    Args:
        start_date: Optional start date in YYYY-MM-DD format (defaults to next unscheduled date)
        num_days: Number of days to schedule (default: 7)

    Returns:
        Formatted string with shift details including ward, time, and requirements.
    """
    # Parse start_date if provided, otherwise use next unscheduled date
    if start_date:
        try:
            parsed_date = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            return f"Error: Invalid date format '{start_date}'. Use YYYY-MM-DD format."
    else:
        # Use the next unscheduled date
        next_date = get_next_unscheduled_date()
        parsed_date = datetime.strptime(next_date, "%Y-%m-%d")

    # Check for overlap with existing rosters
    overlap_info = check_period_overlap(
        parsed_date.strftime("%Y-%m-%d"), num_days
    )

    shifts = generate_shifts(start_date=parsed_date, num_days=num_days)

    # Group shifts by date for display
    result = f"SHIFTS TO BE FILLED ({num_days} days)\n" + "=" * 50 + "\n"
    result += f"Period: {parsed_date.strftime('%Y-%m-%d')} to {(parsed_date + timedelta(days=num_days - 1)).strftime('%Y-%m-%d')}\n"

    # Show overlap warning if applicable
    if overlap_info["has_overlap"]:
        result += "\n⚠️  WARNING: This period overlaps with existing rosters:\n"
        for r in overlap_info["overlapping_rosters"]:
            status_icon = "✅" if r["status"] == "finalized" else "📝"
            result += f"   {status_icon} {r['roster_id']} ({r['status']}): {r['period']}\n"
        result += f"\n   Suggested next available date: {overlap_info['suggested_start']}\n"
        result += (
            "   To regenerate, the existing roster must be deleted first.\n"
        )

    current_date = None
    for s in shifts:
        if s["date"] != current_date:
            current_date = s["date"]
            is_weekend = s["day"] in ["Saturday", "Sunday"]
            weekend_marker = " [WEEKEND]" if is_weekend else ""
            result += f"\n📆 {s['date']} ({s['day']}){weekend_marker}\n"
            result += "-" * 40 + "\n"

        result += f"  📅 {s['id']}: {s['ward']} Ward\n"
        result += f"     Time: {s['start']} - {s['end']}\n"
        result += f"     Required: {', '.join(s['required_certs'])} | Min Level: {s['min_level']}\n"

    result += f"\nTotal shifts: {len(shifts)}\n"
    return result


def get_regulations() -> str:
    """
    Retrieves the hospital regulations and labor laws that must be followed
    when creating nurse schedules. Loads from data/regulations/hospital_rules.txt.
    """
    return load_regulations()


def get_nurse_json() -> str:
    """
    Returns nurse data in JSON format for the solver tool.
    """
    nurses = load_nurses()
    return json.dumps([n.model_dump() for n in nurses], default=str)


def get_shifts_json(start_date: str = "", num_days: int = 7) -> str:
    """
    Returns shift data in JSON format for the solver tool.

    Args:
        start_date: Optional start date in YYYY-MM-DD format (defaults to today)
        num_days: Number of days to schedule (default: 7)
    """
    # Parse start_date if provided
    if start_date:
        try:
            parsed_date = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            return json.dumps(
                {
                    "error": f"Invalid date format '{start_date}'. Use YYYY-MM-DD."
                }
            )
    else:
        parsed_date = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    raw_shifts = generate_shifts(start_date=parsed_date, num_days=num_days)

    # Convert to solver-compatible format with datetime objects
    shifts = []
    for s in raw_shifts:
        date = datetime.strptime(s["date"], "%Y-%m-%d")
        start_hour, start_min = map(int, s["start"].split(":"))
        end_hour, end_min = map(int, s["end"].split(":"))

        start_time = date.replace(hour=start_hour, minute=start_min)
        # Handle overnight shifts
        if end_hour < start_hour:
            end_time = (date + timedelta(days=1)).replace(
                hour=end_hour, minute=end_min
            )
        else:
            end_time = date.replace(hour=end_hour, minute=end_min)

        shifts.append(
            {
                "id": s["id"],
                "ward": s["ward"],
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "required_certifications": s["required_certs"],
                "min_level": s["min_level"],
            }
        )

    return json.dumps(shifts, default=str)
