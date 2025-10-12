from abc import ABC, abstractmethod
from typing import List
import re

from benchmark_framework.models.model_config import ModelConfig


class BaseModel(ABC):
    """
    Abstract base class for language model implementations.

    Provides a common interface for different LLM providers (OpenAI, Google, etc.).
    Concrete implementations must implement the `generate_response` method to handle
    model-specific API calls and response formatting.
    """

    def __init__(self, model_name: str, model_config: ModelConfig, **kwargs):
        super().__init__()
        self.model_name = model_name
        self.model_config = model_config

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """
        Generate a response from the language model for a given prompt.
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
