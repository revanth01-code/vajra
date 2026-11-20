from typing import Any

from src.services.history_service import HistoryServiceError, retrieve_similar_incidents


def history_retriever(state: dict[str, Any]) -> dict[str, Any]:
    parsed_error = state.get("parsed_error", {})
    error_message = parsed_error.get("error_message", "")
    try:
        return {"retrieved_incidents": retrieve_similar_incidents(error_message)}
    except HistoryServiceError as error:
        return {
            "retrieved_incidents": [],
            "warnings": [*state.get("warnings", []), str(error)],
        }
