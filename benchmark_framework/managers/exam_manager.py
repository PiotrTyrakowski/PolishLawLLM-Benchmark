import json
from pathlib import Path

from benchmark_framework.constants import ENCODING
from benchmark_framework.types.exam import Exam
from benchmark_framework.utils import extract_answer_from_response
from benchmark_framework.managers.base_manager import BaseManager


class ExamManager(BaseManager):
    """
    Manager for handling legal exam benchmark evaluations.
    """

    def __init__(self, model_name: str):
        super().__init__(model_name, "exams")

    def get_tasks(self) -> list[Exam]:
        return self.tasks
        
    def get_result(self, exam: Exam, model_response: str, model_tools: str) -> dict:
        extracted_answer = extract_answer_from_response(model_response)
        is_correct = extracted_answer == exam.answer
        
        result = {
            "year": exam.year,
            "exam_type": exam.exam_type,
            "question": exam.question,
            "choices": exam.choices,
            "answer": exam.answer,
            "legal_basis": exam.legal_basis,
            "model_name": self.model_name,
            "model_tools": model_tools if model_tools is not None else "None",
            "model_response": model_response,
            "extracted_answer": extracted_answer,
            "is_correct": is_correct
        }

        self.results.append(result)
        return result
    
    