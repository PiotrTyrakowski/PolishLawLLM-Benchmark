from abc import ABC, abstractmethod
from typing import Iterable, Sequence, Optional
import string


class BaseMetric(ABC):
    """
    Common interface for evaluation metrics.
    """

    def __init__(self, name: str):
        self.name = name

    def __call__(
        self, prediction: str, reference: str, code_abbr: Optional[str] = None
    ) -> float:
        """Compute a single metric score."""
        normalized_prediction = prediction.strip()
        normalized_reference = reference.strip()
        score = float(
            self._compute(normalized_prediction, normalized_reference, code_abbr)
        )
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
        # Create translation table to remove all punctuation
        chars_to_remove = string.punctuation.replace("^", "")
        translator = str.maketrans("", "", chars_to_remove)

        # Remove punctuation and split into words
        cleaned_text = text.replace("\n", " ").translate(translator)
        return cleaned_text.strip().lower().split()

    @abstractmethod
    def _compute(
        self, prediction: str, reference: str, code_abbr: Optional[str] = None
    ) -> float:
        """Return the raw metric value."""
