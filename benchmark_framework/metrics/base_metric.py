from abc import ABC, abstractmethod
from typing import Iterable


class BaseMetric(ABC):
    """
    Common interface for evaluation metrics producing scores normalized to the [0, 1] interval.
    """

    lower_bound: float = 0.0
    upper_bound: float = 1.0

    def __init__(self, name: str):
        self.name = name

    def __call__(self, prediction: str, reference: str) -> float:
        """
        Compute the metric score for the given prediction and reference text.
        Implementations must keep the returned score within [0.0, 1.0].
        """

   