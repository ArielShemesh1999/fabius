"""
HRIS Management Tools - Add, update, and manage nurse records.

These tools modify the mock_hris.json file to add new nurses,
promote existing nurses, and update certifications.
"""

import json
import os
from datetime import datetime, timedelta

from nexshift_agent.sub_agents.config import MAX_INLINE_DATES, SENIORITY_ORDER

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data")
HRIS_FILE = os.path.join(DATA_DIR, "mock_hris.json")
NURSE_STATS_FILE = os.path.join(DATA_DIR, "nurse_stats.json")


def _load_hris() -> list:
    """Load HRIS data."""
    try:
        with open(HRIS_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save_hris(data: list) -> None:
    """Save HRIS data."""
    with open(HRIS_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


def _load_nurse_stats() -> dict:
    """Load nurse stats."""
    try:
        with open(NURSE_STATS_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_nurse_stats(data: dict) -> None:
    """Save nurse stats."""
    with open(NURSE_STATS_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


def _get_next_nurse_id(nurses: list) -> str:
    """Generate the next nurse ID."""
    max_num = 0
    for nurse in nurses:
        nurse_id = nurse.get("id", "")
        if nurse_id.startswith("nurse_"):
            try:
                num = int(nurse_id.split("_")[1])
                max_num = max(max_num, num)
            except (IndexError, ValueError):
                pass
    return f"nurse_{max_num + 1:03d}"


def add_nurse(
    name: str,
    seniority_level: str = "Junior",
    contract_type: str = "FullTime",
    certifications: str = "BLS",
    avoid_night_shifts: bool = False,
    preferred_days: str = "",
) -> str:
    """
    Adds a new nurse to the HRIS system.

    Args:
        name: The nurse's name (required)
        seniority_level: "Junior", "Mid", or "Senior" (default: Junior)
        contract_type: "FullTime", "PartTime", or "Casual" (default: FullTime)
        certifications: Comma-separated list of certifications (default: "BLS")
                       Options: BLS, ACLS, ICU
        avoid_night_shifts: Whether nurse prefers to avoid night shifts (default: False)
        preferred_days: Comma-separated list of preferred days (e.g., "Monday,Tuesday,Wednesday")

    Returns:
        Confirmation message with the new nurse's details.
    """
    # Validate seniority level
    valid_levels = ["Junior", "Mid", "Senior"]
    if seniority_level not in valid_levels:
        return f"Error: Invalid seniority level '{seniority_level}'. Must be one of: {', '.join(valid_levels)}"

    # Validate contract type
    valid_contracts = ["FullTime", "PartTime", "Casual"]
    if contract_type not in valid_contracts:
        return f"Error: Invalid contract type '{contract_type}'. Must be one of: {', '.join(valid_contracts)}"

    # Parse certifications
    cert_list = [
        c.strip().upper() for c in certifications.split(",") if c.strip()
    ]
    valid_certs = ["BLS", "ACLS", "ICU"]
    for cert in cert_list:
        if cert not in valid_certs:
            return f"Error: Invalid certification '{cert}'. Valid options: {', '.join(valid_certs)}"

    if not cert_list:
        cert_list = ["BLS"]

    # Parse preferred days
    day_list = []
    if preferred_days:
        valid_days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        for raw_day in preferred_days.split(","):
            cleaned_day = raw_day.strip().capitalize()
            if cleaned_day in valid_days:
                day_list.append(cleaned_day)

    # Load existing data
    nurses = _load_hris()

    # Check for duplicate name
    for nurse in nurses:
        if nurse.get("name", "").lower() == name.lower():
            return f"Error: A nurse named '{name}' already exists (ID: {nurse['id']}). Use a different name."

    # Generate new ID
    new_id = _get_next_nurse_id(nurses)

    # Create new nurse record
    new_nurse = {
        "id": new_id,
        "name": name,
        "certifications": cert_list,
        "seniority_level": seniority_level,
        "contract_type": contract_type,
        "preferences": {
            "avoid_night_shifts": avoid_night_shifts,
            "preferred_days": day_list,
            "adhoc_requests": [],
        },
        "history_summary": {
            "last_shift": None,
            "consecutive_shifts": 0,
            "weekend_shifts_last_month": 0,
        },
    }

    # Add to HRIS
    nurses.append(new_nurse)
    _save_hris(nurses)

    # Initialize nurse stats (fresh nurse with 0 fatigue)
    stats = _load_nurse_stats()
    stats[new_id] = {
        "nurse_name": name,
        "total_shifts_30d": 0,
        "weekend_shifts_30d": 0,
        "night_shifts_30d": 0,
        "consecutive_shifts_current": 0,
        "last_shift_date": "",
        "preferences_honored_rate": 1.0,
        "fatigue_score": 0.0,
        "updated_at": datetime.now().isoformat(),
    }
    _save_nurse_stats(stats)

    # Build response
    result = "SUCCESS: New nurse added to the system.\n\n"
    result += "NURSE DETAILS\n"
    result += f"{'=' * 40}\n"
    result += f"ID: {new_id}\n"
    result += f"Name: {name}\n"
    result += f"Seniority: {seniority_level}\n"
    result += f"Contract: {contract_type}\n"
    result += f"Certifications: {', '.join(cert_list)}\n"
    result += f"Avoid Night Shifts: {'Yes' if avoid_night_shifts else 'No'}\n"
    if day_list:
        result += f"Preferred Days: {', '.join(day_list)}\n"
    result += "\nFatigue Score: 0.0 (Fresh)\n"
    result += "\nThe nurse is now available for roster generation."

    return result


def promote_nurse(nurse_id: str, new_level: str) -> str:
    """
    Promotes an existing nurse to a higher seniority level.

    Args:
        nurse_id: The nurse's ID (e.g., "nurse_002") or name
        new_level: The new seniority level ("Mid" or "Senior")

    Returns:
        Confirmation message with the updated details.
    """
    valid_levels = ["Junior", "Mid", "Senior"]

    if new_level not in valid_levels:
        return f"Error: Invalid level '{new_level}'. Must be one of: {', '.join(valid_levels)}"

    nurses = _load_hris()

    # Find nurse by ID or name
    found_nurse = None
    for nurse in nurses:
        if (
            nurse.get("id") == nurse_id
            or nurse.get("name", "").lower() == nurse_id.lower()
        ):
            found_nurse = nurse
            break

    if not found_nurse:
        return f"Error: Nurse '{nurse_id}' not found."

    current_level = found_nurse.get("seniority_level", "Junior")
    current_order = SENIORITY_ORDER.get(current_level, 0)
    new_order = SENIORITY_ORDER.get(new_level, 0)

    if new_order <= current_order:
        return f"Error: Cannot promote {found_nurse['name']} from {current_level} to {new_level}. Must promote to a higher level."

    # Update the nurse's level
    old_level = found_nurse["seniority_level"]
    found_nurse["seniority_level"] = new_level
    _save_hris(nurses)

    result = "SUCCESS: Nurse promoted.\n\n"
    result += "PROMOTION DETAILS\n"
    result += f"{'=' * 40}\n"
    result += f"Nurse: {found_nurse['name']} ({found_nurse['id']})\n"
    result += f"Previous Level: {old_level}\n"
    result += f"New Level: {new_level}\n"
    result += f"\nThe nurse can now be assigned to {new_level}-level shifts."

    return result


def update_nurse_certifications(
    nurse_id: str, add_certifications: str = "", remove_certifications: str = ""
) -> str:
    """
    Updates a nurse's certifications.

    Args:
        nurse_id: The nurse's ID (e.g., "nurse_002") or name
        add_certifications: Comma-separated certifications to add (e.g., "ICU,ACLS")
        remove_certifications: Comma-separated certifications to remove (e.g., "BLS")

    Returns:
        Confirmation message with updated certifications.
    """
    valid_certs = ["BLS", "ACLS", "ICU"]

    nurses = _load_hris()

    # Find nurse by ID or name
    found_nurse = None
    for nurse in nurses:
        if (
            nurse.get("id") == nurse_id
            or nurse.get("name", "").lower() == nurse_id.lower()
        ):
            found_nurse = nurse
            break

    if not found_nurse:
        return f"Error: Nurse '{nurse_id}' not found."

    current_certs = set(found_nurse.get("certifications", []))
    original_certs = current_certs.copy()

    # Add certifications
    added = []
    if add_certifications:
        for raw_cert in add_certifications.split(","):
            cleaned_cert = raw_cert.strip().upper()
            if cleaned_cert not in valid_certs:
                return f"Error: Invalid certification '{cleaned_cert}'. Valid options: {', '.join(valid_certs)}"
            if cleaned_cert not in current_certs:
                current_certs.add(cleaned_cert)
                added.append(cleaned_cert)

    # Remove certifications
    removed = []
    if remove_certifications:
        for raw_cert in remove_certifications.split(","):
            cleaned_cert = raw_cert.strip().upper()
            if cleaned_cert in current_certs:
                current_certs.remove(cleaned_cert)
                removed.append(cleaned_cert)

    if not added and not removed:
        return f"No changes made. {found_nurse['name']} currently has: {', '.join(original_certs)}"

    # Update and save
    found_nurse["certifications"] = list(current_certs)
    _save_hris(nurses)

    result = "SUCCESS: Certifications updated.\n\n"
    result += "CERTIFICATION UPDATE\n"
    result += f"{'=' * 40}\n"
    result += f"Nurse: {found_nurse['name']} ({found_nurse['id']})\n"
    result += f"Previous: {', '.join(sorted(original_certs))}\n"
    result += f"Current: {', '.join(sorted(current_certs))}\n"
    if added:
        result += f"Added: {', '.join(added)}\n"
    if removed:
        result += f"Removed: {', '.join(removed)}\n"

    # Ward eligibility
    result += "\nWard Eligibility:\n"
    if "ICU" in current_certs:
        result += "  - ICU: Yes\n"
    else:
        result += "  - ICU: No (requires ICU certification)\n"

    if "ACLS" in current_certs and "BLS" in current_certs:
        result += "  - Emergency: Yes\n"
    else:
        result += "  - Emergency: No (requires ACLS + BLS)\n"

    result += f"  - General: {'Yes' if 'BLS' in current_certs else 'No (requires BLS)'}\n"

    return result


def update_nurse_preferences(
    nurse_id: str,
    avoid_night_shifts: bool | None = None,
    preferred_days: str = "",
) -> str:
    """
    Updates a nurse's scheduling preferences.

    Args:
        nurse_id: The nurse's ID (e.g., "nurse_002") or name
        avoid_night_shifts: Set to True/False to update night shift preference
        preferred_days: Comma-separated list of preferred days (replaces existing)
                       Use empty string to keep current, use "clear" to remove all

    Returns:
        Confirmation message with updated preferences.
    """
    nurses = _load_hris()

    # Find nurse by ID or name
    found_nurse = None
    for nurse in nurses:
        if (
            nurse.get("id") == nurse_id
            or nurse.get("name", "").lower() == nurse_id.lower()
        ):
            found_nurse = nurse
            break

    if not found_nurse:
        return f"Error: Nurse '{nurse_id}' not found."

    prefs = found_nurse.get("preferences", {})
    changes = []

    # Update night shift preference
    if avoid_night_shifts is not None:
        old_value = prefs.get("avoid_night_shifts", False)
        if old_value != avoid_night_shifts:
            prefs["avoid_night_shifts"] = avoid_night_shifts
            changes.append(
                f"Avoid Night Shifts: {old_value} → {avoid_night_shifts}"
            )

    # Update preferred days
    if preferred_days:
        old_days = prefs.get("preferred_days", [])
        if preferred_days.lower() == "clear":
            new_days = []
        else:
            valid_days = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
            new_days = []
            for raw_day in preferred_days.split(","):
                cleaned_day = raw_day.strip().capitalize()
                if cleaned_day in valid_days:
                    new_days.append(cleaned_day)

        if old_days != new_days:
            prefs["preferred_days"] = new_days
            changes.append(f"Preferred Days: {old_days} → {new_days}")

    if not changes:
        return f"No changes made to {found_nurse['name']}'s preferences."

    found_nurse["preferences"] = prefs
    _save_hris(nurses)

    result = "SUCCESS: Preferences updated.\n\n"
    result += "PREFERENCE UPDATE\n"
    result += f"{'=' * 40}\n"
    result += f"Nurse: {found_nurse['name']} ({found_nurse['id']})\n\n"
    result += "Changes:\n"
    for change in changes:
        result += f"  - {change}\n"

    return result


def remove_nurse(nurse_id: str) -> str:
    """
    Removes a nurse from the HRIS system.

    Args:
        nurse_id: The nurse's ID (e.g., "nurse_002") or name

    Returns:
        Confirmation message.
    """
    nurses = _load_hris()

    # Find nurse by ID or name
    found_index = None
    found_nurse = None
    for i, nurse in enumerate(nurses):
        if (
            nurse.get("id") == nurse_id
            or nurse.get("name", "").lower() == nurse_id.lower()
        ):
            found_index = i
            found_nurse = nurse
            break

    if found_nurse is None or found_index is None:
        return f"Error: Nurse '{nurse_id}' not found."

    # Remove from HRIS
    nurses.pop(found_index)
    _save_hris(nurses)

    # Remove from stats
    stats = _load_nurse_stats()
    if found_nurse["id"] in stats:
        del stats[found_nurse["id"]]
        _save_nurse_stats(stats)

    result = "SUCCESS: Nurse removed from the system.\n\n"
    result += f"Removed: {found_nurse['name']} ({found_nurse['id']})\n"
    result += (
        "\nNote: Any pending rosters with this nurse should be regenerated."
    )

    return result


def list_available_certifications() -> str:
    """
    Lists all available certifications and their requirements.

    Returns:
        Information about certifications.
    """
    result = "AVAILABLE CERTIFICATIONS\n"
    result += "=" * 40 + "\n\n"

    result += "BLS (Basic Life Support)\n"
    result += "  - Required for: General Ward\n"
    result += "  - Prerequisite for: ACLS\n\n"

    result += "ACLS (Advanced Cardiac Life Support)\n"
    result += "  - Required for: Emergency Ward (with BLS)\n"
    result += "  - Prerequisite: BLS\n\n"

    result += "ICU (Intensive Care Unit)\n"
    result += "  - Required for: ICU Ward\n"
    result += "  - Specialized critical care certification\n\n"

    result += "WARD REQUIREMENTS\n"
    result += "-" * 40 + "\n"
    result += "ICU Ward:       ICU certification required\n"
    result += "Emergency Ward: ACLS + BLS certifications required\n"
    result += "General Ward:   BLS certification required\n"

    return result


def add_time_off_request(
    nurse_id: str, start_date: str, end_date: str = "", reason: str = "TimeOff"
) -> str:
    """
    Adds a time-off request for a nurse (sick leave, vacation, unavailable period).

    The nurse will NOT be assigned any shifts during this period when generating rosters.

    Args:
        nurse_id: The nurse's ID (e.g., "nurse_002") or name
        start_date: Start date of unavailability in YYYY-MM-DD format
        end_date: End date of unavailability in YYYY-MM-DD format (defaults to start_date for single day)
        reason: Reason for time off (e.g., "Sick", "Vacation", "Personal", "Training")

    Returns:
        Confirmation message with the time-off details.

    Examples:
        - Single day sick leave: add_time_off_request("Bob", "2025-12-10", reason="Sick")
        - Week vacation: add_time_off_request("Bob", "2025-12-09", "2025-12-15", "Vacation")
    """
    nurses = _load_hris()

    # Find nurse by ID or name
    found_nurse = None
    for nurse in nurses:
        if (
            nurse.get("id") == nurse_id
            or nurse.get("name", "").lower() == nurse_id.lower()
        ):
            found_nurse = nurse
            break

    if not found_nurse:
        return f"Error: Nurse '{nurse_id}' not found."

    # Parse dates
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        return (
            f"Error: Invalid start_date format '{start_date}'. Use YYYY-MM-DD."
        )

    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return (
                f"Error: Invalid end_date format '{end_date}'. Use YYYY-MM-DD."
            )
    else:
        end = start

    if end < start:
        return f"Error: end_date ({end_date}) cannot be before start_date ({start_date})."

    # Sanitize reason (remove underscores to avoid parsing issues)
    reason = reason.replace("_", "-")

    # Generate time-off entries for each day in the range
    # Format: "Off_YYYY-MM-DD_Reason_XXX"
    prefs = found_nurse.get("preferences", {})
    if "adhoc_requests" not in prefs:
        prefs["adhoc_requests"] = []

    added_dates = []
    skipped_dates = []
    current = start
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        request_entry = f"Off_{date_str}_Reason_{reason}"

        # Check if this date already has a time-off request
        existing = [
            r
            for r in prefs["adhoc_requests"]
            if r.startswith(f"Off_{date_str}_")
        ]
        if existing:
            skipped_dates.append(date_str)
        else:
            prefs["adhoc_requests"].append(request_entry)
            added_dates.append(date_str)

        current += timedelta(days=1)

    if not added_dates:
        return f"No new time-off added. All dates already have existing requests: {', '.join(skipped_dates)}"

    found_nurse["preferences"] = prefs
    _save_hris(nurses)

    # Build response
    result = "SUCCESS: Time-off request added.\n\n"
    result += "TIME-OFF DETAILS\n"
    result += f"{'=' * 40}\n"
    result += f"Nurse: {found_nurse['name']} ({found_nurse['id']})\n"
    result += f"Reason: {reason}\n"
    result += f"Period: {start_date} to {end.strftime('%Y-%m-%d')}\n"
    result += f"Days blocked: {len(added_dates)}\n"

    if len(added_dates) <= MAX_INLINE_DATES:
        result += f"Dates: {', '.join(added_dates)}\n"
    else:
        result += f"Dates: {added_dates[0]} ... {added_dates[-1]} ({len(added_dates)} days)\n"

    if skipped_dates:
        result += f"\nSkipped (already blocked): {', '.join(skipped_dates)}\n"

    result += "\nThe nurse will NOT be assigned shifts on these dates."

    return result


def remove_time_off_request(
    nurse_id: str,
    start_date: str = "",
    end_date: str = "",
    clear_all: bool = False,
) -> str:
    """
    Removes time-off requests for a nurse.

    Args:
        nurse_id: The nurse's ID (e.g., "nurse_002") or name
        start_date: Start date to remove in YYYY-MM-DD format (required unless clear_all=True)
        end_date: End date to remove in YYYY-MM-DD format (defaults to start_date)
        clear_all: If True, removes ALL time-off requests for the nurse

    Returns:
        Confirmation message.

    Examples:
        - Remove single day: remove_time_off_request("Bob", "2025-12-10")
        - Remove period: remove_time_off_request("Bob", "2025-12-09", "2025-12-15")
        - Clear all: remove_time_off_request("Bob", clear_all=True)
    """
    nurses = _load_hris()

    # Find nurse by ID or name
    found_nurse = None
    for nurse in nurses:
        if (
            nurse.get("id") == nurse_id
            or nurse.get("name", "").lower() == nurse_id.lower()
        ):
            found_nurse = nurse
            break

    if not found_nurse:
        return f"Error: Nurse '{nurse_id}' not found."

    prefs = found_nurse.get("preferences", {})
    adhoc = prefs.get("adhoc_requests", [])

    if not adhoc:
        return f"No time-off requests found for {found_nurse['name']}."

    if clear_all:
        # Remove all time-off requests
        time_off_requests = [r for r in adhoc if r.startswith("Off_")]
        other_requests = [r for r in adhoc if not r.startswith("Off_")]

        if not time_off_requests:
            return f"No time-off requests found for {found_nurse['name']}."

        prefs["adhoc_requests"] = other_requests
        found_nurse["preferences"] = prefs
        _save_hris(nurses)

        result = "SUCCESS: All time-off requests cleared.\n\n"
        result += f"Nurse: {found_nurse['name']} ({found_nurse['id']})\n"
        result += f"Removed: {len(time_off_requests)} time-off request(s)\n"
        result += "\nThe nurse is now available for scheduling on all dates."
        return result

    # Remove specific dates
    if not start_date:
        return "Error: start_date is required (or use clear_all=True to remove all requests)."

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        return (
            f"Error: Invalid start_date format '{start_date}'. Use YYYY-MM-DD."
        )

    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return (
                f"Error: Invalid end_date format '{end_date}'. Use YYYY-MM-DD."
            )
    else:
        end = start

    # Find and remove matching requests
    dates_to_remove = set()
    current = start
    while current <= end:
        dates_to_remove.add(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    removed = []
    remaining = []
    for req in adhoc:
        if req.startswith("Off_"):
            parts = req.split("_")
            if len(parts) >= 2 and parts[1] in dates_to_remove:  # noqa: PLR2004
                removed.append(req)
                continue
        remaining.append(req)

    if not removed:
        return f"No time-off requests found for {found_nurse['name']} in the specified period ({start_date} to {end.strftime('%Y-%m-%d')})."

    prefs["adhoc_requests"] = remaining
    found_nurse["preferences"] = prefs
    _save_hris(nurses)

    result = "SUCCESS: Time-off request(s) removed.\n\n"
    result += f"Nurse: {found_nurse['name']} ({found_nurse['id']})\n"
    result += f"Period: {start_date} to {end.strftime('%Y-%m-%d')}\n"
    result += f"Removed: {len(removed)} day(s)\n"
    result += "\nThe nurse is now available for scheduling on these dates."

    return result


def list_time_off_requests(nurse_id: str = "") -> str:
    """
    Lists all time-off requests, optionally filtered by nurse.

    Args:
        nurse_id: Optional nurse ID or name to filter by. If empty, shows all nurses.

    Returns:
        Formatted list of all time-off requests.
    """
    nurses = _load_hris()

    if nurse_id:
        # Filter to specific nurse
        found_nurse = None
        for nurse in nurses:
            if (
                nurse.get("id") == nurse_id
                or nurse.get("name", "").lower() == nurse_id.lower()
            ):
                found_nurse = nurse
                break

        if not found_nurse:
            return f"Error: Nurse '{nurse_id}' not found."

        nurses = [found_nurse]

    result = "TIME-OFF REQUESTS\n" + "=" * 50 + "\n\n"

    total_requests = 0
    nurses_with_requests = 0

    for nurse in nurses:
        prefs = nurse.get("preferences", {})
        adhoc = prefs.get("adhoc_requests", [])
        time_off = [r for r in adhoc if r.startswith("Off_")]

        if time_off:
            nurses_with_requests += 1
            result += f"{nurse['name']} ({nurse['id']}):\n"

            # Parse and sort by date
            parsed = []
            for req in time_off:
                parts = req.split("_")
                if len(parts) >= 4:  # noqa: PLR2004
                    date = parts[1]
                    reason = parts[3] if len(parts) > 3 else "Unspecified"  # noqa: PLR2004
                    parsed.append((date, reason))
                elif len(parts) >= 2:  # noqa: PLR2004
                    parsed.append((parts[1], "Unspecified"))

            parsed.sort(key=lambda x: x[0])

            # Group consecutive dates with same reason
            if parsed:
                groups = []
                current_group = {
                    "start": parsed[0][0],
                    "end": parsed[0][0],
                    "reason": parsed[0][1],
                }

                for i in range(1, len(parsed)):
                    date, reason = parsed[i]
                    prev_date = datetime.strptime(
                        current_group["end"], "%Y-%m-%d"
                    )
                    curr_date = datetime.strptime(date, "%Y-%m-%d")

                    if (
                        curr_date - prev_date
                    ).days == 1 and reason == current_group["reason"]:
                        current_group["end"] = date
                    else:
                        groups.append(current_group)
                        current_group = {
                            "start": date,
                            "end": date,
                            "reason": reason,
                        }

                groups.append(current_group)

                for g in groups:
                    if g["start"] == g["end"]:
                        result += f"  - {g['start']}: {g['reason']}\n"
                    else:
                        start_dt = datetime.strptime(g["start"], "%Y-%m-%d")
                        end_dt = datetime.strptime(g["end"], "%Y-%m-%d")
                        days = (end_dt - start_dt).days + 1
                        result += f"  - {g['start']} to {g['end']} ({days} days): {g['reason']}\n"

                total_requests += len(time_off)
            result += "\n"

    if nurses_with_requests == 0:
        result += "No time-off requests found.\n"
    else:
        result += "-" * 50 + "\n"
        result += f"Total: {total_requests} day(s) blocked for {nurses_with_requests} nurse(s)\n"

    return result
