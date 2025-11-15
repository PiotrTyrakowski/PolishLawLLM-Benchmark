from typing import List, Dict, Any
import re
from parsers_refactored.extractors.base_extractor import BaseExtractor
from parsers_refactored.extractors.regex_patterns import RegexPatterns


class QuestionExtractor(BaseExtractor):
    """Extract questions from PDF text."""

    def extract(self, text: str) -> List[Dict[str, Any]]:
        """Extract questions from text using regex pattern."""
        questions = []
        matches = list(RegexPatterns.question_pattern().finditer(text))

        for match in matches:
            try:
                question_num = int(match.group(1))
            except ValueError:
                continue

            questions.append(
                {
                    "question_number": question_num,
                    "question": self._clean_text(match.group(2)),
                    "A": self._clean_text(match.group(3)),
                    "B": self._clean_text(match.group(4)),
                    "C": self._clean_text(match.group(5)),
                }
            )

        return questions

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean and normalize text."""
        return re.sub(r"\s+", " ", text.strip())
