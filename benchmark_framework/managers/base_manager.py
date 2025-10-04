import json
from abc import ABC
from benchmark_framework.types.task import Task
from benchmark_framework.utils import initialize_tasks
from benchmark_framework.constants import ENCODING, RESULTS_PATH


class BaseManager(ABC):
    """
    Abstract base class for benchmark managers.

    Handles task initialization, result collection, and file output for
    different types of benchmark evaluations.
    """

    def __init__(self, model_name: str, dataset_name: str):
        super().__init__()
        self.model_name = model_name
        self.tasks = initialize_tasks(dataset_name)
        self.results = []

        # Set fixed output directory structure: PolishLawLLM-Benchmark/results/dataset_name/
        self.base_dir = RESULTS_PATH / dataset_name
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_tasks(self) -> list[Task]:
        return self.tasks

    def get_result(self, task: Task, model_response: str, model_tools: str) -> dict:
        """
        Generate a result dictionary for a completed task.

        Args:
            task: The task that was evaluated
            model_response: The raw response from the model

        Returns:
            dict: A dictionary containing task details, model response, and evaluation results
        """
        pass

    def append_to_file(self, output_file: str, result: dict):
        full_path = self.base_dir / output_file
        with open(full_path, "a", encoding=ENCODING) as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

    def save_all_results(self, output_file: str):
        full_path = self.base_dir / output_file
        with open(full_path, "w", encoding=ENCODING) as f:
            for result in self.results:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")

    def get_summary(self) -> dict:
        total = len(self.results)
        correct = sum(1 for result in self.results if result["is_correct"])

        return {
            "model_name": self.model_name,
            "total_tasks": total,
            "correct_answers": correct,
            "accuracy": correct / total if total > 0 else 0.0,
        }
