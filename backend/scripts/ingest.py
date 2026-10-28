"""Ingests one pdf into qdrant. Run from backend/: python -m scripts.ingest path/to/file.pdf"""

import argparse
import sys
from pathlib import Path

from ingest.chunk import chunk_units
from ingest.extract import extract_units
from ingest.store import delete_by_filename, upsert_chunks


def ingest_pdf(path: Path, replace: bool = True) -> dict:
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--keep-existing", action="store_true", help="do not delete earlier points for this filename")
    args = ap.parse_args()

    r = ingest_pdf(args.pdf, replace=not args.keep_existing)
    print(f"{r['filename']}: pages={r['pages']} tables={r['tables']} chunks={r['chunks']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
