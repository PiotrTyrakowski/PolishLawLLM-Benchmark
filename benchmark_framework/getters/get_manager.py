from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.managers.exam_manager import ExamManager
from benchmark_framework.managers.base_manager import BaseManager

# Model registry mapping model names to their corresponding classes
MANAGER_REGISTRY = {
    "exams": ExamManager,
}

def get_manager_by_dataset(dataset_name: str, model_name: str) -> BaseManager:
    """
    Factory function to get a manager instance by dataset name.

    Args:
        dataset_name: The name of the dataset manager to instantiate.

    Returns:
        An instance of the specified manager class.
    """
    manager_class = MANAGER_REGISTRY.get(dataset_name)
    if not manager_class:
        raise ValueError(f"Dataset name '{dataset_name}' is not recognized.")

    manager_instance = manager_class(model_name)

    return manager_instance
