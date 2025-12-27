from collections import Counter
from typing import Optional, List, Sequence
from src.benchmark_framework.metrics.base_metric import BaseMetric


class RougeNMetric(BaseMetric):
    """
    Implementation of the ROUGE-N metric returning a weighted average of F1 scores.

    The ngram_importances parameter specifies weights for different n-gram lengths.
    Index i corresponds to the weight for n-grams of length (i+1).
    For example, ngram_importances=[1, 1, 1] weights unigrams, bigrams, and trigrams equally.
    """

    def __init__(self, ngrams_importances: List[float] = [1, 1, 1]) -> None:
        super().__init__(f"rouge_n_f1")
        self.ngrams_importances = ngrams_importances

    def _compute(
        self, prediction: str, reference: str, code_abbr: Optional[str] = None
    ) -> float:
        """
        Calculate weighted average of ROUGE-N F1 scores across all n-gram lengths.
        The index i in ngram_importances corresponds to the weight for n-grams of length i.
        """
        if not self.ngrams_importances:
            return 0.0

        # Get tokens to determine maximum possible n-gram size
        pred_tokens = self.get_normalized_words(prediction)
        ref_tokens = self.get_normalized_words(reference)
        max_possible_n = min(len(pred_tokens), len(ref_tokens))

        # If both texts are empty, return 0
        if max_possible_n == 0:
            return 0.0

        weighted_sum = 0.0
        total_weight = 0.0

        for n, weight in enumerate(self.ngrams_importances, start=1):
            if weight > 0 and n <= max_possible_n:
                f1_score = self.calculate_f1(prediction, reference, n)
                weighted_sum += weight * f1_score
                total_weight += weight

        if total_weight == 0:
            return 0.0

        result = weighted_sum / total_weight
        assert 0.0 <= result <= 1.0
        return result

    def _calculate_intersection_ngrams_count(
        self, pred_ngrams_counts, ref_ngrams_counts
    ) -> int:
        intersection_ngram_counts = 0
        for ngram, count in pred_ngrams_counts.items():
            intersection_ngram_counts += min(count, ref_ngrams_counts.get(ngram, 0))
        return intersection_ngram_counts

    def calculate_precision(self, prediction: str, reference: str, n: int) -> float:
        """Calculate ROUGE-N precision score."""
        pred_tokens = self.get_normalized_words(prediction)
        ref_tokens = self.get_normalized_words(reference)

        pred_counts = self.get_ngrams(pred_tokens, n)
        ref_counts = self.get_ngrams(ref_tokens, n)

        intersection_ngram_counts = self._calculate_intersection_ngrams_count(
            pred_counts, ref_counts
        )
        pred_total_count = sum(pred_counts.values())

        precision = (
            intersection_ngram_counts / pred_total_count
            if pred_total_count > 0
            else 0.0
        )
        assert 0.0 <= precision <= 1.0
        return precision

    def calculate_recall(self, prediction: str, reference: str, n: int) -> float:
        """Calculate ROUGE-N recall score."""
        pred_tokens = self.get_normalized_words(prediction)
        ref_tokens = self.get_normalized_words(reference)

        pred_counts = self.get_ngrams(pred_tokens, n)
        ref_counts = self.get_ngrams(ref_tokens, n)

        intersection_ngram_counts = self._calculate_intersection_ngrams_count(
            pred_counts, ref_counts
        )
        ref_total_count = sum(ref_counts.values())

        recall = (
            intersection_ngram_counts / ref_total_count if ref_total_count > 0 else 0.0
        )
        assert 0.0 <= recall <= 1.0
        return recall

    def calculate_f1(self, prediction: str, reference: str, n: int) -> float:
        """Calculate ROUGE-N F1 score from precision and recall."""
        precision = self.calculate_precision(prediction, reference, n)
        recall = self.calculate_recall(prediction, reference, n)

        # Calculate F1 Score
        if precision + recall == 0:
            return 0.0

        f1 = 2 * (precision * recall) / (precision + recall)
        assert 0.0 <= f1 <= 1.0
        return f1

    @staticmethod
    def get_ngrams(tokens: Sequence[str], n: int) -> Counter[tuple[str, ...]]:
        if n <= 0:
            raise ValueError(f"n must be > 0, got {n}")
        return Counter(
            tuple(tokens[i : i + n]) for i in range(max(len(tokens) - n + 1, 0))
        )
