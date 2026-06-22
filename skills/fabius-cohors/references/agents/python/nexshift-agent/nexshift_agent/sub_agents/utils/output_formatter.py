"""
Universal output formatter for chat-friendly rendering.
Detects content type and converts to well-formatted markdown.
"""

import re
from datetime import datetime, timedelta
from typing import Any

from nexshift_agent.sub_agents.config import (
    DAY_SHIFT_START_HOUR,
    EVENING_SHIFT_START_HOUR,
    NIGHT_SHIFT_START_HOUR,
)


class OutputFormatter:
    """Converts agent output to well-formatted markdown."""

    def format(self, text: str) -> str:
        """
        Detect content type and apply appropriate formatting.
        """
        if not text:
            return text

        # Try each formatter in order of specificity
        if self._is_roster(text):
            return self._format_roster(text)
        elif self._is_nurse_list(text):
            return self._format_nurse_list(text)
        elif self._is_availability(text):
            return self._format_availability(text)
        elif self._is_nurse_profile(text):
            return self._format_nurse_profile(text)
        elif self._is_staffing_summary(text):
            return self._format_staffing_summary(text)
        elif self._is_shifts_list(text):
            return self._format_shifts_list(text)
        elif self._is_pending_rosters(text):
            return self._format_pending_rosters(text)

        # No special formatting needed
        return text

    # =========================================================================
    # Detection methods
    # =========================================================================

    def _is_nurse_list(self, text: str) -> bool:
        return bool(re.search(r"\[(OK|HIGH|MOD)\].*nurse_\d+", text)) or bool(
            re.search(
                r"(ALL NURSES|SENIOR NURSES|AVAILABLE NURSES).*={10,}",
                text,
                re.I | re.S,
            )
        )

    def _is_roster(self, text: str) -> bool:
        # Detect roster output that needs calendar formatting
        # Match patterns like "ROSTER:" or roster IDs with assignments
        # BUT exclude list outputs (ALL ROSTERS, PENDING ROSTERS)
        if re.search(r"ALL ROSTERS|PENDING ROSTERS", text, re.I):
            return False
        return bool(re.search(r"ROSTER[:\s].*roster_\d+", text, re.I)) or bool(
            re.search(r"ASSIGNMENTS:.*\d{4}-\d{2}-\d{2}", text, re.I | re.S)
        )

    def _is_availability(self, text: str) -> bool:
        return bool(
            re.search(r"NURSE AVAILABILITY.*\d{4}-\d{2}-\d{2}", text, re.I)
        )

    def _is_nurse_profile(self, text: str) -> bool:
        return bool(re.search(r"NURSE PROFILE:", text, re.I))

    def _is_staffing_summary(self, text: str) -> bool:
        # Disabled - the raw output is already well-formatted and regex parsing
        # causes issues when LLM reformats the content before callback
        return False

    def _is_shifts_list(self, text: str) -> bool:
        return bool(re.search(r"SHIFTS TO BE FILLED", text, re.I))

    def _is_pending_rosters(self, text: str) -> bool:
        # Disabled - the raw output is already well-formatted
        return False

    # =========================================================================
    # Formatting methods
    # =========================================================================

    def _format_nurse_list(self, text: str) -> str:
        """Format nurse list as markdown table."""
        lines = text.strip().split("\n")

        # Extract title from first line
        title = "Nurses"
        if lines and "=" in lines[0]:
            title = lines[0].strip()
        elif lines:
            title = lines[0].strip()

        # Parse nurse entries
        nurses = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            # Match pattern: [OK] Name (nurse_xxx) or similar
            match = re.match(
                r"\[(OK|HIGH|MOD)\]\s+(\w+)\s+\((nurse_\d+)\)", line
            )
            if match:
                status_code = match.group(1)
                name = match.group(2)
                nurse_id = match.group(3)

                status = (
                    "🟢"
                    if status_code == "OK"
                    else "🟡"
                    if status_code == "MOD"
                    else "🔴"
                )

                # Next line has details
                details = ""
                if i + 1 < len(lines):
                    details = lines[i + 1].strip()
                    i += 1

                # Parse details: "Senior | FullTime | ACLS, BLS, ICU"
                parts = [p.strip() for p in details.split("|")]
                level = parts[0] if len(parts) > 0 else ""
                contract = parts[1] if len(parts) > 1 else ""
                certs = parts[2] if len(parts) > 2 else ""  # noqa: PLR2004

                nurses.append(
                    {
                        "status": status,
                        "name": name,
                        "id": nurse_id,
                        "level": level,
                        "contract": contract,
                        "certs": certs,
                    }
                )
            i += 1

        if not nurses:
            return text  # Couldn't parse, return original

        # Build markdown table
        result = f"## {title}\n\n"
        result += "| Status | Name | ID | Level | Contract | Certifications |\n"
        result += "|--------|------|----|-------|----------|----------------|\n"

        for n in nurses:
            result += f"| {n['status']} | {n['name']} | {n['id']} | {n['level']} | {n['contract']} | {n['certs']} |\n"

        # Extract total if present
        total_match = re.search(r"Total:\s*(\d+)\s*nurses", text, re.I)
        if total_match:
            result += f"\n**Total: {total_match.group(1)} nurses**"

        return result

    def _format_roster(self, text: str) -> str:
        """Format roster as 7-day calendar view."""
        # Extract roster ID - handles formats like roster_202512052008 or roster_20251209165648_2930
        roster_match = re.search(r"(roster_[\w]+)", text, re.I)
        roster_id = roster_match.group(1) if roster_match else "Unknown"

        # Extract status
        status_match = re.search(r"Status:\s*(\w+)", text, re.I)
        status = status_match.group(1).upper() if status_match else "DRAFT"

        # Extract period
        period_match = re.search(
            r"Period:\s*(\d{4}-\d{2}-\d{2}).*?to\s*(\d{4}-\d{2}-\d{2})",
            text,
            re.I,
        )
        if period_match:
            start_date_str = period_match.group(1)
            end_date_str = period_match.group(2)
        else:
            # Try to infer from assignments
            date_matches = re.findall(r"(\d{4}-\d{2}-\d{2})", text)
            if date_matches:
                start_date_str = min(date_matches)
                end_date_str = max(date_matches)
            else:
                return text  # Can't determine period

        # Extract compliance and empathy
        compliance_match = re.search(r"Compliance:\s*(\w+)", text, re.I)
        compliance = compliance_match.group(1) if compliance_match else "N/A"

        empathy_match = re.search(r"Empathy.*?:\s*([\d.]+)", text, re.I)
        empathy = empathy_match.group(1) if empathy_match else "N/A"

        # Parse assignments - look for nurse_id -> shift patterns
        assignments = []
        # Pattern: nurse_xxx → Ward or nurse_xxx -> shift_xxx
        for match in re.finditer(r"(nurse_\d+)\s*(?:→|->)\s*(\w+)", text):
            nurse_id = match.group(1)
            info = match.group(2)
            assignments.append({"nurse_id": nurse_id, "info": info})

        # Also try parsing structured assignment lines
        for match in re.finditer(
            r"'nurse_id':\s*'(nurse_\d+)'.*?'shift_id':\s*'(shift_\d+)'", text
        ):
            nurse_id = match.group(1)
            shift_id = match.group(2)
            assignments.append({"nurse_id": nurse_id, "shift_id": shift_id})

        # Pattern: time | ward | name (nurse_id) - format from get_roster()
        for match in re.finditer(
            r"(\d{2}:\d{2}-\d{2}:\d{2})\s*\|\s*(\w+)[^|]*\|\s*[^(]+\((nurse_\d+)\)",
            text,
        ):
            time_info = match.group(1)
            ward = match.group(2)
            nurse_id = match.group(3)
            assignments.append(
                {"nurse_id": nurse_id, "info": f"{ward} ({time_info})"}
            )

        # Build header
        result = f"## Roster: {roster_id}\n\n"
        result += f"**Period**: {start_date_str} to {end_date_str} | "
        result += f"**Status**: {status} | "
        result += f"**Compliance**: {compliance} | "
        result += f"**Empathy**: {empathy}\n\n"

        # Build calendar view
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            total_days = (end_date - start_date).days + 1

            if not assignments:
                # Could not parse assignments from the text - return original
                # This happens when LLM summarizes instead of returning raw tool output
                return text

            # Parse assignments with date info from get_roster() format
            # Format: "📅 2025-12-04 (Wednesday)" followed by assignment lines
            # "   07:00-15:00 | Ward A     | Alice Smith (nurse_001)"
            nurse_schedule = {}  # {nurse_id: {date_str: ward_shift_type}}
            nurse_names = {}  # {nurse_id: name}

            current_date = None
            for line in text.split("\n"):
                # Match date header: "📅 2025-12-04 (Wednesday)"
                date_header = re.search(
                    r"📅\s*(\d{4}-\d{2}-\d{2})\s*\((\w+)\)", line
                )
                if date_header:
                    current_date = date_header.group(1)
                    continue

                # Match assignment: "   07:00-15:00 | Ward A     | Alice Smith (nurse_001)"
                assign_match = re.search(
                    r"(\d{2}:\d{2})-(\d{2}:\d{2})\s*\|\s*(\w+)[^|]*\|\s*([^(]+)\((nurse_\d+)\)",
                    line,
                )
                if assign_match and current_date:
                    start_time = assign_match.group(1)
                    ward = assign_match.group(3)[:3]  # Truncate ward name
                    name = assign_match.group(4).strip()
                    nurse_id = assign_match.group(5)

                    # Determine shift type from start time
                    hour = int(start_time.split(":")[0])
                    if (
                        hour >= NIGHT_SHIFT_START_HOUR
                        or hour < DAY_SHIFT_START_HOUR
                    ):
                        shift_type = "N"  # Night
                    elif hour >= EVENING_SHIFT_START_HOUR:
                        shift_type = "E"  # Evening
                    else:
                        shift_type = "D"  # Day

                    if nurse_id not in nurse_schedule:
                        nurse_schedule[nurse_id] = {}

                    val = f"{ward}-{shift_type}"
                    if current_date in nurse_schedule[nurse_id]:
                        nurse_schedule[nurse_id][current_date] += " " + val
                    else:
                        nurse_schedule[nurse_id][current_date] = val

                    nurse_names[nurse_id] = name

            if not nurse_schedule:
                # Fallback: show simple summary if calendar parsing failed
                nurse_assignments = {}
                for a in assignments:
                    nid = a.get("nurse_id", "")
                    if nid not in nurse_assignments:
                        nurse_assignments[nid] = []
                    nurse_assignments[nid].append(
                        a.get("info") or a.get("shift_id", "")
                    )

                result += "### Assignments Summary\n\n"
                result += "| Nurse | Shifts |\n"
                result += "|-------|--------|\n"
                for nurse_id, shifts in sorted(nurse_assignments.items()):
                    result += f"| {nurse_id} | {len(shifts)} shifts |\n"
                result += f"\n**Total**: {len(assignments)} assignments across {len(nurse_assignments)} nurses\n"
                return result

            # Build 7-day calendar chunks
            chunk_size = 7
            num_chunks = (total_days + chunk_size - 1) // chunk_size
            roster_nurse_ids = sorted(nurse_schedule.keys())

            for chunk_idx in range(num_chunks):
                chunk_start = start_date + timedelta(
                    days=chunk_idx * chunk_size
                )
                chunk_end = min(
                    chunk_start + timedelta(days=chunk_size - 1), end_date
                )
                chunk_days = (chunk_end - chunk_start).days + 1

                if num_chunks > 1:
                    result += f"### Week {chunk_idx + 1}\n\n"

                # Build header row with day names
                headers = ["Nurse"]
                dates_in_chunk = []
                for i in range(chunk_days):
                    d = chunk_start + timedelta(days=i)
                    dates_in_chunk.append(d.strftime("%Y-%m-%d"))
                    day_abbr = d.strftime("%a")  # Mon, Tue, etc.
                    day_num = d.strftime("%d")
                    headers.append(f"{day_abbr} {day_num}")
                headers.append("Total")

                # Header row
                result += "| " + " | ".join(headers) + " |\n"
                result += "|" + "|".join(["---"] * len(headers)) + "|\n"

                # Data rows
                for nurse_id in roster_nurse_ids:
                    name = nurse_names.get(nurse_id, nurse_id)
                    row = [name]
                    nurse_total = 0

                    for date_str in dates_in_chunk:
                        cell = nurse_schedule.get(nurse_id, {}).get(
                            date_str, "-"
                        )
                        row.append(cell)
                        if cell != "-":
                            nurse_total += len(cell.split(" "))

                    row.append(str(nurse_total))
                    result += "| " + " | ".join(row) + " |\n"

                result += "\n"

            # Legend
            result += "**Legend**: D=Day | E=Evening | N=Night | Ward abbreviations (ICU, Gen, Eme, etc.)\n"

        except ValueError:
            result += "_Could not parse roster dates_\n"

        return result

    def _format_availability(self, text: str) -> str:
        """Format availability as sectioned list."""
        # Extract date
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})\s*\((\w+)\)", text)
        if date_match:
            date_str = date_match.group(1)
            day_name = date_match.group(2)
        else:
            date_str = "Unknown"
            day_name = ""

        result = f"## Availability: {date_str}"
        if day_name:
            result += f" ({day_name})"
        result += "\n\n"

        # Parse sections
        sections: dict[str, Any] = {
            "available": [],
            "limited": [],
            "unavailable": [],
        }

        current_section = None
        for raw_line in text.split("\n"):
            line = raw_line.strip()
            if re.search(r"AVAILABLE\s*\(\d+\)", line, re.I):
                current_section = "available"
                count_match = re.search(r"\((\d+)\)", line)
                sections["available_count"] = (
                    count_match.group(1) if count_match else "0"
                )
            elif re.search(r"LIMITED.*AVAILABILITY\s*\(\d+\)", line, re.I):
                current_section = "limited"
                count_match = re.search(r"\((\d+)\)", line)
                sections["limited_count"] = (
                    count_match.group(1) if count_match else "0"
                )
            elif re.search(r"UNAVAILABLE\s*\(\d+\)", line, re.I):
                current_section = "unavailable"
                count_match = re.search(r"\((\d+)\)", line)
                sections["unavailable_count"] = (
                    count_match.group(1) if count_match else "0"
                )
            elif current_section and line.startswith(("+", "?", "-")):
                # Parse entry: "+ Name - details" or "? Name - details"
                entry = line[1:].strip()
                sections[current_section].append(entry)

        # Build formatted output
        result += f"### ✅ Available ({sections.get('available_count', len(sections['available']))})\n\n"
        for entry in sections["available"]:
            result += f"- {entry}\n"
        if not sections["available"]:
            result += "_None_\n"
        result += "\n"

        result += f"### ⚠️ Limited ({sections.get('limited_count', len(sections['limited']))})\n\n"
        for entry in sections["limited"]:
            result += f"- {entry}\n"
        if not sections["limited"]:
            result += "_None_\n"
        result += "\n"

        result += f"### ❌ Unavailable ({sections.get('unavailable_count', len(sections['unavailable']))})\n\n"
        for entry in sections["unavailable"]:
            result += f"- {entry}\n"
        if not sections["unavailable"]:
            result += "_None_\n"

        return result

    def _format_nurse_profile(self, text: str) -> str:
        """Format nurse profile with sections."""
        # Extract nurse name
        name_match = re.search(r"NURSE PROFILE:\s*(\w+)", text, re.I)
        name = name_match.group(1) if name_match else "Unknown"

        result = f"## Nurse: {name}\n\n"

        # Extract key-value pairs
        def extract_value(pattern: str) -> str:
            match = re.search(pattern, text, re.I)
            return match.group(1).strip() if match else "N/A"

        # Basic Info section
        result += "### Basic Info\n\n"
        result += f"- **ID**: {extract_value(r'ID:\s*([^\n]+)')}\n"
        result += (
            f"- **Seniority**: {extract_value(r'Seniority:\s*([^\n]+)')}\n"
        )
        result += f"- **Contract**: {extract_value(r'Contract:\s*([^\n]+)')}\n"
        result += f"- **Certifications**: {extract_value(r'Certifications:\s*([^\n]+)')}\n"
        result += "\n"

        # Preferences section
        result += "### Preferences\n\n"
        result += f"- **Avoid Night Shifts**: {extract_value(r'Avoid night shifts:\s*([^\n]+)')}\n"
        result += f"- **Preferred Days**: {extract_value(r'Preferred days:\s*([^\n]+)')}\n"
        result += "\n"

        # Current Status section
        result += "### Current Status\n\n"
        result += (
            f"- **Last Shift**: {extract_value(r'Last shift:\s*([^\n]+)')}\n"
        )
        result += f"- **Consecutive Shifts**: {extract_value(r'Consecutive shifts:\s*([^\n]+)')}\n"
        result += f"- **Shifts (30d)**: {extract_value(r'Shifts \(30d\):\s*([^\n]+)')}\n"
        result += f"- **Weekend Shifts**: {extract_value(r'Weekend shifts.*?:\s*([^\n]+)')}\n"
        result += f"- **Fatigue**: {extract_value(r'Fatigue:\s*([^\n]+)')}\n"

        return result

    def _format_staffing_summary(self, text: str) -> str:
        """Format staffing summary."""
        result = "## Staffing Summary\n\n"

        def extract_value(pattern: str) -> str:
            match = re.search(pattern, text, re.I | re.S)
            return match.group(1).strip() if match else "N/A"

        # Workforce stats
        result += (
            f"- **Total Nurses**: {extract_value(r'Total nurses:\s*(\d+)')}\n"
        )
        result += f"- **By Seniority**: {extract_value(r'By seniority:\s*([^\n]+)')}\n"
        result += (
            f"- **By Contract**: {extract_value(r'By contract:\s*([^\n]+)')}\n"
        )
        result += "\n"

        # Fatigue status
        result += "### Fatigue Status\n\n"
        good_match = re.search(r"\[OK\].*?Good:\s*(\d+)", text, re.I)
        mod_match = re.search(r"\[MOD\].*?Moderate:\s*(\d+)", text, re.I)
        high_match = re.search(r"\[HIGH\].*?High Risk:\s*(\d+)", text, re.I)

        good = good_match.group(1) if good_match else "0"
        moderate = mod_match.group(1) if mod_match else "0"
        high = high_match.group(1) if high_match else "0"

        result += f"- 🟢 Good: {good} nurses\n"
        result += f"- 🟡 Moderate: {moderate} nurses\n"
        result += f"- 🔴 High Risk: {high} nurses\n"
        result += "\n"

        # Upcoming shifts
        result += "### Upcoming Shifts\n\n"
        total_shifts = extract_value(r"Total:\s*(\d+)\s*shifts")
        result += f"- **Total**: {total_shifts} shifts\n"

        icu_match = re.search(r"ICU:\s*(\d+)", text)
        emergency_match = re.search(r"Emergency:\s*(\d+)", text)
        general_match = re.search(r"General:\s*(\d+)", text)

        if icu_match:
            result += f"- **ICU**: {icu_match.group(1)}\n"
        if emergency_match:
            result += f"- **Emergency**: {emergency_match.group(1)}\n"
        if general_match:
            result += f"- **General**: {general_match.group(1)}\n"
        result += "\n"

        # Alerts
        if re.search(r"ALERTS:", text, re.I):
            result += "### ⚠️ Alerts\n\n"
            # Extract alert lines
            alerts_section = re.search(
                r"ALERTS:\s*(.*?)(?:\n\n|\Z)", text, re.I | re.S
            )
            if alerts_section:
                for raw_line in alerts_section.group(1).split("\n"):
                    line = raw_line.strip()
                    if line and not line.startswith("="):
                        result += f"- {line}\n"
        elif re.search(r"No staffing alerts", text, re.I):
            result += "### ✅ No Alerts\n\n"
            result += "_All staffing levels are healthy_\n"

        return result

    def _format_shifts_list(self, text: str) -> str:
        """Format shifts list as table grouped by date."""
        # Extract header info
        days_match = re.search(r"\((\d+)\s*days\)", text, re.I)
        days = days_match.group(1) if days_match else "7"

        result = f"## Shifts to Fill ({days} days)\n\n"

        # Parse shifts grouped by date
        current_date = None
        shifts = []

        for raw_line in text.split("\n"):
            line = raw_line.strip()

            # Date header: "📆 2025-12-04 (Wednesday)"
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})\s*\((\w+)\)", line)
            if date_match:
                current_date = f"{date_match.group(1)} ({date_match.group(2)})"
                continue

            # Shift entry: "📅 shift_001: ICU Ward"
            shift_match = re.search(r"(shift_\d+):\s*(\w+)\s*Ward", line)
            if shift_match and current_date:
                shift_id = shift_match.group(1)
                ward = shift_match.group(2)
                shifts.append(
                    {
                        "date": current_date,
                        "id": shift_id,
                        "ward": ward,
                        "time": "",
                        "certs": "",
                        "level": "",
                    }
                )
                continue

            # Time line: "Time: 08:00 - 16:00"
            time_match = re.search(
                r"Time:\s*(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})", line
            )
            if time_match and shifts:
                shifts[-1]["time"] = (
                    f"{time_match.group(1)}-{time_match.group(2)}"
                )
                continue

            # Requirements line: "Required: ICU | Min Level: Senior"
            req_match = re.search(
                r"Required:\s*([^|]+)\|\s*Min Level:\s*(\w+)", line
            )
            if req_match and shifts:
                shifts[-1]["certs"] = req_match.group(1).strip()
                shifts[-1]["level"] = req_match.group(2).strip()

        if not shifts:
            return text  # Couldn't parse

        # Build table
        result += "| Date | Shift | Ward | Time | Certs | Level |\n"
        result += "|------|-------|------|------|-------|-------|\n"

        prev_date = None
        for s in shifts:
            date_display = s["date"] if s["date"] != prev_date else ""
            prev_date = s["date"]
            result += f"| {date_display} | {s['id']} | {s['ward']} | {s['time']} | {s['certs']} | {s['level']} |\n"

        # Total
        total_match = re.search(r"Total shifts:\s*(\d+)", text, re.I)
        if total_match:
            result += f"\n**Total: {total_match.group(1)} shifts**"

        return result

    def _format_pending_rosters(self, text: str) -> str:
        """Format pending rosters list."""
        result = "## Pending Rosters\n\n"

        # Parse roster entries
        rosters = []
        current_roster = {}

        for raw_line in text.split("\n"):
            line = raw_line.strip()

            # Roster ID line
            roster_match = re.search(r"(roster_\w+)", line)
            if roster_match and not line.startswith("Period"):
                if current_roster:
                    rosters.append(current_roster)
                current_roster = {"id": roster_match.group(1)}
                continue

            # Period line
            period_match = re.search(r"Period:\s*(\S+)\s*to\s*(\S+)", line)
            if period_match and current_roster:
                current_roster["period"] = (
                    f"{period_match.group(1)} to {period_match.group(2)}"
                )
                continue

            # Generated line
            gen_match = re.search(r"Generated:\s*(.+)", line)
            if gen_match and current_roster:
                current_roster["generated"] = gen_match.group(1)
                continue

            # Assignments line
            assign_match = re.search(r"Assignments:\s*(\d+)", line)
            if assign_match and current_roster:
                current_roster["assignments"] = assign_match.group(1)

        if current_roster:
            rosters.append(current_roster)

        if not rosters:
            return "## Pending Rosters\n\n_No pending rosters_\n"

        # Build table
        result += "| Roster ID | Period | Assignments | Generated |\n"
        result += "|-----------|--------|-------------|----------|\n"

        for r in rosters:
            result += f"| {r.get('id', '')} | {r.get('period', '')} | {r.get('assignments', '')} | {r.get('generated', '')[:10] if r.get('generated') else ''} |\n"

        result += f"\n**Total: {len(rosters)} pending**\n"
        result += "\n_Use `finalize_roster(id)` to approve or `reject_roster(id)` to reject_"

        return result
