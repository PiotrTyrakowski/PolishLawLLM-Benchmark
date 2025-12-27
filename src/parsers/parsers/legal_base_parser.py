import json
from pathlib import Path
from typing import Dict
from src.parsers.extractors.pdf_text_extractor import LegalBaseTextExtractor
from src.parsers.extractors.legal_content_extractor import LegalContentExtractor


class LegalBaseParser:
    """Orchestrates the reading of a Legal Code PDF and saving extracted articles."""

    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"File not found: {pdf_path}")
        self.reader = LegalBaseTextExtractor()
        self.extractor = LegalContentExtractor()

    def save_all_articles(self, output_path: Path) -> Dict[str, str]:
        """
        Extract all articles from the document and save them to a JSON file.
        Returns:
            Dict[str, str]: Dictionary mapping article numbers to their formatted text.
                           Keys are article numbers (e.g., '1', '10', '37a').
                           Values are the formatted article content.
        """
        raw_text = self.reader.extract_text(self.pdf_path, start_page=1)
        articles = self.extractor.extract(raw_text)

        assert output_path is not None

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)

        print(f"Saved {len(articles)} articles to {output_path}")
        return articles
