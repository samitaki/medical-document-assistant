import re

import anthropic

from app.config import get_settings
from app.errors import ServiceError
from rag.prompt import SYSTEM, build_messages

MAX_TOKENS = 1024
SNIPPET_CHARS = 300
CITATION = re.compile(r"\[(\d+)\]")

NO_CONTEXT = "I have nothing indexed that relates to this question, so I cannot answer it."

_client: anthropic.Anthropic | None = None


def client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        key = get_settings().anthropic_api_key
        if not key:
            raise ServiceError("ANTHROPIC_API_KEY is not set, so answers cannot be generated.")
        _client = anthropic.Anthropic(api_key=key)
    return _client


def generate(question: str, chunks: list[dict], history: list[dict] | None = None) -> dict:
    if not chunks:
        return {"answer": NO_CONTEXT, "citations": []}

    try:
        resp = client().messages.create(
            model=get_settings().chat_model,
            max_tokens=MAX_TOKENS,
            system=SYSTEM,
            messages=build_messages(question, chunks, history),
        )
    except anthropic.APIError as e:
        raise ServiceError(f"The answer model is unavailable: {e.message}", status=502) from e

    text = "".join(block.text for block in resp.content if block.type == "text")
    return {"answer": text, "citations": citations_for(text, chunks)}


def citations_for(answer: str, chunks: list[dict]) -> list[dict]:
    """Maps each [n] in the answer back to its chunk, in order of first appearance.

    A number the model made up has no chunk behind it, so it is dropped rather than guessed at.
    """
    out = []
    seen = set()
    for match in CITATION.findall(answer):
        n = int(match)
        if n in seen or not 1 <= n <= len(chunks):
            continue
        seen.add(n)
        c = chunks[n - 1]
        out.append(
            {
                "n": n,
                "filename": c["filename"],
                "page": c["page"],
                "kind": c["kind"],
                "snippet": _snippet(c["text"]),
            }
        )
    return out


def _snippet(text: str) -> str:
    flat = " ".join(text.split())
    return flat if len(flat) <= SNIPPET_CHARS else flat[:SNIPPET_CHARS].rstrip() + "..."
