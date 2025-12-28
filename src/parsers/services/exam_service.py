from src.common.domain.exam import Exam
from src.parsers.parsers.base import BaseParser
from src.parsers.services.legal_basis_service import LegalBasisService


class ExamService:
    """Orchestrates exam parsing workflow."""

    def __init__(
        self,
        question_parser: BaseParser,
        answer_parser: BaseParser,
        legal_basis_service: LegalBasisService,
    ):
        self.question_parser = question_parser
        self.answer_parser = answer_parser
        self.legal_basis_service = legal_basis_service

    def process_exam(self, exam_type: str, year: int) -> Exam:
        """Parse, and combine exam data."""
        questions = self.question_parser.parse()
        answers = self.answer_parser.parse()
        exam_tasks = self.legal_basis_service.enrich_with_legal_content(
            questions, answers, exam_type, year
        )
        exam = Exam(year=year, exam_type=exam_type, tasks=exam_tasks)
        return exam
