from pathlib import Path

from ingest.chunk import chunk_units
from ingest.extract import extract_units
from ingest.store import delete_by_filename, upsert_chunks


def ingest_pdf(path: Path, replace: bool = True) -> dict:
    """Extracts, chunks and stores one pdf. Returns the counts worth eyeballing."""
    units = extract_units(path)
    chunks = chunk_units(units)
    if replace:
        delete_by_filename(path.name)
    upsert_chunks(chunks)
    return {
        "filename": path.name,
        "pages": max((u["page"] for u in units), default=0),
        "tables": sum(1 for u in units if u["kind"] == "table"),
        "chunks": len(chunks),
    }
