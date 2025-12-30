import json
from pathlib import Path
from typing import Dict, List
from src.parsers.domain.question import Question
from src.parsers.domain.answer import Answer
from src.common.domain.exam import ExamQuestion
from src.parsers.extractors.legal_reference_extractor import LegalReferenceExtractor
from src.parsers.extractors.legal_content_extractor import LegalContentExtractor
from src.common.text_formatter import TextFormatter


class LegalBasisService:
    """Manage legal basis extraction using pre-generated corpus files."""

    def __init__(self, corpus_year_dir: Path):
        self.corpus_year_dir = corpus_year_dir
        self.corpuses: Dict[str, Dict[str, str]] = {}
        self.basis_extractor = LegalReferenceExtractor()
        self._load_corpuses()

    def _load_corpuses(self) -> None:
        json_files = list(self.corpus_year_dir.glob("*.json"))
        for json_file in json_files:
            code_name = json_file.stem.lower()
            with open(json_file, "r", encoding="utf-8") as f:
                self.corpuses[code_name] = json.load(f)

    def enrich_with_legal_content(
        self,
        questions: List[Question],
        answers: List[Answer],
        exam_type: str,
        year: int,
    ) -> List[ExamQuestion]:
        """Combine questions with answers and legal basis content."""
        answer_dict = {a.question_id: a for a in answers}
        enriched_questions = []

        for question in questions:
            answer = answer_dict.get(question.id)
            if not answer:
                continue

            try:
                content = self._extract_legal_content(answer.legal_basis)
                choices = {
                    "A": question.option_a,
                    "B": question.option_b,
                    "C": question.option_c,
                }
                enriched_questions.append(
                    ExamQuestion(
                        id=question.id,
                        year=year,
                        exam_type=exam_type,
                        question=question.text,
                        choices=choices,
                        answer=answer.answer,
                        legal_basis=answer.legal_basis,
                        legal_basis_content=content,
                    )
                )
            except Exception as e:
                print(
                    f"  Warning: {e} for question {question.id} and {answer.legal_basis}"
                )
                continue

        return enriched_questions

    def _extract_legal_content(self, legal_basis: str) -> str:
        """Extract content for a legal basis reference."""
        legal_reference = self.basis_extractor.extract(legal_basis)

        article_num = legal_reference.article
        paragraph_num = legal_reference.paragraph
        point_num = legal_reference.point
        code_abbr = legal_reference.code

        if (
            (article_num and "^" in article_num)
            or (paragraph_num and "^" in paragraph_num)
            or (point_num and "^" in point_num)
        ):
            raise ValueError(
                f"Warning: Superscript detected in article number {legal_basis}. Skipping extraction."
            )

        if not article_num or not code_abbr:
            raise ValueError(f"Invalid legal basis: {legal_basis}")

        formatted_code = TextFormatter.format_code_abbreviation(code_abbr)
        corpus = self.corpuses.get(formatted_code)

        if not corpus:
            raise ValueError(f"Corpus not found for code: {formatted_code}")

        article_text = corpus.get(article_num)
        if not article_text:
            raise ValueError(f"Article {article_num} not found in {formatted_code}")

        # Extract based on components present
        if point_num:
            return LegalContentExtractor.get_point(
                article_text, point_num, paragraph_num
            )
        elif paragraph_num:
            return LegalContentExtractor.get_paragraph(article_text, paragraph_num)
        else:
            return TextFormatter.format_extracted_text(article_text)
