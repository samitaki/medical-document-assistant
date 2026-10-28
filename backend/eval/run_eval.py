"""Retrieval eval over the sample pdfs, with and without the reranker.

Needs qdrant up and both models downloaded. Run from backend/: python -m eval.run_eval
This is not a pytest suite, it is a thing you run and read.
"""

import sys
from pathlib import Path

import yaml

from app.config import get_settings
from ingest.pipeline import ingest_pdf
from rag.rerank import rerank
from rag.retrieve import retrieve

QUESTIONS = Path(__file__).parent / "questions.yaml"
SAMPLES = Path(__file__).resolve().parents[2] / "sample_docs"


def load_questions() -> list[dict]:
    return yaml.safe_load(QUESTIONS.read_text())


def ingest_samples() -> None:
    for pdf in sorted(SAMPLES.glob("*.pdf")):
        r = ingest_pdf(pdf)
        print(f"  {r['filename']}: pages={r['pages']} tables={r['tables']} chunks={r['chunks']}")


def first_hit(chunks: list[dict], q: dict) -> int | None:
    """1-based rank of the first chunk that actually holds the answer, or None.

    For a question marked table the answer is only in the table, and the prose on the same page
    does not count. Without that the medication table and the prose above it look identical here.
    """
    for i, c in enumerate(chunks, start=1):
        if c["filename"] != q["filename"] or c["page"] not in q["pages"]:
            continue
        if q.get("table") and c["kind"] != "table":
            continue
        return i
    return None


def run(questions: list[dict], use_rerank: bool) -> list[dict]:
    s = get_settings()
    rows = []
    for q in questions:
        candidates = retrieve(q["question"], s.candidate_k if use_rerank else s.top_k)
        chunks = rerank(q["question"], candidates, s.top_k) if use_rerank else candidates
        key = "rerank_score" if use_rerank else "score"
        rows.append(
            {
                "question": q["question"],
                "table": q.get("table", False),
                "rank": first_hit(chunks, q),
                "top3": [(c["filename"], c["page"], c["kind"], round(c[key], 3)) for c in chunks[:3]],
            }
        )
    return rows


def metrics(rows: list[dict]) -> dict:
    ranks = [r["rank"] for r in rows]
    n = len(ranks)
    return {
        "recall@3": sum(1 for r in ranks if r and r <= 3) / n,
        "recall@5": sum(1 for r in ranks if r and r <= 5) / n,
        "mrr": sum(1 / r for r in ranks if r) / n,
    }


def print_detail(title: str, rows: list[dict]) -> None:
    print(f"\n{title}")
    for r in rows:
        mark = f"hit  rank {r['rank']}" if r["rank"] else "MISS      "
        tag = " [table]" if r["table"] else ""
        print(f"  {mark}  {r['question']}{tag}")
        for filename, page, kind, score in r["top3"]:
            print(f"        {score:>7}  {filename} p{page} ({kind})")


def main() -> int:
    questions = load_questions()
    print(f"ingesting {len(list(SAMPLES.glob('*.pdf')))} sample pdfs")
    ingest_samples()

    off = run(questions, use_rerank=False)
    on = run(questions, use_rerank=True)

    print_detail("--- retrieval only (qdrant top 5) ---", off)
    print_detail(f"--- with reranker (qdrant top {get_settings().candidate_k} -> top 5) ---", on)

    a, b = metrics(off), metrics(on)
    print(f"\n{len(questions)} questions")
    print(f"{'metric':<10} {'no rerank':>10} {'rerank':>10}")
    for k in ("recall@3", "recall@5", "mrr"):
        print(f"{k:<10} {a[k]:>10.3f} {b[k]:>10.3f}")

    moved = [
        (o["question"], o["rank"], n["rank"])
        for o, n in zip(off, on)
        if o["rank"] != n["rank"]
    ]
    print("\nquestions whose first correct rank changed")
    for question, before, after in moved or []:
        print(f"  {before or 'miss'} -> {after or 'miss'}  {question}")
    if not moved:
        print("  none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
