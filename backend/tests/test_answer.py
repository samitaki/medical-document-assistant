import pytest

from rag import answer
from rag.answer import NO_CONTEXT, citations_for, generate
from rag.snippet import snippet_for

CHUNKS = [
    {"filename": "a.pdf", "page": 1, "kind": "text", "text": "first chunk about the admission"},
    {"filename": "b.pdf", "page": 7, "kind": "table", "text": "|Drug|Dose|\n|---|---|\n|Amoxicillin|500 mg|"},
]


def test_citation_resolves_to_the_chunk_it_numbers():
    cites = citations_for("The dose was 500 mg [2].", CHUNKS, "what dose")

    assert len(cites) == 1
    assert cites[0]["n"] == 2
    assert cites[0]["filename"] == "b.pdf"
    assert cites[0]["page"] == 7
    assert cites[0]["kind"] == "table"


def test_unknown_citation_numbers_are_dropped():
    cites = citations_for("Claim [1], invented [9], zero [0], repeat [1].", CHUNKS, "")

    assert [c["n"] for c in cites] == [1]


def test_empty_store_answers_without_calling_the_model(monkeypatch):
    def explode():
        raise AssertionError("the model must not be called when there is nothing to cite")

    monkeypatch.setattr(answer, "client", explode)

    assert generate("anything at all", []) == {"answer": NO_CONTEXT, "citations": []}


@pytest.fixture
def lab_table():
    rows = [
        "|Analyte|Result|Unit|Reference range|",
        "|---|---|---|---|",
        "|Haemoglobin|11.2|g/dL|13.0 - 17.0|",
        "|Sodium|136|mmol/L|135 - 145|",
        "|Creatinine|124|umol/L|60 - 110|",
        "|Ferritin|18|ug/L|30 - 400|",
        "|Vitamin B12|212|pmol/L|145 - 570|",
    ]
    return {"filename": "lab.pdf", "page": 2, "kind": "table", "text": "\n".join(rows)}


def test_table_snippet_shows_the_row_the_question_asks_about(lab_table):
    snippet = snippet_for(lab_table, "What was the ferritin result and its reference range?")

    assert "|Ferritin|18|ug/L|30 - 400|" in snippet
    assert snippet.startswith("|Analyte|Result|Unit|Reference range|")
    assert "Haemoglobin" not in snippet


def test_table_snippet_falls_back_when_nothing_matches(lab_table):
    snippet = snippet_for(lab_table, "who signed the discharge summary")

    assert snippet.startswith("|Analyte|Result|Unit|Reference range|")
    assert "Haemoglobin" in snippet


def test_text_snippet_is_still_the_top_of_the_chunk():
    chunk = {"filename": "a.pdf", "page": 1, "kind": "text", "text": "alpha beta gamma " * 40}

    snippet = snippet_for(chunk, "gamma")

    assert snippet.startswith("alpha beta gamma")
    assert snippet.endswith("...")
