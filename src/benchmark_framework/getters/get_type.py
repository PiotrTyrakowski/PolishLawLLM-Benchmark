from src.common.domain.exam import ExamQuestion
from src.common.domain.judgment import Judgment
from src.common.domain.task import Task

TYPE_REGISTRY = {
    "exams": ExamQuestion,
    "judgments": Judgment,
}


def get_task_by_dataset(dataset_name: str, task_raw: dict) -> Task:
    """
    Factory function to get a task instance by dataset name.
    """
    type_class = TYPE_REGISTRY.get(dataset_name)
    if not type_class:
        raise ValueError(f"Model name '{dataset_name}' is not recognized.")
    type_instance = type_class.from_dict(task_raw)
    return type_instance
