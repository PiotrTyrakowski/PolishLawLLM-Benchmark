from typing import Optional
from src.benchmark_framework.metrics.base_metric import BaseMetric


class ExactMatchMetric(BaseMetric):
    """Binary metric for comparing texts."""

    def __init__(self) -> None:
        super().__init__("exact_match")

    def _compute(
        self, prediction: str, reference: str, code_abbr: Optional[str] = None
    ) -> float:
        prediction_words = self.get_normalized_words(prediction)
        reference_words = self.get_normalized_words(reference)
        return 1.0 if prediction_words == reference_words else 0.0
