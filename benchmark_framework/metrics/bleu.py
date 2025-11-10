
import math
from typing import Sequence
from base_metric import BaseMetric
from collections import Counter


class BleuMetric(BaseMetric):
    """Standard BLEU-N precision with Brevity Penalty and customizable n-gram importances."""

    def __init__(
        self, 
        ngram_importances: Sequence[float] = [1, 1, 1, 1]
    ) -> None:
        """
        Args:
            ngram_importances: Importance for each n-gram size (from 1 to max_n) default [1, 1, 1, 1]
            
        """
        self.max_n = len(ngram_importances) 
        super().__init__(f"bleu_max_{self.max_n}gram")
        self.ngram_importances = [x / sum(ngram_importances) for x in ngram_importances] 


    def _compute(self, prediction: str, reference: str) -> float:
        cand_tokens = prediction.lower().split()
        ref_tokens = reference.lower().split()
        if not cand_tokens or not ref_tokens:
            return 0.0

        bp = 1.0 if len(cand_tokens) > len(ref_tokens) else math.exp(
            1 - len(ref_tokens) / max(len(cand_tokens), 1)
        )

        log_precision_sum = 0.0
        for n, importance in enumerate(self.ngram_importances, start=1):
            cand_counts = self._ngrams(cand_tokens, n)
            ref_counts = self._ngrams(ref_tokens, n)
            if not cand_counts:
                return 0.0
            overlap = sum(
                min(count, ref_counts.get(ngram, 0)) for ngram, count in cand_counts.items()
            )
            precision = overlap / sum(cand_counts.values()) + self.epsylon  # >0
            log_precision_sum += importance * math.log(precision)

        return float(bp * math.exp(log_precision_sum))

    @staticmethod
    def _ngrams(tokens: Sequence[str], n: int) -> Counter[tuple[str, ...]]:
        return Counter(tuple(tokens[i : i + n]) for i in range(max(len(tokens) - n + 1, 0)))




