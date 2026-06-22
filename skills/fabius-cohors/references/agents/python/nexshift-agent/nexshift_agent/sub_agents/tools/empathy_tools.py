"""
Empathy Validation Tools - Tools for empathy-focused roster analysis.

These tools help the Empathy Advocate agent analyze rosters for fairness,
burnout prevention, and preference honoring.
"""

import json
import os
from datetime import datetime, timedelta

from nexshift_agent.sub_agents.config import (
    BURNOUT_HEAVY_WORKLOAD_SHIFTS,
    BURNOUT_MANY_NIGHT_SHIFTS,
    BURNOUT_MULTIPLE_WEEKEND_SHIFTS,
    DISPLAY_MAX_ITEMS,
    EMPATHY_ACCEPTABLE_THRESHOLD,
    EMPATHY_BURNOUT_PENALTY,
    EMPATHY_BURNOUT_PENALTY_CAP,
    EMPATHY_GOOD_THRESHOLD,
    EMPATHY_PREFERENCE_PENALTY,
    EMPATHY_PREFERENCE_PENALTY_CAP,
    FATIGUE_DISPLAY_HIGH,
    FATIGUE_DISPLAY_MODERATE,
    SHIFT_VARIANCE_HIGH,
    SHIFT_VARIANCE_HIGH_DEDUCTION,
    SHIFT_VARIANCE_MODERATE,
    SHIFT_VARIANCE_MODERATE_DEDUCTION,
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data")
ROSTERS_DIR = os.path.join(DATA_DIR, "rosters")
NURSE_STATS_FILE = os.path.join(DATA_DIR, "nurse_stats.json")


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
    """Generate shift data for analysis."""
    shift_templates = [
        {"ward": "ICU", "start": "00:00", "end": "08:00", "all_week": True},
        {"ward": "ICU", "start": "08:00", "end": "16:00", "all_week": True},
        {"ward": "ICU", "start": "16:00", "end": "00:00", "all_week": True},
        {
            "ward": "Emergency",
            "start": "00:00",
            "end": "08:00",
            "all_week": True,
        },
        {
            "ward": "Emergency",
            "start": "08:00",
            "end": "16:00",
            "all_week": True,
        },
        {
            "ward": "Emergency",
            "start": "16:00",
            "end": "00:00",
            "all_week": True,
        },
        {
            "ward": "General",
            "start": "08:00",
            "end": "16:00",
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
                    "is_night": template["start"] == "00:00"
                    or str(template["start"]) >= "20:00",
                    "is_weekend": is_weekend,
                }
            )
            shift_counter += 1

    return shifts


def get_roster_assignments(roster_id: str = "") -> str:
    """
    Retrieves all assignments from a specific roster with detailed shift information.

    This tool loads a roster and enriches each assignment with:
    - Nurse name and preferences
    - Shift details (ward, date, time)
    - Whether it's a night shift or weekend shift

    Args:
        roster_id: The roster ID to load. If empty, loads the most recent draft.

    Returns:
        Formatted string with all assignments and their details.
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
            return "ERROR: No draft roster found."

        drafts.sort(key=lambda x: x[1].get("generated_at", ""), reverse=True)
        roster = drafts[0][1]
        roster_id = roster.get("id", drafts[0][0].replace(".json", ""))

    # Load nurse data
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

    assignments = roster.get("assignments", [])

    # Build result
    result = "=" * 60 + "\n"
    result += f"ROSTER ASSIGNMENTS: {roster_id}\n"
    result += "=" * 60 + "\n\n"
    result += (
        f"Period: {period.get('start', 'N/A')} to {period.get('end', 'N/A')}\n"
    )
    result += f"Total Assignments: {len(assignments)}\n\n"

    # Group by nurse for empathy analysis
    by_nurse = {}
    for assignment in assignments:
        nurse_id = assignment.get("nurse_id", "")
        shift_id = assignment.get("shift_id", "")

        nurse = nurses.get(nurse_id, {})
        shift = shifts.get(shift_id, {})

        if nurse_id not in by_nurse:
            by_nurse[nurse_id] = {
                "name": nurse.get("name", nurse_id),
                "preferences": nurse.get("preferences", {}),
                "seniority": nurse.get("seniority_level", "Unknown"),
                "contract": nurse.get("contract_type", "Unknown"),
                "shifts": [],
            }

        by_nurse[nurse_id]["shifts"].append(
            {
                "shift_id": shift_id,
                "ward": shift.get("ward", "?"),
                "date": shift.get("date", "?"),
                "day": shift.get("day", "?"),
                "time": f"{shift.get('start', '?')}-{shift.get('end', '?')}",
                "is_night": shift.get("is_night", False),
                "is_weekend": shift.get("is_weekend", False),
            }
        )

    # Format output by nurse
    result += "ASSIGNMENTS BY NURSE:\n"
    result += "-" * 60 + "\n\n"

    for nurse_id in sorted(by_nurse.keys()):
        info = by_nurse[nurse_id]
        prefs = info["preferences"]

        result += f"👤 {info['name']} ({nurse_id})\n"
        result += f"   Seniority: {info['seniority']} | Contract: {info['contract']}\n"
        result += "   Preferences:\n"
        result += f"     - Avoid night shifts: {prefs.get('avoid_night_shifts', False)}\n"
        result += f"     - Preferred days: {', '.join(prefs.get('preferred_days', [])) or 'None'}\n"

        # Count shift types
        total = len(info["shifts"])
        nights = sum(1 for s in info["shifts"] if s["is_night"])
        weekends = sum(1 for s in info["shifts"] if s["is_weekend"])

        result += f"   Assigned: {total} shifts ({nights} night, {weekends} weekend)\n"

        # Check for preference violations
        violations = []
        if prefs.get("avoid_night_shifts") and nights > 0:
            violations.append(
                f"⚠️ Has {nights} night shift(s) despite preference to avoid"
            )

        preferred_days = prefs.get("preferred_days", [])
        if preferred_days:
            non_preferred = [
                s for s in info["shifts"] if s["day"] not in preferred_days
            ]
            if non_preferred:
                violations.append(
                    f"⚠️ {len(non_preferred)} shift(s) on non-preferred days"
                )

        if violations:
            result += "   Concerns:\n"
            for v in violations:
                result += f"     {v}\n"

        result += "   Schedule:\n"
        for s in sorted(info["shifts"], key=lambda x: (x["date"], x["time"])):
            night_marker = "🌙" if s["is_night"] else "  "
            weekend_marker = "📅" if s["is_weekend"] else "  "
            result += f"     {s['date']} ({s['day'][:3]}) {s['time']} {s['ward']:10} {night_marker}{weekend_marker}\n"

        result += "\n"

    return result


def analyze_roster_fairness(roster_id: str = "") -> str:
    """
    Analyzes a roster for fairness metrics and potential burnout risks.

    This tool computes:
    - Shift distribution across nurses
    - Weekend shift fairness
    - Night shift distribution
    - Preference violation summary
    - Burnout risk indicators

    Args:
        roster_id: The roster ID to analyze. If empty, analyzes the most recent draft.

    Returns:
        A fairness analysis report with metrics and concerns.
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
            return "ERROR: No draft roster found."

        drafts.sort(key=lambda x: x[1].get("generated_at", ""), reverse=True)
        roster = drafts[0][1]
        roster_id = roster.get("id", drafts[0][0].replace(".json", ""))

    # Load data
    nurses_list = _load_hris()
    nurses = {n["id"]: n for n in nurses_list}
    stats = _load_json(NURSE_STATS_FILE)

    # Determine roster period
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
        start_date = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    shifts_list = _generate_shifts(start_date, num_days)
    shifts = {s["id"]: s for s in shifts_list}

    # Analyze assignments
    nurse_metrics = {}
    preference_violations = []

    for assignment in roster.get("assignments", []):
        nurse_id = assignment.get("nurse_id", "")
        shift_id = assignment.get("shift_id", "")

        nurse = nurses.get(nurse_id, {})
        shift = shifts.get(shift_id, {})

        if nurse_id not in nurse_metrics:
            nurse_metrics[nurse_id] = {
                "name": nurse.get("name", nurse_id),
                "contract": nurse.get("contract_type", "FullTime"),
                "total_shifts": 0,
                "night_shifts": 0,
                "weekend_shifts": 0,
                "hours": 0,
                "fatigue_score": stats.get(nurse_id, {}).get(
                    "fatigue_score", 0
                ),
                "prefs": nurse.get("preferences", {}),
            }

        m = nurse_metrics[nurse_id]
        m["total_shifts"] += 1
        m["hours"] += 8

        if shift.get("is_night"):
            m["night_shifts"] += 1
            if m["prefs"].get("avoid_night_shifts"):
                preference_violations.append(
                    {
                        "nurse": m["name"],
                        "nurse_id": nurse_id,
                        "type": "night_shift",
                        "detail": f"Assigned night shift on {shift.get('date')}",
                    }
                )

        if shift.get("is_weekend"):
            m["weekend_shifts"] += 1

        preferred_days = m["prefs"].get("preferred_days", [])
        if preferred_days and shift.get("day") not in preferred_days:
            preference_violations.append(
                {
                    "nurse": m["name"],
                    "nurse_id": nurse_id,
                    "type": "non_preferred_day",
                    "detail": f"Assigned on {shift.get('day')} (prefers: {', '.join(preferred_days)})",
                }
            )

    # Calculate fairness metrics
    if nurse_metrics:
        shift_counts = [m["total_shifts"] for m in nurse_metrics.values()]
        weekend_counts = [m["weekend_shifts"] for m in nurse_metrics.values()]
        night_counts = [m["night_shifts"] for m in nurse_metrics.values()]

        avg_shifts = sum(shift_counts) / len(shift_counts)
        max_shifts = max(shift_counts)
        min_shifts = min(shift_counts)
        shift_variance = max_shifts - min_shifts

        avg_weekends = (
            sum(weekend_counts) / len(weekend_counts) if weekend_counts else 0
        )
        avg_nights = (
            sum(night_counts) / len(night_counts) if night_counts else 0
        )
    else:
        avg_shifts = max_shifts = min_shifts = shift_variance = 0
        avg_weekends = avg_nights = 0

    # Identify burnout risks
    burnout_risks = []
    for nurse_id, m in nurse_metrics.items():
        risk_factors = []

        if m["fatigue_score"] >= FATIGUE_DISPLAY_HIGH:
            risk_factors.append(
                f"High fatigue score ({m['fatigue_score']:.2f})"
            )

        if m["total_shifts"] >= BURNOUT_HEAVY_WORKLOAD_SHIFTS:
            risk_factors.append(f"Heavy workload ({m['total_shifts']} shifts)")

        if m["night_shifts"] >= BURNOUT_MANY_NIGHT_SHIFTS:
            risk_factors.append(f"Many night shifts ({m['night_shifts']})")

        if m["weekend_shifts"] >= BURNOUT_MULTIPLE_WEEKEND_SHIFTS:
            risk_factors.append(
                f"Multiple weekend shifts ({m['weekend_shifts']})"
            )

        if risk_factors:
            burnout_risks.append(
                {
                    "nurse": m["name"],
                    "nurse_id": nurse_id,
                    "factors": risk_factors,
                }
            )

    # Calculate empathy score
    # Start at 1.0 and deduct for issues
    empathy_score = 1.0

    # Deduct for preference violations
    pref_penalty = min(
        len(preference_violations) * EMPATHY_PREFERENCE_PENALTY,
        EMPATHY_PREFERENCE_PENALTY_CAP,
    )
    empathy_score -= pref_penalty

    # Deduct for shift imbalance
    if shift_variance > SHIFT_VARIANCE_HIGH:
        empathy_score -= SHIFT_VARIANCE_HIGH_DEDUCTION
    elif shift_variance > SHIFT_VARIANCE_MODERATE:
        empathy_score -= SHIFT_VARIANCE_MODERATE_DEDUCTION

    # Deduct for burnout risks
    burnout_penalty = min(
        len(burnout_risks) * EMPATHY_BURNOUT_PENALTY,
        EMPATHY_BURNOUT_PENALTY_CAP,
    )
    empathy_score -= burnout_penalty

    empathy_score = max(0.0, round(empathy_score, 2))

    # Build result
    result = "=" * 60 + "\n"
    result += "ROSTER FAIRNESS ANALYSIS\n"
    result += "=" * 60 + "\n\n"
    result += f"Roster: {roster_id}\n"
    result += f"Nurses scheduled: {len(nurse_metrics)}\n\n"

    result += f"EMPATHY SCORE: {empathy_score:.2f}\n"
    if empathy_score >= EMPATHY_GOOD_THRESHOLD:
        result += "Assessment: GOOD - Roster is fair and considerate\n\n"
    elif empathy_score >= EMPATHY_ACCEPTABLE_THRESHOLD:
        result += "Assessment: ACCEPTABLE - Some concerns but workable\n\n"
    else:
        result += (
            "Assessment: NEEDS ATTENTION - Significant fairness issues\n\n"
        )

    result += "DISTRIBUTION METRICS:\n"
    result += "-" * 40 + "\n"
    result += f"  Average shifts per nurse: {avg_shifts:.1f}\n"
    result += f"  Shift range: {min_shifts} to {max_shifts} (variance: {shift_variance})\n"
    result += f"  Average weekend shifts: {avg_weekends:.1f}\n"
    result += f"  Average night shifts: {avg_nights:.1f}\n\n"

    if preference_violations:
        result += f"PREFERENCE VIOLATIONS ({len(preference_violations)}):\n"
        result += "-" * 40 + "\n"
        for v in preference_violations[:DISPLAY_MAX_ITEMS]:
            result += f"  - {v['nurse']}: {v['detail']}\n"
        if len(preference_violations) > DISPLAY_MAX_ITEMS:
            result += f"  ... and {len(preference_violations) - DISPLAY_MAX_ITEMS} more\n"
        result += "\n"
    else:
        result += "PREFERENCE VIOLATIONS: None\n\n"

    if burnout_risks:
        result += f"BURNOUT RISKS ({len(burnout_risks)}):\n"
        result += "-" * 40 + "\n"
        for r in burnout_risks:
            result += f"  ⚠️ {r['nurse']} ({r['nurse_id']}):\n"
            for f in r["factors"]:
                result += f"     - {f}\n"
        result += "\n"
    else:
        result += "BURNOUT RISKS: None identified\n\n"

    result += "NURSE WORKLOAD SUMMARY:\n"
    result += "-" * 40 + "\n"
    result += (
        f"{'Name':<15} {'Shifts':>6} {'Night':>6} {'Wknd':>6} {'Fatigue':>8}\n"
    )
    result += "-" * 40 + "\n"

    for nurse_id in sorted(nurse_metrics.keys()):
        m = nurse_metrics[nurse_id]
        fatigue_str = f"{m['fatigue_score']:.2f}"
        if m["fatigue_score"] >= FATIGUE_DISPLAY_HIGH:
            fatigue_str += " 🔴"
        elif m["fatigue_score"] >= FATIGUE_DISPLAY_MODERATE:
            fatigue_str += " 🟡"
        result += f"{m['name']:<15} {m['total_shifts']:>6} {m['night_shifts']:>6} {m['weekend_shifts']:>6} {fatigue_str:>8}\n"

    result += "\n" + "=" * 60 + "\n"

    # Update roster metadata with empathy score
    empathy_notes = (
        f"{len(preference_violations)} preference violation(s), {len(burnout_risks)} burnout risk(s)"
        if empathy_score < EMPATHY_GOOD_THRESHOLD
        else "Good - Roster is fair and considerate"
    )
    roster_file = os.path.join(ROSTERS_DIR, f"{roster_id}.json")
    if os.path.exists(roster_file):
        roster_data = _load_json(roster_file)
        if "metadata" not in roster_data:
            roster_data["metadata"] = {}
        roster_data["metadata"]["empathy_score"] = empathy_score
        roster_data["metadata"]["empathy_notes"] = empathy_notes
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
                    log["metadata"]["empathy_score"] = empathy_score
                    log["metadata"]["empathy_notes"] = empathy_notes
                    break
            _save_json(history_file, history)

    return result
