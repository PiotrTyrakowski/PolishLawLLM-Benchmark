from typing import List, Tuple
from pathlib import Path
from parsers_refactored.parsers.base import BaseParser
from parsers_refactored.domain.answer import Answer
from parsers_refactored.extractors.answer_extractor import AnswerExtractor
from parsers_refactored.utils.pdf_utils import PDFTextExtractor


class PDFAnswerParser(BaseParser[Answer]):
    """Parse answers from PDF files."""

    def __init__(
        self,
        file_path: Path,
        extractor: AnswerExtractor = None,
        pdf_reader: PDFTextExtractor = None,
    ):
        super().__init__(file_path)
        self.extractor = extractor or AnswerExtractor()
        self.pdf_reader = pdf_reader or PDFTextExtractor()

    def parse(self) -> List[Answer]:
        """Extract answers from PDF."""
        text = self.pdf_reader.extract_text(self.file_path, start_page=1)
        return self.extractor.extract(text)

    def validate(self, answer: Answer) -> Tuple[bool, List[str]]:
        """Validate answer completeness."""
        errors = []

        if answer.correct_answer not in ["A", "B", "C"]:
            errors.append(f"Invalid answer: {answer.correct_answer}")

        if not answer.legal_basis:
            errors.append("Missing legal basis")

        return len(errors) == 0, errors
