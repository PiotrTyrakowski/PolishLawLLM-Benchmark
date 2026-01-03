import re
from typing import Dict, Optional
from src.parsers.extractors.base_extractor import BaseExtractor
from src.common.text_formatter import TextFormatter
from src.parsers.extractors.regex_patterns import RegexPatterns

PARAGRAPH_INDENT_SPACES = 10


class LegalContentExtractor(BaseExtractor):
    """Extracts articles, paragraphs, and points from full legal code text."""

    def extract(self, text: str) -> Dict[str, str]:
        """Extracts all articles from the text."""
        articles = {}
        article_pattern = (
            rf"Art\.\s+({RegexPatterns.ENTITY_ID})\.\s+"  # Capture article number
            r"(.*?)"  # Capture article content (non-greedy)
            r"(?="  # Lookahead for:
            rf"(?:Art\.\s+{RegexPatterns.ENTITY_ID}\s*\.)|"  # Next article OR
            r"(?:KSIĘGA\s+[A-Z]+)|"  # Book heading OR
            r"(?:CZĘŚĆ\s+[A-Z]+)|"  # Part heading OR
            r"(?:TYTUŁ\s+[IVXLCDM]+)|"  # Title heading OR
            r"(?:DZIAŁ\s+[IVXLCDM]+)|"  # Section heading OR
            r"(?:Rozdział\s+[IVXLCDM\d]+)|"  # Chapter heading OR
            r"(?:Oddział\s+[IVXLCDM\d]+)|"  # Chapter heading OR
            r"$"  # End of document
            r")"
        )
        matches = re.finditer(article_pattern, text, re.DOTALL)
        for match in matches:
            articles[match.group(1)] = match.group(2).strip()
        return articles

    @staticmethod
    def _get_raw_paragraph(article_text: str, paragraph_number: str) -> str:
        """Get specific paragraph from article."""
        safe_paragraph_number = re.escape(paragraph_number)
        paragraph_pattern = (
            rf"^(?:\s{{{PARAGRAPH_INDENT_SPACES}}}\s*)?"
            rf"§\s+{safe_paragraph_number}\.\s+"
            rf"(.+?)"
            rf"(?=^\s{{{PARAGRAPH_INDENT_SPACES}}}\s*§\s+{RegexPatterns.ENTITY_ID}\.|\Z)"
        )

        match = re.search(paragraph_pattern, article_text, re.MULTILINE | re.DOTALL)
        if not match:
            raise ValueError(f"Paragraph {paragraph_number} not found in the article")

        return match.group(1)

    @staticmethod
    def get_paragraph(
        article_text: str,
        paragraph_number: str,
    ) -> str:
        """Get specific paragraph from article."""
        raw_paragraph = LegalContentExtractor._get_raw_paragraph(
            article_text, paragraph_number
        )
        return TextFormatter.format_extracted_text(raw_paragraph)

    @staticmethod
    def get_point(
        article_text: str,
        point_number: str,
        paragraph_number: Optional[str] = None,
    ) -> str:
        """Get specific point from article or paragraph."""
        text = (
            LegalContentExtractor._get_raw_paragraph(article_text, paragraph_number)
            if paragraph_number
            else article_text
        )

        safe_point_number = re.escape(point_number)
        point_pattern = rf"(?:^|\s){safe_point_number}\)\s+(.+?)(?=(?:^|\n)\s*{RegexPatterns.ENTITY_ID}\)|\Z)"

        match = re.search(point_pattern, text, re.MULTILINE | re.DOTALL)
        if not match:
            raise ValueError(f"Point {point_number} not found in the article")

        return TextFormatter.format_extracted_text(match.group(1))
