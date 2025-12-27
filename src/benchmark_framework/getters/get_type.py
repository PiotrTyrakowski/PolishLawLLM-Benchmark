from src.domain.exam import ExamQuestion
from src.benchmark_framework.types.judgment import Judgment
from src.domain.task import Task

TYPE_REGISTRY = {
    "exams": ExamQuestion,
    "judgments": Judgment,
}


def get_task_by_dataset(dataset_name: str, task_raw: dict) -> Task:
    """
    Factory function to get a task instance by dataset name.

    Args:
        dataset_name: The name of the dataset task to instantiate.
        task_raw: The raw task data.

    Returns:
        An instance of the specified task class.
    """
    type_class = TYPE_REGISTRY.get(dataset_name)
    if not type_class:
        raise ValueError(f"Model name '{dataset_name}' is not recognized.")
    type_instance = type_class.from_dict(task_raw)
    return type_instance
