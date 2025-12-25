from pathlib import Path
from typing import Optional
from src.benchmark_framework.models.base_model import BaseModel
from src.benchmark_framework.managers.exam_manager import ExamManager
from src.benchmark_framework.managers.judgment_manager import JudgmentManager
from src.benchmark_framework.managers.base_manager import BaseManager

MANAGER_REGISTRY = {"exams": ExamManager, "judgments": JudgmentManager}


def get_manager(
    task_type: str,
    model: BaseModel,
    tasks_path: Path,
    year: Optional[int] = None,
) -> BaseManager:
    """
    Factory function to get a manager instance by dataset name.
    """
    manager_class = MANAGER_REGISTRY.get(task_type)
    if not manager_class:
        raise ValueError(f"Dataset name '{task_type}' is not recognized.")
    manager_instance = manager_class(model, tasks_path, year=year)
    return manager_instance
