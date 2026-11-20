from datetime import datetime
import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.config.chroma import search_incidents
from src.config.db import engine
from src.models.investigation import Investigation


SIMILARITY_THRESHOLD = 0.1


class HistoryServiceError(RuntimeError):
    """Raised when the historical incident lookup cannot be completed."""


def retrieve_similar_incidents(error_message: str) -> list[dict[str, Any]]:
    try:
        return search_incidents(
            error_message,
            top_k=3,
            threshold=SIMILARITY_THRESHOLD,
        )
    except (OSError, RuntimeError, ValueError) as error:
        raise HistoryServiceError("Historical incident search is unavailable.") from error


def list_investigations(limit: int = 20) -> list[Investigation]:
    with Session(engine) as session:
        return list(
            session.scalars(
                select(Investigation)
                .order_by(Investigation.created_at.desc())
                .limit(limit)
            )
        )


def get_investigation(session_id: str) -> Investigation | None:
    with Session(engine) as session:
        return session.get(Investigation, session_id)


def save_investigation(state: dict[str, Any], status: str = "completed") -> None:
    parsed_error = state.get("parsed_error", {})
    hypotheses = state.get("hypotheses", [])
    top_hypothesis = hypotheses[0] if hypotheses else {}
    investigation = Investigation(
        id=state["session_id"],
        created_at=datetime.utcnow(),
        sanitized_input=state.get("sanitized_input", ""),
        service_name=parsed_error.get("service", "unknown"),
        error_type=parsed_error.get("error_type", "unknown"),
        top_hypothesis_cause=top_hypothesis.get("cause"),
        top_hypothesis_confidence=top_hypothesis.get("confidence"),
        report_markdown=state.get("report_markdown"),
        warnings=json.dumps(state.get("warnings", [])),
        status=status,
    )
    with Session(engine) as session:
        session.add(investigation)
        session.commit()
