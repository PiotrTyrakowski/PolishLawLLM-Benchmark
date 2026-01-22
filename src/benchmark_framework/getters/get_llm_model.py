import re

from src.benchmark_framework.models.anthropic import AnthropicModel
from src.benchmark_framework.models.openai import OpenAIModel
from src.benchmark_framework.models.base_model import BaseModel
from src.benchmark_framework.models.gemini import GeminiModel
from src.benchmark_framework.configs.model_config import ModelConfig
from src.benchmark_framework.models.mistral_model import MistralModel
from src.benchmark_framework.models.hfe_model import HFEndpointModel
from src.benchmark_framework.models.open_router import OpenRouterModel

MODEL_REGISTRY = {
    "gemini": GeminiModel,
    "speakleash": HFEndpointModel,
    "deepseek": OpenRouterModel,
    "meta": OpenRouterModel,
    "gpt": OpenAIModel,
    "claude": AnthropicModel,
    "CYFRAGOVPL": HFEndpointModel,
    "perplexity": OpenRouterModel,
    "qwen": OpenRouterModel,
    "x": OpenRouterModel,
    "z": OpenRouterModel,
    "mistralai": OpenRouterModel,
    "mistral": MistralModel,
    "nvidia": OpenRouterModel,
    "google": OpenRouterModel,
}


def _get_model_type(model_name: str) -> str:
    """
    Get the model type from the model name (e.g. gemini for gemini-3-flash-preview)
    """
    model_name_split = re.split(r"[/ -]+", model_name)
    assert len(model_name_split) >= 1
    return model_name_split[0]


def get_llm_model(model_name, model_config: ModelConfig) -> BaseModel:
    """
    Factory function to get a model instance by name.
    """
    model_type = _get_model_type(model_name)
    model_class = MODEL_REGISTRY.get(model_type)
    if not model_class:
        raise ValueError(f"Model name '{model_name}' is not recognized.")
    model_instance = model_class(model_name, model_config)
    return model_instance
