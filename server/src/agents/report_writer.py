from typing import Any

from src.services.anthropic_service import generate_report


def report_writer(state: dict[str, Any]) -> dict[str, Any]:
    return {"report_markdown": generate_report(state)}
