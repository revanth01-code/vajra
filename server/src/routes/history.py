import json

from fastapi import APIRouter, HTTPException

from src.services.history_service import get_investigation, list_investigations


router = APIRouter()


@router.get("/history")
def history() -> list[dict[str, object]]:
    return [
        {
            "id": item.id,
            "created_at": item.created_at,
            "service_name": item.service_name,
            "error_type": item.error_type,
            "top_hypothesis_cause": item.top_hypothesis_cause,
            "status": item.status,
        }
        for item in list_investigations()
    ]


@router.get("/history/{session_id}")
def history_detail(session_id: str) -> dict[str, object]:
    item = get_investigation(session_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Investigation not found.")
    return {
        "id": item.id,
        "created_at": item.created_at,
        "sanitized_input": item.sanitized_input,
        "service_name": item.service_name,
        "error_type": item.error_type,
        "top_hypothesis_cause": item.top_hypothesis_cause,
        "top_hypothesis_confidence": item.top_hypothesis_confidence,
        "report_markdown": item.report_markdown,
        "warnings": json.loads(item.warnings),
        "status": item.status,
    }
