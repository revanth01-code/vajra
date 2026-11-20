import asyncio
import json
from typing import Any, AsyncIterator
from uuid import uuid4

from src.agents.pipeline import IncidentState, build_pipeline
from src.services.history_service import save_investigation
from src.services.sanitizer import sanitize_text


_NODE_LABELS = {
    "error_parser": "Parsing error",
    "history_retriever": "Searching past incidents",
    "change_correlator": "Checking recent changes",
    "hypothesis_agent": "Generating hypotheses",
    "report_writer": "Writing report",
}


def _event(
    node: str,
    status: str,
    summary: str,
    data: dict[str, Any] | None = None,
) -> str:
    payload: dict[str, Any] = {"node": node, "status": status, "summary": summary}
    if data is not None:
        payload["data"] = data
    return f"data: {json.dumps(payload, default=str)}\n\n"


def _node_summary(node: str, state: dict[str, Any]) -> str:
    if node == "error_parser":
        parsed = state.get("parsed_error", {})
        return f"{parsed.get('service', 'unknown')} / {parsed.get('error_type', 'unknown')}"
    if node == "history_retriever":
        return f"Found {len(state.get('retrieved_incidents', []))} similar incidents."
    if node == "change_correlator":
        suspicious = sum(
            1 for commit in state.get("recent_commits", []) if commit.get("suspicious")
        )
        return f"Found {suspicious} suspicious recent commits."
    if node == "hypothesis_agent":
        return f"Generated {len(state.get('hypotheses', []))} hypotheses."
    return "Incident report generated."


async def stream_investigation(
    incident_text: str,
    repo_url: str | None,
) -> AsyncIterator[str]:
    session_id = str(uuid4())
    state: IncidentState = {
        "raw_input": incident_text,
        "sanitized_input": sanitize_text(incident_text),
        "repo_url": repo_url,
        "session_id": session_id,
        "warnings": [],
    }
    stream = build_pipeline().stream(state, stream_mode="updates")

    try:
        for node in _NODE_LABELS:
            yield _event(node, "running", _NODE_LABELS[node])
            update = await asyncio.to_thread(next, stream, None)
            if update is None:
                raise RuntimeError(f"Pipeline ended before node {node} completed.")
            for node_update in update.values():
                state.update(node_update)
            warning_nodes = {"history_retriever", "change_correlator"}
            status = "warning" if state.get("warnings") and node in warning_nodes else "complete"
            yield _event(node, status, _node_summary(node, state))

        save_investigation(state)
        yield _event(
            "pipeline",
            "completed",
            "Investigation completed.",
            {
                "session_id": session_id,
                "hypotheses": state.get("hypotheses", []),
                "report_markdown": state.get("report_markdown", ""),
                "warnings": state.get("warnings", []),
            },
        )
    except Exception as error:
        state["warnings"] = [*state.get("warnings", []), str(error)]
        save_investigation(state, status="failed")
        yield _event("pipeline", "error", "Investigation failed.", {"session_id": session_id})
