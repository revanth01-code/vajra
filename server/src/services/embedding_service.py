from functools import lru_cache
from typing import Sequence


MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _get_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


def embed_texts(texts: Sequence[str]) -> list[list[float]]:
    if not texts:
        return []
    embeddings = _get_model().encode(list(texts), normalize_embeddings=True)
    return embeddings.tolist()


def embed_text(text: str) -> list[float]:
    embeddings = embed_texts([text])
    return embeddings[0]
