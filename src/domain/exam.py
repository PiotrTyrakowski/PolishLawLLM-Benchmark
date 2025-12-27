from dataclasses import dataclass
from typing import List, Dict, TypedDict
from src.domain.task import Task


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


@dataclass
class ExamQuestion(Task):
    """
    Represents a legal exam question with multiple choice answers.
    Unified class replacing parsers.domain.ExamTask and benchmark_framework.types.Exam.
    """

    exam_type: str
    year: int
    question: str
    choices: Dict[str, str]
    answer: str
    legal_basis: str
    legal_basis_content: str

    def __init__(
        self,
        id: int,
        year: int,
        exam_type: str,
        question: str,
        choices: Dict[str, str],
        answer: str,
        legal_basis: str,
        legal_basis_content: str,
    ):
        super().__init__(id=id)
        self.year = year
        self.exam_type = exam_type
        self.question = question
        self.choices = choices
        self.answer = answer
        self.legal_basis = legal_basis
        self.legal_basis_content = legal_basis_content

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "year": self.year,
            "exam_type": self.exam_type,
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
            "legal_basis": self.legal_basis,
            "legal_basis_content": self.legal_basis_content,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ExamQuestion":
        return cls(
            id=data.get("id"),
            year=data.get("year"),
            exam_type=data.get("exam_type"),
            question=data.get("question"),
            choices=data.get("choices"),
            answer=data.get("answer"),
            legal_basis=data.get("legal_basis"),
            legal_basis_content=data.get("legal_basis_content"),
        )

    def get_prompt(self) -> str:
        prompt = f"Pytanie: {self.question}\n\n"
        prompt += "Odpowiedzi:\n"
        for key, val in self.choices.items():
            prompt += f"{key}) {val}\n"
        return prompt

    def get_year(self) -> int:
        return self.year


@dataclass
class Exam:
    """
    Represents a collection of exam questions (an entire exam).
    """

    exam_type: str
    year: int
    tasks: List[ExamQuestion]

    def to_jsonl_data(self) -> List[Dict]:
        data = []
        for t in self.tasks:
            d = t.to_dict()
            # Ensure consistency
            d["exam_type"] = self.exam_type
            d["year"] = self.year
            data.append(d)
        return data
