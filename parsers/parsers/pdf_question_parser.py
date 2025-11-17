from typing import List, Tuple
from pathlib import Path
from parsers.parsers.base import BaseParser
from parsers.domain.question import Question
from parsers.extractors.question_extractor import QuestionExtractor
from parsers.utils.pdf_utils import PDFTextExtractor


class PDFQuestionParser(BaseParser[Question]):
    """Parse questions from PDF files."""

    def __init__(
        self,
        file_path: Path,
        extractor: QuestionExtractor = None,
        pdf_reader: PDFTextExtractor = None,
    ):
        super().__init__(file_path)
        self.extractor = extractor or QuestionExtractor()
        self.pdf_reader = pdf_reader or PDFTextExtractor()

    def parse(self) -> List[Question]:
        text = self.pdf_reader.extract_text(self.file_path, start_page=2)
        return self.extractor.extract(text)

    def validate(self, question: Question) -> Tuple[bool, List[str]]:
        errors = []

        if not question.text or len(question.text) < 10:
            errors.append("Question text too short")

        for opt_name, opt_value in [
            ("A", question.option_a),
            ("B", question.option_b),
            ("C", question.option_c),
        ]:
            if not opt_value:
                errors.append(f"Missing option {opt_name}")

        return len(errors) == 0, errors
