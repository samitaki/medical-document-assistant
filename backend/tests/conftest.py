from pathlib import Path

import pytest

SAMPLES = Path(__file__).resolve().parents[2] / "sample_docs"


@pytest.fixture(scope="session")
def lab_pdf() -> Path:
    return SAMPLES / "lab_results_report.pdf"


@pytest.fixture(scope="session")
def discharge_pdf() -> Path:
    return SAMPLES / "discharge_summary.pdf"
