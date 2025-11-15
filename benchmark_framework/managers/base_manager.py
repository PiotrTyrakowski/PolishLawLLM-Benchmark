import json
import os
from abc import ABC, abstractmethod
from pathlib import Path

from benchmark_framework.types.task import Task
from benchmark_framework.utils import initialize_tasks
from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.metrics.base_metric import BaseMetric
from typing import List
from benchmark_framework.constants import (
    ENCODING,
    RESULTS_PATH,
    DATA_PATH,
    SYSTEM_PROMPTS,
)


# TODO: implement with metrics
class BaseManager(ABC):
    """
    Abstract base class for benchmark managers.

    Handles task initialization, result collection, and file output for
    different types of benchmark evaluations.
    """

    def __init__(
        self,
        model: BaseModel,
        manager_type: str,
        metrics: List[BaseMetric],
        tasks_path: Path = DATA_PATH,
    ):
        super().__init__()
        self.model = model
        self.metrics = metrics
        self.tasks = initialize_tasks(manager_type.lower(), tasks_path)
        self.results = []
        self.system_prompt = SYSTEM_PROMPTS[manager_type.upper()]

        assert self.system_prompt is not None
        assert self.tasks is not None

        self.base_dir = RESULTS_PATH / manager_type
        self.base_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def _extract_answer_from_response(self, response_text: str) -> str:
        """
        Extract answer from model response.
        """
        pass

    @abstractmethod
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
