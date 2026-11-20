from typing import Any

from src.services.anthropic_service import generate_hypotheses


def hypothesis_agent(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "hypotheses": generate_hypotheses(
            parsed_error=state.get("parsed_error", {}),
            retrieved_incidents=state.get("retrieved_incidents", []),
            recent_commits=state.get("recent_commits", []),
        )
    }
