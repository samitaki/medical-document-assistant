import html
from pathlib import Path

import fitz

# a block counts as part of a table when most of its area sits inside the table bbox.
# it is not 1.0 because pymupdf block rects are a little looser than the table rect.
TABLE_OVERLAP = 0.6


def extract_units(path: str | Path) -> list[dict]:
    """Returns one unit per table and one per page of prose, in reading order.

    Each unit is {text, filename, page, kind} with page 1-based, the number a human
    sees in a pdf reader. kind is "table" or "text".
    """
    path = Path(path)
    doc = fitz.open(path)
    units = []

    for page in doc:
        page_no = page.number + 1
        boxes = []

        # tables come first so the prose pass can skip the area they cover
        for table in page.find_tables().tables:
            boxes.append(fitz.Rect(table.bbox))
            md = _unescape(table.to_markdown()).strip()
            if md:
                units.append(_unit(md, path.name, page_no, "table"))

        prose = _prose_outside(page, boxes)
        if prose:
            units.append(_unit(prose, path.name, page_no, "text"))

    doc.close()
    return units


def _unescape(md: str) -> str:
    # to_markdown escapes cell text and then escapes the ampersands again, so a hyphen
    # comes out as &amp;#45;. two passes turn that back into readable text.
    return html.unescape(html.unescape(md))


def _unit(text: str, filename: str, page: int, kind: str) -> dict:
    return {"text": text, "filename": filename, "page": page, "kind": kind}


def _prose_outside(page: fitz.Page, boxes: list[fitz.Rect]) -> str:
    # a table that runs over a page break is seen by find_tables as two unrelated tables,
    # so the second part loses the header row. known gap, not worth fixing yet.
    parts = []
    for x0, y0, x1, y1, text, _, _ in page.get_text("blocks"):
        if not text.strip():
            continue
        rect = fitz.Rect(x0, y0, x1, y1)
        if any(_covered(rect, box) for box in boxes):
            continue
        parts.append(text.strip())
    return "\n\n".join(parts)


def _covered(rect: fitz.Rect, box: fitz.Rect) -> bool:
    if rect.is_empty:
        return False
    overlap = rect & box
    return overlap.get_area() / rect.get_area() >= TABLE_OVERLAP
