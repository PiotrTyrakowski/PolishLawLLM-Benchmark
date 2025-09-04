from abc import ABC, abstractmethod
from typing import List
import re


class BaseModel(ABC):
    """
    Abstract base class for language model implementations.

    Provides a common interface for different LLM providers (OpenAI, Google, etc.).
    Concrete implementations must implement the `generate_response` method to handle
    model-specific API calls and response formatting.
    """

    def __init__(self, model_name: str, **kwargs):
        super().__init__()
        self.model_name = model_name

    def get_model_name(self):
        return self.model_name

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """
        Generate a response from the language model for a given prompt.

        Args:
            prompt: The formatted question prompt including the question and multiple choice options.

        Returns:
            str: The raw text response from the model, containing the selected answer with string "ANSWER: X".
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

