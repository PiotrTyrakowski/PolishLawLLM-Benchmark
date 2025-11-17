from benchmark_framework.metrics.base_metric import BaseMetric


class ExactMatchMetric(BaseMetric):
    """Binary metric for comparing discrete labels (e.g., answers A/B/C/D)."""

    def __init__(self) -> None:
        super().__init__("exact_match")

    def _compute(self, prediction: str, reference: str) -> float:
        """
        Returns 1.0 if normalized prediction matches normalized reference, else 0.0
        """
        prediction_words = self.get_normalized_words(prediction)
        reference_words = self.get_normalized_words(reference)
        return 1.0 if prediction_words == reference_words else 0.0
