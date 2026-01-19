import pytest
from pathlib import Path

from src.parsers.parsers.getters import get_questions_parser
from src.parsers.domain.question import Question


def get_pdf_path():
    """Helper function to get the path to the 2025 exam PDF."""
    file_path = (
        Path(__file__).parent
        / ".."
        / ".."
        / ".."
        / ".."
        / "data"
        / "pdfs"
        / "2025"
        / "Zestaw_pytań_testowych_na_egzamin_wstępny_dla_kandydatów_na_aplikantów_adwokackich_i_radcowskich_27_września_2025.pdf"
    )
    return file_path.resolve()


@pytest.fixture
def parser_with_mock():
    return get_questions_parser(file_path=get_pdf_path())


def test_parse_returns_question_objects(parser_with_mock):
    """Test that parse returns a list of Question objects."""
    questions = parser_with_mock.parse()

    assert isinstance(questions, list)
    assert len(questions) > 0
    assert all(isinstance(q, Question) for q in questions)


def test_parse_extracts_all_questions(parser_with_mock):
    """Test that all 150 questions are extracted from the exam."""
    questions = parser_with_mock.parse()
    assert len(questions) == 150


def test_parse_question_numbers_are_sequential(parser_with_mock):
    """Test that question numbers are sequential from 1 to 150."""
    questions = parser_with_mock.parse()

    question_numbers = [q.id for q in questions]
    assert question_numbers == list(range(1, 151))


def test_parse_first_question_content(parser_with_mock):
    """Test that the first question is correctly parsed."""
    questions = parser_with_mock.parse()

    first_question = questions[0]
    assert first_question.id == 1
    assert (
        first_question.text
        == "Zgodnie z Kodeksem karnym, czyn zabroniony uważa się za popełniony w miejscu, w którym:"
    )
    assert (
        first_question.option_a
        == "sprawca działał lub zaniechał działania, do którego był obowiązany, albo gdzie skutek stanowiący znamię czynu zabronionego nastąpił lub według zamiaru sprawcy miał nastąpić,"
    )
    assert first_question.option_b == "ujawniono czyn zabroniony,"
    assert first_question.option_c == "zatrzymano sprawcę czynu zabronionego."


def test_parse_last_question_content(parser_with_mock):
    """Test that the last question is correctly parsed."""
    questions = parser_with_mock.parse()

    first_question = questions[-1]
    assert first_question.id == 150
    assert (
        first_question.text
        == "Zgodnie z ustawą o Rzeczniku Praw Obywatelskich, jeżeli Rzecznik Praw Obywatelskich zrzekł się wykonywania obowiązków:"
    )
    assert (
        first_question.option_a
        == "Senat podejmuje uchwałę w sprawie jego odwołania na wniosek Marszałka Senatu,"
    )
    assert (
        first_question.option_b
        == "Sejm podejmuje uchwałę w sprawie jego odwołania na wniosek Marszałka Sejmu,"
    )
    assert (
        first_question.option_c
        == "Rzecznika Praw Obywatelskich odwołuje Prezydent Rzeczypospolitej Polskiej."
    )
