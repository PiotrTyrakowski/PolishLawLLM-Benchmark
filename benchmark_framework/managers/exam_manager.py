import json
from pathlib import Path
from dataclasses import asdict

from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.types.exam import Exam
from benchmark_framework.utils import extract_answer_from_response
from benchmark_framework.managers.base_manager import BaseManager
from benchmark_framework.constants import DATA_PATH
from benchmark_framework.metrics.base_metric import BaseMetric
from benchmark_framework.metrics.exact_match import ExactMatchMetric


class ExamManager(BaseManager):
    """
    Manager for handling legal exam benchmark evaluations.
    """

    def __init__(self, model: BaseModel, tasks_path: Path = DATA_PATH):
        super().__init__(model, "exams", tasks_path)

    def get_tasks(self) -> list[Exam]:
        return self.tasks

    def get_metrics(self) -> list[BaseMetric]:
        return [
            ExactMatchMetric(),
        ]

    def get_result(self, exam: Exam, model_response: str) -> dict:
        extracted_answer = extract_answer_from_response(model_response)
        extract_legal_basis = self.extract_legal_basis_from_response(model_response)
        is_correct = extracted_answer == exam.answer

        metrics_results = {
            metric.name: metric(extract_legal_basis, exam.legal_basis_content)
            for metric in self.get_metrics()
        }

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
            "legal_basis_content": exam.legal_basis_content,
            "metrics": metrics_results,
        }

        self.results.append(result)
        return result
