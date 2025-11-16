from pathlib import Path
from typing import Optional
import re
from parsers.utils.pdf_utils import LegalBaseTextExtractor
from parsers.utils.text_utils import TextFormatter


class LegalBaseParser:
    """Parse legal code documents to extract article content."""

    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"File not found: {pdf_path}")
        self.pdf_reader = LegalBaseTextExtractor()
        self.formatter = TextFormatter()
        self.content = self._extract_full_text()

    def _extract_full_text(self) -> str:
        return self.pdf_reader.extract_text(self.pdf_path, start_page=1)

    def get_article(self, article_number: str) -> str:
        raw_content = self._get_raw_article(article_number)
        return self.formatter.format_extracted_text(raw_content)

    def get_paragraph(self, article_number: str, paragraph_number: str) -> str:
        """Get specific paragraph from article."""
        article_text = self._get_raw_article(article_number)

        paragraph_pattern = (
            rf"^(?:\s{{11}}\s*)?"
            rf"§\s+{paragraph_number}\.\s+"
            rf"(.+?)"
            rf"(?=^\s{{11}}\s*§\s+\d+[a-z]*\.|\Z)"
        )

        match = re.search(paragraph_pattern, article_text, re.MULTILINE | re.DOTALL)
        if not match:
            raise ValueError(
                f"Paragraph {paragraph_number} not found in article {article_number}"
            )

        return self.formatter.format_extracted_text(match.group(1))

    def get_point(
        self,
        article_number: str,
        point_number: str,
        paragraph_number: Optional[str] = None,
    ) -> str:
        """Get specific point from article or paragraph."""
        text = (
            self.get_paragraph(article_number, paragraph_number)
            if paragraph_number
            else self.get_article(article_number)
        )

        point_pattern = rf"(?:^|\s){point_number}\)\s+(.+?)(?=(?:^|\s)\d+[a-z]*\)|\Z)"

        match = re.search(point_pattern, text, re.MULTILINE | re.DOTALL)
        if not match:
            raise ValueError(
                f"Point {point_number} not found in article {article_number}"
            )

        return self.formatter.format_extracted_text(match.group(1))

    def _get_raw_article(self, article_number: str) -> str:
        """Extract raw article text from content."""
        article_pattern = (
            rf"Art\.\s+{article_number}[a-z]?\.\s+"
            rf"(.*?)"
            rf"(?=(?:Art\.\s+\d+[a-z]?\.|Rozdział\s+[IVXLCDM]+|$))"
        )
        match = re.search(article_pattern, self.content, re.DOTALL)
        if not match:
            raise ValueError(f"Article {article_number} not found")
        return match.group(1)
