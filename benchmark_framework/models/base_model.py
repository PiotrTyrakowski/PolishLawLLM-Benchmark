from abc import ABC, abstractmethod

from benchmark_framework.configs.model_config import ModelConfig
from benchmark_framework.configs.runner_config import RunnerConfig


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

    def get_default_runner_config(self):
        return RunnerConfig()

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

    def generate_batch_response(self, prompts: list[str], batch_size: int) -> list[str]:
        return [self.generate_response(prompt) for prompt in prompts]
