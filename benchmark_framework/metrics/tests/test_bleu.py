import pytest
from benchmark_framework.metrics.weighted_bleu import WeightedBleuMetric


# Basic functionality tests
def test_bleu_identical_texts_returns_one():
    """Test that two identical texts return a BLEU score of 1.0."""
    metric = WeightedBleuMetric()
    text = "zakaz prowadzenia pojazdów"

    score = metric(prediction=text, reference=text)

    assert score == 1.0, f"Expected score 1.0 for identical texts, got {score}"


def test_bleu_completely_different_texts_returns_zero():
    """Test that texts with no overlapping words return 0.0."""
    metric = WeightedBleuMetric()
    prediction = "apple orange banana"
    reference = "car truck motorcycle"

    score = metric(prediction=prediction, reference=reference)

    assert (
        score == 0.0
    ), f"Expected score 0.0 for completely different texts, got {score}"


def test_bleu_partial_overlap():
    """Test BLEU score with partial word overlap."""
    metric = WeightedBleuMetric()
    prediction = "the cat sat on the mat"
    reference = "the dog sat on the floor"

    score = metric(prediction=prediction, reference=reference)

    # Should have partial overlap (the, sat, on, the)
    assert 0.0 < score < 1.0, f"Expected score between 0 and 1, got {score}"


# Punctuation and whitespace normalization tests
def test_bleu_ignores_punctuation():
    """Test that BLEU ignores punctuation differences."""
    metric = WeightedBleuMetric()
    prediction = "zakaz prowadzenia pojazdów"
    reference = "zakaz, prowadzenia pojazdów!"

    score = metric(prediction=prediction, reference=reference)

    assert score == 1.0, f"Expected score 1.0 when ignoring punctuation, got {score}"


def test_bleu_normalizes_whitespace():
    """Test that BLEU handles extra whitespace correctly."""
    metric = WeightedBleuMetric()
    prediction = "zakaz   prowadzenia    pojazdów"
    reference = "zakaz prowadzenia pojazdów"

    score = metric(prediction=prediction, reference=reference)

    assert score == 1.0, f"Expected score 1.0 with normalized whitespace, got {score}"


def test_bleu_case_insensitive():
    """Test that BLEU is case insensitive."""
    metric = WeightedBleuMetric()
    prediction = "Zakaz Prowadzenia Pojazdów"
    reference = "zakaz prowadzenia pojazdów"

    score = metric(prediction=prediction, reference=reference)

    assert score == 1.0, f"Expected score 1.0 for case differences, got {score}"


# Word order tests
def test_bleu_sensitive_to_word_order():
    """Test that BLEU is sensitive to word order (affects n-grams > 1)."""
    metric = WeightedBleuMetric()
    prediction = "pojazdów prowadzenia zakaz"
    reference = "zakaz prowadzenia pojazdów"

    score = metric(prediction=prediction, reference=reference)

    # Should be less than 1.0 because bigrams/trigrams don't match
    assert (
        0.0 < score < 1.0
    ), f"Expected score between 0 and 1 for reordered words, got {score}"


def test_bleu_empty_prediction_returns_zero():
    """Test that empty prediction returns 0.0."""
    metric = WeightedBleuMetric()

    score = metric(prediction="", reference="zakaz prowadzenia pojazdów")

    assert score == 0.0, f"Expected score 0.0 for empty prediction, got {score}"


def test_bleu_empty_reference_returns_zero():
    """Test that empty reference returns 0.0."""
    metric = WeightedBleuMetric()

    score = metric(prediction="zakaz prowadzenia pojazdów", reference="")

    assert score == 0.0, f"Expected score 0.0 for empty reference, got {score}"


# Brevity penalty tests
def test_bleu_shorter_prediction_applies_brevity_penalty():
    """Test that shorter predictions have lower scores due to brevity penalty."""
    metric = WeightedBleuMetric()
    prediction = "the cat"
    reference = "the cat sat on the mat"

    score = metric(prediction=prediction, reference=reference)

    # Perfect precision but short length
    assert 0.0 < score < 1.0, f"Expected brevity penalty to reduce score, got {score}"


def test_bleu_longer_prediction_no_brevity_penalty():
    """Test that longer predictions don't get brevity penalty."""
    metric = WeightedBleuMetric()
    prediction = "the cat sat on the mat and the floor"
    reference = "the cat sat on the mat"

    score = metric(prediction=prediction, reference=reference)

    # Should have good overlap, no brevity penalty
    assert (
        0.0 < score <= 1.0
    ), f"Expected no brevity penalty for longer prediction, got {score}"


# N-gram tests
def test_bleu_unigram_only_metric():
    """Test BLEU with only unigram importance."""
    metric = WeightedBleuMetric(ngram_importances=[1])
    prediction = "cat the sat"  # Different order
    reference = "the cat sat"

    score = metric(prediction=prediction, reference=reference)

    # With only unigrams, order doesn't matter
    assert score == 1.0, f"Expected score 1.0 for unigram-only metric, got {score}"


def test_bleu_custom_ngram_importances():
    """Test BLEU with custom n-gram importances."""
    metric = WeightedBleuMetric(ngram_importances=[1, 2, 3, 4])
    prediction = "the cat sat on the mat"
    reference = "the cat sat on the mat"

    score = metric(prediction=prediction, reference=reference)

    assert (
        score == 1.0
    ), f"Expected score 1.0 for identical texts with custom importances, got {score}"


def test_bleu_bigram_matching():
    """Test that bigram matching affects score."""
    metric = WeightedBleuMetric()
    prediction = "the cat sat"
    reference = "the cat sat"

    score_perfect = metric(prediction=prediction, reference=reference)

    prediction_reordered = "cat the sat"
    score_reordered = metric(prediction=prediction_reordered, reference=reference)

    print(score_perfect, score_reordered)

    # Perfect order should score higher than reordered
    assert (
        score_perfect > score_reordered
    ), "Expected higher score for correct word order"


# Repeated words tests
def test_bleu_handles_repeated_words():
    """Test that BLEU correctly handles repeated words."""
    metric = WeightedBleuMetric()
    prediction = "the the the cat"
    reference = "the cat"

    score = metric(prediction=prediction, reference=reference)

    # Should not get full credit for repeated words
    assert 0.0 < score < 1.0, f"Expected reduced score for repeated words, got {score}"


def test_bleu_matches_repeated_words_in_reference():
    """Test that BLEU correctly matches repeated words in reference."""
    metric = WeightedBleuMetric()
    prediction = "the the cat"
    reference = "the the cat"

    score = metric(prediction=prediction, reference=reference)

    assert score == 1.0, f"Expected score 1.0 for matching repeated words, got {score}"


# Edge case: single word
def test_bleu_single_word_match():
    """Test BLEU with single matching word."""
    metric = WeightedBleuMetric()
    prediction = "cat"
    reference = "cat"

    score = metric(prediction=prediction, reference=reference)

    assert score == 1.0, f"Expected score 1.0 for single word match, got {score}"


def test_bleu_single_word_mismatch():
    """Test BLEU with single non-matching word."""
    metric = WeightedBleuMetric()
    prediction = "cat"
    reference = "dog"

    score = metric(prediction=prediction, reference=reference)

    assert score == 0.0, f"Expected score 0.0 for single word mismatch, got {score}"


# Special characters and numbers
def test_bleu_with_numbers():
    """Test BLEU handles numbers correctly."""
    metric = WeightedBleuMetric()
    prediction = "zakaz 123 prowadzenia"
    reference = "zakaz 123 prowadzenia"

    score = metric(prediction=prediction, reference=reference)

    assert score == 1.0, f"Expected score 1.0 for texts with numbers, got {score}"


def test_bleu_mixed_punctuation_and_text():
    """Test BLEU with heavily punctuated text."""
    metric = WeightedBleuMetric()
    prediction = "Hello, world! How are you?"
    reference = "Hello world How are you"

    score = metric(prediction=prediction, reference=reference)

    assert score == 1.0, f"Expected score 1.0 after punctuation removal, got {score}"


# Score range validation
def test_bleu_score_always_in_valid_range():
    """Test that BLEU scores are always between 0 and 1."""
    metric = WeightedBleuMetric()
    test_cases = [
        ("a b c", "x y z"),
        ("a b c d e", "a b"),
        ("the cat", "the cat sat on the mat"),
        ("", "test"),
        ("test", ""),
    ]

    for pred, ref in test_cases:
        score = metric(prediction=pred, reference=ref)
        assert (
            0.0 <= score <= 1.0
        ), f"Score {score} out of range [0,1] for pred='{pred}', ref='{ref}'"
