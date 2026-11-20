from typing import Annotated

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.services.investigation_service import stream_investigation


router = APIRouter()


class InvestigationRequest(BaseModel):
    incident_text: Annotated[str, Field(min_length=1, max_length=10000)]
    repo_url: str | None = None


@router.post("/investigate")
async def investigate(request: InvestigationRequest) -> StreamingResponse:
    return StreamingResponse(
        stream_investigation(request.incident_text, request.repo_url),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
