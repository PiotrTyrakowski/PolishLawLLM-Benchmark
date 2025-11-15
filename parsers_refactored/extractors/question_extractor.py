from typing import List, Dict, Any
import re
from parsers_refactored.extractors.base_extractor import BaseExtractor
from parsers_refactored.extractors.regex_patterns import RegexPatterns
from parsers_refactored.domain.question import Question


class QuestionExtractor(BaseExtractor):
    """Extract questions from PDF text."""

    def extract(self, text: str) -> List[Question]:
        """Extract questions from text using regex pattern."""
        questions = []
        matches = list(RegexPatterns.question_pattern().finditer(text))

        for match in matches:
            try:
                question_num = int(match.group(1))
            except ValueError:
                continue

            questions.append(
                Question(
                    id=question_num,
                    text=self._clean_text(match.group(2)),
                    option_a=self._clean_text(match.group(3)),
                    option_b=self._clean_text(match.group(4)),
                    option_c=self._clean_text(match.group(5)),
                )
            )

        return questions

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean and normalize text."""
        return re.sub(r"\s+", " ", text.strip())
