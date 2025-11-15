import json
import re
from pathlib import Path
from dataclasses import asdict
from typing import List

from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.types.exam import Exam
from benchmark_framework.managers.base_manager import BaseManager
from benchmark_framework.constants import DATA_PATH
from benchmark_framework.metrics.base_metric import BaseMetric


# TODO: implement with metrics
class ExamManager(BaseManager):
    """
    Manager for handling legal exam benchmark evaluations.
    """

    def __init__(
        self, model: BaseModel, metrics: List[BaseMetric], tasks_path: Path = DATA_PATH
    ):
        super().__init__(model, "exams", metrics, tasks_path)

    def get_result(self, exam: Exam, model_response: str) -> dict:
        extracted_answer = self._extract_answer_from_response(model_response)
        is_correct = extracted_answer == exam.answer

        result = {
            "year": exam.year,
            "exam_type": exam.exam_type,
            "question": exam.question,
            "choices": exam.choices,
            "answer": exam.answer,
            "legal_basis": exam.legal_basis,
            "model_name": self.model.model_name,
            "model_config": json.dumps(asdict(self.model.model_config)),
            "model_response": model_response,
            "extracted_answer": extracted_answer,
            "is_correct": is_correct,
        }

        self.results.append(result)
        return result

    def _extract_answer_from_response(self, response_text: str) -> str:
        """
        Extract answer from model response that ends with "ANSWER: X" format.
        Returns:
            Single letter answer (A, B, or C) or original text if parsing fails
        """
        response_text = response_text.strip()

        match = re.search(r"ANSWER:\s*([ABC])", response_text, re.IGNORECASE)
        if match:
            return match.group(1).upper()

        # Fallback: look for single letter at the end
        for letter in ["A", "B", "C"]:
            if letter in response_text[-5:]:
                return letter

        # Return full response if parsing fails
        return response_text
