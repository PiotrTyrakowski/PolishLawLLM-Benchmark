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


def test_extract_article_1_paragraph_1(extractor_instance):
    paragraph = extractor_instance.get_paragraph(1, 1)
    print("\n--- Article 1, Paragraph 1 ---\n" + paragraph)


def test_extract_article_1_paragraph_2(extractor_instance):
    paragraph = extractor_instance.get_paragraph(1, 2)
    print("\n--- Article 1, Paragraph 2 ---\n" + paragraph)
