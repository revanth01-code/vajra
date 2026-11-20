import json
from pathlib import Path
import sys


SERVER_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVER_ROOT))

from src.config.chroma import add_incidents, get_chroma_document_count


DATA_PATH = SERVER_ROOT / "data" / "seed_incidents.json"


def seed_incidents() -> int:
    incidents = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    add_incidents(incidents)
    return get_chroma_document_count()


if __name__ == "__main__":
    print(f"Past incidents collection contains {seed_incidents()} documents.")
