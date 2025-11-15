import json
import os
from abc import ABC
from pathlib import Path

from benchmark_framework.types.task import Task
from benchmark_framework.utils import initialize_tasks
from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.constants import (
    ENCODING,
    RESULTS_PATH,
    DATA_PATH,
    SYSTEM_PROMPTS,
)


class BaseManager(ABC):
    """
    Abstract base class for benchmark managers.

    Handles task initialization, result collection, and file output for
    different types of benchmark evaluations.
    """

    def __init__(
        self, model: BaseModel, manager_type: str, tasks_path: Path = DATA_PATH
    ):
        super().__init__()
        self.model = model
        self.tasks = initialize_tasks(manager_type.lower(), tasks_path)
        self.results = []
        self.system_prompt = SYSTEM_PROMPTS[manager_type.upper()]

        assert system_prompt is not None
        assert tasks is not None

        self.base_dir = RESULTS_PATH / manager_type
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_model(self) -> BaseModel:
        return self.model

    def get_tasks(self) -> list[Task]:
        return self.tasks

    def get_system_prompt(self) -> str:
        return system_prompt

    def get_result(self, task: Task, model_response: str) -> dict:
        """
        Generate a result dictionary for a completed task.
        Returns:
            dict: A dictionary containing task details, model response, and evaluation results
        """
        pass

    def append_to_file(self, output_file: str, result: dict):
        full_path = self.base_dir / output_file
        os.makedirs(full_path.parent, exist_ok=True)
        with open(full_path, "a", encoding=ENCODING) as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

    def save_all_results(self, output_file: str):
        full_path = self.base_dir / output_file
        os.makedirs(full_path.parent, exist_ok=True)
        with open(full_path, "w", encoding=ENCODING) as f:
            for result in self.results:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")

    def get_summary(self) -> dict:
        total = len(self.results)
        correct = sum(1 for result in self.results if result["is_correct"])

        return {
            "model_name": self.model.model_name,
            "total_tasks": total,
            "correct_answers": correct,
            "accuracy": correct / total if total > 0 else 0.0,
        }
