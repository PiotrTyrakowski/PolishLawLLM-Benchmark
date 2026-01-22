from typing import Optional, List
from src.benchmark_framework.metrics.base_metric import BaseMetric


class RougeWMetric(BaseMetric):
    """
    Implementation of the ROUGE-W metric using Weighted Longest Common Subsequence.

    Attributes:
        alpha: The weighting parameter. Higher values give more weight
               to consecutive matches. Must be >= 1.0.
               Weighting function is f(k) = k^alpha.
        beta: Parameter for F-measure calculation. When beta = 1, precision and
              recall have equal weight. Higher beta values favor recall.
    """

    def __init__(self, alpha: float = 1.2, beta: float = 1.0) -> None:
        """
        Initialize the ROUGE-W metric.
        """
        super().__init__("rouge_w")
        if alpha < 1.0:
            raise ValueError("alpha must be >= 1.0")
        self.alpha = alpha
        self.beta = beta
        self.tolerance = 1e-9

    def _compute(
        self, prediction: str, reference: str, code_abbr: Optional[str] = None
    ) -> float:
        return self.calculate_f_measure(prediction, reference)

    def _weight_function(self, k: int) -> float:
        return k**self.alpha

    def _inverse_weight_function(self, value: float) -> float:
        if value < 0:
            raise ValueError("value must be >= 0")
        return value ** (1.0 / self.alpha)

    def calculate_wlcs(
        self, prediction_tokens: List[str], reference_tokens: List[str]
    ) -> float:
        """
        Calculate the Weighted Longest Common Subsequence score.
        """
        m = len(reference_tokens)
        n = len(prediction_tokens)

        if m == 0 or n == 0:
            return 0.0

        # c[i][j] stores the WLCS score
        # w[i][j] stores the length of consecutive matches ending at (i, j)
        c: List[List[float]] = [[0.0] * (n + 1) for _ in range(m + 1)]
        w: List[List[int]] = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if reference_tokens[i - 1] == prediction_tokens[j - 1]:
                    # Match found, extend consecutive sequence
                    k = w[i - 1][j - 1]
                    c[i][j] = (
                        c[i - 1][j - 1]
                        + self._weight_function(k + 1)
                        - self._weight_function(k)
                    )
                    w[i][j] = k + 1
                else:
                    # No match, take the best from left or above
                    if c[i - 1][j] > c[i][j - 1]:
                        c[i][j] = c[i - 1][j]
                        w[i][j] = 0
                    else:
                        c[i][j] = c[i][j - 1]
                        w[i][j] = 0

        return c[m][n]

    def calculate_recall(self, prediction: str, reference: str) -> float:
        pred_tokens = self.get_normalized_words(prediction)
        ref_tokens = self.get_normalized_words(reference)

        m = len(ref_tokens)
        if m == 0:
            return 0.0

        wlcs = self.calculate_wlcs(pred_tokens, ref_tokens)
        recall = self._inverse_weight_function(wlcs) / m

        if recall < 0:
            if recall < -self.tolerance:
                raise ValueError(f"Recall {recall} is significantly below 0")
            recall = 0.0
        elif recall > 1:
            if recall > 1 + self.tolerance:
                raise ValueError(f"Recall {recall} is significantly above 1")
            recall = 1.0

        return recall

    def calculate_precision(self, prediction: str, reference: str) -> float:
        pred_tokens = self.get_normalized_words(prediction)
        ref_tokens = self.get_normalized_words(reference)

        n = len(pred_tokens)
        if n == 0:
            return 0.0

        wlcs = self.calculate_wlcs(pred_tokens, ref_tokens)
        precision = self._inverse_weight_function(wlcs) / n

        if precision < 0:
            if precision < -self.tolerance:
                raise ValueError(f"Precision {precision} is significantly below 0")
            precision = 0.0
        elif precision > 1:
            if precision > 1 + self.tolerance:
                raise ValueError(f"Precision {precision} is significantly above 1")
            precision = 1.0

        return precision

    def calculate_f_measure(self, prediction: str, reference: str) -> float:
        recall = self.calculate_recall(prediction, reference)
        precision = self.calculate_precision(prediction, reference)
        beta_squared = self.beta**2

        denominator = recall + beta_squared * precision
        if denominator == 0:
            return 0.0

        f_measure = (1 + beta_squared) * precision * recall / denominator

        if f_measure < 0:
            if f_measure < -self.tolerance:
                raise ValueError(f"F-measure {f_measure} is significantly below 0")
            f_measure = 0.0
        elif f_measure > 1:
            if f_measure > 1 + self.tolerance:
                raise ValueError(f"F-measure {f_measure} is significantly above 1")
            f_measure = 1.0

        return f_measure
