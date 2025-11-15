from dataclasses import dataclass
from typing import Dict


@dataclass
class Question:
    """Domain model for an exam question."""

    number: int
    text: str
    option_a: str
    option_b: str
    option_c: str

    def to_dict(self) -> Dict:
        return {
            "question_number": self.number,
            "question": self.text,
            "A": self.option_a,
            "B": self.option_b,
            "C": self.option_c,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Question":
        return cls(
            number=data["question_number"],
            text=data["question"],
            option_a=data["A"],
            option_b=data["B"],
            option_c=data["C"],
        )
