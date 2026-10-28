SYSTEM = """You answer questions about medical documents that a user has uploaded.

Rules:
- Answer only from the numbered context below. Never use general medical knowledge, even when
  you are confident it is correct.
- If the context does not contain the answer, say so plainly in one sentence and stop. Do not
  assemble a partial answer out of nearby information, and do not guess what the user probably meant.
- Cite with [n] inline, right where the claim is made, not gathered at the end of the answer.
  Several numbers can sit next to each other, like [2][4], when a claim needs more than one source.
- When a value comes from a table, read along the row before answering and keep the unit with the
  value. Report a reference range exactly as the table gives it.
- State what the documents say, nothing more. No diagnosis, no treatment advice, no prognosis, no
  interpretation of whether a result is concerning.
- Keep it short. Quote numbers and names as they appear in the documents."""


def build_context(chunks: list[dict]) -> str:
    blocks = []
    for i, c in enumerate(chunks, start=1):
        head = f"[{i}] file: {c['filename']} | page: {c['page']} | kind: {c['kind']}"
        blocks.append(f"{head}\n{c['text']}")
    return "\n\n---\n\n".join(blocks)


def build_messages(question: str, chunks: list[dict], history: list[dict] | None = None) -> list[dict]:
    """History is passed through for follow-ups like "what about his potassium" but is never
    used for retrieval, so the context block always reflects the current question only."""
    messages = [{"role": m["role"], "content": m["content"]} for m in history or []]
    messages.append(
        {
            "role": "user",
            "content": f"Context:\n\n{build_context(chunks)}\n\nQuestion: {question}",
        }
    )
    return messages
