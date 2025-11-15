from typing import List, Dict, Any
import re
from parsers_refactored.extractors.base_extractor import BaseExtractor
from parsers_refactored.extractors.regex_patterns import RegexPatterns


class AnswerExtractor(BaseExtractor):
    """Extract answers from PDF text."""

    def extract(self, text: str) -> List[Dict[str, Any]]:
        """Extract answers from text using regex pattern."""
        answers = []
        matches = list(RegexPatterns.answer_pattern().finditer(text))

        for match in matches:
            try:
                question_number = int(match.group(2))
            except ValueError:
                continue

            legal_basis = re.sub(r"\s+", " ", match.group(1).strip())
            correct_answer = match.group(3).strip()

            answers.append(
                {
                    "question_number": question_number,
                    "correct_answer": correct_answer,
                    "legal_basis": legal_basis,
                }
            )

        return answers
