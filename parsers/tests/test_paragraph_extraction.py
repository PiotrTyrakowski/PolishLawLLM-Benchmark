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


@pytest.mark.parametrize(
    "article_num,paragraph_num,expected_text",
    [
        (
            1,
            1,
            "Odpowiedzialności karnej podlega ten tylko, kto popełnia czyn zabroniony pod groźbą kary przez ustawę obowiązującą w czasie jego popełnienia.",
        ),
        (
            1,
            2,
            "Nie stanowi przestępstwa czyn zabroniony, którego społeczna szkodliwość jest znikoma.",
        ),
    ],
)
def test_extract_paragraph(
    extractor_instance, article_num, paragraph_num, expected_text
):
    """Test that paragraph extraction returns the expected text."""
    result = extractor_instance.get_paragraph(article_num, paragraph_num)
    assert (
        result == expected_text
    ), f"Art. {article_num} § {paragraph_num} does not match expected text"
