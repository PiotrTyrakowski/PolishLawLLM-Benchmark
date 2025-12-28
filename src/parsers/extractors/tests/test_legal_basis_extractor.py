import pytest
from src.parsers.extractors.legal_reference_extractor import LegalReferenceExtractor
from src.parsers.utils.text_formatter import TextFormatter


@pytest.fixture
def extractor():
    return LegalReferenceExtractor()


@pytest.mark.parametrize(
    "legal_basis,expected",
    [
        # Basic article only
        (
            "art. 12 k.k.",
            {
                "article_number": "12",
                "paragraph_number": None,
                "point_number": None,
                "code_abbreviation": "k.k.",
            },
        ),
        # Article with paragraph
        (
            "art. 6 § 2 k.k.",
            {
                "article_number": "6",
                "paragraph_number": "2",
                "point_number": None,
                "code_abbreviation": "k.k.",
            },
        ),
        # Article with point
        (
            "art. 9 pkt 1 k.p.",
            {
                "article_number": "9",
                "paragraph_number": None,
                "point_number": "1",
                "code_abbreviation": "k.p.",
            },
        ),
        # Article with paragraph and point
        (
            "art. 15 § 2 pkt 1 k.p.",
            {
                "article_number": "15",
                "paragraph_number": "2",
                "point_number": "1",
                "code_abbreviation": "k.p.",
            },
        ),
        # Article number with letter suffix
        (
            "art. 6a § 2 k.k.",
            {
                "article_number": "6a",
                "paragraph_number": "2",
                "point_number": None,
                "code_abbreviation": "k.k.",
            },
        ),
        # Complex code abbreviation (k.r. i o.)
        (
            "art. 10 § 1 k.r. i o.",
            {
                "article_number": "10",
                "paragraph_number": "1",
                "point_number": None,
                "code_abbreviation": "k.r. i o.",
            },
        ),
        # Complex code abbreviation with spaces (k. r. i o.)
        (
            "art. 10 § 1 k. r. i o.",
            {
                "article_number": "10",
                "paragraph_number": "1",
                "point_number": None,
                "code_abbreviation": "k. r. i o.",
            },
        ),
    ],
)
def test_parse_valid_legal_basis(extractor, legal_basis, expected):
    """Test parsing of valid legal basis strings."""
    result = extractor.extract(legal_basis)

    assert result.article == expected["article_number"]
    assert result.paragraph == expected["paragraph_number"]
    assert result.point == expected["point_number"]
    assert result.code == expected["code_abbreviation"]


@pytest.mark.parametrize(
    "legal_basis,expected_code",
    [
        ("art. 1 k.c.", "k.c."),  # Civil Code
        ("art. 1 k.p.c.", "k.p.c."),  # Civil Procedure Code
        ("art. 1 k.k.", "k.k."),  # Criminal Code
        ("art. 1 k.p.k.", "k.p.k."),  # Criminal Procedure Code
        ("art. 1 k.p.", "k.p."),  # Labor Code
        ("art. 1 k.p.a.", "k.p.a."),  # Administrative Procedure Code
        ("art. 1 k.s.h.", "k.s.h."),  # Commercial Companies Code
        ("art. 1 k.w.", "k.w."),  # Electoral Code
        ("art. 1 k.k.s.", "k.k.s."),  # Fiscal Criminal Code
    ],
)
def test_parse_different_code_abbreviations(extractor, legal_basis, expected_code):
    """Test parsing of different Polish legal code abbreviations."""
    result = extractor.extract(legal_basis)
    assert result.code == expected_code


@pytest.mark.parametrize(
    "input_abbr,expected_output",
    [
        ("k.k.", "kk"),
        ("k.p.c.", "kpc"),
        ("k.c.", "kc"),
        ("k.r. i o.", "krio"),
        ("k. r. i o.", "krio"),
        ("K.K.", "kk"),  # Uppercase
        ("K.P.C.", "kpc"),  # Uppercase
        ("k . k .", "kk"),  # Extra spaces
        ("kk", "kk"),  # Already formatted
    ],
)
def test_format_code_abbreviation(input_abbr, expected_output):
    """Test formatting of various code abbreviations."""
    result = TextFormatter.format_code_abbreviation(input_abbr)
    assert result == expected_output
