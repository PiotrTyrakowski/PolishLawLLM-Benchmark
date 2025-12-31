from typing import List
from src.parsers.extractors.base_extractor import BaseExtractor
from src.parsers.extractors.regex_patterns import RegexPatterns
from src.parsers.domain.question import Question
from src.common.text_formatter import TextFormatter


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
                    text=TextFormatter.clean_whitespace(match.group(2)),
                    option_a=TextFormatter.clean_whitespace(match.group(3)),
                    option_b=TextFormatter.clean_whitespace(match.group(4)),
                    option_c=TextFormatter.clean_whitespace(match.group(5)),
                )
            )

        return questions
