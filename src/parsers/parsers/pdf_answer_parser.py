from typing import List, Tuple
from pathlib import Path
from src.parsers.parsers.base import BaseParser
from src.parsers.domain.answer import Answer
from src.parsers.extractors.answer_extractor import AnswerExtractor
from src.parsers.extractors.pdf_table_extractor import PdfTableExtractor


class PDFAnswerParser(BaseParser[Answer]):
    """Parse answers from PDF files."""

    def __init__(
        self,
        file_path: Path,
        extractor: AnswerExtractor = None,
        pdf_reader: PdfTableExtractor = None,
    ):
        super().__init__(file_path)
        self.extractor = extractor or AnswerExtractor()
        self.pdf_reader = pdf_reader or PdfTableExtractor()

    def parse(self) -> List[Answer]:
        """Extract answers from PDF."""
        text = self.pdf_reader.extract_text(self.file_path, start_page=1)
        return self.extractor.extract(text)

    def validate(self, answer: Answer) -> Tuple[bool, List[str]]:
        """Validate answer completeness."""
        errors = []

        if answer.answer not in ["A", "B", "C"]:
            errors.append(f"Invalid answer: {answer.answer}")

        if not answer.legal_basis:
            errors.append("Missing legal basis")

        return len(errors) == 0, errors
