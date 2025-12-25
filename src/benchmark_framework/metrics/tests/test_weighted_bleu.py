import pytest
import json
import tempfile
from pathlib import Path
from src.benchmark_framework.metrics.weighted_bleu import WeightedBleuMetric


@pytest.fixture
def corpus_directory():
    """Create a temporary directory with sample corpus files for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        corpus_path = Path(tmpdir)

        kk = {
            "1": "The quick brown fox jumps over the lazy dog",
            "2": "A journey of a thousand miles begins with a single step",
            "3": "To be or not to be that is the question",
            "4": "All that glitters is not gold",
            "5": "The early bird catches the worm",
        }

        corp2 = {
            "1": "The xylophone makes beautiful music when played correctly",
            "2": "The piano makes beautiful music when played correctly",
            "3": "The guitar makes beautiful music when played correctly",
            "4": "The violin makes beautiful music when played correctly",
            "5": "The drums makes beautiful music when played correctly",
        }

        with open(corpus_path / "kk.json", "w") as f:
            json.dump(kk, f)
        with open(corpus_path / "corp2.json", "w") as f:
            json.dump(corp2, f)

        yield corpus_path


def test_weighted_bleu_with_corpus_directory(corpus_directory):
    # Initialize metric with corpus directory
    metric = WeightedBleuMetric(
        ngram_importances=[1, 1, 1, 1], corpuses_dir=corpus_directory
    )

    # Verify metric name includes "weighted"
    assert "weighted_bleu" in metric.name
    assert metric.idf_lookup is not None
    assert "kk" in metric.idf_lookup

    reference = "quick brown fox"
    prediction = "quick brown fox"
    score_perfect = metric._compute(prediction, reference, code_abbr="kk")
    assert score_perfect > 0.95, f"Perfect match should score high, got {score_perfect}"


def test_weighted_bleu_with_corpus2(corpus_directory):
    metric = WeightedBleuMetric(
        ngram_importances=[1, 1, 1, 1], corpuses_dir=corpus_directory
    )

    assert "weighted_bleu" in metric.name
    assert metric.idf_lookup is not None
    assert "corp2" in metric.idf_lookup

    reference = "violin makes beautiful music"
    prediction1 = "violin makes beautiful cars"
    prediction2 = "cars makes beautiful music"
    score1 = metric._compute(prediction1, reference, code_abbr="corp2")
    score2 = metric._compute(prediction2, reference, code_abbr="corp2")
    assert 0 < score2 < score1 < 1
