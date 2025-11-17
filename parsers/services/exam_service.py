from pathlib import Path
from typing import List
from parsers.domain.exam import Exam
from parsers.domain.question import Question
from parsers.domain.answer import Answer
from parsers.parsers.base import BaseParser
from parsers.services.legal_basis_service import LegalBasisService


class ExamService:
    """Orchestrates exam parsing workflow."""

    def __init__(
        self,
        question_parser: BaseParser[Question],
        answer_parser: BaseParser[Answer],
        legal_basis_service: LegalBasisService,
    ):
        self.question_parser = question_parser
        self.answer_parser = answer_parser
        self.legal_basis_service = legal_basis_service

    def process_exam(self, exam_type: str, year: int) -> Exam:
        """Parse, and combine exam data."""
        # Parse
        questions = self.question_parser.parse()
        answers = self.answer_parser.parse()

        print(f"  Found {len(questions)} questions and {len(answers)} answers")

        # Enrich with legal basis content
        exam_tasks = self.legal_basis_service.enrich_with_legal_content(
            questions, answers
        )

        # Create domain aggregate
        exam = Exam(year=year, exam_type=exam_type, tasks=exam_tasks)

        return exam
