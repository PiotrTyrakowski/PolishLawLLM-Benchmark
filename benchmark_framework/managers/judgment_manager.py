import json
import re
from pathlib import Path
from dataclasses import asdict
from typing import List

from benchmark_framework.models.base_model import BaseModel
from benchmark_framework.types.judgment import Judgment
from benchmark_framework.managers.base_manager import BaseManager
from benchmark_framework.constants import DATA_PATH
from benchmark_framework.metrics.base_metric import BaseMetric


class JudgmentManager(BaseManager):
    """
    Manager for handling legal judgment benchmark evaluations.
    """

    def __init__(
        self, model: BaseModel, tasks_path: Path = DATA_PATH
    ):
        super().__init__(model, "judgments", tasks_path)

    def get_tasks(self) -> list[Judgment]:
        return self.tasks

    def get_result(self, judgment: Judgment, model_response: str) -> dict:
        extracted_legal_basis = self._extract_legal_basis_from_response(model_response)
        extracted_legal_basis_content = self._extract_content_from_response(model_response)
        
        # Check if both legal basis and content match
        is_legal_basis_correct = (
            extracted_legal_basis.strip().lower() == judgment.legal_basis.strip().lower()
        )

        metrics_results = {
            metric.name: metric(extracted_legal_basis_content, judgment.legal_basis_content)
            for metric in self.get_metrics()
        }

        result = {
            "judgment_link": judgment.judgment_link,
            # "masked_justification_text": judgment.masked_justification_text, TODO: talk what to do with this because its very logn to jsut store it in jsonl
            "legal_basis": judgment.legal_basis,
            "legal_basis_content": judgment.legal_basis_content,
            "model_name": self.model.model_name,
            "model_config": json.dumps(asdict(self.model.model_config)),
            "model_response": model_response,
            "extracted_legal_basis": extracted_legal_basis,
            "extracted_legal_basis_content": extracted_legal_basis_content,
            "is_legal_basis_correct": is_legal_basis_correct,
            "metrics": metrics_results,
        }

        self.results.append(result)
        return result

    def _extract_answer_from_response(self, response_text: str) -> str:
        """
        Extract answer from model response.
        For judgments, this extracts the legal basis (art reference).
        """
        return self._extract_legal_basis_from_response(response_text)

    @staticmethod
    def _extract_legal_basis_from_response(response_text: str) -> str:
        """
        Extract legal basis (art reference) from model response in JSON format.
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
            # Try different possible keys
            art = (
                json_response.get("art", "")
                or json_response.get("legal_basis", "")
                or json_response.get("article", "")
            )
            return art.strip() if art else ""
        except json.JSONDecodeError:
            # Try regex patterns for art reference
            art_patterns = [
                r'"art"\s*:\s*"([^"]+)"',
                r'"legal_basis"\s*:\s*"([^"]+)"',
                r'"article"\s*:\s*"([^"]+)"',
                r"art\s*[:=]\s*['\"]([^'\"]+)['\"]",
            ]
            for pattern in art_patterns:
                match = re.search(pattern, response_text, re.IGNORECASE)
                if match:
                    return match.group(1).strip()

            # Try to find JSON object with art field
            json_match = re.search(r'\{.*?"art".*?\}', response_text, re.DOTALL | re.IGNORECASE)
            if json_match:
                try:
                    json_response = json.loads(json_match.group(0))
                    art = json_response.get("art", "")
                    return art.strip() if art else ""
                except json.JSONDecodeError:
                    pass

        return ""


    def get_summary(self) -> dict:
        total = len(self.results)
        correct = sum(1 for result in self.results if result.get("is_legal_basis_correct", False))

        return {
            "model_name": self.model.model_name,
            "total_tasks": total,
            "correct_answers": correct,
            "accuracy": correct / total if total > 0 else 0.0,
        }
