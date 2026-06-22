from typing import Any

from pydantic import BaseModel


class SolverConstraint(BaseModel):
    type: str  # e.g., "max_shifts", "avoid_shift", "min_rest"
    params: dict[str, Any]


def parse_constraints(nl_requests: list[str]) -> list[SolverConstraint]:
    """
    Parses natural language requests into structured constraints.
    In a real implementation, this would likely use an LLM call or be part of the Agent's logic.
    For this tool, we'll provide a simple mapping for demonstration.
    """
    constraints = []
    for req in nl_requests:
        if "off" in req.lower():
            # Example: "I need next Friday off" -> Avoid shift on that date
            # Simplified parsing logic
            constraints.append(
                SolverConstraint(type="avoid_shift", params={"reason": req})
            )
    return constraints
