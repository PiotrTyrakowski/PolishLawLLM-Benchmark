from base_metric import BaseMetric

class ExactMatchMetric(BaseMetric):
    """Binary metric for comparing discrete labels (e.g., answers A/B/C/D)."""

    def __init__(self) -> None:
        super().__init__("exact_match")

    def _compute(self, prediction: str, reference: str) -> float:
        normalize = lambda text: "".join(text.split()).upper()
        return 1.0 if normalize(prediction) == normalize(reference) else 0.0