#  Copyright 2025 Google LLC. This software is provided as-is, without warranty or representation.
"""ADK Skill: HUD Fair Market Rents (FMR). Talent Relocation & COLA."""

import json
import logging
import os

import requests

# Configure simplified logging to capture API interactions
logger = logging.getLogger(__name__)

# HUD API key (JWT Bearer Token)
# Final quote-safe and whitespace-scrubbed token handle
h_raw = os.getenv("HUD_API_KEY", "").strip()
HUD_API_KEY = h_raw.replace('"', "").replace("'", "")


def get_hud_entity_id(county_fips: str) -> str:
    """Standardize entity ID: Austin (48453) -> 4845399999."""
    if len(county_fips) == 5:
        return f"{county_fips}99999"
    return county_fips


def fetch_hud_fmr_data(county_fips: str) -> str:
    """Fetches HUD FMR with Title Case key matching for FY2026."""
    if not HUD_API_KEY:
        return json.dumps(
            {"ERROR": "HUD_API_KEY environment variable is empty."}, indent=2
        )

    eid = get_hud_entity_id(county_fips)
    # FY2026 is currently active for MSAs like Austin
    for year in ["2026", "2025", "2024"]:
        try:
            url = f"https://www.huduser.gov/hudapi/public/fmr/data/{eid}?year={year}"
            headers = {"Authorization": f"Bearer {HUD_API_KEY}"}
            response = requests.get(url, headers=headers, timeout=12)

            if response.status_code == 200:
                full_payload = response.json()
                data_wrap = full_payload.get("data", {})
                basic = data_wrap.get("basicdata", {})
                # KEY: 'Two-Bedroom' (verified via network capture)
                rent = basic.get("Two-Bedroom") or basic.get("fmr_2")

                if rent:
                    return json.dumps(
                        {
                            "Geography": data_wrap.get(
                                "county_name", "Unknown"
                            ),
                            "Rent_2BR": f"${float(rent):,.0f}",
                            "Year": year,
                            "Source": f"HUD User API (FMR/{year})",
                        },
                        indent=2,
                    )
            elif response.status_code == 401:
                return json.dumps(
                    {
                        "ERROR": "HUD API Token Unauthorized (401). Check registration."
                    },
                    indent=2,
                )
        except Exception:
            continue

    return json.dumps(
        {
            "ERROR": f"FMR lookup failed for FIPS {county_fips}. Verification required."
        },
        indent=2,
    )


def fetch_hud_income_limits(county_fips: str) -> str:
    """Fetches HUD Income Limits (AMI) with nested JSON schema matching."""
    if not HUD_API_KEY:
        return json.dumps(
            {"ERROR": "HUD_API_KEY empty or invalid format."}, indent=2
        )

    eid = get_hud_entity_id(county_fips)
    for year in ["2025", "2024"]:
        try:
            url = f"https://www.huduser.gov/hudapi/public/il/data/{eid}?year={year}"
            headers = {"Authorization": f"Bearer {HUD_API_KEY}"}
            response = requests.get(url, headers=headers, timeout=12)

            if response.status_code == 200:
                payload = response.json().get("data", {})
                # SCHEMA: Very Low Income (50% AMI) is stored in 'very_low'
                very_low = payload.get("very_low", {})
                # Key: 'il50_p1' for 1-person, 'il50_4' for 4-person
                income = very_low.get("il50_p1") or payload.get(
                    "il_data", {}
                ).get("il50_4")

                if income:
                    return json.dumps(
                        {
                            "Geography": payload.get("county_name", "Unknown"),
                            "AMI_50_Level": f"${float(income):,.0f}",
                            "Year": year,
                            "Source": f"HUD User API (IL/{year})",
                        },
                        indent=2,
                    )
        except Exception:
            continue

    return json.dumps(
        {"ERROR": f"Income Limit lookup failed for FIPS {county_fips}."},
        indent=2,
    )


def analyze_housing_affordability(county_fips: str) -> str:
    """Consolidated site-selection affordability report."""
    fmr = json.loads(fetch_hud_fmr_data(county_fips))
    il = json.loads(fetch_hud_income_limits(county_fips))

    if "ERROR" in fmr or "ERROR" in il:
        return json.dumps(
            {
                "ERROR": f"HUD Analytics Pipeline Broken: {fmr.get('ERROR', '')} {il.get('ERROR', '')}"
            },
            indent=2,
        )

    try:
        r_val = float(fmr["Rent_2BR"].replace("$", "").replace(",", ""))
        i_val = float(il["AMI_50_Level"].replace("$", "").replace(",", ""))
        # 50% AMI Threshold check
        monthly_income = i_val / 12
        burden_pct = (r_val / monthly_income) * 100

        verdict = (
            "Severely Burdened"
            if burden_pct > 50
            else "High Cost"
            if burden_pct > 30
            else "Optimal"
        )

        return json.dumps(
            {
                "Geography": fmr["Geography"],
                "Analysis": "Housing Affordability vs. 50% AMI",
                "FMR_Rent_2BR": fmr["Rent_2BR"],
                "Monthly_Income_50_AMI": f"${monthly_income:,.2f}",
                "Rent_to_Income_Ratio": f"{burden_pct:.1f}%",
                "Site_Selection_Verdict": verdict,
                "Source": f"Grounded HUD Analytics (FMR:{fmr['Year']}/IL:{il['Year']})",
            },
            indent=2,
        )
    except Exception as e:
        return json.dumps({"ERROR": f"Calculation error: {e!s}"}, indent=2)
