import json
from pathlib import Path
from typing import TypedDict, Union

from benchmark_framework.types.task import Task
from benchmark_framework.constants import ENCODING


class ExamResult(TypedDict):
    id: int
    year: int
    exam_type: str
    question: str
    choices: dict[str, str]
    correct_answer: str
    legal_basis: str
    legal_basis_content: str

    model_name: str
    model_response: str
    model_config: str
    model_answer: str
    model_legal_basis: str
    model_legal_basis_content: str


class Exam(Task):
    """
    Represents a legal exam question with multiple choice answers.
    """

    def __init__(
        self,
        id,
        year,
        exam_type,
        question,
        choices,
        answer,
        legal_basis,
        legal_basis_content,
    ):
        super().__init__(id=id)
        self.year = year
        self.exam_type = exam_type
        self.question = question
        self.choices = choices
        self.answer = answer
        self.legal_basis = legal_basis
        self.legal_basis_content = legal_basis_content

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data["id"],
            data["year"],
            data["exam_type"],
            data["question"],
            data["choices"],
            data["answer"],
            data["legal_basis"],
            data["legal_basis_content"],
        )

    def get_prompt(self) -> str:
        prompt = f"Pytanie: {self.question}\n\n"
        prompt += "Odpowiedzi:\n"
        for key, val in self.choices.items():
            prompt += f"{key}) {val}\n"
        return prompt

    def get_year(self) -> int:
        return self.year


def load_exams(jsonl_path: Path) -> list[Exam]:
    exams = []
    with open(jsonl_path, encoding=ENCODING) as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            exams.append(Exam.from_dict(obj))
    return exams
