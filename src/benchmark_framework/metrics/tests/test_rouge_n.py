import pytest
from collections import Counter
from src.benchmark_framework.metrics.rouge_n import RougeNMetric


class TestRougeNGetNgrams:
    """Tests for the _get_ngrams static method."""

    def test_get_ngrams_unigrams(self):
        """Test unigram extraction."""
        tokens = ["the", "cat", "sat"]
        result = RougeNMetric.get_ngrams(tokens, n=1)

        expected = Counter([("the",), ("cat",), ("sat",)])
        assert result == expected

    def test_get_ngrams_bigrams(self):
        """Test bigram extraction."""
        tokens = ["the", "cat", "sat"]
        result = RougeNMetric.get_ngrams(tokens, n=2)

        expected = Counter([("the", "cat"), ("cat", "sat")])
        assert result == expected

    def test_get_ngrams_trigrams(self):
        """Test trigram extraction."""
        tokens = ["the", "cat", "sat", "down"]
        result = RougeNMetric.get_ngrams(tokens, n=3)

        expected = Counter([("the", "cat", "sat"), ("cat", "sat", "down")])
        assert result == expected

    def test_get_ngrams_empty_tokens(self):
        """Test n-gram extraction from empty token list."""
        tokens = []
        result = RougeNMetric.get_ngrams(tokens, n=1)

        assert result == Counter()

    def test_get_ngrams_tokens_shorter_than_n(self):
        """Test when token list is shorter than n."""
        tokens = ["the", "cat"]
        result = RougeNMetric.get_ngrams(tokens, n=3)

        assert result == Counter()

    def test_get_ngrams_tokens_equal_to_n(self):
        """Test when token list length equals n."""
        tokens = ["the", "cat", "sat"]
        result = RougeNMetric.get_ngrams(tokens, n=3)

        expected = Counter([("the", "cat", "sat")])
        assert result == expected

    def test_get_ngrams_single_token_unigram(self):
        """Test single token with unigram."""
        tokens = ["hello"]
        result = RougeNMetric.get_ngrams(tokens, n=1)

        expected = Counter([("hello",)])
        assert result == expected

    def test_get_ngrams_single_token_bigram(self):
        """Test single token with bigram returns empty."""
        tokens = ["hello"]
        result = RougeNMetric.get_ngrams(tokens, n=2)

        assert result == Counter()

    def test_get_ngrams_duplicate_ngrams(self):
        """Test counting of duplicate n-grams."""
        tokens = ["the", "cat", "the", "cat"]
        result = RougeNMetric.get_ngrams(tokens, n=2)

        # ("the", "cat") appears twice
        assert result[("the", "cat")] == 2
        assert result[("cat", "the")] == 1

    def test_get_ngrams_n_zero(self):
        """Test n=0 returns empty counter."""
        tokens = ["the", "cat", "sat"]
        with pytest.raises(ValueError, match="n must be > 0, got 0"):
            RougeNMetric.get_ngrams(tokens, n=0)

    def test_get_ngrams_large_n(self):
        """Test with very large n value."""
        tokens = ["a", "b", "c"]
        result = RougeNMetric.get_ngrams(tokens, n=100)

        assert result == Counter()

    def test_get_ngrams_fourgrams(self):
        """Test 4-gram extraction."""
        tokens = ["a", "b", "c", "d", "e"]
        result = RougeNMetric.get_ngrams(tokens, n=4)

        expected = Counter([("a", "b", "c", "d"), ("b", "c", "d", "e")])
        assert result == expected


class TestRougeNIntersectionCount:
    """Tests for the _calculate_intersection_ngrams_count method."""

    def test_intersection_identical_counters(self):
        """Test intersection with identical counters."""
        metric = RougeNMetric()
        pred_counts = Counter([("a",), ("b",), ("c",)])
        ref_counts = Counter([("a",), ("b",), ("c",)])

        result = metric._calculate_intersection_ngrams_count(pred_counts, ref_counts)

        assert result == 3

    def test_intersection_no_overlap(self):
        """Test intersection with no overlapping n-grams."""
        metric = RougeNMetric()
        pred_counts = Counter([("a",), ("b",)])
        ref_counts = Counter([("x",), ("y",)])

        result = metric._calculate_intersection_ngrams_count(pred_counts, ref_counts)

        assert result == 0

    def test_intersection_partial_overlap(self):
        """Test intersection with partial overlap."""
        metric = RougeNMetric()
        pred_counts = Counter([("a",), ("b",), ("c",)])
        ref_counts = Counter([("a",), ("x",), ("y",)])

        result = metric._calculate_intersection_ngrams_count(pred_counts, ref_counts)

        assert result == 1

    def test_intersection_with_duplicates_pred_more(self):
        """Test intersection when prediction has more duplicates."""
        metric = RougeNMetric()
        pred_counts = Counter({("a",): 5, ("b",): 2})
        ref_counts = Counter({("a",): 2, ("b",): 1})

        result = metric._calculate_intersection_ngrams_count(pred_counts, ref_counts)

        # min(5, 2) + min(2, 1) = 2 + 1 = 3
        assert result == 3

    def test_intersection_with_duplicates_ref_more(self):
        """Test intersection when reference has more duplicates."""
        metric = RougeNMetric()
        pred_counts = Counter({("a",): 2, ("b",): 1})
        ref_counts = Counter({("a",): 5, ("b",): 3})

        result = metric._calculate_intersection_ngrams_count(pred_counts, ref_counts)

        # min(2, 5) + min(1, 3) = 2 + 1 = 3
        assert result == 3

    def test_intersection_empty_pred(self):
        """Test intersection with empty prediction counter."""
        metric = RougeNMetric()
        pred_counts = Counter()
        ref_counts = Counter([("a",), ("b",)])

        result = metric._calculate_intersection_ngrams_count(pred_counts, ref_counts)

        assert result == 0

    def test_intersection_empty_ref(self):
        """Test intersection with empty reference counter."""
        metric = RougeNMetric()
        pred_counts = Counter([("a",), ("b",)])
        ref_counts = Counter()

        result = metric._calculate_intersection_ngrams_count(pred_counts, ref_counts)

        assert result == 0

    def test_intersection_both_empty(self):
        """Test intersection with both counters empty."""
        metric = RougeNMetric()
        pred_counts = Counter()
        ref_counts = Counter()

        result = metric._calculate_intersection_ngrams_count(pred_counts, ref_counts)

        assert result == 0


class TestRougeNPrecision:
    """Tests for ROUGE-N precision calculation."""

    def test_precision_identical_texts_returns_one(self):
        """Test that identical texts return precision of 1.0."""
        metric = RougeNMetric()
        text = "the cat sat on the mat"

        precision = metric.calculate_precision(prediction=text, reference=text, n=1)

        assert (
            precision == 1.0
        ), f"Expected precision 1.0 for identical texts, got {precision}"

    def test_precision_bigrams_identical_texts_returns_one(self):
        """Test that identical texts return precision of 1.0 for bigrams."""
        metric = RougeNMetric()
        text = "the cat sat on the mat"

        precision = metric.calculate_precision(prediction=text, reference=text, n=2)

        assert (
            precision == 1.0
        ), f"Expected precision 1.0 for identical texts with bigrams, got {precision}"

    def test_precision_trigrams_identical_texts_returns_one(self):
        """Test that identical texts return precision of 1.0 for trigrams."""
        metric = RougeNMetric()
        text = "the cat sat on the mat"

        precision = metric.calculate_precision(prediction=text, reference=text, n=3)

        assert (
            precision == 1.0
        ), f"Expected precision 1.0 for identical texts with trigrams, got {precision}"

    def test_precision_no_overlap_returns_zero(self):
        """Test that texts with no common unigrams return precision of 0.0."""
        metric = RougeNMetric()
        prediction = "abc def"
        reference = "xyz uvw"

        precision = metric.calculate_precision(
            prediction=prediction, reference=reference, n=1
        )

        assert (
            precision == 0.0
        ), f"Expected precision 0.0 for non-overlapping texts, got {precision}"

    def test_precision_partial_overlap_unigrams(self):
        """Test precision with partial overlap in unigrams."""
        metric = RougeNMetric()
        prediction = "the cat sat"  # 3 unigrams
        reference = "the dog sat"  # 3 unigrams, 2 match ("the", "sat")

        precision = metric.calculate_precision(
            prediction=prediction, reference=reference, n=1
        )

        # Prediction has 3 unigrams: "the", "cat", "sat"
        # Matches with reference: "the", "sat" = 2 matches
        # Precision = 2/3 = 0.666...
        expected = 2.0 / 3.0
        assert (
            abs(precision - expected) < 0.001
        ), f"Expected precision {expected}, got {precision}"

    def test_precision_partial_overlap_bigrams(self):
        """Test precision with partial overlap in bigrams."""
        metric = RougeNMetric()
        prediction = "the cat sat on mat"  # 4 bigrams: ("the","cat"), ("cat","sat"), ("sat","on"), ("on","mat")
        reference = "the cat lay on mat"  # 4 bigrams: ("the","cat"), ("cat","lay"), ("lay","on"), ("on","mat")

        precision = metric.calculate_precision(
            prediction=prediction, reference=reference, n=2
        )

        # Matches: ("the","cat"), ("on","mat") = 2 matches out of 4 in prediction
        # Precision = 2/4 = 0.5
        expected = 2.0 / 4.0
        assert (
            abs(precision - expected) < 0.001
        ), f"Expected precision {expected}, got {precision}"

    def test_precision_prediction_longer_than_reference(self):
        """Test precision when prediction is longer than reference."""
        metric = RougeNMetric()
        prediction = "the cat sat on the mat and the dog"  # Many unigrams
        reference = "the cat"  # Only 2 unigrams

        precision = metric.calculate_precision(
            prediction=prediction, reference=reference, n=1
        )

        # Prediction has 9 unigrams, but only 3 match with reference ("the" appears 3 times, "cat" once)
        # But reference only has "the" once and "cat" once
        # Matches: min(3, 1) for "the" + min(1, 1) for "cat" = 2
        # Precision = 2/9
        expected = 2.0 / 9.0
        assert (
            abs(precision - expected) < 0.001
        ), f"Expected precision {expected}, got {precision}"

    def test_precision_empty_prediction_returns_zero(self):
        """Test that empty prediction returns precision of 0.0."""
        metric = RougeNMetric()
        prediction = ""
        reference = "the cat sat"

        precision = metric.calculate_precision(
            prediction=prediction, reference=reference, n=1
        )

        assert (
            precision == 0.0
        ), f"Expected precision 0.0 for empty prediction, got {precision}"

    def test_precision_empty_reference_returns_zero(self):
        """Test that empty reference returns precision of 0.0."""
        metric = RougeNMetric()
        prediction = "the cat sat"
        reference = ""

        precision = metric.calculate_precision(
            prediction=prediction, reference=reference, n=1
        )

        assert (
            precision == 0.0
        ), f"Expected precision 0.0 for empty reference, got {precision}"

    def test_precision_with_punctuation_normalization(self):
        """Test that punctuation is normalized correctly in precision calculation."""
        metric = RougeNMetric()
        prediction = "Hello, world!"
        reference = "Hello world"

        precision = metric.calculate_precision(
            prediction=prediction, reference=reference, n=1
        )

        # After normalization: "hello world" vs "hello world"
        assert (
            precision == 1.0
        ), f"Expected precision 1.0 after punctuation normalization, got {precision}"

    def test_precision_polish_text(self):
        """Test precision with Polish text."""
        metric = RougeNMetric()
        prediction = "zakaz prowadzenia pojazdów"
        reference = "zakaz prowadzenia"

        precision = metric.calculate_precision(
            prediction=prediction, reference=reference, n=1
        )

        # Prediction: "zakaz", "prowadzenia", "pojazdów" (3 unigrams)
        # Reference: "zakaz", "prowadzenia" (2 unigrams)
        # Matches: 2
        # Precision = 2/3
        expected = 2.0 / 3.0
        assert (
            abs(precision - expected) < 0.001
        ), f"Expected precision {expected}, got {precision}"

    def test_precision_polish_text_2(self):
        """Test precision with Polish text."""
        metric = RougeNMetric()
        prediction = "zakaz prowadzenia"
        reference = "zakaz prowadzenia pojazdów"

        precision = metric.calculate_precision(
            prediction=prediction, reference=reference, n=1
        )

        expected = 1.0
        assert (
            abs(precision - expected) < 0.001
        ), f"Expected precision {expected}, got {precision}"

    def test_precision_both_empty_returns_zero(self):
        """Test that both empty texts return precision of 0.0."""
        metric = RougeNMetric()

        precision = metric.calculate_precision(prediction="", reference="", n=1)

        assert precision == 0.0

    def test_precision_only_whitespace(self):
        """Test precision with only whitespace."""
        metric = RougeNMetric()

        precision = metric.calculate_precision(
            prediction="   ", reference="the cat", n=1
        )

        assert precision == 0.0

    def test_precision_only_punctuation(self):
        """Test precision with only punctuation (empty after normalization)."""
        metric = RougeNMetric()

        precision = metric.calculate_precision(
            prediction="...", reference="the cat", n=1
        )

        assert precision == 0.0

    def test_precision_n_larger_than_text(self):
        """Test precision when n is larger than text length."""
        metric = RougeNMetric()

        precision = metric.calculate_precision(
            prediction="hello", reference="hello", n=5
        )

        # Both have 1 word, can't form 5-grams
        assert precision == 0.0

    def test_precision_fourgrams(self):
        """Test precision with 4-grams."""
        metric = RougeNMetric()
        text = "the quick brown fox jumps"

        precision = metric.calculate_precision(prediction=text, reference=text, n=4)

        assert precision == 1.0

    def test_precision_repeated_words_in_prediction(self):
        """Test precision with repeated words in prediction."""
        metric = RougeNMetric()
        prediction = "the the the"  # 3 unigrams, all "the"
        reference = "the cat"  # 2 unigrams

        precision = metric.calculate_precision(
            prediction=prediction, reference=reference, n=1
        )

        # Prediction has 3 "the", reference has 1 "the"
        # Intersection = min(3, 1) = 1
        # Precision = 1/3
        expected = 1.0 / 3.0
        assert abs(precision - expected) < 0.001

    def test_precision_numbers(self):
        """Test precision with numbers."""
        metric = RougeNMetric()

        precision = metric.calculate_precision(
            prediction="article 123 456", reference="article 123 789", n=1
        )

        # Unigrams: ["article", "123", "456"] vs ["article", "123", "789"]
        # Matches: "article", "123" = 2 out of 3
        expected = 2.0 / 3.0
        assert abs(precision - expected) < 0.001


class TestRougeNRecall:
    """Tests for ROUGE-N recall calculation."""

    def test_recall_identical_texts_returns_one(self):
        """Test that identical texts return recall of 1.0."""
        metric = RougeNMetric()
        text = "the cat sat on the mat"

        recall = metric.calculate_recall(prediction=text, reference=text, n=1)

        assert recall == 1.0, f"Expected recall 1.0 for identical texts, got {recall}"

    def test_recall_bigrams_identical_texts_returns_one(self):
        """Test that identical texts return recall of 1.0 for bigrams."""
        metric = RougeNMetric()
        text = "the cat sat on the mat"

        recall = metric.calculate_recall(prediction=text, reference=text, n=2)

        assert (
            recall == 1.0
        ), f"Expected recall 1.0 for identical texts with bigrams, got {recall}"

    def test_recall_trigrams_identical_texts_returns_one(self):
        """Test that identical texts return recall of 1.0 for trigrams."""
        metric = RougeNMetric()
        text = "the cat sat on the mat"

        recall = metric.calculate_recall(prediction=text, reference=text, n=3)

        assert (
            recall == 1.0
        ), f"Expected recall 1.0 for identical texts with trigrams, got {recall}"

    def test_recall_no_overlap_returns_zero(self):
        """Test that texts with no common unigrams return recall of 0.0."""
        metric = RougeNMetric()
        prediction = "abc def"
        reference = "xyz uvw"

        recall = metric.calculate_recall(
            prediction=prediction, reference=reference, n=1
        )

        assert (
            recall == 0.0
        ), f"Expected recall 0.0 for non-overlapping texts, got {recall}"

    def test_recall_partial_overlap_unigrams(self):
        """Test recall with partial overlap in unigrams."""
        metric = RougeNMetric()
        prediction = "the cat sat"  # 3 unigrams
        reference = "the dog sat"  # 3 unigrams, 2 match ("the", "sat")

        recall = metric.calculate_recall(
            prediction=prediction, reference=reference, n=1
        )

        # Reference has 3 unigrams: "the", "dog", "sat"
        # Matches with prediction: "the", "sat" = 2 matches
        # Recall = 2/3 = 0.666...
        expected = 2.0 / 3.0
        assert (
            abs(recall - expected) < 0.001
        ), f"Expected recall {expected}, got {recall}"

    def test_recall_partial_overlap_bigrams(self):
        """Test recall with partial overlap in bigrams."""
        metric = RougeNMetric()
        prediction = "the cat sat on mat"  # 4 bigrams
        reference = "the cat lay on mat"  # 4 bigrams

        recall = metric.calculate_recall(
            prediction=prediction, reference=reference, n=2
        )

        # Reference bigrams: ("the","cat"), ("cat","lay"), ("lay","on"), ("on","mat")
        # Matches: ("the","cat"), ("on","mat") = 2 matches out of 4 in reference
        # Recall = 2/4 = 0.5
        expected = 2.0 / 4.0
        assert (
            abs(recall - expected) < 0.001
        ), f"Expected recall {expected}, got {recall}"

    def test_recall_prediction_longer_than_reference(self):
        """Test recall when prediction is longer than reference."""
        metric = RougeNMetric()
        prediction = "the cat sat on the mat and the dog"  # Many unigrams
        reference = "the cat"  # Only 2 unigrams

        recall = metric.calculate_recall(
            prediction=prediction, reference=reference, n=1
        )

        # Reference has 2 unigrams: "the", "cat"
        # Both are in prediction
        # Recall = 2/2 = 1.0
        expected = 1.0
        assert (
            abs(recall - expected) < 0.001
        ), f"Expected recall {expected}, got {recall}"

    def test_recall_prediction_shorter_than_reference(self):
        """Test recall when prediction is shorter than reference."""
        metric = RougeNMetric()
        prediction = "the cat"
        reference = "the cat sat on the mat"

        recall = metric.calculate_recall(
            prediction=prediction, reference=reference, n=1
        )

        # Reference has 6 unigrams: "the" (x2), "cat", "sat", "on", "mat"
        # Prediction has: "the", "cat"
        # Matches: min(1, 2) for "the" + min(1, 1) for "cat" = 2
        # Recall = 2/6 = 0.333...
        expected = 2.0 / 6.0
        assert (
            abs(recall - expected) < 0.001
        ), f"Expected recall {expected}, got {recall}"

    def test_recall_empty_prediction_returns_zero(self):
        """Test that empty prediction returns recall of 0.0."""
        metric = RougeNMetric()
        prediction = ""
        reference = "the cat sat"

        recall = metric.calculate_recall(
            prediction=prediction, reference=reference, n=1
        )

        assert recall == 0.0, f"Expected recall 0.0 for empty prediction, got {recall}"

    def test_recall_empty_reference_returns_zero(self):
        """Test that empty reference returns recall of 0.0."""
        metric = RougeNMetric()
        prediction = "the cat sat"
        reference = ""

        recall = metric.calculate_recall(
            prediction=prediction, reference=reference, n=1
        )

        assert recall == 0.0, f"Expected recall 0.0 for empty reference, got {recall}"

    def test_recall_with_punctuation_normalization(self):
        """Test that punctuation is normalized correctly in recall calculation."""
        metric = RougeNMetric()
        prediction = "Hello, world!"
        reference = "Hello world"

        recall = metric.calculate_recall(
            prediction=prediction, reference=reference, n=1
        )

        # After normalization: "hello world" vs "hello world"
        assert (
            recall == 1.0
        ), f"Expected recall 1.0 after punctuation normalization, got {recall}"

    def test_recall_polish_text(self):
        """Test recall with Polish text."""
        metric = RougeNMetric()
        prediction = "zakaz prowadzenia"
        reference = "zakaz prowadzenia pojazdów"

        recall = metric.calculate_recall(
            prediction=prediction, reference=reference, n=1
        )

        # Reference: "zakaz", "prowadzenia", "pojazdów" (3 unigrams)
        # Prediction: "zakaz", "prowadzenia" (2 unigrams)
        # Matches: 2
        # Recall = 2/3
        expected = 2.0 / 3.0
        assert (
            abs(recall - expected) < 0.001
        ), f"Expected recall {expected}, got {recall}"

    def test_recall_polish_text_2(self):
        """Test recall with Polish text."""
        metric = RougeNMetric()
        prediction = "zakaz prowadzenia pojazdów"
        reference = "zakaz prowadzenia"

        recall = metric.calculate_recall(
            prediction=prediction, reference=reference, n=1
        )

        expected = 1.0
        assert (
            abs(recall - expected) < 0.001
        ), f"Expected recall {expected}, got {recall}"

    def test_recall_both_empty_returns_zero(self):
        """Test that both empty texts return recall of 0.0."""
        metric = RougeNMetric()

        recall = metric.calculate_recall(prediction="", reference="", n=1)

        assert recall == 0.0

    def test_recall_only_whitespace(self):
        """Test recall with only whitespace."""
        metric = RougeNMetric()

        recall = metric.calculate_recall(prediction="the cat", reference="   ", n=1)

        # Empty reference = 0 recall
        assert recall == 0.0

    def test_recall_only_punctuation(self):
        """Test recall with only punctuation (empty after normalization)."""
        metric = RougeNMetric()

        recall = metric.calculate_recall(prediction="the cat", reference="...", n=1)

        assert recall == 0.0

    def test_recall_n_larger_than_text(self):
        """Test recall when n is larger than text length."""
        metric = RougeNMetric()

        recall = metric.calculate_recall(prediction="hello", reference="hello", n=5)

        assert recall == 0.0

    def test_recall_fourgrams(self):
        """Test recall with 4-grams."""
        metric = RougeNMetric()
        text = "the quick brown fox jumps"

        recall = metric.calculate_recall(prediction=text, reference=text, n=4)

        assert recall == 1.0

    def test_recall_repeated_words_in_reference(self):
        """Test recall with repeated words in reference."""
        metric = RougeNMetric()
        prediction = "the cat"  # 2 unigrams
        reference = "the the the"  # 3 unigrams, all "the"

        recall = metric.calculate_recall(
            prediction=prediction, reference=reference, n=1
        )

        # Reference has 3 "the", prediction has 1 "the"
        # Intersection = min(1, 3) = 1
        # Recall = 1/3
        expected = 1.0 / 3.0
        assert abs(recall - expected) < 0.001

    def test_recall_numbers(self):
        """Test recall with numbers."""
        metric = RougeNMetric()

        recall = metric.calculate_recall(
            prediction="article 123 456", reference="article 123 789", n=1
        )

        # Reference unigrams: ["article", "123", "789"]
        # Matches: "article", "123" = 2 out of 3
        expected = 2.0 / 3.0
        assert abs(recall - expected) < 0.001


class TestRougeNF1:
    """Tests for ROUGE-N F1 score calculation."""

    def test_f1_identical_texts_returns_one(self):
        """Test that identical texts return F1 of 1.0."""
        metric = RougeNMetric()
        text = "the cat sat on the mat"

        f1 = metric.calculate_f1(prediction=text, reference=text, n=1)

        assert f1 == 1.0, f"Expected F1 1.0 for identical texts, got {f1}"

    def test_f1_combines_precision_and_recall(self):
        """Test that F1 correctly combines precision and recall."""
        metric = RougeNMetric()
        prediction = "the cat"  # 2 unigrams
        reference = "the cat sat"  # 3 unigrams

        # Precision: 2/2 = 1.0 (both words in prediction are in reference)
        # Recall: 2/3 = 0.666... (2 out of 3 reference words are captured)
        # F1 = 2 * (1.0 * 0.666...) / (1.0 + 0.666...) = 2 * 0.666... / 1.666... = 0.8

        precision = metric.calculate_precision(prediction, reference, n=1)
        recall = metric.calculate_recall(prediction, reference, n=1)
        f1 = metric.calculate_f1(prediction, reference, n=1)

        expected_f1 = 2 * (precision * recall) / (precision + recall)
        assert abs(f1 - expected_f1) < 0.001, f"Expected F1 {expected_f1}, got {f1}"

    def test_f1_empty_texts_returns_zero(self):
        """Test that empty texts return F1 of 0.0."""
        metric = RougeNMetric()

        f1 = metric.calculate_f1(prediction="", reference="", n=1)

        assert f1 == 0.0, f"Expected F1 0.0 for empty texts, got {f1}"

    def test_f1_no_overlap_returns_zero(self):
        """Test F1 with no overlapping words."""
        metric = RougeNMetric()

        f1 = metric.calculate_f1(prediction="abc def", reference="xyz uvw", n=1)

        assert f1 == 0.0

    def test_f1_perfect_precision_partial_recall(self):
        """Test F1 with perfect precision but partial recall."""
        metric = RougeNMetric()
        prediction = "the cat"
        reference = "the cat sat on mat"

        f1 = metric.calculate_f1(prediction, reference, n=1)
        precision = metric.calculate_precision(prediction, reference, n=1)
        recall = metric.calculate_recall(prediction, reference, n=1)

        # Precision = 1.0, Recall = 2/5 = 0.4
        expected_f1 = 2 * precision * recall / (precision + recall)
        assert abs(f1 - expected_f1) < 0.001

    def test_f1_perfect_recall_partial_precision(self):
        """Test F1 with perfect recall but partial precision."""
        metric = RougeNMetric()
        prediction = "the cat sat on mat"
        reference = "the cat"

        f1 = metric.calculate_f1(prediction, reference, n=1)
        precision = metric.calculate_precision(prediction, reference, n=1)
        recall = metric.calculate_recall(prediction, reference, n=1)

        # Recall = 1.0, Precision = 2/5 = 0.4
        expected_f1 = 2 * precision * recall / (precision + recall)
        assert abs(f1 - expected_f1) < 0.001

    def test_f1_bigrams(self):
        """Test F1 with bigrams."""
        metric = RougeNMetric()
        text = "the quick brown fox"

        f1 = metric.calculate_f1(prediction=text, reference=text, n=2)

        assert f1 == 1.0

    def test_f1_trigrams(self):
        """Test F1 with trigrams."""
        metric = RougeNMetric()
        text = "the quick brown fox jumps"

        f1 = metric.calculate_f1(prediction=text, reference=text, n=3)

        assert f1 == 1.0

    def test_f1_is_harmonic_mean(self):
        """Test that F1 is the harmonic mean of precision and recall."""
        metric = RougeNMetric()
        prediction = "a b c d"
        reference = "a b x y"

        precision = metric.calculate_precision(prediction, reference, n=1)
        recall = metric.calculate_recall(prediction, reference, n=1)
        f1 = metric.calculate_f1(prediction, reference, n=1)

        expected = 2 * precision * recall / (precision + recall)
        assert abs(f1 - expected) < 0.001


class TestRougeNWeightedAverage:
    """Tests for weighted average F1 calculation."""

    def test_weighted_average_single_ngram(self):
        """Test weighted average with single n-gram size."""
        metric = RougeNMetric(ngrams_importances=[1.0])
        text = "the cat sat"

        score = metric(prediction=text, reference=text)

        # Should equal unigram F1
        f1_unigram = metric.calculate_f1(text, text, n=1)
        assert abs(score - f1_unigram) < 0.001, f"Expected {f1_unigram}, got {score}"

    def test_weighted_average_equal_weights(self):
        """Test weighted average with equal weights."""
        metric = RougeNMetric(ngrams_importances=[1.0, 1.0, 1.0])
        text = "the cat sat on mat"

        score = metric(prediction=text, reference=text)

        # Should be average of unigram, bigram, and trigram F1
        f1_1 = metric.calculate_f1(text, text, n=1)
        f1_2 = metric.calculate_f1(text, text, n=2)
        f1_3 = metric.calculate_f1(text, text, n=3)
        expected = (f1_1 + f1_2 + f1_3) / 3.0

        assert abs(score - expected) < 0.001, f"Expected {expected}, got {score}"

    def test_weighted_average_different_weights(self):
        """Test weighted average with different weights."""
        metric = RougeNMetric(ngrams_importances=[1.0, 2.0, 3.0])
        text = "the cat sat on mat"

        score = metric(prediction=text, reference=text)

        # Weighted average: (1*F1_1 + 2*F1_2 + 3*F1_3) / (1+2+3)
        f1_1 = metric.calculate_f1(text, text, n=1)
        f1_2 = metric.calculate_f1(text, text, n=2)
        f1_3 = metric.calculate_f1(text, text, n=3)
        expected = (1.0 * f1_1 + 2.0 * f1_2 + 3.0 * f1_3) / 6.0

        assert abs(score - expected) < 0.001, f"Expected {expected}, got {score}"

    def test_weighted_average_mixed_zero_nonzero_weights(self):
        """Test weighted average with mixed zero and non-zero weights."""
        metric = RougeNMetric(ngrams_importances=[0.0, 1.0, 0.0])
        text = "the cat sat on mat"

        score = metric(prediction=text, reference=text)

        # Only bigram (n=2) should contribute
        f1_bigram = metric.calculate_f1(text, text, n=2)
        assert abs(score - f1_bigram) < 0.001

    def test_weighted_average_many_ngram_sizes(self):
        """Test weighted average with many n-gram sizes."""
        metric = RougeNMetric(ngrams_importances=[1.0, 1.0, 1.0, 1.0, 1.0])
        text = "one two three four five six"

        score = metric(prediction=text, reference=text)

        # All n-gram F1s should be 1.0 for identical text
        assert abs(score - 1.0) < 0.001


class TestRougeNCallableInterface:
    """Tests for the callable interface (__call__ method)."""

    def test_call_returns_weighted_f1(self):
        """Test that calling the metric returns weighted F1."""
        metric = RougeNMetric(ngrams_importances=[1.0, 1.0, 1.0])
        text = "the cat sat"

        result = metric(prediction=text, reference=text)

        assert abs(result - 1.0) < 0.001

    def test_call_with_code_abbr_parameter(self):
        """Test that code_abbr parameter is accepted (even if unused)."""
        metric = RougeNMetric()
        text = "the cat sat"

        result = metric(prediction=text, reference=text, code_abbr="TEST")

        assert abs(result - 1.0) < 0.001

    def test_call_identical_texts(self):
        """Test calling with identical texts returns 1.0."""
        metric = RougeNMetric()
        text = "hello world"

        result = metric(prediction=text, reference=text)

        assert abs(result - 1.0) < 0.001

    def test_call_no_overlap(self):
        """Test calling with no overlap returns 0.0."""
        metric = RougeNMetric()

        result = metric(prediction="abc def", reference="xyz uvw")

        assert result == 0.0

    def test_call_strips_whitespace(self):
        """Test that __call__ strips leading/trailing whitespace."""
        metric = RougeNMetric()

        result = metric(prediction="  hello world  ", reference="hello world")

        assert abs(result - 1.0) < 0.001


class TestRougeNScoreBatch:
    """Tests for the score_batch method."""

    def test_score_batch_basic(self):
        """Test basic batch scoring."""
        metric = RougeNMetric()
        predictions = ["hello world", "the cat sat", "foo bar"]
        references = ["hello world", "the cat sat", "foo bar"]

        scores = list(metric.score_batch(predictions, references))

        assert len(scores) == 3
        for score in scores:
            assert abs(score - 1.0) < 0.001

    def test_score_batch_mixed_similarity(self):
        """Test batch scoring with varying similarity."""
        metric = RougeNMetric()
        predictions = ["hello world", "abc def", "the cat"]
        references = ["hello world", "xyz uvw", "the dog"]

        scores = list(metric.score_batch(predictions, references))

        assert len(scores) == 3
        assert abs(scores[0] - 1.0) < 0.001  # Identical
        assert scores[1] == 0.0  # No overlap
        assert 0 < scores[2] < 1.0  # Partial overlap

    def test_score_batch_empty_lists(self):
        """Test batch scoring with empty lists."""
        metric = RougeNMetric()

        scores = list(metric.score_batch([], []))

        assert scores == []

    def test_score_batch_single_item(self):
        """Test batch scoring with single item."""
        metric = RougeNMetric()

        scores = list(metric.score_batch(["hello"], ["hello"]))

        assert len(scores) == 1
        assert abs(scores[0] - 1.0) < 0.001

    def test_score_batch_mismatched_lengths_raises(self):
        """Test that mismatched lengths raise assertion error."""
        metric = RougeNMetric()

        with pytest.raises(AssertionError):
            list(metric.score_batch(["a", "b"], ["a"]))


class TestRougeNNormalization:
    """Tests for text normalization behavior."""

    def test_normalization_lowercase(self):
        """Test that text is lowercased."""
        metric = RougeNMetric()

        result = metric(prediction="HELLO WORLD", reference="hello world")

        assert abs(result - 1.0) < 0.001

    def test_normalization_mixed_case(self):
        """Test with mixed case text."""
        metric = RougeNMetric()

        result = metric(prediction="HeLLo WoRLd", reference="hello world")

        assert abs(result - 1.0) < 0.001

    def test_normalization_punctuation_comma(self):
        """Test removal of commas."""
        metric = RougeNMetric()

        result = metric(prediction="hello, world", reference="hello world")

        assert abs(result - 1.0) < 0.001

    def test_normalization_punctuation_period(self):
        """Test removal of periods."""
        metric = RougeNMetric()

        result = metric(prediction="hello world.", reference="hello world")

        assert abs(result - 1.0) < 0.001

    def test_normalization_punctuation_exclamation(self):
        """Test removal of exclamation marks."""
        metric = RougeNMetric()

        result = metric(prediction="hello world!", reference="hello world")

        assert abs(result - 1.0) < 0.001

    def test_normalization_punctuation_question(self):
        """Test removal of question marks."""
        metric = RougeNMetric()

        result = metric(prediction="hello world?", reference="hello world")

        assert abs(result - 1.0) < 0.001

    def test_normalization_multiple_punctuation(self):
        """Test removal of multiple punctuation marks."""
        metric = RougeNMetric()

        result = metric(
            prediction="Hello, World! How are you?", reference="hello world how are you"
        )

        assert abs(result - 1.0) < 0.001

    def test_normalization_quotes(self):
        """Test removal of quotes."""
        metric = RougeNMetric()

        result = metric(prediction="\"hello\" 'world'", reference="hello world")

        assert abs(result - 1.0) < 0.001

    def test_normalization_parentheses(self):
        """Test removal of parentheses."""
        metric = RougeNMetric()

        result = metric(prediction="(hello) [world]", reference="hello world")

        assert abs(result - 1.0) < 0.001

    def test_normalization_preserves_numbers(self):
        """Test that numbers are preserved."""
        metric = RougeNMetric()

        result = metric(prediction="article 123", reference="article 123")

        assert abs(result - 1.0) < 0.001


class TestRougeNEdgeCases:
    """Tests for various edge cases."""

    def test_single_word_identical(self):
        """Test with single identical word."""
        metric = RougeNMetric()

        result = metric(prediction="hello", reference="hello")

        # Only unigram can be computed, bigram and trigram return 0
        # With default weights [1,1,1], only unigram (1.0) contributes non-zero
        assert abs(result - 1.0) < 0.001

    def test_single_word_different(self):
        """Test with single different word."""
        metric = RougeNMetric()

        result = metric(prediction="hello", reference="world")

        assert result == 0.0

    def test_very_long_text(self):
        """Test with very long text."""
        metric = RougeNMetric()
        words = ["word" + str(i) for i in range(10000)]
        text = " ".join(words)

        result = metric(prediction=text, reference=text)

        assert abs(result - 1.0) < 0.001

    def test_special_characters_in_words(self):
        """Test handling of special characters within words."""
        metric = RougeNMetric()

        # Hyphenated words - punctuation is stripped
        result = metric(prediction="self-driving car", reference="selfdriving car")

        # After removing punctuation: "selfdriving car" vs "selfdriving car"
        assert abs(result - 1.0) < 0.001

    def test_newlines_and_tabs(self):
        """Test handling of newlines and tabs."""
        metric = RougeNMetric()

        result = metric(prediction="hello\nworld\tthere", reference="hello world there")

        assert abs(result - 1.0) < 0.001

    def test_multiple_spaces(self):
        """Test handling of multiple consecutive spaces."""
        metric = RougeNMetric()

        result = metric(
            prediction="hello    world     there", reference="hello world there"
        )

        assert abs(result - 1.0) < 0.001

    def test_default_ngram_importances(self):
        """Test default n-gram importances are [1, 1, 1]."""
        metric = RougeNMetric()

        assert metric.ngrams_importances == [1, 1, 1]

    def test_metric_name(self):
        """Test that metric name is set correctly."""
        metric = RougeNMetric()

        assert metric.name == "rouge_n_f1"

    def test_get_normalized_words_method(self):
        """Test the get_normalized_words helper method."""
        metric = RougeNMetric()

        result = metric.get_normalized_words("Hello, World! How's it going?")

        assert result == ["hello", "world", "hows", "it", "going"]

    def test_symmetry_for_identical_length(self):
        """Test that swapping pred/ref gives same result for identical length texts."""
        metric = RougeNMetric()
        text1 = "the cat sat"
        text2 = "the dog ran"

        result1 = metric(prediction=text1, reference=text2)
        result2 = metric(prediction=text2, reference=text1)

        # F1 should be symmetric when texts have same length
        assert abs(result1 - result2) < 0.001
