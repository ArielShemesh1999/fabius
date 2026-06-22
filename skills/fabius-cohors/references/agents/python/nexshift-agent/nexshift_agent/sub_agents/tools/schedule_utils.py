"""
Schedule utilities for period management.

Provides shared scheduling functions used by both data_loader and history_tools,
extracted here to avoid circular imports between those modules.
"""

import json
import os
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data")
SHIFT_HISTORY_FILE = os.path.join(DATA_DIR, "shift_history.json")
ROSTERS_DIR = os.path.join(DATA_DIR, "rosters")


def _load_json(filepath: str) -> dict:
    """Load JSON file, return empty dict if not found."""
    try:
        with open(filepath) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def get_scheduled_periods() -> list:
    """
    Returns a list of all scheduled periods from finalized and draft rosters.
    Only includes rosters that still have their roster file.

    Returns:
        List of dicts with roster_id, status, start, end dates.
    """
    history = _load_json(SHIFT_HISTORY_FILE)
    periods = []

    for log in history.get("logs", []):
        status = log.get("status", "")
        if status not in ["finalized", "draft"]:
            continue

        roster_id = log.get("roster_id") or log.get("id")

        # Verify the roster file still exists
        roster_file = os.path.join(ROSTERS_DIR, f"{roster_id}.json")
        if not os.path.exists(roster_file):
            continue  # Skip if roster file was deleted

        period = log.get("period", {})
        if period.get("start") and period.get("end"):
            periods.append(
                {
                    "roster_id": roster_id,
                    "status": status,
                    "start": period["start"],
                    "end": period["end"],
                }
            )

    return sorted(periods, key=lambda x: x["start"])


def get_next_unscheduled_date() -> str:
    """
    Finds the next date that doesn't have a finalized roster.

    Returns:
        Date string in YYYY-MM-DD format for the next unscheduled date.
    """
    periods = get_scheduled_periods()

    # Only consider finalized rosters for determining next date
    finalized_periods = [p for p in periods if p["status"] == "finalized"]

    if not finalized_periods:
        # No finalized rosters, start from today
        return datetime.now().strftime("%Y-%m-%d")

    # Find the latest end date from finalized rosters
    latest_end = max(p["end"] for p in finalized_periods)

    try:
        latest_end_dt = datetime.strptime(latest_end, "%Y-%m-%d")
        next_date = latest_end_dt + timedelta(days=1)
        today = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        next_date = max(next_date, today)
        return next_date.strftime("%Y-%m-%d")
    except ValueError:
        return datetime.now().strftime("%Y-%m-%d")


def check_period_overlap(start_date: str, num_days: int = 7) -> dict:
    """
    Checks if the requested period overlaps with existing rosters.

    Args:
        start_date: Start date in YYYY-MM-DD format
        num_days: Number of days to schedule

    Returns:
        Dict with overlap info:
        - has_overlap: bool
        - overlapping_rosters: list of roster info
        - suggested_start: next available start date
    """
    try:
        req_start = datetime.strptime(start_date, "%Y-%m-%d")
        req_end = req_start + timedelta(days=num_days - 1)
    except ValueError:
        return {
            "has_overlap": False,
            "overlapping_rosters": [],
            "suggested_start": start_date,
            "error": "Invalid date format",
        }

    periods = get_scheduled_periods()
    overlapping = []

    for p in periods:
        try:
            p_start = datetime.strptime(p["start"], "%Y-%m-%d")
            p_end = datetime.strptime(p["end"], "%Y-%m-%d")

            # Check for overlap: NOT (req_end < p_start OR req_start > p_end)
            if not (req_end < p_start or req_start > p_end):
                overlapping.append(
                    {
                        "roster_id": p["roster_id"],
                        "status": p["status"],
                        "period": f"{p['start']} to {p['end']}",
                    }
                )
        except ValueError:
            continue

    # Find suggested start date
    suggested_start = get_next_unscheduled_date()

    return {
        "has_overlap": len(overlapping) > 0,
        "overlapping_rosters": overlapping,
        "suggested_start": suggested_start,
        "requested_period": f"{start_date} to {req_end.strftime('%Y-%m-%d')}",
    }
