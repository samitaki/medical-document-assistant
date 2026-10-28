import re

SNIPPET_CHARS = 300

# words that match everything and nothing, dropping them keeps the row scoring honest
STOPWORDS = {
    "a", "about", "and", "are", "as", "at", "be", "by", "did", "do", "does", "for", "from",
    "had", "has", "have", "he", "her", "his", "how", "in", "is", "it", "its", "of", "on",
    "or", "range", "result", "results", "she", "the", "their", "there", "they", "this",
    "to", "value", "was", "were", "what", "when", "which", "who", "with", "you",
}


def snippet_for(chunk: dict, question: str) -> str:
    """The piece of the chunk worth showing under a citation.

    For a table this is the header plus the rows that match the question, because the top of a
    long table says nothing about the row that was actually cited.
    """
    if chunk["kind"] == "table":
        rows = _matching_rows(chunk["text"], question)
        if rows:
            return rows
    return trim(chunk["text"])


def trim(text: str) -> str:
    flat = " ".join(text.split())
    return flat if len(flat) <= SNIPPET_CHARS else flat[:SNIPPET_CHARS].rstrip() + "..."


def _matching_rows(table: str, question: str) -> str:
    lines = [ln for ln in table.splitlines() if ln.strip()]
    if len(lines) < 3:
        return ""

    header, sep, body = lines[0], lines[1], lines[2:]
    terms = _terms(question)
    scored = [(_overlap(_terms(row), terms), i, row) for i, row in enumerate(body)]
    scored = [s for s in scored if s[0] > 0]
    if not scored:
        return ""

    scored.sort(key=lambda s: (-s[0], s[1]))
    budget = SNIPPET_CHARS - len(header) - len(sep)
    keep = []
    for score, i, row in scored:
        if budget - len(row) < 0:
            break
        budget -= len(row) + 1
        keep.append((i, row))

    if not keep:
        return ""

    keep.sort()
    out = [header, sep] + [row for _, row in keep]
    if len(keep) < len(body):
        out.append("...")
    return "\n".join(out)


def _terms(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w for w in words if len(w) > 2 and w not in STOPWORDS}


def _overlap(row_terms: set[str], question_terms: set[str]) -> int:
    return len(row_terms & question_terms)
