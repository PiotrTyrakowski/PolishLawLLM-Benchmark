from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelInfo:
    """Information about a model."""

    parameters: Optional[float]  # Number of parameters in billions (B), None if unknown
    shortcut: str


MODEL_CONFIG: dict[str, ModelInfo] = {
    "CYFRAGOVPL-PLLuM-12B-instruct": ModelInfo(parameters=12, shortcut="P"),
    "speakleash-bielik-11b-v3.0-instruct": ModelInfo(parameters=11, shortcut="B"),
    "google-gemma-3-12b-it": ModelInfo(parameters=12, shortcut="G"),
    "meta-llama-llama-3.1-405b-instruct": ModelInfo(parameters=405, shortcut="L"),
    "meta-llama-llama-3.3-70b-instruct": ModelInfo(parameters=70, shortcut="L2"),
    "mistral-large-latest": ModelInfo(parameters=675, shortcut="M"),
    "mistralai-mistral-nemo": ModelInfo(parameters=12, shortcut="m"),
    "deepseek-deepseek-v3.2": ModelInfo(parameters=685, shortcut="D"),
    "meta-llama-llama-4-maverick": ModelInfo(parameters=400, shortcut="LM"),
}


def get_model_info(model_name: str) -> ModelInfo:
    """Get model info by name, with fallback to original name."""
    return MODEL_CONFIG.get(model_name, ModelInfo(parameters=None, shortcut=model_name))
