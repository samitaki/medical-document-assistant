import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel, Field
from qdrant_client.http.exceptions import ResponseHandlingException, UnexpectedResponse

from app.config import get_settings
from app.errors import ServiceError
from ingest.pipeline import ingest_pdf
from ingest.store import delete_all, delete_by_filename, list_documents
from rag.answer import generate
from rag.retrieve import retrieve

router = APIRouter()

PDF_MAGIC = b"%PDF"


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    history: list[Message] = []


@contextmanager
def qdrant_errors():
    try:
        yield
    except (ResponseHandlingException, UnexpectedResponse) as e:
        raise ServiceError(
            f"Cannot reach the vector database at {get_settings().qdrant_url}. "
            "Start it with: docker compose up -d"
        ) from e


@router.post("/documents")
def upload_documents(files: list[UploadFile] = File(...)) -> dict:
    indexed, failed = [], []

    # a temp dir keeps the original filename, which the citations are built from
    with tempfile.TemporaryDirectory() as tmp:
        for f in files:
            name = Path(f.filename or "unnamed").name
            data = f.file.read()

            if not name.lower().endswith(".pdf") or not data.startswith(PDF_MAGIC):
                failed.append({"filename": name, "error": "not a pdf"})
                continue

            path = Path(tmp) / name
            path.write_bytes(data)
            with qdrant_errors():
                indexed.append(ingest_pdf(path))

    if not indexed and failed:
        raise ServiceError("None of the uploaded files are pdfs.", status=400)

    return {"indexed": indexed, "failed": failed}


@router.get("/documents")
def get_documents() -> dict:
    with qdrant_errors():
        return {"documents": list_documents()}


@router.delete("/documents/{filename}")
def delete_document(filename: str) -> dict:
    with qdrant_errors():
        delete_by_filename(filename)
    return {"deleted": filename}


@router.delete("/documents")
def delete_documents() -> dict:
    with qdrant_errors():
        delete_all()
    return {"deleted": "all"}


@router.post("/chat")
def chat(req: ChatRequest) -> dict:
    s = get_settings()
    with qdrant_errors():
        chunks = retrieve(req.question, s.candidate_k if s.rerank_enabled else s.top_k)
    if s.rerank_enabled:
        # imported here so a default install does not need torch
        from rag.rerank import rerank

        chunks = rerank(req.question, chunks, s.top_k)
    return generate(req.question, chunks, [m.model_dump() for m in req.history])
