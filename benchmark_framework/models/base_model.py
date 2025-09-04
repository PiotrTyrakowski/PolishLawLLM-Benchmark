from abc import ABC, abstractmethod
from typing import List
import re


class BaseModel(ABC):
    """
    Abstract base class for all LLM adapters.
    Concrete implementations must implement `generate_response`.
    """

    def __init__(self, model_name: str, **kwargs):
        super().__init__()
        self.model_name = model_name

    def get_model_name(self):
        return self.model_name

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """
        Generate an answer for a multiple-choice question.

        Args:
            prompt: The question prompt (with question and choices).

        Returns:
             A string containing the model response. 
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

