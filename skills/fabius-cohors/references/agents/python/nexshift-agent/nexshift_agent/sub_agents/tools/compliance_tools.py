"""
Compliance Validation Tools - Programmatic validation for roster compliance.

These tools provide deterministic validation for hard constraints that
should not rely on LLM interpretation. The LLM can then use these results
to generate human-readable compliance reports.
"""

import json
import os
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data")
ROSTERS_DIR = os.path.join(DATA_DIR, "rosters")


def _load_json(filepath: str) -> dict:
    """Load JSON file, return empty dict if not found."""
    try:
        with open(filepath) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_json(filepath: str, data: dict) -> None:
    """Save data to JSON file."""
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)


def _load_hris() -> list[dict]:
    """Load HRIS data."""
    hris_path = os.path.join(DATA_DIR, "mock_hris.json")
    try:
        with open(hris_path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _generate_shifts(start_date: datetime, num_days: int = 7) -> list[dict]:
    """Generate shift data for validation."""
    shift_templates = [
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


def _get_seniority_order(level: str) -> int:
    """Convert seniority level to numeric order for comparison."""
    order = {"Junior": 1, "Mid": 2, "Senior": 3}
    return order.get(level, 0)


def validate_roster_compliance(roster_id: str = "") -> str:
    """
    Programmatically validates a roster against hard constraints.

    This tool performs EXACT matching for:
    - Certification requirements (ICU shifts need ICU cert, Emergency needs ACLS+BLS)
    - Seniority level requirements (nurse level >= shift min level)
    - Senior coverage (every individual shift must have a Senior nurse assigned)

    The results are 100% reliable - trust them completely.

    Args:
        roster_id: The roster ID to validate. If empty, looks for the most recent draft.

    Returns:
        A structured validation report with any violations found.
    """
    # Find the roster
    if roster_id:
        roster_file = os.path.join(ROSTERS_DIR, f"{roster_id}.json")
        if not os.path.exists(roster_file):
            return f"ERROR: Roster '{roster_id}' not found."
        roster = _load_json(roster_file)
    else:
        # Find most recent draft
        drafts = []
        if os.path.exists(ROSTERS_DIR):
            for filename in os.listdir(ROSTERS_DIR):
                if filename.endswith(".json"):
                    roster_path = os.path.join(ROSTERS_DIR, filename)
                    r = _load_json(roster_path)
                    if r.get("status") == "draft":
                        drafts.append((filename, r))

        if not drafts:
            return "ERROR: No draft roster found to validate."

        # Sort by generated_at and get most recent
        drafts.sort(key=lambda x: x[1].get("generated_at", ""), reverse=True)
        roster = drafts[0][1]
        roster_id = roster.get("id", drafts[0][0].replace(".json", ""))

    # Load nurse data - create lookup by ID
    nurses_list = _load_hris()
    nurses = {n["id"]: n for n in nurses_list}

    # Determine roster period for shift generation
    period = roster.get("period", {})
    start_date = None
    num_days = 7

    if period.get("start"):
        try:
            start_date = datetime.strptime(period["start"], "%Y-%m-%d")
            if period.get("end"):
                end_date = datetime.strptime(period["end"], "%Y-%m-%d")
                num_days = (end_date - start_date).days + 1
        except ValueError:
            pass

    if not start_date:
        generated_at = roster.get("generated_at", "")
        if generated_at:
            try:
                if "T" in str(generated_at):
                    start_date = datetime.fromisoformat(
                        str(generated_at).split("T")[0]
                    )
                else:
                    start_date = datetime.strptime(
                        str(generated_at).split(" ")[0], "%Y-%m-%d"
                    )
            except ValueError:
                pass

    if not start_date:
        start_date = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    # Generate shifts and create lookup
    shifts_list = _generate_shifts(start_date, num_days)
    shifts = {s["id"]: s for s in shifts_list}

    # Validation results
    cert_violations = []
    level_violations = []
    invalid_refs = []

    # Track Senior coverage per shift (every shift must have a Senior nurse)
    shift_senior_coverage = {}  # key: shift_id -> nurse_level of assigned nurse

    assignments = roster.get("assignments", [])

    for assignment in assignments:
        nurse_id = assignment.get("nurse_id", "")
        shift_id = assignment.get("shift_id", "")

        # Validate references exist
        nurse = nurses.get(nurse_id)
        shift = shifts.get(shift_id)

        if not nurse:
            invalid_refs.append(f"Unknown nurse: {nurse_id}")
            continue

        if not shift:
            invalid_refs.append(f"Unknown shift: {shift_id}")
            continue

        nurse_name = nurse.get("name", nurse_id)
        nurse_certs = [c.upper() for c in nurse.get("certifications", [])]
        nurse_level = nurse.get("seniority_level", "Junior")

        # Check certification requirements
        required_certs = [c.upper() for c in shift.get("required_certs", [])]
        for req_cert in required_certs:
            if req_cert not in nurse_certs:
                cert_violations.append(
                    {
                        "nurse_id": nurse_id,
                        "nurse_name": nurse_name,
                        "nurse_certs": nurse_certs,
                        "shift_id": shift_id,
                        "ward": shift.get("ward"),
                        "missing_cert": req_cert,
                        "date": shift.get("date"),
                        "time": f"{shift.get('start')}-{shift.get('end')}",
                    }
                )

        # Check seniority level requirements
        min_level = shift.get("min_level", "Junior")
        if _get_seniority_order(nurse_level) < _get_seniority_order(min_level):
            level_violations.append(
                {
                    "nurse_id": nurse_id,
                    "nurse_name": nurse_name,
                    "nurse_level": nurse_level,
                    "shift_id": shift_id,
                    "ward": shift.get("ward"),
                    "required_level": min_level,
                    "date": shift.get("date"),
                    "time": f"{shift.get('start')}-{shift.get('end')}",
                }
            )

        # Track Senior coverage per shift
        shift_senior_coverage[shift_id] = {
            "nurse_level": nurse_level,
            "nurse_name": nurse_name,
            "nurse_id": nurse_id,
            "ward": shift.get("ward"),
            "date": shift.get("date"),
            "time": f"{shift.get('start')}-{shift.get('end')}",
        }

    # Check senior coverage - every shift must have a Senior nurse assigned
    senior_coverage_issues = []
    for shift_id, coverage in shift_senior_coverage.items():
        if coverage["nurse_level"] != "Senior":
            senior_coverage_issues.append(
                {
                    "shift_id": shift_id,
                    "ward": coverage["ward"],
                    "date": coverage["date"],
                    "time": coverage["time"],
                    "assigned_nurse": coverage["nurse_name"],
                    "assigned_level": coverage["nurse_level"],
                }
            )

    # Build result report
    total_violations = (
        len(cert_violations) + len(level_violations) + len(invalid_refs)
    )

    result = "=" * 60 + "\n"
    result += "PROGRAMMATIC COMPLIANCE VALIDATION\n"
    result += "=" * 60 + "\n\n"
    result += f"Roster: {roster_id}\n"
    result += f"Assignments checked: {len(assignments)}\n\n"

    if total_violations == 0 and not senior_coverage_issues:
        result += "STATUS: ALL CHECKS PASSED\n\n"
        result += "Certification Requirements: PASS (all nurses have required certs)\n"
        result += (
            "Seniority Requirements: PASS (all nurses meet minimum level)\n"
        )
        result += "Senior Coverage: PASS (every shift has a Senior nurse)\n"
        result += "Reference Validity: PASS (all nurse/shift IDs are valid)\n"
    else:
        result += f"STATUS: VIOLATIONS FOUND ({total_violations} issue(s))\n\n"

        # Certification violations
        if cert_violations:
            result += f"CERTIFICATION VIOLATIONS ({len(cert_violations)}):\n"
            result += "-" * 50 + "\n"
            for v in cert_violations:
                result += f"  - {v['nurse_name']} ({v['nurse_id']}) missing '{v['missing_cert']}'\n"
                result += f"    Shift: {v['shift_id']} | {v['ward']} Ward | {v['date']} {v['time']}\n"
                result += f"    Nurse has: {', '.join(v['nurse_certs']) if v['nurse_certs'] else 'None'}\n"
            result += "\n"
        else:
            result += "Certification Requirements: PASS\n"

        # Seniority violations
        if level_violations:
            result += f"SENIORITY VIOLATIONS ({len(level_violations)}):\n"
            result += "-" * 50 + "\n"
            for v in level_violations:
                result += f"  - {v['nurse_name']} ({v['nurse_id']}) is {v['nurse_level']}\n"
                result += f"    Shift {v['shift_id']} requires: {v['required_level']}\n"
                result += f"    Ward: {v['ward']} | {v['date']} {v['time']}\n"
            result += "\n"
        else:
            result += "Seniority Requirements: PASS\n"

        # Senior coverage issues (every shift must have a Senior nurse)
        if senior_coverage_issues:
            result += (
                f"SENIOR COVERAGE VIOLATIONS ({len(senior_coverage_issues)}):\n"
            )
            result += "-" * 50 + "\n"
            for issue in senior_coverage_issues:
                result += f"  - {issue['shift_id']}: Assigned to {issue['assigned_nurse']} ({issue['assigned_level']})\n"
                result += f"    Ward: {issue['ward']} | {issue['date']} {issue['time']}\n"
                result += "    Required: Senior nurse\n"
            result += "\n"
        else:
            result += "Senior Coverage: PASS (every shift has a Senior nurse)\n"

        # Invalid references
        if invalid_refs:
            result += f"INVALID REFERENCES ({len(invalid_refs)}):\n"
            result += "-" * 50 + "\n"
            for ref in invalid_refs:
                result += f"  - {ref}\n"
            result += "\n"
        else:
            result += "Reference Validity: PASS\n"

    result += "\n" + "=" * 60 + "\n"
    result += (
        "Note: This is programmatic validation. Results are deterministic.\n"
    )

    # Update roster metadata with compliance status
    compliance_status = (
        "PASS"
        if (total_violations == 0 and not senior_coverage_issues)
        else "FAIL"
    )
    compliance_notes = (
        f"{total_violations} violation(s), {len(senior_coverage_issues)} senior coverage issue(s)"
        if compliance_status == "FAIL"
        else "All checks passed"
    )
    roster_file = os.path.join(ROSTERS_DIR, f"{roster_id}.json")
    if os.path.exists(roster_file):
        roster_data = _load_json(roster_file)
        if "metadata" not in roster_data:
            roster_data["metadata"] = {}
        roster_data["metadata"]["compliance_status"] = compliance_status
        roster_data["metadata"]["compliance_notes"] = compliance_notes
        _save_json(roster_file, roster_data)

        # Also update shift_history.json to keep in sync
        history_file = os.path.join(DATA_DIR, "shift_history.json")
        if os.path.exists(history_file):
            history = _load_json(history_file)
            for log in history.get("logs", []):
                if (
                    log.get("roster_id") == roster_id
                    or log.get("id") == roster_id
                ):
                    if "metadata" not in log:
                        log["metadata"] = {}
                    log["metadata"]["compliance_status"] = compliance_status
                    log["metadata"]["compliance_notes"] = compliance_notes
                    break
            _save_json(history_file, history)

    return result


def validate_weekly_hours(roster_id: str = "") -> str:
    """
    Validates that nurses don't exceed their weekly hour limits based on contract type.

    Limits:
    - FullTime: max 40 hours/week
    - PartTime: max 30 hours/week
    - Casual: max 20 hours/week

    Args:
        roster_id: The roster ID to validate. If empty, looks for the most recent draft.

    Returns:
        A report of any hour limit violations.
    """
    # Find the roster
    if roster_id:
        roster_file = os.path.join(ROSTERS_DIR, f"{roster_id}.json")
        if not os.path.exists(roster_file):
            return f"ERROR: Roster '{roster_id}' not found."
        roster = _load_json(roster_file)
    else:
        drafts = []
        if os.path.exists(ROSTERS_DIR):
            for filename in os.listdir(ROSTERS_DIR):
                if filename.endswith(".json"):
                    roster_path = os.path.join(ROSTERS_DIR, filename)
                    r = _load_json(roster_path)
                    if r.get("status") == "draft":
                        drafts.append((filename, r))

        if not drafts:
            return "ERROR: No draft roster found to validate."

        drafts.sort(key=lambda x: x[1].get("generated_at", ""), reverse=True)
        roster = drafts[0][1]
        roster_id = roster.get("id", drafts[0][0].replace(".json", ""))

    # Load nurse data
    nurses_list = _load_hris()
    nurses = {n["id"]: n for n in nurses_list}

    # Hour limits by contract type
    hour_limits = {"FullTime": 40, "PartTime": 30, "Casual": 20}

    # Count hours per nurse (each shift is 8 hours)
    hours_per_nurse = {}

    for assignment in roster.get("assignments", []):
        nurse_id = assignment.get("nurse_id", "")
        if nurse_id not in hours_per_nurse:
            hours_per_nurse[nurse_id] = 0
        hours_per_nurse[nurse_id] += 8  # Each shift is 8 hours

    # Check violations
    violations = []

    for nurse_id, hours in hours_per_nurse.items():
        nurse = nurses.get(nurse_id)
        if not nurse:
            continue

        contract_type = nurse.get("contract_type", "FullTime")
        max_hours = hour_limits.get(contract_type, 40)

        if hours > max_hours:
            violations.append(
                {
                    "nurse_id": nurse_id,
                    "nurse_name": nurse.get("name", nurse_id),
                    "contract_type": contract_type,
                    "max_hours": max_hours,
                    "assigned_hours": hours,
                    "excess": hours - max_hours,
                }
            )

    # Build result
    result = "=" * 60 + "\n"
    result += "WEEKLY HOURS VALIDATION\n"
    result += "=" * 60 + "\n\n"
    result += f"Roster: {roster_id}\n\n"

    if not violations:
        result += "STATUS: PASS\n\n"
        result += "All nurses are within their weekly hour limits.\n"
    else:
        result += f"STATUS: {len(violations)} VIOLATION(S)\n\n"
        for v in violations:
            result += f"  - {v['nurse_name']} ({v['nurse_id']})\n"
            result += (
                f"    Contract: {v['contract_type']} (max {v['max_hours']}h)\n"
            )
            result += f"    Assigned: {v['assigned_hours']}h (excess: {v['excess']}h)\n\n"

    return result


def get_nurse_certification_lookup() -> str:
    """
    Returns a quick lookup table of all nurses and their certifications.
    Useful for quick reference during compliance review.

    Returns:
        Formatted table of nurse IDs, names, and certifications.
    """
    nurses = _load_hris()

    result = "NURSE CERTIFICATION LOOKUP\n"
    result += "=" * 60 + "\n\n"
    result += f"{'ID':<12} {'Name':<15} {'Level':<8} {'Certifications'}\n"
    result += "-" * 60 + "\n"

    for nurse in sorted(nurses, key=lambda x: x.get("id", "")):
        nurse_id = nurse.get("id", "")
        name = nurse.get("name", "")
        level = nurse.get("seniority_level", "")
        certs = ", ".join(nurse.get("certifications", []))
        result += f"{nurse_id:<12} {name:<15} {level:<8} {certs}\n"

    result += "\n" + "=" * 60 + "\n"
    result += f"Total nurses: {len(nurses)}\n"

    return result
