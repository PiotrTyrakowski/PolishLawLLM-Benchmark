import pytest
from pathlib import Path

from src.parsers.parsers.getters import get_answers_parser
from src.parsers.domain.answer import Answer


@pytest.fixture
def parser():
    pdf_path = Path(__file__).parent / "test_data" / "test_answers.pdf"
    if not pdf_path.exists():
        pytest.skip(f"PDF file not found: {pdf_path}")
    return get_answers_parser(file_path=pdf_path)


def test_parse_returns_answer_objects(parser):
    answers = parser.parse()

    assert isinstance(answers, list)
    assert len(answers) > 0
    assert all(isinstance(a, Answer) for a in answers)


def test_parse_extracts_all_answers(parser):
    answers = parser.parse()
    assert len(answers) == 80


def test_parse_first_answer_content(parser):
    """Test that the first question is correctly parsed."""
    answers = parser.parse()

    first_answer = answers[0]
    assert first_answer.question_id == 1
    assert first_answer.answer == "A"
    assert first_answer.legal_basis == "art. 6 § 2 k.k."


def test_parse_last_answer_content(parser):
    """Test that the last question is correctly parsed."""
    answers = parser.parse()

    last_answer = answers[-1]
    assert last_answer.question_id == 119
    assert last_answer.answer == "A"
    assert last_answer.legal_basis == "art. 119 § 1 k.p.a."


def test_parse_answer_with_superindex(parser):
    """Test that the answer with superindex is correctly parsed."""
    answers = parser.parse()

    answer = next((a for a in answers if a.question_id == 100), None)
    assert answer is not None
    assert answer.question_id == 100
    assert answer.answer == "C"
    assert answer.legal_basis == "art. 300^73 § 1 k.s.h."


def test_parse_at_the_bottom_of_the_page(parser):
    """Test that the answer at the bottom of the page is correctly parsed."""
    answers = parser.parse()

    answer = next((a for a in answers if a.question_id == 45), None)
    assert answer is not None
    assert answer.question_id == 45
    assert answer.answer == "C"
    assert answer.legal_basis == "art. 645 § 1 k.c."
