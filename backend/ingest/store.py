import uuid

from fastembed import TextEmbedding
from qdrant_client import QdrantClient, models

from app.config import get_settings

EMBED_BATCH = 64
# stable namespace so re-ingesting the same file overwrites its points instead of adding new ones
POINT_NAMESPACE = uuid.UUID("7f1d2e3a-55b1-4c2e-9f8a-6d0b1c4e7a90")

_embedder: TextEmbedding | None = None
_client: QdrantClient | None = None


def embedder() -> TextEmbedding:
    # loading the onnx weights takes a few seconds, so keep one instance per process
    global _embedder
    if _embedder is None:
        _embedder = TextEmbedding(get_settings().embedding_model)
    return _embedder


def client() -> QdrantClient:
    global _client
    if _client is None:
        # the default 5s is not enough for the first write after the container starts
        _client = QdrantClient(url=get_settings().qdrant_url, timeout=30)
    return _client


def ensure_collection() -> None:
    name = get_settings().qdrant_collection
    if client().collection_exists(name):
        return
    client().create_collection(
        name,
        vectors_config=models.VectorParams(
            size=embedder().embedding_size,
            distance=models.Distance.COSINE,
        ),
    )


def upsert_chunks(chunks: list[dict]) -> int:
    if not chunks:
        return 0
    ensure_collection()
    name = get_settings().qdrant_collection

    for start in range(0, len(chunks), EMBED_BATCH):
        batch = chunks[start : start + EMBED_BATCH]
        vectors = embedder().embed([c["text"] for c in batch])
        points = [
            models.PointStruct(id=_point_id(c), vector=list(vec), payload=c)
            for c, vec in zip(batch, vectors)
        ]
        client().upsert(name, points=points, wait=True)

    return len(chunks)


def search(query: str, k: int = 5) -> list[dict]:
    """Returns the matching chunk payloads, each with its cosine score added."""
    name = get_settings().qdrant_collection
    if not client().collection_exists(name):
        return []

    # bge models want a short instruction prefix on the query side, query_embed adds it
    vector = list(next(iter(embedder().query_embed(query))))
    hits = client().query_points(name, query=vector, limit=k, with_payload=True).points
    return [{**h.payload, "score": h.score} for h in hits]


def delete_by_filename(filename: str) -> None:
    name = get_settings().qdrant_collection
    if not client().collection_exists(name):
        return
    client().delete(
        name,
        points_selector=models.Filter(
            must=[models.FieldCondition(key="filename", match=models.MatchValue(value=filename))]
        ),
        wait=True,
    )


def _point_id(chunk: dict) -> str:
    return str(uuid.uuid5(POINT_NAMESPACE, f"{chunk['filename']}:{chunk['chunk_index']}"))
