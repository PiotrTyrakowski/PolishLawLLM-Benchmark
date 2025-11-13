import pytest

from parsers.parse_answers import ANSWERS_REGEXP


@pytest.mark.parametrize(
    "text,question_number,correct_answer,legal_basis",
    [
        (
            "art. 17 § 1 k.s.h.\n1. A",
            "1",
            "A",
            "art. 17 § 1 k.s.h.",
        ),
        (
            "art. 16 § 1 k.k.\n1. A",
            "1",
            "A",
            "art. 16 § 1 k.k.",
        ),
        (
            "art. 77 k.p.k.\n1. A",
            "1",
            "A",
            "art. 77 k.p.k.",
        ),
        (
            "art. 607b k.p.k.\n1. A",
            "1",
            "A",
            "art. 607b k.p.k.",
        ),
        (
            "art. 10 § 1 k.r. i o.\n1. A",
            "1",
            "A",
            "art. 10 § 1 k.r. i o.",
        ),
        (
            "art. 83 § 1a k. r. i o.\n1. A",
            "1",
            "A",
            "art. 83 § 1a k. r. i o.",
        ),
        (
            "art. 39 pkt 3 k.k.\n1. A",
            "1",
            "A",
            "art. 39 pkt 3 k.k.",
        ),
    ],
)
def test_extract_answers_regexp(text, question_number, correct_answer, legal_basis):
    """Test that ANSWERS_REGEXP matches the expected pattern."""
    match = ANSWERS_REGEXP.search(text)
    assert match is not None
    assert match.group(1) == legal_basis  # Group 1 is legal_basis
    assert match.group(2) == question_number  # Group 2 is question_number
    assert match.group(3) == correct_answer  # Group 3 is correct_answer
