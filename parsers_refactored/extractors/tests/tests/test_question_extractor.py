import pytest
from parsers_refactored.extractors.question_extractor import QuestionExtractor


@pytest.fixture
def extractor():
    return QuestionExtractor()


def test_extract_single_question(extractor):
    """Test extraction of a single question."""
    text = """
    1. Które z poniższych aktów prawnych jest aktem prawa powszechnie obowiązującego?
    A. Zarządzenie Prezesa Rady Ministrów
    B. Ustawa uchwalona przez Sejm
    C. Okólnik ministra
    """

    questions = extractor.extract(text)

    assert len(questions) == 1
    assert questions[0]["question_number"] == 1
    assert "aktem prawa" in questions[0]["question"]
    assert "Zarządzenie" in questions[0]["A"]
    assert "Ustawa" in questions[0]["B"]
    assert "Okólnik" in questions[0]["C"]


def test_extract_multiple_questions(extractor):
    """Test extraction of multiple questions."""
    text = """
    1. Pierwsze pytanie?
    A. Odpowiedź A1
    B. Odpowiedź B1
    C. Odpowiedź C1
    
    2. Drugie pytanie?
    A. Odpowiedź A2
    B. Odpowiedź B2
    C. Odpowiedź C2
    
    3. Trzecie pytanie?
    A. Odpowiedź A3
    B. Odpowiedź B3
    C. Odpowiedź C3
    """

    questions = extractor.extract(text)

    assert len(questions) == 3
    assert questions[0]["question_number"] == 1
    assert questions[1]["question_number"] == 2
    assert questions[2]["question_number"] == 3
