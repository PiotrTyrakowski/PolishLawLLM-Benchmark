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
    assert article is not None, "Article 1 was not found in the provided PDF"
    assert "Art. 1." in article
    print(article + "\n--- End of Article 1 ---\n")
    assert len(article) > 20


def test_extract_article_2(extractor_instance):
    article = extractor_instance.get_article(2)
    assert article is not None, "Article 2 was not found in the provided PDF"
    assert "Art. 2." in article
    print(article + "\n--- End of Article 2 ---\n")
    assert len(article) > 20
