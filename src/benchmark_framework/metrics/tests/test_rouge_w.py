import pytest
from src.benchmark_framework.metrics.rouge_w import RougeWMetric


class TestRougeWInitialization:
    """Tests for ROUGE-W metric initialization."""

    def test_default_initialization(self):
        """Test default initialization with alpha=1.2 and beta=1.0."""
        metric = RougeWMetric()

        assert metric.alpha == 1.2
        assert metric.beta == 1.0
        assert metric.name == "rouge_w"

    def test_custom_alpha(self):
        """Test initialization with custom alpha value."""
        metric = RougeWMetric(alpha=2.0)

        assert metric.alpha == 2.0
        assert metric.beta == 1.0

    def test_custom_beta(self):
        """Test initialization with custom beta value."""
        metric = RougeWMetric(beta=2.0)

        assert metric.alpha == 1.2
        assert metric.beta == 2.0

    def test_custom_alpha_and_beta(self):
        """Test initialization with both custom alpha and beta."""
        metric = RougeWMetric(alpha=1.5, beta=0.5)

        assert metric.alpha == 1.5
        assert metric.beta == 0.5

    def test_alpha_less_than_one_raises_error(self):
        """Test that alpha < 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="alpha must be >= 1.0"):
            RougeWMetric(alpha=0.5)


class TestWeightingFunction:
    """Tests for the weighting function f(k) = k^alpha."""

    def test_weight_function_alpha_one(self):
        """Test that f(k) = k when alpha = 1.0."""
        metric = RougeWMetric(alpha=1.0)

        assert metric._weight_function(1) == 1.0
        assert metric._weight_function(2) == 2.0
        assert metric._weight_function(3) == 3.0
        assert metric._weight_function(5) == 5.0

    def test_weight_function_alpha_two(self):
        """Test that f(k) = k^2 when alpha = 2.0."""
        metric = RougeWMetric(alpha=2.0)

        assert metric._weight_function(1) == 1.0
        assert metric._weight_function(2) == 4.0
        assert metric._weight_function(3) == 9.0
        assert metric._weight_function(5) == 25.0

    def test_weight_function_default_alpha(self):
        """Test weighting function with default alpha=1.2."""
        metric = RougeWMetric()

        assert abs(metric._weight_function(1) - 1.0) < 0.001
        assert abs(metric._weight_function(2) - (2**1.2)) < 0.001
        assert abs(metric._weight_function(3) - (3**1.2)) < 0.001
        assert metric._weight_function(0) == 0.0


class TestInverseWeightingFunction:
    """Tests for the inverse weighting function f^(-1)(x) = x^(1/α)."""

    def test_inverse_weight_function_alpha_one(self):
        """Test that f^(-1)(x) = x when alpha = 1.0."""
        metric = RougeWMetric(alpha=1.0)

        assert metric._inverse_weight_function(1.0) == 1.0
        assert metric._inverse_weight_function(2.0) == 2.0
        assert metric._inverse_weight_function(4.0) == 4.0

    def test_inverse_weight_function_alpha_two(self):
        """Test that f^(-1)(x) = sqrt(x) when alpha = 2.0."""
        metric = RougeWMetric(alpha=2.0)

        assert abs(metric._inverse_weight_function(1.0) - 1.0) < 0.001
        assert abs(metric._inverse_weight_function(4.0) - 2.0) < 0.001
        assert abs(metric._inverse_weight_function(9.0) - 3.0) < 0.001

    def test_inverse_weight_function_roundtrip(self):
        """Test that f^(-1)(f(k)) = k."""
        metric = RougeWMetric(alpha=1.5)

        for k in [1, 2, 3, 5, 10]:
            weighted = metric._weight_function(k)
            result = metric._inverse_weight_function(weighted)
            assert abs(result - k) < 0.001

    def test_inverse_weight_function_zero_returns_zero(self):
        """Test that f^(-1)(0) = 0."""
        metric = RougeWMetric()

        assert metric._inverse_weight_function(0.0) == 0.0

    def test_inverse_weight_function_negative_raises_error(self):
        """Test that f^(-1)(negative) = 0."""
        metric = RougeWMetric()
        with pytest.raises(ValueError, match="value must be >= 0"):
            metric._inverse_weight_function(-1.0)


class TestCalculateWLCS:
    """Tests for the Weighted LCS calculation."""

    def test_wlcs_identical_sequences(self):
        """Test WLCS with identical sequences."""
        metric = RougeWMetric(alpha=2.0)
        tokens = ["a", "b", "c", "d"]

        wlcs = metric.calculate_wlcs(tokens, tokens)

        # All 4 tokens match consecutively: f(4) = 4^2 = 16
        assert abs(wlcs - 16.0) < 0.001

    def test_wlcs_no_common_elements(self):
        """Test WLCS with no common elements returns 0."""
        metric = RougeWMetric()
        pred = ["a", "b", "c"]
        ref = ["x", "y", "z"]

        wlcs = metric.calculate_wlcs(pred, ref)

        assert wlcs == 0.0

    def test_wlcs_empty_prediction(self):
        """Test WLCS with empty prediction returns 0."""
        metric = RougeWMetric()

        wlcs = metric.calculate_wlcs([], ["a", "b", "c"])

        assert wlcs == 0.0

    def test_wlcs_empty_reference(self):
        """Test WLCS with empty reference returns 0."""
        metric = RougeWMetric()

        wlcs = metric.calculate_wlcs(["a", "b", "c"], [])

        assert wlcs == 0.0

    def test_wlcs_both_empty(self):
        """Test WLCS with both empty returns 0."""
        metric = RougeWMetric()

        wlcs = metric.calculate_wlcs([], [])

        assert wlcs == 0.0

    def test_wlcs_single_match(self):
        """Test WLCS with single matching element."""
        metric = RougeWMetric(alpha=2.0)

        wlcs = metric.calculate_wlcs(["a"], ["a"])

        # Single match: f(1) = 1
        assert abs(wlcs - 1.0) < 0.001

    def test_wlcs_consecutive_matches_vs_non_consecutive(self):
        """Test that consecutive matches get higher score than non-consecutive."""
        metric = RougeWMetric(alpha=2.0)

        pred_consecutive = ["a", "b", "c", "d", "e"]
        ref_consecutive = ["a", "b", "c"]
        wlcs_consecutive = metric.calculate_wlcs(pred_consecutive, ref_consecutive)

        pred_non_consecutive = ["a", "d", "b", "e", "c"]
        wlcs_non_consecutive = metric.calculate_wlcs(
            pred_non_consecutive, ref_consecutive
        )

        # Consecutive: f(3) = 9
        # Non-consecutive: f(1) + f(1) + f(1) = 3
        assert wlcs_consecutive > wlcs_non_consecutive
        assert abs(wlcs_consecutive - 9.0) < 0.001
        assert abs(wlcs_non_consecutive - 3.0) < 0.001

    def test_wlcs_mixed_consecutive_and_non_consecutive(self):
        """Test WLCS with mixed consecutive and non-consecutive matches."""
        metric = RougeWMetric(alpha=2.0)

        # "a b" consecutive, then gap, then "d"
        pred = ["a", "b", "c", "d"]
        ref = ["a", "b", "d"]

        wlcs = metric.calculate_wlcs(pred, ref)

        # "a b" consecutive: f(2) = 4
        # "d" separate: f(1) = 1
        # Total: 4 + 1 = 5
        assert abs(wlcs - 5.0) < 0.001

    def test_wlcs_alpha_one_equals_standard_lcs(self):
        """Test that WLCS with alpha=1.0 equals standard LCS length."""
        metric = RougeWMetric(alpha=1.0)

        pred = ["a", "b", "c", "d", "e"]
        ref = ["a", "b", "c"]

        wlcs = metric.calculate_wlcs(pred, ref)

        # Standard LCS length = 3 (a, b, c)
        assert abs(wlcs - 3.0) < 0.001

    def test_wlcs_order_matters(self):
        """Test that WLCS respects sequence order."""
        metric = RougeWMetric(alpha=2.0)

        pred = ["a", "b", "c"]
        ref_ordered = ["a", "b", "c"]
        ref_reversed = ["c", "b", "a"]

        wlcs_ordered = metric.calculate_wlcs(pred, ref_ordered)
        assert abs(wlcs_ordered - 9.0) < 0.001

        wlcs_reversed = metric.calculate_wlcs(pred, ref_reversed)
        assert abs(wlcs_reversed - 1.0) < 0.001


class TestRougeWRecall:
    """Tests for ROUGE-W recall calculation."""

    def test_recall_identical_texts(self):
        """Test that identical texts return recall of 1.0."""
        metric = RougeWMetric()
        text = "the cat sat on the mat"

        recall = metric.calculate_recall(text, text)

        assert abs(recall - 1.0) < 0.001

    def test_recall_empty_prediction(self):
        """Test that empty prediction returns recall of 0.0."""
        metric = RougeWMetric()

        recall = metric.calculate_recall("", "the cat sat")

        assert recall == 0.0

    def test_recall_empty_reference(self):
        """Test that empty reference returns recall of 0.0."""
        metric = RougeWMetric()

        recall = metric.calculate_recall("the cat sat", "")

        assert recall == 0.0

    def test_recall_both_empty(self):
        """Test that both empty returns recall of 0.0."""
        metric = RougeWMetric()

        recall = metric.calculate_recall("", "")

        assert recall == 0.0

    def test_recall_no_overlap(self):
        """Test recall with no overlapping words."""
        metric = RougeWMetric()

        recall = metric.calculate_recall("abc def", "xyz uvw")

        assert recall == 0.0

    def test_recall_partial_overlap(self):
        """Test recall with partial overlap."""
        metric = RougeWMetric(alpha=1.0)

        prediction = "the cat sat"
        reference = "the dog sat"

        recall = metric.calculate_recall(prediction, reference)

        # Reference: ["the", "dog", "sat"]
        # LCS with prediction: "the", "sat" = length 2 (not consecutive)
        # Recall = 2/3 = 0.666...
        expected = 2.0 / 3.0
        assert abs(recall - expected) < 0.001

    def test_recall_all_reference_words_in_prediction(self):
        """Test recall when all reference words appear in prediction."""
        metric = RougeWMetric(alpha=1.0)

        prediction = "the big cat sat on mat"
        reference = "the cat sat"

        recall = metric.calculate_recall(prediction, reference)

        # Reference has 3 words, all found in prediction (not all consecutive)
        # LCS = "the", "cat", "sat" = 3
        # Recall = 3/3 = 1.0
        assert abs(recall - 1.0) < 0.001

    def test_recall_consecutive_matches_improve_score(self):
        """Test that consecutive matches improve recall when alpha > 1."""
        metric = RougeWMetric(alpha=2.0)

        # Case 1: Prediction with consecutive match "a b c"
        prediction_consecutive = "a b c x y"
        reference = "a b c"
        recall_consecutive = metric.calculate_recall(prediction_consecutive, reference)

        # Case 2: Prediction with non-consecutive matches
        prediction_scattered = "a x b y c"
        recall_scattered = metric.calculate_recall(prediction_scattered, reference)

        # Both have same LCS length but consecutive should score higher
        assert recall_consecutive > recall_scattered
        assert abs(recall_consecutive - 1.0) < 0.001  # Perfect consecutive match


class TestRougeWPrecision:
    """Tests for ROUGE-W precision calculation."""

    def test_precision_identical_texts(self):
        """Test that identical texts return precision of 1.0."""
        metric = RougeWMetric()
        text = "the cat sat on the mat"

        precision = metric.calculate_precision(text, text)

        assert abs(precision - 1.0) < 0.001

    def test_precision_empty_prediction(self):
        """Test that empty prediction returns precision of 0.0."""
        metric = RougeWMetric()

        precision = metric.calculate_precision("", "the cat sat")

        assert precision == 0.0

    def test_precision_empty_reference(self):
        """Test that empty reference returns precision of 0.0."""
        metric = RougeWMetric()

        precision = metric.calculate_precision("the cat sat", "")

        # Prediction has words but no matches possible
        assert precision == 0.0

    def test_precision_both_empty(self):
        """Test that both empty returns precision of 0.0."""
        metric = RougeWMetric()

        precision = metric.calculate_precision("", "")

        assert precision == 0.0

    def test_precision_no_overlap(self):
        """Test precision with no overlapping words."""
        metric = RougeWMetric()

        precision = metric.calculate_precision("abc def", "xyz uvw")

        assert precision == 0.0

    def test_precision_partial_overlap(self):
        """Test precision with partial overlap."""
        metric = RougeWMetric(alpha=1.0)

        prediction = "the cat sat"
        reference = "the dog sat"

        precision = metric.calculate_precision(prediction, reference)

        # Prediction: ["the", "cat", "sat"]
        # LCS with reference: "the", "sat" = length 2
        # Precision = 2/3 = 0.666...
        expected = 2.0 / 3.0
        assert abs(precision - expected) < 0.001

    def test_precision_prediction_longer_than_reference(self):
        """Test precision when prediction is much longer than reference."""
        metric = RougeWMetric(alpha=1.0)

        prediction = "the cat sat on the mat and the dog"
        reference = "the cat"

        precision = metric.calculate_precision(prediction, reference)

        # Prediction: 9 words, LCS = "the", "cat" = 2
        # Precision = 2/9
        expected = 2.0 / 9.0
        assert abs(precision - expected) < 0.001

    def test_precision_all_prediction_words_in_reference(self):
        """Test precision when all prediction words appear in reference."""
        metric = RougeWMetric(alpha=1.0)

        prediction = "the cat"
        reference = "the big cat sat on mat"

        precision = metric.calculate_precision(prediction, reference)

        # Prediction has 2 words, both found in reference
        # LCS = "the", "cat" = 2
        # Precision = 2/2 = 1.0
        assert abs(precision - 1.0) < 0.001


class TestRougeWFMeasure:
    """Tests for ROUGE-W F-measure calculation."""

    def test_f_measure_identical_texts(self):
        """Test that identical texts return F-measure of 1.0."""
        metric = RougeWMetric()
        text = "the cat sat on the mat"

        f_measure = metric.calculate_f_measure(text, text)

        assert abs(f_measure - 1.0) < 0.001

    def test_f_measure_empty_prediction(self):
        """Test that empty prediction returns F-measure of 0.0."""
        metric = RougeWMetric()

        f_measure = metric.calculate_f_measure("", "the cat sat")

        assert f_measure == 0.0

    def test_f_measure_empty_reference(self):
        """Test that empty reference returns F-measure of 0.0."""
        metric = RougeWMetric()

        f_measure = metric.calculate_f_measure("the cat sat", "")

        assert f_measure == 0.0

    def test_f_measure_both_empty(self):
        """Test that both empty returns F-measure of 0.0."""
        metric = RougeWMetric()

        f_measure = metric.calculate_f_measure("", "")

        assert f_measure == 0.0

    def test_f_measure_no_overlap(self):
        """Test F-measure with no overlapping words."""
        metric = RougeWMetric()

        f_measure = metric.calculate_f_measure("abc def", "xyz uvw")

        assert f_measure == 0.0

    def test_f_measure_combines_precision_and_recall(self):
        """Test that F-measure correctly combines precision and recall."""
        metric = RougeWMetric(beta=1.0)
        prediction = "the cat sat"
        reference = "the cat"

        precision = metric.calculate_precision(prediction, reference)
        recall = metric.calculate_recall(prediction, reference)
        f_measure = metric.calculate_f_measure(prediction, reference)

        # F1 = 2 * P * R / (P + R)
        expected = 2 * precision * recall / (precision + recall)
        assert abs(f_measure - expected) < 0.001

    def test_f_measure_beta_one_is_harmonic_mean(self):
        """Test that beta=1 gives harmonic mean of precision and recall."""
        metric = RougeWMetric(beta=1.0)
        prediction = "the big cat sat"
        reference = "the cat ran"

        precision = metric.calculate_precision(prediction, reference)
        recall = metric.calculate_recall(prediction, reference)
        f_measure = metric.calculate_f_measure(prediction, reference)

        expected_harmonic_mean = 2 * precision * recall / (precision + recall)
        assert abs(f_measure - expected_harmonic_mean) < 0.001

    def test_f_measure_high_beta_favors_recall(self):
        """Test that higher beta gives more weight to recall."""
        prediction = "a b"  # High precision, lower recall
        reference = "a b c d e"

        metric_beta_1 = RougeWMetric(beta=1.0, alpha=1.0)
        metric_beta_2 = RougeWMetric(beta=2.0, alpha=1.0)

        # With alpha=1.0:
        # Precision = 2/2 = 1.0 (both words match)
        # Recall = 2/5 = 0.4

        f1 = metric_beta_1.calculate_f_measure(prediction, reference)
        f2 = metric_beta_2.calculate_f_measure(prediction, reference)

        # Higher beta should result in lower score when recall is low
        assert f2 < f1

    def test_f_measure_low_beta_favors_precision(self):
        """Test that lower beta gives more weight to precision."""
        prediction = "a b c d e"  # Lower precision, high recall
        reference = "a b"

        metric_beta_1 = RougeWMetric(beta=1.0, alpha=1.0)
        metric_beta_half = RougeWMetric(beta=0.5, alpha=1.0)

        # With alpha=1.0:
        # Precision = 2/5 = 0.4
        # Recall = 2/2 = 1.0 (all reference words match)

        f1 = metric_beta_1.calculate_f_measure(prediction, reference)
        f_half = metric_beta_half.calculate_f_measure(prediction, reference)

        # Lower beta should result in lower score when precision is low
        assert f_half < f1


class TestRougeWNormalization:
    """Tests for text normalization behavior."""

    def test_case_insensitive(self):
        """Test that comparison is case insensitive."""
        metric = RougeWMetric()

        result = metric(prediction="The Cat Sat", reference="the cat sat")

        assert abs(result - 1.0) < 0.001

    def test_punctuation_removal(self):
        """Test that punctuation is removed."""
        metric = RougeWMetric()

        result = metric(prediction="Hello, world!", reference="Hello world")

        assert abs(result - 1.0) < 0.001

    def test_various_punctuation(self):
        """Test removal of various punctuation marks."""
        metric = RougeWMetric()

        result = metric(
            prediction="Hello... world?! How's it going?",
            reference="Hello world Hows it going",
        )

        assert abs(result - 1.0) < 0.001

    def test_whitespace_normalization(self):
        """Test that extra whitespace is normalized."""
        metric = RougeWMetric()

        result = metric(prediction="  hello   world  ", reference="hello world")

        assert abs(result - 1.0) < 0.001


class TestRougeWEdgeCases:
    """Tests for edge cases."""

    def test_very_long_sequences(self):
        """Test with very long sequences."""
        metric = RougeWMetric()

        words = ["word" + str(i) for i in range(1000)]
        text = " ".join(words)

        result = metric(prediction=text, reference=text)

        assert abs(result - 1.0) < 0.001

    def test_numbers_as_words(self):
        """Test handling of numbers."""
        metric = RougeWMetric()

        result = metric(
            prediction="article 123 section 456", reference="article 123 section 456"
        )

        assert abs(result - 1.0) < 0.001


class TestRougeWAlphaComparison:
    """Tests comparing behavior with different alpha values."""

    def test_higher_alpha_penalizes_gaps_more(self):
        """Test that higher alpha values penalize gaps in matches more."""
        # Text with non-consecutive matches
        prediction = "a x b y c"
        reference = "a b c"

        metric_alpha_1 = RougeWMetric(alpha=1.0)
        metric_alpha_2 = RougeWMetric(alpha=2.0)
        metric_alpha_3 = RougeWMetric(alpha=3.0)

        score_1 = metric_alpha_1.calculate_f_measure(prediction, reference)
        score_2 = metric_alpha_2.calculate_f_measure(prediction, reference)
        score_3 = metric_alpha_3.calculate_f_measure(prediction, reference)

        # Higher alpha should give lower scores for scattered matches
        assert score_1 > score_2 > score_3


class TestRougeWMathematicalProperties:
    """Tests for mathematical properties of ROUGE-W."""

    def test_symmetry_of_f_measure_with_equal_lengths(self):
        """Test F-measure is symmetric when texts have equal length and beta=1."""
        metric = RougeWMetric(beta=1.0)

        text1 = "the cat sat"
        text2 = "a dog ran"

        f1 = metric.calculate_f_measure(text1, text2)
        f2 = metric.calculate_f_measure(text2, text1)

        # With same lengths and beta=1, should be symmetric
        assert abs(f1 - f2) < 0.001

    def test_recall_and_precision_swap_roles(self):
        """Test that swapping prediction and reference swaps recall and precision."""
        metric = RougeWMetric()

        pred = "a b c d e"
        ref = "a b c"

        recall_1 = metric.calculate_recall(pred, ref)
        precision_1 = metric.calculate_precision(pred, ref)

        recall_2 = metric.calculate_recall(ref, pred)
        precision_2 = metric.calculate_precision(ref, pred)

        # Recall with (pred, ref) should equal Precision with (ref, pred)
        assert abs(recall_1 - precision_2) < 0.001
        assert abs(precision_1 - recall_2) < 0.001

    def test_wlcs_commutative(self):
        """Test that WLCS is commutative (same result swapping arguments)."""
        metric = RougeWMetric()

        tokens1 = ["a", "b", "c", "d"]
        tokens2 = ["a", "x", "c", "y"]

        wlcs_1 = metric.calculate_wlcs(tokens1, tokens2)
        wlcs_2 = metric.calculate_wlcs(tokens2, tokens1)

        assert abs(wlcs_1 - wlcs_2) < 0.001
