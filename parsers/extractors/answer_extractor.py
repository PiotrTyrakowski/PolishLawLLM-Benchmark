from typing import List, Dict, Any
import re
from parsers.domain.answer import Answer
from parsers.extractors.base_extractor import BaseExtractor
from parsers.extractors.regex_patterns import RegexPatterns


class AnswerExtractor(BaseExtractor):
    """Extract answers from PDF text."""

    def extract(self, text: str) -> List[Answer]:
        """Extract answers from text using regex pattern."""
        answers = []
        matches = list(RegexPatterns.answer_pattern().finditer(text))

        for match in matches:
            try:
                question_number = int(match.group(1))
            except ValueError:
                continue

            correct_answer = match.group(2).strip()
            legal_basis = re.sub(r"\s+", " ", match.group(3).strip())

            answers.append(
                Answer(
                    question_id=question_number,
                    answer=correct_answer,
                    legal_basis=legal_basis,
                )
            )

        return answers
