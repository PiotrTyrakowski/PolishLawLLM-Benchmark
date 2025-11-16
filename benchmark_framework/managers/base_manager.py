import json
import os
from abc import ABC, abstractmethod
import re
from pathlib import Path

from benchmark_framework.types.task import Task
from benchmark_framework.metrics.base_metric import BaseMetric
from benchmark_framework.utils import initialize_tasks
from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.constants import ENCODING, RESULTS_PATH, DATA_PATH


class BaseManager(ABC):
    """
    Abstract base class for benchmark managers.

    Handles task initialization, result collection, and file output for
    different types of benchmark evaluations.
    """

    def __init__(
        self, model: BaseModel, dataset_name: str, tasks_path: Path = DATA_PATH
    ):
        super().__init__()
        self.model = model
        self.tasks = initialize_tasks(dataset_name, tasks_path)
        self.results = []

        self.base_dir = RESULTS_PATH / dataset_name
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_tasks(self) -> list[Task]:
        return self.tasks

    @abstractmethod
    def get_metrics(self) -> list[BaseMetric]:
        """
        Returns a list of metrics to be used for evaluating the model.
        """
        pass

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

    @staticmethod
    def extract_legal_basis_from_response(response_text: str) -> str:
        """
        Extract legal_basis_content from model response in JSON format.
        Handles markdown code blocks and incomplete/truncated JSON.
        """
        response_text = response_text.strip()

        # Remove markdown code block markers if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            response_text = "\n".join(lines).strip()

        try:
            json_response = json.loads(response_text)
            return json_response.get("legal_basis_content", "")
        except json.JSONDecodeError:
            content_match = re.search(
                r'"legal_basis_content"\s*:\s*"([^"]*)"', response_text, re.DOTALL
            )
            if content_match:
                return content_match.group(1)
            else:
                json_match = re.search(
                    r'\{.*?"legal_basis_content".*?\}', response_text, re.DOTALL
                )
                if json_match:
                    try:
                        json_response = json.loads(json_match.group(0))
                        return json_response.get("legal_basis_content", "")
                    except json.JSONDecodeError:
                        pass

        return ""
