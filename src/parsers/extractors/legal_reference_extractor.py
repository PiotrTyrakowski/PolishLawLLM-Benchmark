from src.parsers.extractors.regex_patterns import RegexPatterns
from src.parsers.domain.legal_reference import LegalReference
from src.parsers.extractors.base_extractor import BaseExtractor


class LegalReferenceExtractor(BaseExtractor):
    """Extract components from legal basis strings."""

    def extract(self, legal_basis: str) -> LegalReference:
        """Extract legal basis from string."""
        article_match = RegexPatterns.article_capture_pattern().search(legal_basis)
        paragraph_match = RegexPatterns.paragraph_capture_pattern().search(legal_basis)
        point_match = RegexPatterns.point_capture_pattern().search(legal_basis)
        code_match = RegexPatterns.code_capture_pattern().search(legal_basis)

        if article_match is None or code_match is None:
            raise ValueError(f"Invalid legal basis: {legal_basis}")

        return LegalReference(
            article=article_match.group(1) if article_match else None,
            paragraph=paragraph_match.group(1) if paragraph_match else None,
            point=point_match.group(1) if point_match else None,
            code=code_match.group(1) if code_match else None,
        )
