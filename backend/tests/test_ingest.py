from ingest.chunk import CHUNK_SIZE, chunk_units
from ingest.extract import extract_units


def test_chunk_keeps_the_page_it_came_from(lab_pdf):
    units = extract_units(lab_pdf)
    chunks = chunk_units(units)

    # the lab report runs onto a second page, so a chunk from each page must exist
    assert {c["page"] for c in chunks} == {1, 2}
    for c in chunks:
        source = [u for u in units if u["page"] == c["page"] and u["kind"] == c["kind"]]
        assert any(c["text"] in u["text"] for u in source)


def test_table_is_never_split(discharge_pdf):
    units = extract_units(discharge_pdf)
    table = next(u for u in units if u["kind"] == "table")
    chunks = chunk_units(units)

    kept = [c for c in chunks if c["kind"] == "table" and c["page"] == table["page"]]
    assert len(kept) == 1
    assert kept[0]["text"] == table["text"]


def test_long_table_passes_through_whole():
    rows = "\n".join(f"|Row {i}|{i}|mmol/L|1 - 9|" for i in range(400))
    table = {"text": f"|A|B|C|D|\n|---|---|---|---|\n{rows}", "filename": "x.pdf", "page": 1, "kind": "table"}

    chunks = chunk_units([table])

    assert len(chunks) == 1
    assert len(chunks[0]["text"]) > CHUNK_SIZE


def test_table_numbers_are_not_also_in_the_prose(lab_pdf):
    units = extract_units(lab_pdf)
    prose = "\n".join(u["text"] for u in units if u["kind"] == "text")
    tables = "\n".join(u["text"] for u in units if u["kind"] == "table")

    assert "|Ferritin|18|ug/L|30 - 400|" in tables
    # the comments section discusses ferritin in words, but the measured row belongs to the table only
    assert "ferritin" in prose
    assert "Ferritin" not in prose
    assert "ug/L" not in prose
