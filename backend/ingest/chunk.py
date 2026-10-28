from langchain_text_splitters import RecursiveCharacterTextSplitter

CHUNK_SIZE = 800
CHUNK_OVERLAP = 120

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def chunk_units(units: list[dict]) -> list[dict]:
    """Splits prose units, passes tables through whole, and keeps the page on every chunk."""
    chunks = []
    for u in units:
        # splitting a table breaks the header off its rows, which makes the numbers unreadable
        parts = [u["text"]] if u["kind"] == "table" else splitter.split_text(u["text"])
        for part in parts:
            if not part.strip():
                continue
            chunks.append(
                {
                    "text": part,
                    "filename": u["filename"],
                    "page": u["page"],
                    "kind": u["kind"],
                    "chunk_index": len(chunks),
                }
            )
    return chunks
