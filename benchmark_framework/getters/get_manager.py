from pathlib import Path
from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.managers.exam_manager import ExamManager
from benchmark_framework.managers.judgment_manager import JudgmentManager
from benchmark_framework.managers.base_manager import BaseManager
from benchmark_framework.constants import DATA_PATH

MANAGER_REGISTRY = {"exams": ExamManager, "judgments": JudgmentManager}


def get_manager(
    dataset_name: str,
    model: BaseModel,
    metric: BaseMetric,
    tasks_path: Path = DATA_PATH,
) -> BaseManager:
    """
    Factory function to get a manager instance by dataset name.
    """
    manager_class = MANAGER_REGISTRY.get(dataset_name)
    if not manager_class:
        raise ValueError(f"Dataset name '{dataset_name}' is not recognized.")
    manager_instance = manager_class(model, metric, tasks_path)
    return manager_instance
