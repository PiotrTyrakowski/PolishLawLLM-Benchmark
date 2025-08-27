from abc import ABC, abstractmethod
from typing import List


class BaseModel(ABC):
    """
    Abstract base class for all LLM adapters.
    Concrete implementations must implement `generate_answer`.
    """

    def __init__(self, **kwargs):
        super().__init__()

    @abstractmethod
    def generate_answer(self, question: str, choices: List[str]) -> str:
        """
        Generate an answer for a multiple-choice question.

        Args:
            question: The question prompt (without choices).
            choices: List of choice strings, e.g. ["A) …", "B) …", "C) …", "D) …"].

        Returns:
            A string containing the model’s answer, e.g. "A".
        """
        pass

    def setup(self):
        """
        Optional: load models, warm up, or authenticate.
        Called once before batch generation.
        """
        return

    def teardown(self):
        """
        Optional: cleanup resources (e.g. close sessions).
        Called once after all generations.
        """
        return
