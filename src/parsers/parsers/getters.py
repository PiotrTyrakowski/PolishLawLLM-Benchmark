from pathlib import Path

from src.parsers.parsers.parser import Parser
from src.parsers.extractors.question_extractor import QuestionExtractor
from src.parsers.extractors.answer_extractor import AnswerExtractor
from src.parsers.extractors.legal_content_extractor import LegalContentExtractor
from src.parsers.pdf_readers.pdf_legal_text_reader import PdfLegalTextReader
from src.parsers.pdf_readers.pdf_text_reader import PdfTextReader
from src.parsers.pdf_readers.pdf_table_reader import PdfTableReader


def get_questions_parser(file_path: Path) -> Parser:
    return Parser(
        file_path=file_path,
        extractor=QuestionExtractor(),
        pdf_reader=PdfTextReader(),
        start_page=2,
    )


def get_answers_parser(file_path: Path) -> Parser:
    return Parser(
        file_path=file_path,
        extractor=AnswerExtractor(),
        pdf_reader=PdfTableReader(),
        start_page=1,
    )


def get_legal_base_parser(file_path: Path) -> Parser:
    return Parser(
        file_path=file_path,
        extractor=LegalContentExtractor(),
        pdf_reader=PdfLegalTextReader(),
        start_page=1,
    )
