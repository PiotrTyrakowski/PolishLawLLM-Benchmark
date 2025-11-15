from dataclasses import dataclass
from typing import List, Dict
from domain.question import Question
from domain.answer import Answer
from domain.legal_reference import LegalReference


@dataclass
class ExamQuestion:
    question: Question
    correct_answer: str
    legal_bases: List[LegalReference]

    def to_dict(self) -> Dict:
        result = self.question.to_dict()
        result["correct_answer"] = self.correct_answer
        result["legal_bases"] = [lb.to_dict() for lb in self.legal_bases]
        return result


@dataclass
class Exam:
    exam_type: str
    year: int
    questions: List[ExamQuestion]

    @property
    def total_questions(self) -> int:
        return len(self.questions)

    def to_jsonl_data(self) -> List[Dict]:
        return [q.to_dict() for q in self.questions]
