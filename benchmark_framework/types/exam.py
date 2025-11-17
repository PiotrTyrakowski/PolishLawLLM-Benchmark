import json
from pathlib import Path
from benchmark_framework.types.task import Task
from benchmark_framework.constants import ENCODING


class Exam(Task):
    """
    Represents a legal exam question with multiple choice answers.

    Contains all the information needed for a single exam question including
    the question text, answer choices, correct answer, and legal basis.
    """

    def __init__(self, id, year, exam_type, question, choices, answer, legal_basis):
        super().__init__()
        self.id = id
        self.year = year
        self.exam_type = exam_type
        self.question = question
        self.choices = choices
        self.answer = answer
        self.legal_basis = legal_basis

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
        )

    def get_prompt(self) -> str:
        """
        Get the prompt for the exam. question and choices are in the context.
        """
        prompt = f"Pytanie: {self.question}\n\n"
        prompt += "Odpowiedzi:\n"
        for key, val in self.choices.items():
            prompt += f"{key}) {val}\n"
        return prompt


def load_exams(jsonl_path: Path) -> list[Exam]:
    exams = []
    with open(jsonl_path, encoding=ENCODING) as f:
        for line in f:
            obj = json.loads(line)
            exams.append(
                Exam(
                    obj["id"],
                    obj["year"],
                    obj["exam_type"],
                    obj["question"],
                    obj["choices"],
                    obj["answer"],
                    obj["legal_basis"],
                )
            )
    return exams
