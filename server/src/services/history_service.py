from datetime import datetime
import json
from typing import Any

from chromadb.errors import ChromaError
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.config.chroma import get_chroma_collection
from src.config.db import engine
from src.models.investigation import Investigation
from src.services.embedding_service import embed_text


SIMILARITY_THRESHOLD = 0.6


class HistoryServiceError(RuntimeError):
    """Raised when the historical incident lookup cannot be completed."""


def _distance_to_similarity(distance: float, collection: Any) -> float:
    space = (collection.metadata or {}).get("hnsw:space", "l2")
    if space == "cosine":
        return 1 - distance
    return 1 - (distance / 2)


def retrieve_similar_incidents(error_message: str) -> list[dict[str, Any]]:
    try:
        collection = get_chroma_collection()
        if collection.count() == 0:
            return []

        result = collection.query(
            query_embeddings=[embed_text(error_message)],
            n_results=3,
            include=["documents", "metadatas", "distances"],
        )
    except (ChromaError, OSError, RuntimeError) as error:
        raise HistoryServiceError("Historical incident search is unavailable.") from error

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]
    incidents: list[dict[str, Any]] = []

    for document, metadata, distance in zip(documents, metadatas, distances):
        similarity = _distance_to_similarity(float(distance), collection)
        if similarity < SIMILARITY_THRESHOLD:
            continue
        incidents.append(
            {
                "incident_description": document,
                "root_cause": metadata.get("root_cause", ""),
                "fix_applied": metadata.get("fix_applied", ""),
                "service_type": metadata.get("service_type", ""),
                "similarity": round(similarity, 4),
            }
        )
    return incidents


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
