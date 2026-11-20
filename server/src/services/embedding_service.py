from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


_vectorizer = TfidfVectorizer(
    max_features=1000,
    stop_words="english",
    ngram_range=(1, 2),
)
_corpus: list[str] = []
_matrix = None


def fit_corpus(texts: list[str]) -> None:
    global _matrix, _corpus
    _corpus = texts
    if texts:
        _matrix = _vectorizer.fit_transform(texts)


def embed_query(text: str):
    if _matrix is None or not _corpus:
        return None
    return _vectorizer.transform([text])


def find_similar(query_text: str, top_k: int = 3, threshold: float = 0.1):
    query_vec = embed_query(query_text)
    if query_vec is None:
        return []
    scores = cosine_similarity(query_vec, _matrix).flatten()
    top_indices = np.argsort(scores)[::-1][:top_k]
    results = []
    for idx in top_indices:
        if scores[idx] >= threshold:
            results.append((int(idx), float(scores[idx])))
    return results
