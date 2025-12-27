from pathlib import Path
from typing import Callable
import pdfplumber
from src.parsers.pdf_readers.base_pdf_reader import BasePdfReader


class PdfTextReader(BasePdfReader):
    """Standard reader for Exam Question PDFs."""

    def read(self, pdf_path: Path, start_page: int = 1) -> str:
        return self.extract_text(pdf_path, start_page)

    def extract_text(
        self, pdf_path: Path, start_page: int = 1, min_char_size: float = 9.0
    ) -> str:
        """
        Extract text from PDF starting from specified page.

        Args:
            pdf_path: Path to PDF file
            start_page: Page number to start extraction (1-indexed)
            min_char_size: Minimum character size to include

        Returns:
            Extracted text
        """
        text_parts = []

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[start_page - 1 :]:
                filter_fn = self._make_char_filter(min_size=min_char_size)
                filtered_page = page.filter(filter_fn)
                page_text = filtered_page.extract_text(
                    x_tolerance=3, y_tolerance=3, layout=True
                )
                if page_text:
                    text_parts.append(page_text)

        result = "\n".join(text_parts)
        result = self._filter_exam_headers(result)
        return result

    @staticmethod
    def _make_char_filter(min_size: float = 9.0) -> Callable:
        """Create character filter function."""

        def char_filter(char):
            if "size" in char and char["size"] < min_size:
                return False
            return True

        return char_filter

    @staticmethod
    def _filter_exam_headers(text: str) -> str:
        """Filter out any lines containing the exam header text."""
        lines = text.split("\n")
        filtered_lines = [
            line
            for line in lines
            if "EGZAMIN WSTĘPNY DLA KANDYDATÓW" not in line
            and "EGZAMIN KONKURSOWY" not in line
        ]
        return "\n".join(filtered_lines)
