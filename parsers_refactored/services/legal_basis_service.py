from pathlib import Path
from typing import Dict, List
from parsers_refactored.domain.question import Question
from parsers_refactored.domain.answer import Answer
from parsers_refactored.domain.exam import ExamTask
from parsers_refactored.parsers.legal_base_parser import LegalBaseParser
from parsers_refactored.extractors.legal_basis_extractor import LegalBasisExtractor


class LegalBasisService:
    """Manage legal basis extraction and enrichment."""

    def __init__(self, legal_base_dir: Path):
        self.legal_base_dir = legal_base_dir
        self.parsers: Dict[str, LegalBaseParser] = {}
        self.basis_extractor = LegalBasisExtractor()
        self._initialize_parsers()

    def _initialize_parsers(self) -> None:
        """Initialize legal code parsers."""
        pdf_files = list(self.legal_base_dir.glob("*.pdf"))
        for pdf_file in pdf_files:
            code_name = pdf_file.stem.lower()
            self.parsers[code_name] = LegalBaseParser(pdf_file)

    def enrich_with_legal_content(
        self, questions: List[Question], answers: List[Answer]
    ) -> List[ExamTask]:
        """Combine questions with answers and legal basis content."""
        answer_dict = {a.question_number: a for a in answers}
        enriched_questions = []

        for question in questions:
            answer = answer_dict.get(question.number)
            if not answer:
                continue

            try:
                content = self._extract_legal_content(answer.legal_basis)
                enriched_questions.append(
                    ExamTask(
                        question=question, answer=answer, legal_basis_content=content
                    )
                )
            except Exception as e:
                print(f"  Warning: {e} for question {question.number}")
                continue

        return enriched_questions

    def _extract_legal_content(self, legal_basis: str) -> str:
        """Extract content for a legal basis reference."""
        components = self.basis_extractor.parse(legal_basis)

        article_num = components["article_number"]
        paragraph_num = components["paragraph_number"]
        point_num = components["point_number"]
        code_abbr = components["code_abbreviation"]

        if not article_num or not code_abbr:
            raise ValueError(f"Invalid legal basis: {legal_basis}")

        formatted_code = self.basis_extractor.format_code_abbreviation(code_abbr)
        parser = self.parsers.get(formatted_code)

        if not parser:
            raise ValueError(f"Parser not found for code: {formatted_code}")

        # Extract based on components present
        if paragraph_num and point_num:
            return parser.get_point(article_num, point_num, paragraph_num)
        elif paragraph_num:
            return parser.get_paragraph(article_num, paragraph_num)
        elif point_num:
            return parser.get_point(article_num, point_num)
        else:
            return parser.get_article(article_num)
