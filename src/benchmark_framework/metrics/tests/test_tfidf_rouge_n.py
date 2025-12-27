import json
import math
import tempfile
import pytest
from pathlib import Path

from src.benchmark_framework.metrics.tfidf_rouge_n import TFIDFRougeNMetric


def create_metric_with_corpus(
    corpus_data: dict, corpus_name: str = "test", ngram_importances=None
):
    tmp_dir = tempfile.mkdtemp()
    corpus_file = Path(tmp_dir) / f"{corpus_name}.json"
    with open(corpus_file, "w") as f:
        json.dump(corpus_data, f)
    if ngram_importances is not None:
        return TFIDFRougeNMetric(
            corpuses_dir=Path(tmp_dir), ngrams_importances=ngram_importances
        )
    return TFIDFRougeNMetric(corpuses_dir=Path(tmp_dir))


class TestBuildIdfLookup:
    """Tests for the build_idf_lookup method in TFIDFRougeNMetric."""

    def test_idf_lookup_stores_corpus_by_filename(self):
        """Test that IDF lookup is keyed by corpus filename (without extension)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            corpus_data = {"1": "hello world"}
            corpus_file = Path(tmp_dir) / "my_corpus.json"
            with open(corpus_file, "w") as f:
                json.dump(corpus_data, f)

            metric = TFIDFRougeNMetric(corpuses_dir=Path(tmp_dir))

            assert "my_corpus" in metric.idf_lookup
            assert len(metric.idf_lookup) == 1

    def test_idf_calculation_common_vs_rare_words(self):
        """Test that rare words have higher IDF than common words."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            corpus_data = {
                "1": "the cat",
                "2": "the dog",
                "3": "the bird",
                "4": "unique word",
            }
            corpus_file = Path(tmp_dir) / "test.json"
            with open(corpus_file, "w") as f:
                json.dump(corpus_data, f)

            metric = TFIDFRougeNMetric(corpuses_dir=Path(tmp_dir))
            idf_scores = metric.idf_lookup["test"]

            # "the" appears in 3 docs, "unique" appears in 1 doc
            assert idf_scores["the"] < idf_scores["unique"]

    def test_idf_formula_verification(self):
        """Test that IDF follows the formula: log(N/(df+1)) + 1."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            corpus_data = {
                "1": "apple banana",
                "2": "apple cherry",
                "3": "date",
            }
            corpus_file = Path(tmp_dir) / "test.json"
            with open(corpus_file, "w") as f:
                json.dump(corpus_data, f)

            metric = TFIDFRougeNMetric(corpuses_dir=Path(tmp_dir))
            idf_scores = metric.idf_lookup["test"]

            # apple appears in 2 docs, total 3 docs
            # IDF = log(3/(2+1)) + 1 = log(1) + 1
            expected_apple = math.log(1) + 1
            assert abs(idf_scores["apple"] - expected_apple) < 0.0001

            # date appears in 1 doc
            # IDF = log(3/(1+1)) + 1 = log(3/2) + 1
            expected_date = math.log(3 / 2) + 1
            assert abs(idf_scores["date"] - expected_date) < 0.0001


class TestGetTokensTfidf:
    """Tests for the get_tokens_tfidf method."""

    def test_tfidf_returns_dict_with_unique_tokens(self):
        """Test that get_tokens_tfidf returns a dict keyed by unique tokens."""
        corpus_data = {"1": "apple banana cherry"}
        metric = create_metric_with_corpus(corpus_data)

        ref_tokens = ["apple", "banana", "cherry"]
        weights = metric.get_tokens_tfidf(ref_tokens, "test")

        assert set(weights.keys()) == {"apple", "banana", "cherry"}

    def test_tfidf_tf_component(self):
        """Test that TF is calculated as count/total_tokens."""
        corpus_data = {"1": "word another"}
        metric = create_metric_with_corpus(corpus_data)

        # "word" appears twice, "another" appears once, total 3 tokens
        ref_tokens = ["word", "word", "another"]
        weights = metric.get_tokens_tfidf(ref_tokens, "test")

        # Both have same IDF (appear in 1 doc out of 1)
        idf_word = metric.idf_lookup["test"]["word"]
        idf_another = metric.idf_lookup["test"]["another"]

        # TF for "word" = 2/3, TF for "another" = 1/3
        expected_word = (2 / 3) * idf_word
        expected_another = (1 / 3) * idf_another

        assert abs(weights["word"] - expected_word) < 0.0001
        assert abs(weights["another"] - expected_another) < 0.0001

    def test_tfidf_higher_frequency_gives_higher_weight(self):
        """Test that tokens appearing more frequently in reference have higher TF-IDF."""
        corpus_data = {"1": "apple banana cherry"}
        metric = create_metric_with_corpus(corpus_data)

        # "apple" appears 3 times, "banana" appears 1 time
        ref_tokens = ["apple", "apple", "apple", "banana"]
        weights = metric.get_tokens_tfidf(ref_tokens, "test")

        # Same IDF for both, but different TF
        assert weights["apple"] > weights["banana"]

    def test_tfidf_raises_for_unknown_token(self):
        """Test that get_tokens_tfidf raises ValueError for tokens not in corpus."""
        corpus_data = {"1": "known words only"}
        metric = create_metric_with_corpus(corpus_data)

        ref_tokens = ["unknown"]

        with pytest.raises(
            ValueError, match="Token 'unknown' not found in test IDF lookup"
        ):
            metric.get_tokens_tfidf(ref_tokens, "test")

    def test_tfidf_case_sensitive_token_lookup(self):
        """Test that token lookup is case-sensitive against lowercased IDF keys."""
        corpus_data = {"1": "Hello World"}
        metric = create_metric_with_corpus(corpus_data)

        # IDF lookup stores lowercase keys
        assert "hello" in metric.idf_lookup["test"]
        assert "Hello" not in metric.idf_lookup["test"]

        # get_tokens_tfidf expects tokens to already be normalized
        ref_tokens = ["hello", "world"]
        weights = metric.get_tokens_tfidf(ref_tokens, "test")

        assert "hello" in weights
        assert "world" in weights

    def test_tfidf_single_token_reference(self):
        """Test TF-IDF with single token reference."""
        corpus_data = {"1": "single"}
        metric = create_metric_with_corpus(corpus_data)

        ref_tokens = ["single"]
        weights = metric.get_tokens_tfidf(ref_tokens, "test")

        # TF = 1/1 = 1, IDF from corpus
        idf = metric.idf_lookup["test"]["single"]
        expected = 1.0 * idf

        assert abs(weights["single"] - expected) < 0.0001

    def test_tfidf_idf_difference_affects_weight(self):
        """Test that tokens with different IDF values produce different weights."""
        corpus_data = {
            "1": "common rare",
            "2": "common another",
            "3": "common something",
        }
        metric = create_metric_with_corpus(corpus_data)

        # Equal TF (1 each), but different IDF
        ref_tokens = ["common", "rare"]
        weights = metric.get_tokens_tfidf(ref_tokens, "test")

        # "common" appears in all 3 docs, "rare" in 1 doc
        # Same TF (1/2 each), but "rare" has higher IDF
        assert weights["rare"] > weights["common"]


class TestGetNgramWeight:
    """Tests for the get_ngram_weight method."""

    def test_ngram_weight_normalized_by_max(self):
        """Test that n-gram weight is normalized by max token weight."""
        corpus_data = {"1": "apple banana"}
        metric = create_metric_with_corpus(corpus_data)

        # Create token weights where one is clearly larger
        token_weights = {"apple": 0.5, "banana": 1.0}

        unigram = ("apple",)
        weight = metric.get_ngram_weight(unigram, token_weights)

        # max_weight = 1.0, so apple weight = 0.5/1.0 = 0.5
        assert abs(weight - 0.5) < 0.0001

    def test_ngram_weight_single_token_max_returns_one(self):
        """Test that unigram with max weight returns 1.0."""
        corpus_data = {"1": "word"}
        metric = create_metric_with_corpus(corpus_data)

        token_weights = {"word": 2.0}

        unigram = ("word",)
        weight = metric.get_ngram_weight(unigram, token_weights)

        # max_weight = 2.0, word weight = 2.0/2.0 = 1.0
        assert abs(weight - 1.0) < 0.0001

    def test_ngram_weight_averages_across_tokens(self):
        """Test that n-gram weight is the average of normalized token weights."""
        corpus_data = {"1": "a b"}
        metric = create_metric_with_corpus(corpus_data)

        token_weights = {"a": 0.4, "b": 0.8}  # max = 0.8

        bigram = ("a", "b")
        weight = metric.get_ngram_weight(bigram, token_weights)

        # normalized: a = 0.4/0.8 = 0.5, b = 0.8/0.8 = 1.0
        # average = (0.5 + 1.0) / 2 = 0.75
        assert abs(weight - 0.75) < 0.0001

    def test_ngram_weight_unknown_token_treated_as_zero(self):
        """Test that tokens not in token_weights are treated as 0."""
        corpus_data = {"1": "known"}
        metric = create_metric_with_corpus(corpus_data)

        token_weights = {"known": 1.0}

        # "unknown" is not in token_weights
        bigram = ("known", "unknown")
        weight = metric.get_ngram_weight(bigram, token_weights)

        unigram = ("unknown",)
        assert metric.get_ngram_weight(unigram, token_weights) == 0

        # known = 1.0/1.0 = 1.0, unknown = 0.0
        # average = (1.0 + 0.0) / 2 = 0.5
        assert abs(weight - 0.5) < 0.0001

    def test_ngram_weight_trigram(self):
        """Test weight calculation for trigrams."""
        corpus_data = {"1": "a b c"}
        metric = create_metric_with_corpus(corpus_data)

        token_weights = {"a": 0.3, "b": 0.6, "c": 0.9}  # max = 0.9

        trigram = ("a", "b", "c")
        weight = metric.get_ngram_weight(trigram, token_weights)

        # normalized: a = 0.3/0.9 = 1/3, b = 0.6/0.9 = 2/3, c = 0.9/0.9 = 1.0
        # average = (1/3 + 2/3 + 1.0) / 3 = 2/3
        expected = (1 / 3 + 2 / 3 + 1.0) / 3
        assert abs(weight - expected) < 0.0001

    def test_ngram_weight_all_unknown_tokens_returns_zero(self):
        """Test that n-gram with all unknown tokens returns 0."""
        corpus_data = {"1": "known"}
        metric = create_metric_with_corpus(corpus_data)

        token_weights = {"known": 1.0}

        bigram = ("unknown1", "unknown2")
        weight = metric.get_ngram_weight(bigram, token_weights)

        assert weight == 0.0

    def test_ngram_weight_bounds_between_zero_and_one(self):
        """Test that n-gram weight is always between 0 and 1."""
        corpus_data = {"1": "a b c d"}
        metric = create_metric_with_corpus(corpus_data)

        token_weights = {"a": 0.1, "b": 100.0, "c": 0.001}

        for ngram in [("a",), ("b",), ("c",), ("a", "b"), ("b", "c"), ("a", "b", "c")]:
            weight = metric.get_ngram_weight(ngram, token_weights)
            assert 0.0 <= weight <= 1.0, f"Weight {weight} for {ngram} out of bounds"

    def test_ngram_weight_equal_weights_returns_one(self):
        """Test that n-gram with all equal weights returns 1.0."""
        corpus_data = {"1": "a b c"}
        metric = create_metric_with_corpus(corpus_data)

        token_weights = {"a": 0.5, "b": 0.5, "c": 0.5}

        trigram = ("a", "b", "c")
        weight = metric.get_ngram_weight(trigram, token_weights)

        # All weights equal to max, so all normalized to 1.0
        # average = (1.0 + 1.0 + 1.0) / 3 = 1.0
        assert abs(weight - 1.0) < 0.0001


class TestCalculateRecall:
    """Tests for the calculate_recall method."""

    def test_recall_identical_texts_returns_one(self):
        """Test that identical texts return recall of 1.0."""
        corpus_data = {"1": "the cat sat on mat"}
        metric = create_metric_with_corpus(corpus_data)

        recall = metric.calculate_recall(
            prediction="the cat sat on mat",
            reference="the cat sat on mat",
            n=1,
            code_abbr="test",
        )

        assert abs(recall - 1.0) < 0.0001

    def test_recall_no_overlap_returns_zero(self):
        """Test that texts with no common words return recall of 0.0."""
        corpus_data = {"1": "apple banana cherry date"}
        metric = create_metric_with_corpus(corpus_data)

        recall = metric.calculate_recall(
            prediction="apple banana", reference="cherry date", n=1, code_abbr="test"
        )

        assert recall == 0.0

    def test_recall_partial_overlap_unigrams(self):
        """Test recall with partial overlap in unigrams."""
        corpus_data = {"1": "the cat dog sat"}
        metric = create_metric_with_corpus(corpus_data)

        # Reference: "the cat sat" (3 unigrams)
        # Prediction: "the dog sat" (3 unigrams)
        # Overlap: "the", "sat" (2 matches out of 3 reference unigrams)
        recall = metric.calculate_recall(
            prediction="the dog sat", reference="the cat sat", n=1, code_abbr="test"
        )

        # With TF-IDF weighting, the exact value depends on token weights
        # but should be between 0 and 1
        assert 0.0 < recall < 1.0

    def test_recall_bigrams_identical_returns_one(self):
        """Test that identical texts return recall of 1.0 for bigrams."""
        corpus_data = {"1": "the quick brown fox"}
        metric = create_metric_with_corpus(corpus_data)

        recall = metric.calculate_recall(
            prediction="the quick brown fox",
            reference="the quick brown fox",
            n=2,
            code_abbr="test",
        )

        assert abs(recall - 1.0) < 0.0001

    def test_recall_bigrams_no_overlap(self):
        """Test bigram recall with no overlapping bigrams."""
        corpus_data = {"1": "a b c d"}
        metric = create_metric_with_corpus(corpus_data)

        # Reference bigrams: ("a", "b"), ("b", "c")
        # Prediction bigrams: ("c", "d")
        # No overlap
        recall = metric.calculate_recall(
            prediction="c d", reference="a b c", n=2, code_abbr="test"
        )

        assert recall == 0.0

    def test_recall_trigrams(self):
        """Test trigram recall calculation."""
        corpus_data = {"1": "one two three four five"}
        metric = create_metric_with_corpus(corpus_data)

        recall = metric.calculate_recall(
            prediction="one two three four five",
            reference="one two three four five",
            n=3,
            code_abbr="test",
        )

        assert abs(recall - 1.0) < 0.0001

    def test_recall_empty_prediction_returns_zero(self):
        """Test that empty prediction returns recall of 0.0."""
        corpus_data = {"1": "hello world"}
        metric = create_metric_with_corpus(corpus_data)

        recall = metric.calculate_recall(
            prediction="", reference="hello world", n=1, code_abbr="test"
        )

        assert recall == 0.0

    def test_recall_empty_reference_returns_zero(self):
        """Test that empty reference returns recall of 0.0."""
        corpus_data = {"1": "hello world"}
        metric = create_metric_with_corpus(corpus_data)

        recall = metric.calculate_recall(
            prediction="hello world", reference="", n=1, code_abbr="test"
        )

        assert recall == 0.0

    def test_recall_prediction_superset_of_reference(self):
        """Test recall when prediction contains all reference words and more."""
        corpus_data = {"1": "the cat sat on mat extra words"}
        metric = create_metric_with_corpus(corpus_data)

        # All reference unigrams are in prediction
        recall = metric.calculate_recall(
            prediction="the cat sat on mat extra words",
            reference="the cat sat",
            n=1,
            code_abbr="test",
        )

        assert abs(recall - 1.0) < 0.0001

    def test_recall_prediction_subset_of_reference(self):
        """Test recall when prediction is subset of reference."""
        corpus_data = {"1": "the cat sat on mat"}
        metric = create_metric_with_corpus(corpus_data)

        # Prediction has fewer words than reference
        recall = metric.calculate_recall(
            prediction="the cat", reference="the cat sat on mat", n=1, code_abbr="test"
        )

        # Not all reference tokens are captured
        assert 0.0 < recall < 1.0

    def test_recall_normalizes_punctuation(self):
        """Test that punctuation is normalized in recall calculation."""
        corpus_data = {"1": "hello world"}
        metric = create_metric_with_corpus(corpus_data)

        recall = metric.calculate_recall(
            prediction="Hello, World!", reference="hello world", n=1, code_abbr="test"
        )

        assert abs(recall - 1.0) < 0.0001

    def test_recall_case_insensitive(self):
        """Test that recall calculation is case insensitive."""
        corpus_data = {"1": "hello world"}
        metric = create_metric_with_corpus(corpus_data)

        recall = metric.calculate_recall(
            prediction="HELLO WORLD", reference="hello world", n=1, code_abbr="test"
        )

        assert abs(recall - 1.0) < 0.0001

    def test_recall_tfidf_weights_rare_words_more(self):
        """Test that rare words contribute more to recall due to higher IDF."""
        corpus_data = {
            "1": "common rare",
            "2": "common word",
            "3": "common another",
        }
        metric = create_metric_with_corpus(corpus_data)

        # Reference with only "common" (appears in all docs, low IDF)
        recall_common = metric.calculate_recall(
            prediction="common", reference="common", n=1, code_abbr="test"
        )

        # Reference with only "rare" (appears in 1 doc, high IDF)
        recall_rare = metric.calculate_recall(
            prediction="rare", reference="rare", n=1, code_abbr="test"
        )

        # Both should be 1.0 when prediction matches reference exactly
        assert abs(recall_common - 1.0) < 0.0001
        assert abs(recall_rare - 1.0) < 0.0001

    def test_recall_missing_rare_word_hurts_more(self):
        """Test that missing a rare word reduces recall more than missing a common word."""
        corpus_data = {
            "1": "common rare",
            "2": "common word",
            "3": "common another",
        }
        metric = create_metric_with_corpus(corpus_data)

        # Miss the common word
        recall_miss_common = metric.calculate_recall(
            prediction="rare",
            reference="common rare",
            n=1,
            code_abbr="test",
        )

        # Miss the rare word
        recall_miss_rare = metric.calculate_recall(
            prediction="common",
            reference="common rare",
            n=1,
            code_abbr="test",
        )

        # Missing the rare word should hurt more (lower recall)
        assert 0 < recall_miss_rare < recall_miss_common < 1


class TestTFIDFRougeNCallableInterface:
    """Tests for the callable interface (__call__ method)."""

    def test_callable_returns_score(self):
        """Test that calling the metric returns a score."""
        corpus_data = {"1": "hello world"}
        metric = create_metric_with_corpus(corpus_data)

        score = metric(
            prediction="hello world", reference="hello world", code_abbr="test"
        )

        assert abs(score - 1.0) < 0.0001

    def test_callable_strips_whitespace(self):
        """Test that callable strips leading/trailing whitespace."""
        corpus_data = {"1": "hello world"}
        metric = create_metric_with_corpus(corpus_data)

        score = metric(
            prediction="  hello world  ", reference="hello world", code_abbr="test"
        )

        assert abs(score - 1.0) < 0.0001

    def test_callable_requires_code_abbr(self):
        """Test that code_abbr is required for TFIDFRougeNMetric."""
        corpus_data = {"1": "hello world"}
        metric = create_metric_with_corpus(corpus_data)

        # Calling without code_abbr should raise an error
        with pytest.raises((TypeError, KeyError, AttributeError)):
            metric(prediction="hello world", reference="hello world")

    def test_callable_invalid_code_abbr_raises(self):
        """Test that invalid code_abbr raises an error."""
        corpus_data = {"1": "hello world"}
        metric = create_metric_with_corpus(corpus_data)

        with pytest.raises((KeyError, AttributeError, TypeError)):
            metric(
                prediction="hello world",
                reference="hello world",
                code_abbr="nonexistent",
            )

    def test_metric_name(self):
        """Test that metric has correct name."""
        corpus_data = {"1": "hello world"}
        metric = create_metric_with_corpus(corpus_data)

        assert metric.name == "rouge_n_tfidf"

    def test_default_ngram_importances(self):
        """Test default n-gram importances are [1, 1, 1]."""
        corpus_data = {"1": "hello world there"}
        metric = create_metric_with_corpus(corpus_data)

        assert metric.ngrams_importances == [1, 1, 1]


class TestTFIDFRougeNEdgeCases:
    """Tests for edge cases and potential bugs."""

    def test_single_word_text(self):
        """Test with single word texts."""
        corpus_data = {"1": "hello"}
        metric = create_metric_with_corpus(corpus_data)

        score = metric(prediction="hello", reference="hello", code_abbr="test")

        assert abs(score - 1.0) < 0.0001

    def test_very_long_text(self):
        """Test with very long text."""
        words = [f"word{i}" for i in range(1000)]
        text = " ".join(words)
        corpus_data = {"1": text}
        metric = create_metric_with_corpus(corpus_data)

        score = metric(prediction=text, reference=text, code_abbr="test")

        assert abs(score - 1.0) < 0.0001

    def test_special_characters_removed(self):
        """Test that special characters are handled properly."""
        corpus_data = {"1": "hello world test"}
        metric = create_metric_with_corpus(corpus_data)

        score = metric(
            prediction="hello... world!!! test???",
            reference="hello world test",
            code_abbr="test",
        )

        assert abs(score - 1.0) < 0.0001

    def test_numbers_preserved(self):
        """Test that numbers are preserved in text."""
        corpus_data = {"1": "article 123 section 456"}
        metric = create_metric_with_corpus(corpus_data)

        score = metric(
            prediction="article 123 section 456",
            reference="article 123 section 456",
            code_abbr="test",
        )

        assert abs(score - 1.0) < 0.0001

    def test_multiple_spaces_handled(self):
        """Test that multiple spaces are handled correctly."""
        corpus_data = {"1": "hello world"}
        metric = create_metric_with_corpus(corpus_data)

        score = metric(
            prediction="hello    world", reference="hello world", code_abbr="test"
        )

        assert abs(score - 1.0) < 0.0001

    def test_newlines_and_tabs_handled(self):
        """Test that newlines and tabs are handled correctly."""
        corpus_data = {"1": "hello world test"}
        metric = create_metric_with_corpus(corpus_data)

        score = metric(
            prediction="hello\nworld\ttest",
            reference="hello world test",
            code_abbr="test",
        )

        assert abs(score - 1.0) < 0.0001
