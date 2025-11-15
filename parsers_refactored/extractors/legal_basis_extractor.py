from typing import Dict, Optional
from parsers_refactored.extractors.regex_patterns import RegexPatterns


class LegalBasisExtractor:
    """Extract components from legal basis strings."""

    def parse(self, legal_basis: str) -> Dict[str, Optional[str]]:
        """Parse legal basis string into components."""
        article_match = RegexPatterns.article_capture_pattern().search(legal_basis)
        paragraph_match = RegexPatterns.paragraph_capture_pattern().search(legal_basis)
        point_match = RegexPatterns.point_capture_pattern().search(legal_basis)
        code_match = RegexPatterns.code_capture_pattern().search(legal_basis)

        return {
            "article_number": article_match.group(1) if article_match else None,
            "paragraph_number": paragraph_match.group(1) if paragraph_match else None,
            "point_number": point_match.group(1) if point_match else None,
            "code_abbreviation": code_match.group(1) if code_match else None,
        }

    @staticmethod
    def format_code_abbreviation(abbreviation: str) -> str:
        """Format code abbreviation for file lookup."""
        return abbreviation.replace(".", "").replace(" ", "").lower()
