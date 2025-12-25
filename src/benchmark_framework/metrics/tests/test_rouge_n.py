import pytest
from src.benchmark_framework.metrics.rouge_n import RougeNMetric


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


class TestRougeNWeightedAverage:
    """Tests for weighted average F1 calculation."""

    def test_weighted_average_single_ngram(self):
        """Test weighted average with single n-gram size."""
        metric = RougeNMetric(ngram_importances=[1.0])
        text = "the cat sat"

        score = metric(prediction=text, reference=text)

        # Should equal unigram F1
        f1_unigram = metric.calculate_f1(text, text, n=1)
        assert abs(score - f1_unigram) < 0.001, f"Expected {f1_unigram}, got {score}"

    def test_weighted_average_equal_weights(self):
        """Test weighted average with equal weights."""
        metric = RougeNMetric(ngram_importances=[1.0, 1.0, 1.0])
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
        metric = RougeNMetric(ngram_importances=[1.0, 2.0, 3.0])
        text = "the cat sat on mat"

        score = metric(prediction=text, reference=text)

        # Weighted average: (1*F1_1 + 2*F1_2 + 3*F1_3) / (1+2+3)
        f1_1 = metric.calculate_f1(text, text, n=1)
        f1_2 = metric.calculate_f1(text, text, n=2)
        f1_3 = metric.calculate_f1(text, text, n=3)
        expected = (1.0 * f1_1 + 2.0 * f1_2 + 3.0 * f1_3) / 6.0

        assert abs(score - expected) < 0.001, f"Expected {expected}, got {score}"

    def test_weighted_average_empty_importances_returns_zero(self):
        """Test that empty importance list returns 0.0."""
        metric = RougeNMetric(ngram_importances=[])

        score = metric(prediction="test", reference="test")

        assert score == 0.0, f"Expected 0.0 for empty importances, got {score}"

    def test_weighted_average_zero_weights_returns_zero(self):
        """Test that all zero weights return 0.0."""
        metric = RougeNMetric(ngram_importances=[0.0, 0.0, 0.0])

        score = metric(prediction="test", reference="test")

        assert score == 0.0, f"Expected 0.0 for all zero weights, got {score}"
