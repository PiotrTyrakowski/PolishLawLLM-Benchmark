import os
import pytest

from parsers.LegalBaseExtractor.LegalBaseExtractor import LegalBaseExtractor


@pytest.fixture(scope="session")
def extractor_instance():
    """Create a single LegalBaseExtractor instance for all tests in the session."""
    pdf_path = "data/kk.pdf"
    if not os.path.exists(pdf_path):
        pytest.skip(f"PDF path set in LEGAL_PDF_PATH does not exist: {pdf_path}")

    extractor = LegalBaseExtractor(pdf_path)
    return extractor
