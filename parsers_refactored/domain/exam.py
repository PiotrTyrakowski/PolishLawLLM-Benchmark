from dataclasses import dataclass
from typing import List, Dict
from parsers_refactored.domain.question import Question
from parsers_refactored.domain.answer import Answer


@dataclass
class ExamTask:
    question: Question
    answer: Answer
    legal_basis_content: str

    def to_dict(self, exam_type: str = None, year: int = None) -> Dict:
        result = self.question.to_dict()
        result["correct_answer"] = self.answer.correct_answer
        result["legal_basis"] = self.answer.legal_basis
        result["legal_basis_content"] = self.legal_basis_content
        if exam_type is not None:
            result["exam_type"] = exam_type
        if year is not None:
            result["year"] = year
        return result

    @classmethod
    def from_dict(cls, data: Dict) -> "ExamTask":
        question = Question.from_dict(data)
        answer = Answer.from_dict(data)
        legal_basis_content = data.get("legal_basis_content")
        if legal_basis_content is None:
            raise ValueError("legal_basis_content is required")
        return cls(
            question=question,
            answer=answer,
            legal_basis_content=legal_basis_content,
        )


@dataclass
class Exam:
    exam_type: str
    year: int
    tasks: List[ExamTask]

    def to_jsonl_data(self) -> List[Dict]:
        return [t.to_dict(exam_type=self.exam_type, year=self.year) for t in self.tasks]
