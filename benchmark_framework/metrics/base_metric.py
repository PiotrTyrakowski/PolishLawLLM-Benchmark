from abc import ABC, abstractmethod
from typing import Iterable, Sequence
from collections import Counter


class BaseMetric(ABC):
    """
    Common interface for evaluation metrics producing scores normalized to the [0, 1] interval.
    """

    def __init__(self, name: str):
        self.name = name
        self.epsylon = 0.0001

    def __call__(self, prediction: str, reference: str) -> float:
        """Compute a single metric score clipped to the [0.0, 1.0] interval."""

        normalized_prediction = self._normalize_text(prediction)
        normalized_reference = self._normalize_text(reference)
        score = float(self._compute(normalized_prediction, normalized_reference))
        return max(0.0, min(1.0, score))

    def score_batch(
        self, predictions: Sequence[str], references: Sequence[str]
    ) -> Iterable[float]:
        """Convenience method for scoring aligned batches of texts."""

        if len(predictions) != len(references):
            raise ValueError("predictions and references must have the same length")
        for pred, ref in zip(predictions, references):
            yield self(pred, ref)

    def _normalize_text(self, text: str) -> str:
        """Hook for subclasses to tweak normalization without overriding __call__."""

        return text.strip()

    def _ngrams(self, tokens: Sequence[str], n: int) -> Counter[tuple[str, ...]]:
        return Counter(tuple(tokens[i : i + n]) for i in range(max(len(tokens) - n + 1, 0)))

    @abstractmethod
    def _compute(self, prediction: str, reference: str) -> float:
        """Return the raw metric value before clipping to [0.0, 1.0]."""

   
