import json
import os
from abc import ABC, abstractmethod
import re
from pathlib import Path

from benchmark_framework.types.task import Task
from benchmark_framework.metrics.base_metric import BaseMetric
from benchmark_framework.utils import initialize_tasks
from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.metrics.exact_match import ExactMatchMetric
from benchmark_framework.metrics.weighted_bleu import WeightedBleuMetric
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
        tasks_path: Path = DATA_PATH,
    ):
        super().__init__()
        self.model = model
        self.tasks = initialize_tasks(manager_type.lower(), tasks_path)
        self.results = []
        self.system_prompt = SYSTEM_PROMPTS[manager_type.upper()]

        assert self.system_prompt is not None
        assert self.tasks is not None

        self.base_dir = RESULTS_PATH / manager_type
        self.base_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def extract_answer_from_response(response_text: str) -> str:
        """
        Extract answer from model response in JSON format.
        Handles markdown code blocks and incomplete/truncated JSON.
        """
        response_text = response_text.strip()
        answer = ""

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
            answer = json_response.get("answer", "").strip().upper()
        except json.JSONDecodeError:
            answer_match = re.search(
                r'"answer"\s*:\s*"([ABC])"', response_text, re.IGNORECASE
            )
            if answer_match:
                answer = answer_match.group(1).upper()
            else:
                json_match = re.search(r'\{.*?"answer".*?\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        json_response = json.loads(json_match.group(0))
                        answer = json_response.get("answer", "").strip().upper()
                    except json.JSONDecodeError:
                        pass

        if answer in ["A", "B", "C"]:
            return answer

        return ""

    def get_metrics(self) -> list[BaseMetric]:
        return [
            ExactMatchMetric(),
            WeightedBleuMetric(), # normal bleu
        ]

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

    @abstractmethod
    def get_summary(self) -> dict:
        """
        Generate a summary of benchmark results.
        Must be implemented by each manager subclass.
        """
        pass

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
