from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.models.gemini import GeminiModel

# Model registry mapping model names to their corresponding classes
MODEL_REGISTRY = {
    "gemini-2.5-pro": GeminiModel,
    "gemini-2.5-flash": GeminiModel,
    "gemini-2.5-flash-lite": GeminiModel,
}


def get_llm_model(model_name, model_tools: str = None) -> BaseModel:
    """
    Factory function to get a model instance by name.

    Args:
        model_name: The name of the model to instantiate.
        model_tools: The tools to use for the model.

    Returns:
        An instance of the specified model class.
    """
    model_class = MODEL_REGISTRY.get(model_name)
    if not model_class:
        raise ValueError(f"Model name '{model_name}' is not recognized.")

    model_instance = model_class(model_name, model_tools)

    return model_instance
