from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.config.db import engine
from src.models.feedback import Feedback
from src.services.history_service import get_investigation


router = APIRouter()


class FeedbackRequest(BaseModel):
    session_id: str
    hypothesis_rank: int = Field(ge=1, le=3)
    rating: Literal["up", "down"]


@router.post("/feedback", status_code=201)
def feedback(request: FeedbackRequest) -> dict[str, str]:
    if get_investigation(request.session_id) is None:
        raise HTTPException(status_code=404, detail="Investigation not found.")
    with Session(engine) as session:
        session.add(
            Feedback(
                session_id=request.session_id,
                hypothesis_rank=request.hypothesis_rank,
                rating=request.rating,
            )
        )
        session.commit()
    return {"status": "created"}
