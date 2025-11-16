from dataclasses import dataclass
from typing import Dict


@dataclass
class Answer:
    question_id: int
    answer: str
    legal_basis: str

    def to_dict(self) -> Dict:
        return {
            "question_id": self.question_id,
            "answer": self.answer,
            "legal_basis": self.legal_basis,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Answer":
        return cls(
            question_id=data["question_id"],
            answer=data["answer"],
            legal_basis=data["legal_basis"],
        )
