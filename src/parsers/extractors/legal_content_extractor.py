import re
from typing import Dict, Optional
from src.parsers.extractors.base_extractor import BaseExtractor
from src.common.text_formatter import TextFormatter


class LegalContentExtractor(BaseExtractor):
    """Extracts articles, paragraphs, and points from full legal code text."""

    def extract(self, text: str) -> Dict[str, str]:
        """Extracts all articles from the text."""
        articles = {}
        article_pattern = (
            r"Art\.\s+(\d+[a-z]?)\.\s+"  # Capture article number
            r"(.*?)"  # Capture article content (non-greedy)
            r"(?="  # Lookahead for:
            r"(?:Art\.\s+\d+[a-z]?\s*\.)|"  # Next article OR
            r"(?:Rozdział\s+[IVXLCDM]+)|"  # Chapter heading OR
            r"(?:Rozdział\s+\d+)|"
            r"(?:TYTUŁ\s+[IVXLCDM]+)|"  # Title heading OR
            r"(?:DZIAŁ\s+[IVXLCDM]+)|"  # Section heading OR
            r"$"  # End of document
            r")"
        )
        matches = re.finditer(article_pattern, text, re.DOTALL)
        for match in matches:
            articles[match.group(1)] = match.group(2)
        return articles

    @staticmethod
    def get_paragraph(article_text: str, paragraph_number: str) -> str:
        """Get specific paragraph from article."""
        paragraph_pattern = (
            rf"^(?:\s{{11}}\s*)?"
            rf"§\s+{paragraph_number}\.\s+"
            rf"(.+?)"
            rf"(?=^\s{{11}}\s*§\s+\d+[a-z]*\.|\Z)"
        )

        match = re.search(paragraph_pattern, article_text, re.MULTILINE | re.DOTALL)
        if not match:
            raise ValueError(f"Paragraph {paragraph_number} not found in the article")

        return TextFormatter.format_extracted_text(match.group(1))

    @staticmethod
    def get_point(
        article_text: str,
        point_number: str,
        paragraph_number: Optional[str] = None,
    ) -> str:
        """Get specific point from article or paragraph."""
        text = (
            LegalContentExtractor.get_paragraph(article_text, paragraph_number)
            if paragraph_number
            else article_text
        )

        point_pattern = rf"(?:^|\s){point_number}\)\s+(.+?)(?=(?:^|\s)\d+[a-z]*\)|\Z)"

        match = re.search(point_pattern, text, re.MULTILINE | re.DOTALL)
        if not match:
            raise ValueError(f"Point {point_number} not found in the article")

        return TextFormatter.format_extracted_text(match.group(1))
