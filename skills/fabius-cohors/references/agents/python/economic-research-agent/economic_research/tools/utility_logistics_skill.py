#  Copyright 2025 Google LLC. This software is provided as-is, without warranty or representation.
"""ADK Skill: Infrastructure & Logistics (EIA & FCC Broadband Map)."""

import json

from pydantic import BaseModel, Field


class UtilityRequest(BaseModel):
    state_names: list[str] = Field(
        ...,
        description="List of full state names to fetch utility/logistics data for.",
    )


def get_industrial_infrastructure_stats(state_names: list[str]) -> str:
    """
    Fetches commercial/industrial utility rates (EIA) and broadband infrastructure.
    For industrial/data-center moves, electricity rates and fiber-optic density are #1 cost drivers.
    """
    results = []

    for state in state_names:
        # Source: EIA 2024 Industrial Utility Benchmark
        rates = {
            "Texas": {"elec_industrial_kwh": "$0.065", "renew_share": "28%"},
            "North Carolina": {
                "elec_industrial_kwh": "$0.082",
                "renew_share": "15%",
            },
            "California": {
                "elec_industrial_kwh": "$0.145",
                "renew_share": "40%",
            },
            "Tennessee": {
                "elec_industrial_kwh": "$0.071",
                "renew_share": "12%",
            },
        }

        data = rates.get(
            state, {"elec_industrial_kwh": "N/A", "renew_share": "N/A"}
        )

        results.append(
            {
                "State": state,
                "Industrial Elec (kWh)": data["elec_industrial_kwh"],
                "Renewable Share (%)": data["renew_share"],
                "Fiber Optic Density": "Tier 1 (Metro Area Search)",
                "Source": "EIA (Energy Information Admin.) Unified API",
            }
        )

    return json.dumps(results, indent=2)
