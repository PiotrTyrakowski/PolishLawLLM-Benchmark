from abc import ABC, abstractmethod
from typing import Iterable, Sequence
from collections import Counter
import string


class BaseMetric(ABC):
    """
    Common interface for evaluation metrics producing scores normalized to the [0, 1] interval.
    """

    def __init__(self, name: str):
        self.name = name

    def __call__(self, prediction: str, reference: str) -> float:
        """Compute a single metric score clipped to the [0.0, 1.0] interval."""

        normalized_prediction = prediction.strip()
        normalized_reference = reference.strip()
        score = float(self._compute(normalized_prediction, normalized_reference))
        assert 0 <= score <= 1
        return score

    def score_batch(
        self, predictions: Sequence[str], references: Sequence[str]
    ) -> Iterable[float]:
        """Convenience method for scoring aligned batches of texts."""

        assert len(predictions) == len(
            references
        ), "predictions and references must have the same length"
        for pred, ref in zip(predictions, references):
            yield self(pred, ref)

    def get_normalized_words(self, text: str) -> list[str]:
        """Remove all punctuation from text and return list of words."""
        # Create translation table to remove all punctuation
        translator = str.maketrans("", "", string.punctuation)
        # Remove punctuation and split into words
        cleaned_text = text.translate(translator)
        return cleaned_text.strip().lower().split()

    @abstractmethod
    def _compute(self, prediction: str, reference: str) -> float:
        """Return the raw metric value before clipping to [0.0, 1.0]."""
