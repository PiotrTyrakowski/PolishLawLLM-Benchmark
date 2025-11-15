from dataclasses import dataclass
from typing import Dict


@dataclass
class Answer:
    question_id: int
    correct_answer: str
    legal_basis: str

    def to_dict(self) -> Dict:
        return {
            "question_id": self.question_id,
            "correct_answer": self.correct_answer,
            "legal_basis": self.legal_basis,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Answer":
        return cls(
            question_id=data["question_id"],
            correct_answer=data["correct_answer"],
            legal_basis=data["legal_basis"],
        )
