from benchmark_framework.managers.exam_manager import ExamManager
from benchmark_framework.managers.base_manager import BaseManager

MANAGER_REGISTRY = {
    "exams": ExamManager,
}


def get_manager_by_dataset(dataset_name: str, model_name: str) -> BaseManager:
    """
    Factory function to get a manager instance by dataset name.
    """
    manager_class = MANAGER_REGISTRY.get(dataset_name)
    if not manager_class:
        raise ValueError(f"Dataset name '{dataset_name}' is not recognized.")
    manager_instance = manager_class(model_name)
    return manager_instance
