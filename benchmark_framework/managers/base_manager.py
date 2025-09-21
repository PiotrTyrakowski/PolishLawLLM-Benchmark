import json
from abc import ABC
from typing import Optional
from benchmark_framework.types.task import Task
from benchmark_framework.utils import initialize_tasks
from pathlib import Path
from benchmark_framework.constants import ENCODING


class BaseManager(ABC):
    """
    Abstract base class for benchmark managers.

    Handles task initialization, result collection, and file output for
    different types of benchmark evaluations.
    """

    def __init__(self, model_name: str, dataset_name: str, tasks_path: Optional[str] = None,
                 output_path: Optional[str] = None):
        super().__init__()
        dataset_name = dataset_name.replace("/", "-")
        self.model_name = model_name
        self.tasks = initialize_tasks(tasks_path if tasks_path else Path(__file__).parent.parent.parent / "data",
                                      dataset_name)
        self.results = []

        base_dir = output_path if output_path else (Path(__file__).parent.parent.parent / "results" / dataset_name)
        base_dir.mkdir(parents=True, exist_ok=True)
        self.output_file = base_dir / f"{self.model_name}.jsonl"

    def get_tasks(self) -> list[Task]:
        return self.tasks

    def get_result(self, task: Task, model_response: str) -> dict:
        """
        Generate a result dictionary for a completed task.

        Args:
            task: The task that was evaluated
            model_response: The raw response from the model

        Returns:
            dict: A dictionary containing task details, model response, and evaluation results
        """
        pass

    def append_to_file(self, result: dict):
        with open(self.output_file, 'a', encoding=ENCODING) as f:
            f.write(json.dumps(result, ensure_ascii=False) + '\n')

    def save_all_results(self):
        with open(self.output_file, 'w', encoding=ENCODING) as f:
            for result in self.results:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')

    def get_summary(self) -> dict:
        total = len(self.results)
        correct = sum(1 for result in self.results if result["is_correct"])

        return {
            "model_name": self.model_name,
            "total_tasks": total,
            "correct_answers": correct,
            "accuracy": correct / total if total > 0 else 0.0
        }
