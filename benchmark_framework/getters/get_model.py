from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.models.gemini import GeminiModel
from benchmark_framework.models.local_model import LocalModel

MODEL_REGISTRY = {
    "gemini-2.5-pro": GeminiModel,
    "gemini-2.5-flash": GeminiModel,
    "gemini-2.5-flash-lite": GeminiModel,
    "speakleash/Bielik-4.5B-v3.0-Instruct": LocalModel,
    "CYFRAGOVPL/Llama-PLLuM-8B-chat": LocalModel,
}


def get_model_by_name(model_name, model_tools: str = None) -> BaseModel:
    """
    Factory function to get a model instance by name.
    """
    model_class = MODEL_REGISTRY.get(model_name)
    if not model_class:
        raise ValueError(f"Model name '{model_name}' is not recognized.")
    model_instance = model_class(model_name, model_tools)
    return model_instance
