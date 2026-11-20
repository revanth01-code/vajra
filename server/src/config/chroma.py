from pathlib import Path

import chromadb

from src.config.env import SERVER_ROOT, settings


def _persist_path() -> str:
    path = Path(settings.chroma_persist_path)
    if not path.is_absolute():
        path = SERVER_ROOT / path
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


client = chromadb.PersistentClient(path=_persist_path())


def get_chroma_collection():
    return client.get_or_create_collection(
        name="past_incidents",
        metadata={"hnsw:space": "cosine"},
    )


def get_chroma_document_count() -> int:
    return get_chroma_collection().count()
