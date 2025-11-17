import json
import re
from pathlib import Path
from dataclasses import asdict

from benchmark_framework.metrics.weighted_bleu import WeightedBleuMetric
from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.types.exam import Exam
from benchmark_framework.managers.base_manager import BaseManager
from benchmark_framework.constants import DATA_PATH
from benchmark_framework.metrics.base_metric import BaseMetric
from benchmark_framework.metrics.exact_match import ExactMatchMetric
from benchmark_framework.metrics.weighted_bleu import WeightedBleuMetric
from parsers.extractors.legal_basis_extractor import LegalBasisExtractor


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
            WeightedBleuMetric(),
        ]

    def get_result(self, exam: Exam, model_response: str) -> dict:
        extracted_answer = self.extract_answer_from_response(model_response)
        extracted_legal_basis_content = self.extract_legal_basis_from_response(
            model_response
        )
        legal_basis_extractor = LegalBasisExtractor()
        extracted_legal_basis = legal_basis_extractor.parse(exam.legal_basis)

        is_correct = extracted_answer == exam.answer

        metrics_results = {
            metric.name: metric(
                extracted_legal_basis_content,
                exam.legal_basis_content,
                extracted_legal_basis.code,
            )
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
