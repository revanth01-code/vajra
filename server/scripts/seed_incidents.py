import json
from pathlib import Path
import sys


SERVER_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVER_ROOT))

from src.config.chroma import get_chroma_collection
from src.services.embedding_service import embed_texts


DATA_PATH = SERVER_ROOT / "data" / "seed_incidents.json"


def seed_incidents() -> int:
    collection = get_chroma_collection()
    if collection.count() >= 20:
        return collection.count()

    incidents = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    embeddings = embed_texts(
        [incident["incident_description"] for incident in incidents]
    )
    collection.upsert(
        ids=[f"seed-{index + 1:03d}" for index in range(len(incidents))],
        documents=[incident["incident_description"] for incident in incidents],
        embeddings=embeddings,
        metadatas=[
            {
                "root_cause": incident["root_cause"],
                "fix_applied": incident["fix_applied"],
                "service_type": incident["service_type"],
            }
            for incident in incidents
        ],
    )
    return collection.count()


if __name__ == "__main__":
    print(f"Past incidents collection contains {seed_incidents()} documents.")
