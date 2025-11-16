import pytest
from benchmark_framework.metrics.exact_match import ExactMatchMetric


def test_exact_match_identical_texts_returns_one():
    """Test that two identical texts return an exact match score of 1.0."""
    metric = ExactMatchMetric()
    text = "zakaz prowadzenia pojazdów"

    score = metric(prediction=text, reference=text)

    assert score == 1.0, f"Expected score 1.0 for identical texts, got {score}"


def test_exact_match_different_texts_returns_zero():
    """Test that two different texts return an exact match score of 0.0."""
    metric = ExactMatchMetric()
    prediction = "zakaz prowadzenia pojazdów"
    reference = "kara grzywny"

    score = metric(prediction=prediction, reference=reference)

    assert score == 0.0, f"Expected score 0.0 for different texts, got {score}"


def test_exact_match_texts_with_punctuation_differences_returns_one():
    """Test that texts differing only in punctuation return an exact match score of 1.0."""
    metric = ExactMatchMetric()
    prediction = "zakaz prowadzenia pojazdów"
    reference = "zakaz prowadzenia pojazdów;"

    score = metric(prediction=prediction, reference=reference)

    assert (
        score == 1.0
    ), f"Expected score 1.0 for texts with only punctuation differences, got {score}"


def test_exact_match_texts_with_multiple_punctuation_marks_returns_one():
    """Test that texts with various punctuation marks are normalized correctly."""
    metric = ExactMatchMetric()
    prediction = "To jest test!"
    reference = "To, jest test."

    score = metric(prediction=prediction, reference=reference)

    assert score == 1.0, f"Expected score 1.0 for texts with punctuation, got {score}"


def test_exact_match_texts_with_extra_whitespace_returns_one():
    """Test that texts with different whitespace are normalized correctly."""
    metric = ExactMatchMetric()
    prediction = "zakaz   prowadzenia    pojazdów"
    reference = "zakaz prowadzenia pojazdów"

    score = metric(prediction=prediction, reference=reference)

    assert (
        score == 1.0
    ), f"Expected score 1.0 for texts with different whitespace, got {score}"


def test_exact_match_texts_with_different_word_order_returns_zero():
    """Test that texts with different word order return 0.0."""
    metric = ExactMatchMetric()
    prediction = "prowadzenia zakaz pojazdów"
    reference = "zakaz prowadzenia pojazdów"

    score = metric(prediction=prediction, reference=reference)

    assert (
        score == 0.0
    ), f"Expected score 0.0 for texts with different word order, got {score}"


def test_exact_match_empty_texts_returns_one():
    """Test that two empty texts return an exact match score of 1.0."""
    metric = ExactMatchMetric()

    score = metric(prediction="", reference="")

    assert score == 1.0, f"Expected score 1.0 for two empty texts, got {score}"


def test_exact_match_one_empty_text_returns_zero():
    """Test that one empty and one non-empty text return 0.0."""
    metric = ExactMatchMetric()

    score = metric(prediction="", reference="zakaz prowadzenia pojazdów")

    assert score == 0.0, f"Expected score 0.0 for empty vs non-empty text, got {score}"
