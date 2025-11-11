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


def test_extract_article_1(extractor_instance):
    """Test that get_article(1) returns content containing 'Art. 1.' and some text."""
    article = extractor_instance.get_article(1)
    print("\n--- Article 1 ---\n" + article)
    assert len(article) > 20


def test_extract_article_2(extractor_instance):
    article = extractor_instance.get_article(2)
    print("\n--- Article 2 ---\n" + article)
    assert len(article) > 20


def test_extract_article_47(extractor_instance):
    article = extractor_instance.get_article(47)
    print("\n--- Article 47 ---\n" + article)
    assert len(article) > 20
