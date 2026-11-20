from fastapi import APIRouter

from src.config.chroma import get_chroma_document_count
from src.config.db import get_investigation_count


router = APIRouter()


@router.get("/health")
def health() -> dict[str, int | str]:
    return {
        "status": "ok",
        "chroma_document_count": get_chroma_document_count(),
        "sqlite_row_count": get_investigation_count(),
    }
