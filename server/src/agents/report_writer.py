from typing import Any

from src.services.anthropic_service import generate_report


def report_writer(state: dict[str, Any]) -> dict[str, Any]:
    hypotheses = state.get("hypotheses", [])
    top_hypothesis = hypotheses[0] if hypotheses else {
        "cause": "No hypothesis was produced.",
        "fix": "Retry the investigation.",
    }
    return {
        "report_markdown": generate_report(
            parsed_error=state.get("parsed_error", {}),
            top_hypothesis=top_hypothesis,
            hypotheses=hypotheses,
        )
    }
