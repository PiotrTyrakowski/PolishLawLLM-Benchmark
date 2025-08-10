from benchmark_framework.models.base import BaseModel
from benchmark_framework.models.gemini import GeminiModel

# Model registry mapping model names to their corresponding classes
MODEL_REGISTRY = {
    "gemini": GeminiModel,
    "gemini-2.5-flash": GeminiModel,
}


def get_model_by_name(model_name) -> BaseModel:
    """
    Factory function to get a model instance by name.

    Args:
        model_name: The name of the model to instantiate.

    Returns:
        An instance of the specified model class.
    """
    model_class = MODEL_REGISTRY.get(model_name)
    if not model_class:
        raise ValueError(f"Model name '{model_name}' is not recognized.")
    return model_class()
