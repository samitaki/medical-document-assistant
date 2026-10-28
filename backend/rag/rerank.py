from sentence_transformers import CrossEncoder

from app.config import get_settings

_model: CrossEncoder | None = None


def model() -> CrossEncoder:
    global _model
    if _model is None:
        _model = CrossEncoder(get_settings().rerank_model)
    return _model


def rerank(question: str, chunks: list[dict], k: int) -> list[dict]:
    """Scores every candidate against the question and keeps the best k, best first."""
    if not chunks:
        return []
    scores = model().predict([(question, c["text"]) for c in chunks])
    ranked = sorted(zip(chunks, scores), key=lambda pair: pair[1], reverse=True)
    return [{**c, "rerank_score": float(s)} for c, s in ranked[:k]]
