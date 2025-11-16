import pytest
from benchmark_framework.metrics.weighted_bleu import WeightedBleuMetric


def test_bleu_identical_texts_returns_score_one():
    """Test that two identical texts return a BLEU score of 1.0 without TF-IDF weighting."""
    metric = WeightedBleuMetric(ngram_importances=[1, 1, 1, 1], resources=None)
    text = "To jest przykładowy tekst testowy w języku polskim"
    score = metric(prediction=text, reference=text)
    assert score == pytest.approx(
        1.0
    ), f"Expected score 1.0 for identical texts, got {score}"


def test_bleu_almost_equal_texts():
    metric = WeightedBleuMetric(ngram_importances=[1, 1, 1, 1], resources=None)
    prediction = "zakaz prowadzenia pojazdów"
    reference = "zakaz prowadzenia pojazdów;"
    score = metric(prediction=prediction, reference=reference)
    print(score)
    assert score == pytest.approx(1.0)
