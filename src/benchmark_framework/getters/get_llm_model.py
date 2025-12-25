import re

from src.benchmark_framework.models.base_model import BaseModel
from src.benchmark_framework.models.bielik import BielikModel
from src.benchmark_framework.models.gemini import GeminiModel
from src.benchmark_framework.models.local_model import LocalModel
from src.benchmark_framework.configs.model_config import ModelConfig
from src.benchmark_framework.models.nvidia_model import NvidiaModel
from src.benchmark_framework.models.nvidia_nim_model import NvidiaNimModel

MODEL_REGISTRY = {
    "gemini": GeminiModel,
    "speakleash": LocalModel,
    "bielik": BielikModel,
    "deepseek": NvidiaModel,
    "meta": NvidiaModel,
    "CYFRAGOVPL": NvidiaNimModel,
}


def _get_model_type(model_name: str) -> str:
    """
    Get the model type from the model name (e.g. gemini, speakleash, CYFRAGOVPL)
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
