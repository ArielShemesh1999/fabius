"""
Query tools for user-facing information retrieval.
Allows users to query nurse status, availability, shifts, and staffing info.
"""

import logging
import os
from datetime import datetime

from nexshift_agent.sub_agents.config import (
    FATIGUE_DISPLAY_HIGH,
    FATIGUE_DISPLAY_MODERATE,
    MAX_CONSECUTIVE_SHIFTS,
    MIN_SENIOR_NURSES,
    WEEKEND_WEEKDAY_START,
)
from nexshift_agent.sub_agents.tools.data_loader import (
    generate_shifts,
    get_shifts_to_fill,
    load_nurses,
)
from nexshift_agent.sub_agents.tools.history_tools import (
    NURSE_STATS_FILE,
    _load_json,
)

logger = logging.getLogger(__name__)


def get_nurse_info(nurse_id: str) -> str:
    """
    Get detailed information about a specific nurse.

    Args:
        nurse_id: Nurse ID (e.g., "nurse_001") or name (e.g., "Alice")

    Returns:
        Formatted nurse profile with certifications, preferences, and current stats.
    """
    nurses = load_nurses()
    stats = _load_json(NURSE_STATS_FILE)

    # Find nurse by ID or name
    nurse = None
    for n in nurses:
        if n.id == nurse_id or n.name.lower() == nurse_id.lower():
            nurse = n
            break

    if not nurse:
        return f"Nurse '{nurse_id}' not found. Use list_nurses() to see all nurses."

    nurse_stats = stats.get(nurse.id, {})
    fatigue = nurse_stats.get("fatigue_score", 0)

    # Fatigue indicator
    if fatigue >= FATIGUE_DISPLAY_HIGH:
        fatigue_indicator = "HIGH RISK - Reduce shifts"
    elif fatigue >= FATIGUE_DISPLAY_MODERATE:
        fatigue_indicator = "Moderate - Monitor closely"
    else:
        fatigue_indicator = "Good"

    result = f"NURSE PROFILE: {nurse.name}\n" + "=" * 50 + "\n\n"
    result += f"ID: {nurse.id}\n"
    result += f"Seniority: {nurse.seniority_level}\n"
    result += f"Contract: {nurse.contract_type}\n"
    result += f"Certifications: {', '.join(nurse.certifications)}\n\n"

    result += "PREFERENCES:\n"
    result += f"  Avoid night shifts: {'Yes' if nurse.preferences.avoid_night_shifts else 'No'}\n"
    result += f"  Preferred days: {', '.join(nurse.preferences.preferred_days) or 'None specified'}\n"
    if nurse.preferences.adhoc_requests:
        result += f"  Active requests: {', '.join(nurse.preferences.adhoc_requests)}\n"

    result += "\nCURRENT STATUS:\n"
    result += f"  Last shift: {nurse_stats.get('last_shift_date', 'N/A')}\n"
    result += f"  Consecutive shifts: {nurse_stats.get('consecutive_shifts_current', 0)}\n"
    result += f"  Shifts (30d): {nurse_stats.get('total_shifts_30d', 0)}\n"
    result += (
        f"  Weekend shifts (30d): {nurse_stats.get('weekend_shifts_30d', 0)}\n"
    )
    result += (
        f"  Night shifts (30d): {nurse_stats.get('night_shifts_30d', 0)}\n"
    )
    result += f"  Fatigue: {fatigue:.2f} - {fatigue_indicator}\n"

    return result


def list_nurses(filter_by: str = "") -> str:
    """
    List all nurses with optional filtering.

    Args:
        filter_by: Optional filter - "senior", "junior", "mid", "available", "fatigued",
                   "fulltime", "parttime", "casual", "icu", "acls", "bls"

    Returns:
        Formatted list of nurses matching the filter.
    """
    nurses = load_nurses()
    stats = _load_json(NURSE_STATS_FILE)

    # Apply filters
    filtered = nurses
    filter_desc = "All Nurses"

    if filter_by:
        filter_lower = filter_by.lower()
        if filter_lower == "senior":
            filtered = [n for n in nurses if n.seniority_level == "Senior"]
            filter_desc = "Senior Nurses"
        elif filter_lower == "junior":
            filtered = [n for n in nurses if n.seniority_level == "Junior"]
            filter_desc = "Junior Nurses"
        elif filter_lower == "mid":
            filtered = [n for n in nurses if n.seniority_level == "Mid"]
            filter_desc = "Mid-Level Nurses"
        elif filter_lower in {"available", "fresh"}:
            filtered = [
                n
                for n in nurses
                if stats.get(n.id, {}).get("fatigue_score", 0)
                < FATIGUE_DISPLAY_MODERATE
            ]
            filter_desc = "Available Nurses (Low Fatigue)"
        elif filter_lower in {"fatigued", "tired"}:
            filtered = [
                n
                for n in nurses
                if stats.get(n.id, {}).get("fatigue_score", 0)
                >= FATIGUE_DISPLAY_MODERATE
            ]
            filter_desc = "Fatigued Nurses"
        elif filter_lower == "fulltime":
            filtered = [n for n in nurses if n.contract_type == "FullTime"]
            filter_desc = "FullTime Nurses"
        elif filter_lower == "parttime":
            filtered = [n for n in nurses if n.contract_type == "PartTime"]
            filter_desc = "PartTime Nurses"
        elif filter_lower == "casual":
            filtered = [n for n in nurses if n.contract_type == "Casual"]
            filter_desc = "Casual Nurses"
        elif filter_lower in ["icu", "acls", "bls"]:
            cert = filter_lower.upper()
            filtered = [n for n in nurses if cert in n.certifications]
            filter_desc = f"Nurses with {cert} Certification"

    if not filtered:
        return f"No nurses found matching filter: {filter_by}"

    result = f"{filter_desc.upper()}\n" + "=" * 50 + "\n\n"

    for n in filtered:
        nurse_stats = stats.get(n.id, {})
        fatigue = nurse_stats.get("fatigue_score", 0)

        if fatigue >= FATIGUE_DISPLAY_HIGH:
            status = "[HIGH]"
        elif fatigue >= FATIGUE_DISPLAY_MODERATE:
            status = "[MOD]"
        else:
            status = "[OK]"

        result += f"{status} {n.name} ({n.id})\n"
        result += f"     {n.seniority_level} | {n.contract_type} | {', '.join(n.certifications)}\n"

    result += f"\nTotal: {len(filtered)} nurses\n"
    return result


def get_nurse_availability(date: str = "") -> str:
    """
    Get nurse availability for a specific date.

    Args:
        date: Date in YYYY-MM-DD format (defaults to today)

    Returns:
        Availability summary showing who can work and any constraints.
    """
    nurses = load_nurses()
    stats = _load_json(NURSE_STATS_FILE)

    # Parse date
    if date:
        try:
            check_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return f"Invalid date format: {date}. Use YYYY-MM-DD."
    else:
        check_date = datetime.now()

    day_name = check_date.strftime("%A")
    is_weekend = check_date.weekday() >= WEEKEND_WEEKDAY_START

    result = (
        f"NURSE AVAILABILITY: {check_date.strftime('%Y-%m-%d')} ({day_name})\n"
    )
    result += "=" * 50 + "\n\n"

    available = []
    limited = []
    unavailable = []

    for n in nurses:
        nurse_stats = stats.get(n.id, {})
        fatigue = nurse_stats.get("fatigue_score", 0)
        consecutive = nurse_stats.get("consecutive_shifts_current", 0)

        constraints = []

        # Check consecutive shift limit
        if consecutive >= MAX_CONSECUTIVE_SHIFTS:
            constraints.append("Max consecutive shifts reached")

        # Check fatigue
        if fatigue >= FATIGUE_DISPLAY_HIGH:
            constraints.append("High fatigue risk")

        # Check adhoc time-off requests
        if n.preferences.adhoc_requests:
            for req in n.preferences.adhoc_requests:
                if req.startswith("Off_"):
                    parts = req.split("_")
                    off_date = parts[1] if len(parts) > 1 else ""
                    if off_date == check_date.strftime("%Y-%m-%d"):
                        constraints.append("Time-off requested")

        # Check preferences (soft constraint)
        if (
            n.preferences.preferred_days
            and day_name not in n.preferences.preferred_days
        ):
            constraints.append(
                f"Prefers: {', '.join(n.preferences.preferred_days)}"
            )

        # Categorize
        if (
            "Max consecutive shifts reached" in constraints
            or "Time-off requested" in constraints
        ):
            unavailable.append((n, constraints))
        elif constraints:
            limited.append((n, constraints))
        else:
            available.append(n)

    # Format output
    result += f"AVAILABLE ({len(available)}):\n"
    for n in available:
        result += f"  + {n.name} - {n.seniority_level}, {', '.join(n.certifications)}\n"

    result += f"\nLIMITED AVAILABILITY ({len(limited)}):\n"
    for n, cons in limited:
        result += f"  ? {n.name} - {'; '.join(cons)}\n"

    result += f"\nUNAVAILABLE ({len(unavailable)}):\n"
    for n, cons in unavailable:
        result += f"  - {n.name} - {'; '.join(cons)}\n"

    if is_weekend:
        result += "\nNote: This is a weekend - fair distribution rules apply.\n"

    return result


def list_nurse_preferences() -> str:
    """
    List all nurses' scheduling preferences.

    Returns:
        Formatted list of all nurses with their preferences including:
        - Night shift avoidance
        - Preferred working days
        - Active time-off requests
    """
    try:
        nurses = load_nurses()

        if not nurses:
            return "No nurses found in the system."

        result = "NURSE PREFERENCES\n" + "=" * 50 + "\n\n"

        avoiding_nights = []
        has_preferred_days = []
        has_time_off = []

        for n in nurses:
            result += f"{n.name} ({n.id}) - {n.seniority_level}\n"

            # Handle preferences safely
            prefs = n.preferences
            if prefs:
                avoid_nights = getattr(prefs, "avoid_night_shifts", False)
                preferred_days = getattr(prefs, "preferred_days", []) or []
                adhoc_requests = getattr(prefs, "adhoc_requests", []) or []

                result += (
                    f"  Avoid night shifts: {'Yes' if avoid_nights else 'No'}\n"
                )

                if preferred_days:
                    result += f"  Preferred days: {', '.join(preferred_days)}\n"
                else:
                    result += "  Preferred days: Any\n"

                if adhoc_requests:
                    result += (
                        f"  Time-off requests: {', '.join(adhoc_requests)}\n"
                    )

                # Track for summary
                if avoid_nights:
                    avoiding_nights.append(n.name)
                if preferred_days:
                    has_preferred_days.append(n.name)
                if adhoc_requests:
                    has_time_off.append(n.name)
            else:
                result += "  Avoid night shifts: No\n"
                result += "  Preferred days: Any\n"

            result += "\n"

        # Summary
        result += "-" * 50 + "\n"
        result += "SUMMARY:\n"
        result += f"  Avoiding night shifts: {len(avoiding_nights)} nurses\n"
        if avoiding_nights:
            result += f"    ({', '.join(avoiding_nights)})\n"
        result += f"  Have preferred days: {len(has_preferred_days)} nurses\n"
        result += f"  Have time-off requests: {len(has_time_off)} nurses\n"

        return result

    except Exception as e:
        return f"Error loading nurse preferences: {e!s}"


def get_upcoming_shifts(days: int = 7) -> str:
    """
    Get shifts that need to be filled for the upcoming period.

    Args:
        days: Number of days to look ahead (default: 7)

    Returns:
        Formatted list of upcoming shifts with requirements.
    """
    return get_shifts_to_fill(num_days=days)


def get_staffing_summary() -> str:
    """
    Get a high-level staffing summary including coverage gaps and alerts.

    Returns:
        Summary of current staffing status, fatigue levels, and potential issues.
    """
    try:
        logger.info(f"get_staffing_summary called. CWD: {os.getcwd()}")
        logger.info(
            f"NURSE_STATS_FILE: {NURSE_STATS_FILE}, exists: {os.path.exists(NURSE_STATS_FILE)}"
        )

        nurses = load_nurses()
        logger.info(f"Loaded {len(nurses)} nurses")

        stats = _load_json(NURSE_STATS_FILE)
        logger.info(f"Loaded stats with {len(stats)} entries")

        shifts = generate_shifts(num_days=7)
        logger.info(f"Generated {len(shifts)} shifts")

    except Exception as e:
        logger.error(
            f"Error loading data in get_staffing_summary: {e}", exc_info=True
        )
        return f"Error loading staffing data: {e!s}"

    result = "STAFFING SUMMARY\n" + "=" * 50 + "\n\n"

    # Nurse counts by type
    by_seniority = {"Senior": 0, "Mid": 0, "Junior": 0}
    by_contract = {"FullTime": 0, "PartTime": 0, "Casual": 0}
    by_fatigue = {"good": 0, "moderate": 0, "high": 0}

    for n in nurses:
        by_seniority[n.seniority_level] = (
            by_seniority.get(n.seniority_level, 0) + 1
        )
        by_contract[n.contract_type] = by_contract.get(n.contract_type, 0) + 1

        fatigue = stats.get(n.id, {}).get("fatigue_score", 0)
        if fatigue >= FATIGUE_DISPLAY_HIGH:
            by_fatigue["high"] += 1
        elif fatigue >= FATIGUE_DISPLAY_MODERATE:
            by_fatigue["moderate"] += 1
        else:
            by_fatigue["good"] += 1

    result += "WORKFORCE:\n"
    result += f"  Total nurses: {len(nurses)}\n"
    result += f"  By seniority: Senior={by_seniority['Senior']}, Mid={by_seniority['Mid']}, Junior={by_seniority['Junior']}\n"
    result += f"  By contract: FullTime={by_contract['FullTime']}, PartTime={by_contract['PartTime']}, Casual={by_contract['Casual']}\n"

    result += "\nFATIGUE STATUS:\n"
    result += f"  [OK] Good: {by_fatigue['good']} nurses\n"
    result += f"  [MOD] Moderate: {by_fatigue['moderate']} nurses\n"
    result += f"  [HIGH] High Risk: {by_fatigue['high']} nurses\n"

    # Shift requirements
    icu_shifts = len([s for s in shifts if s["ward"] == "ICU"])
    emergency_shifts = len([s for s in shifts if s["ward"] == "Emergency"])
    general_shifts = len([s for s in shifts if s["ward"] == "General"])

    result += "\nUPCOMING SHIFTS (7 days):\n"
    result += f"  Total: {len(shifts)} shifts\n"
    result += f"  ICU: {icu_shifts} | Emergency: {emergency_shifts} | General: {general_shifts}\n"

    # Coverage check
    icu_certified = len([n for n in nurses if "ICU" in n.certifications])
    emergency_certified = len(
        [
            n
            for n in nurses
            if "ACLS" in n.certifications and "BLS" in n.certifications
        ]
    )
    senior_count = by_seniority["Senior"]

    result += "\nCOVERAGE CHECK:\n"
    result += f"  ICU-certified nurses: {icu_certified}\n"
    result += f"  Emergency-certified (ACLS+BLS): {emergency_certified}\n"
    result += f"  Senior nurses (required each shift): {senior_count}\n"

    # Alerts
    alerts = []
    if by_fatigue["high"] > 0:
        high_fatigue_names = [
            n.name
            for n in nurses
            if stats.get(n.id, {}).get("fatigue_score", 0)
            >= FATIGUE_DISPLAY_HIGH
        ]
        alerts.append(
            f"[HIGH] {by_fatigue['high']} nurse(s) at high fatigue: {', '.join(high_fatigue_names)}"
        )

    if senior_count < MIN_SENIOR_NURSES:
        alerts.append(
            "[WARN] Low senior nurse coverage - may impact shift requirements"
        )

    if alerts:
        result += "\nALERTS:\n"
        for alert in alerts:
            result += f"  {alert}\n"
    else:
        result += "\n[OK] No staffing alerts.\n"

    return result
