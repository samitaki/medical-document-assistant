"""Ingests one pdf into qdrant. Run from backend/: python -m scripts.ingest path/to/file.pdf"""

import argparse
import sys
from pathlib import Path

from ingest.pipeline import ingest_pdf


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
