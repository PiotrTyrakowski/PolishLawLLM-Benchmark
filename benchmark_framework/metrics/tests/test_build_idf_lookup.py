import json
import math
import pytest
import tempfile
from pathlib import Path
from collections import Counter

from benchmark_framework.metrics.weighted_bleu import WeightedBleuMetric


def test_build_idf_lookup_single_corpus():
    with tempfile.TemporaryDirectory() as tmp_dir:
        corpus_data = {
            "1": "the quick brown fox",
            "2": "the lazy dog",
            "3": "the quick cat",
        }

        corpus_file = Path(tmp_dir) / "test_corpus.json"
        with open(corpus_file, "w") as f:
            json.dump(corpus_data, f)

        metric = WeightedBleuMetric(corpuses_dir=Path(tmp_dir))

        assert "test_corpus" in metric.idf_lookup
        assert len(metric.idf_lookup["test_corpus"]) > 0

        idf_scores = metric.idf_lookup["test_corpus"]
        assert "the" in idf_scores
        assert "dog" in idf_scores

        assert idf_scores["the"] < idf_scores["dog"]


def test_build_idf_lookup_multiple_corpuses():
    with tempfile.TemporaryDirectory() as tmp_dir:
        corpus1_data = {"1": "hello world", "2": "hello universe"}
        corpus1_file = Path(tmp_dir) / "corpus1.json"
        with open(corpus1_file, "w") as f:
            json.dump(corpus1_data, f)

        corpus2_data = {"1": "goodbye world", "2": "farewell earth"}
        corpus2_file = Path(tmp_dir) / "corpus2.json"
        with open(corpus2_file, "w") as f:
            json.dump(corpus2_data, f)

        metric = WeightedBleuMetric(corpuses_dir=Path(tmp_dir))

        assert "corpus1" in metric.idf_lookup
        assert "corpus2" in metric.idf_lookup
        assert len(metric.idf_lookup) == 2


def test_build_idf_lookup_empty_directory():
    with tempfile.TemporaryDirectory() as tmp_dir:
        metric = WeightedBleuMetric(corpuses_dir=Path(tmp_dir))
        assert metric.idf_lookup == {}


def test_build_idf_lookup_idf_calculation():
    with tempfile.TemporaryDirectory() as tmp_dir:
        corpus_data = {
            "1": "apple banana",
            "2": "apple cherry",
            "3": "apple date",
            "4": "banana cherry",
        }

        corpus_file = Path(tmp_dir) / "test.json"
        with open(corpus_file, "w") as f:
            json.dump(corpus_data, f)

        metric = WeightedBleuMetric(corpuses_dir=Path(tmp_dir))
        idf_scores = metric.idf_lookup["test"]

        expected_apple = math.log(5 / 4) + 1
        expected_banana = math.log(5 / 3) + 1

        assert abs(idf_scores["apple"] - expected_apple) < 0.0001
        assert abs(idf_scores["banana"] - expected_banana) < 0.0001


def test_build_idf_lookup_case_insensitive():
    with tempfile.TemporaryDirectory() as tmp_dir:
        corpus_data = {"1": "Hello World", "2": "HELLO universe", "3": "hello there"}

        corpus_file = Path(tmp_dir) / "test.json"
        with open(corpus_file, "w") as f:
            json.dump(corpus_data, f)

        metric = WeightedBleuMetric(corpuses_dir=Path(tmp_dir))
        idf_scores = metric.idf_lookup["test"]

        assert "hello" in idf_scores
        expected_idf = math.log(4 / 4) + 1
        assert abs(idf_scores["hello"] - expected_idf) < 0.0001


def test_build_idf_lookup_duplicate_tokens_in_document():
    with tempfile.TemporaryDirectory() as tmp_dir:
        corpus_data = {"1": "apple apple apple", "2": "banana banana"}

        corpus_file = Path(tmp_dir) / "test.json"
        with open(corpus_file, "w") as f:
            json.dump(corpus_data, f)

        metric = WeightedBleuMetric(corpuses_dir=Path(tmp_dir))
        idf_scores = metric.idf_lookup["test"]

        expected_apple = math.log(3 / 2) + 1
        assert abs(idf_scores["apple"] - expected_apple) < 0.0001


def test_build_idf_lookup_no_corpus_dir():
    metric = WeightedBleuMetric()
    assert metric.idf_lookup is None


def test_build_idf_lookup_non_json_files_ignored():
    with tempfile.TemporaryDirectory() as tmp_dir:
        corpus_data = {"1": "hello world"}
        corpus_file = Path(tmp_dir) / "corpus.json"
        with open(corpus_file, "w") as f:
            json.dump(corpus_data, f)

        text_file = Path(tmp_dir) / "readme.txt"
        with open(text_file, "w") as f:
            f.write("This is not a corpus")

        metric = WeightedBleuMetric(corpuses_dir=Path(tmp_dir))

        assert "corpus" in metric.idf_lookup
        assert "readme" not in metric.idf_lookup
        assert len(metric.idf_lookup) == 1


def test_build_idf_lookup_empty_corpus_file():
    with tempfile.TemporaryDirectory() as tmp_dir:
        corpus_data = {}
        corpus_file = Path(tmp_dir) / "empty.json"
        with open(corpus_file, "w") as f:
            json.dump(corpus_data, f)

        metric = WeightedBleuMetric(corpuses_dir=Path(tmp_dir))

        assert "empty" in metric.idf_lookup
        assert len(metric.idf_lookup["empty"]) == 0
