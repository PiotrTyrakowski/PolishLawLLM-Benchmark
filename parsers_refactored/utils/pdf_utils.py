from pathlib import Path
from typing import Optional, Callable
import pdfplumber


class PDFTextExtractor:
    """Extract text from PDF files with filtering capabilities."""

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

        return "\n".join(text_parts)

    @staticmethod
    def _make_char_filter(min_size: float = 9.0) -> Callable:
        """Create character filter function."""

        def char_filter(char):
            if "size" in char and char["size"] < min_size:
                return False
            return True

        return char_filter
