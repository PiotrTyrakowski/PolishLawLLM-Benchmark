import pytest
from parsers.LegalBaseExtractor.initialize_extractors import parse_legal_basis


@pytest.mark.parametrize(
    "legal_basis,expected_code,expected_article,expected_paragraph,expected_point",
    [
        ("art. 6 § 2 k.k.", "k.k.", "6", "2", None),
        ("art. 9 pkt 1 k.p.", "k.p.", "9", None, "1"),
        ("art. 12 k.k.", "k.k.", "12", None, None),
        ("art. 15 pkt 1 § 2 k.p.", "k.p.", "15", "2", "1"),
        ("art. 6a § 2 k.k.", "k.k.", "6a", "2", None),
        ("art. 10 § 1 k.r. i o.", "k.r. i o.", "10", "1", None),
        ("art. 10 § 1 k. r. i o.", "k. r. i o.", "10", "1", None),
        ("art. 12 pkt 1 § 2 pkt 3 k.p.", "k.p.", "12", "2", "1"),
        ("art.  6  §  2  k.k.", "k.k.", "6", "2", None),
        ("ART. 6 § 2 K.K.", "K.K.", "6", "2", None),
    ],
)
def test_parse_legal_basis(
    legal_basis, expected_code, expected_article, expected_paragraph, expected_point
):
    """Test parsing of various legal basis string formats."""
    result = parse_legal_basis(legal_basis)

    assert result["code_abbreviation"] == expected_code
    assert result["article_number"] == expected_article
    assert result["paragraph_number"] == expected_paragraph
    assert result["point_number"] == expected_point
