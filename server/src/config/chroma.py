from __future__ import annotations

from src.services.embedding_service import fit_corpus, find_similar


_incidents: list[dict] = []


def get_incident_store() -> list[dict]:
    return _incidents


def add_incidents(incidents: list[dict]) -> None:
    global _incidents
    _incidents = incidents
    texts = [
        f"{inc['incident_description']} {inc['root_cause']} {inc['service_type']}"
        for inc in incidents
    ]
    fit_corpus(texts)


def search_incidents(
    query: str,
    top_k: int = 3,
    threshold: float = 0.1,
) -> list[dict]:
    results = find_similar(query, top_k=top_k, threshold=threshold)
    return [
        {**_incidents[idx], "similarity": score}
        for idx, score in results
    ]


def get_chroma_document_count() -> int:
    return len(_incidents)
