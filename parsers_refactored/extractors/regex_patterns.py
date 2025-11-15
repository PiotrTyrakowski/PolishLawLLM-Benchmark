import re


class RegexPatterns:
    """Centralized regex patterns following DRY principle."""

    # Legal basis components
    ARTICLE_PREFIX: str = r"art\."
    ENTITY_ID: str = r"\d+[a-z]*"
    CODE_ABBREVIATION: str = r"(?:[a-z\.]+|k\.r\.\s+i\s+o\.|k\.\s+r\.\s+i\s+o\.)"

    @classmethod
    def point_pattern(cls) -> str:
        return rf"pkt\s+{cls.ENTITY_ID}"

    @classmethod
    def paragraph_pattern(cls) -> str:
        return rf"§\s+{cls.ENTITY_ID}"

    @classmethod
    def full_legal_basis_pattern(cls) -> re.Pattern:
        """Complete legal basis regex pattern."""
        pattern = (
            rf"({cls.ARTICLE_PREFIX}\s+{cls.ENTITY_ID}"
            rf"(?:\s+{cls.point_pattern()})?"
            rf"(?:\s+{cls.paragraph_pattern()})?"
            rf"(?:\s+{cls.point_pattern()})?"
            rf"\s+{cls.CODE_ABBREVIATION})"
        )
        return re.compile(pattern, re.IGNORECASE | re.MULTILINE)

    @classmethod
    def answer_pattern(cls) -> re.Pattern:
        """Pattern for parsing answers from PDF."""
        legal_basis = (
            rf"({cls.ARTICLE_PREFIX}\s+{cls.ENTITY_ID}"
            rf"(?:\s+{cls.point_pattern()})?"
            rf"(?:\s+{cls.paragraph_pattern()})?"
            rf"(?:\s+{cls.point_pattern()})?"
            rf"\s+{cls.CODE_ABBREVIATION})"
        )
        separator = r"\s*\n\s*"
        question_number = r"(\d+)\."
        answer_letter = r"([A-C])"

        pattern = rf"{legal_basis}{separator}{question_number}\s+{answer_letter}"
        return re.compile(pattern, re.IGNORECASE | re.MULTILINE)

    @classmethod
    def question_pattern(cls) -> re.Pattern:
        """Pattern for parsing questions from PDF."""
        pattern = (
            r"(\d+)\.\s+(.*?)\s+"
            r"A\.\s+(.*?)\s+"
            r"B\.\s+(.*?)\s+"
            r"C\.\s+(.*?)"
            r"(?=\n\s*\d+\.\s+|\Z)"
        )
        return re.compile(pattern, re.DOTALL | re.MULTILINE)

    @classmethod
    def article_capture_pattern(cls) -> re.Pattern:
        """Pattern for capturing article number from legal basis."""
        return re.compile(rf"{cls.ARTICLE_PREFIX}\s+({cls.ENTITY_ID})", re.IGNORECASE)

    @classmethod
    def paragraph_capture_pattern(cls) -> re.Pattern:
        """Pattern for capturing paragraph number from legal basis."""
        return re.compile(rf"§\s+({cls.ENTITY_ID})", re.IGNORECASE)

    @classmethod
    def point_capture_pattern(cls) -> re.Pattern:
        """Pattern for capturing point number from legal basis."""
        return re.compile(rf"pkt\s+({cls.ENTITY_ID})", re.IGNORECASE)

    @classmethod
    def code_capture_pattern(cls) -> re.Pattern:
        """Pattern for capturing code abbreviation from legal basis."""
        return re.compile(rf"({cls.CODE_ABBREVIATION})$", re.IGNORECASE)
