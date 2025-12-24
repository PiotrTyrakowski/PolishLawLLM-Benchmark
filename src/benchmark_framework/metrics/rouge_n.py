from collections import Counter
from typing import Optional, List, Sequence
from src.benchmark_framework.metrics.base_metric import BaseMetric


class RougeNMetric(BaseMetric):
    """
    Implementation of the ROUGE-N metric returning the F1 score.
    Defaults to N=3.
    """

    def __init__(self, ngram_importances: Sequence[float] = [1, 1, 1]) -> None:
        super().__init__(f"rouge_n_f1")
        self.ngrams_importances = ngram_importances

    def _compute(
            self, prediction: str, reference: str, code_abbr: Optional[str] = None
    ) -> float:
        return self.calculate_f1(prediction, reference, 3)

    def calculate_f1(self, prediction: str, reference: str, n: int = 3) -> float:
        pred_tokens = self.get_normalized_words(prediction)
        ref_tokens = self.get_normalized_words(reference)

        # Generate n-grams for candidate and reference
        pred_counts = self._get_ngrams(pred_tokens, n)
        ref_counts = self._get_ngrams(ref_tokens, n)

        # If reference is too short to have n-grams, score is 0.0
        # TODO
        if not ref_counts:
            return 0.0

        # Calculate matches (overlap) between candidate and reference n-grams
        match_count = 0
        for ngram, count in pred_counts.items():
            match_count += min(count, ref_counts.get(ngram, 0))

        # Calculate Recall: matches divided by total n-grams in reference
        ref_total = sum(ref_counts.values())
        recall = match_count / ref_total if ref_total > 0 else 0.0

        # Calculate Precision: matches divided by total n-grams in prediction
        pred_total = sum(pred_counts.values())
        precision = match_count / pred_total if pred_total > 0 else 0.0

        # Calculate F1 Score
        if precision + recall == 0:
            return 0.0

        return 2 * (precision * recall) / (precision + recall)

    @staticmethod
    def _get_ngrams(tokens: Sequence[str], n: int) -> Counter[tuple[str, ...]]:
        return Counter(
            tuple(tokens[i : i + n]) for i in range(max(len(tokens) - n + 1, 0))
        )