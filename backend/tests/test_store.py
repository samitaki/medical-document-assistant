import pytest

from ingest import store
from ingest.pipeline import ingest_pdf


class FakeClient:
    """Records what the pipeline would have sent to qdrant."""

    def __init__(self):
        self.points = {}
        self.deleted = []

    def collection_exists(self, name):
        return True

    def upsert(self, name, points, wait=True):
        for p in points:
            self.points[p.id] = p.payload

    def delete(self, name, points_selector, wait=True):
        filename = points_selector.must[0].match.value
        self.deleted.append(filename)
        for pid in [k for k, v in self.points.items() if v["filename"] == filename]:
            del self.points[pid]


class FakeEmbedder:
    embedding_size = 4

    def embed(self, texts):
        return [[0.1, 0.2, 0.3, 0.4] for _ in texts]


@pytest.fixture
def fake(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(store, "client", lambda: client)
    monkeypatch.setattr(store, "embedder", lambda: FakeEmbedder())
    return client


def test_reingesting_replaces_instead_of_duplicating(fake, discharge_pdf):
    first = ingest_pdf(discharge_pdf)
    after_first = dict(fake.points)

    second = ingest_pdf(discharge_pdf)

    assert second["chunks"] == first["chunks"]
    assert len(fake.points) == first["chunks"]
    assert set(fake.points) == set(after_first)
    assert fake.deleted == [discharge_pdf.name, discharge_pdf.name]


def test_two_documents_live_side_by_side(fake, discharge_pdf, lab_pdf):
    a = ingest_pdf(discharge_pdf)
    b = ingest_pdf(lab_pdf)

    assert len(fake.points) == a["chunks"] + b["chunks"]
    assert {p["filename"] for p in fake.points.values()} == {discharge_pdf.name, lab_pdf.name}
