from app.config import get_settings
from ingest.store import search


def retrieve(question: str, k: int | None = None) -> list[dict]:
    """Returns the top k chunk payloads for the question, best first.

    Kept separate from generation so a reranker can sit between the two.
    """
    return search(question, k or get_settings().top_k)
