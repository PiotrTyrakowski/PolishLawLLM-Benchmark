import re
import json
from pathlib import Path
from typing import Optional, Dict
from src.parsers.extractors.pdf_text_extractor import LegalBaseTextExtractor
from src.parsers.utils.text_utils import TextFormatter


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
            LegalBaseParser.get_paragraph(article_text, paragraph_number)
            if paragraph_number
            else article_text
        )

        point_pattern = rf"(?:^|\s){point_number}\)\s+(.+?)(?=(?:^|\s)\d+[a-z]*\)|\Z)"

        match = re.search(point_pattern, text, re.MULTILINE | re.DOTALL)
        if not match:
            raise ValueError(f"Point {point_number} not found in the article")

        return TextFormatter.format_extracted_text(match.group(1))

    def save_all_articles(self, output_path: Optional[Path] = None) -> Dict[str, str]:
        """
        Extract all articles from the document and save them to a JSON file.
        Returns:
            Dict[str, str]: Dictionary mapping article numbers to their formatted text.
                           Keys are article numbers (e.g., '1', '10', '37a').
                           Values are the formatted article content.
        """
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

        matches = re.finditer(article_pattern, self.content, re.DOTALL)

        for match in matches:
            article_num = match.group(1)
            article_text = match.group(2)
            if article_text:
                articles[article_num] = article_text

        if output_path is None:
            output_path = self.pdf_path.parent / f"{self.pdf_path.stem}_articles.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)

        print(f"Saved {len(articles)} articles to {output_path}")

        return articles
