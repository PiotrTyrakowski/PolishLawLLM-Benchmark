import os
import re
from typing import Optional
from parsers.LegalBaseExtractor.LegalBaseExtractor import LegalBaseExtractor
from parsers.parse_answers import (
    ARTICLE_PREFIX,
    ENTITY_ID,
    CODE_ABBREVIATION,
)


def initialize_extractors(pdf_dir: str) -> dict[str, LegalBaseExtractor]:
    all_files = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]
    extractors = {}
    for file in all_files:
        extractor = LegalBaseExtractor(os.path.join(pdf_dir, file))
        extractors[file.split(".")[0]] = extractor
    return extractors


def extract_legal_basis(
    legal_basis: str, extractors: dict[str, LegalBaseExtractor]
) -> str:
    legal_basis_components = parse_legal_basis(legal_basis)

    article_number = legal_basis_components["article_number"]
    paragraph_number = legal_basis_components["paragraph_number"]
    point_number = legal_basis_components["point_number"]
    code_abbreviation = legal_basis_components["code_abbreviation"]

    assert article_number is not None
    assert code_abbreviation is not None

    formatted_code_abbreviation = format_abbreviation(code_abbreviation)
    extractor = extractors[formatted_code_abbreviation]

    legal_basis_content = None
    if paragraph_number is not None and point_number is not None:
        legal_basis_content = extractor.get_point(
            article_number, point_number, paragraph_number
        )
    elif paragraph_number is not None:
        legal_basis_content = extractor.get_paragraph(article_number, paragraph_number)
    elif point_number is not None:
        legal_basis_content = extractor.get_point(article_number, point_number)
    else:
        legal_basis_content = extractor.get_article(article_number)

    return legal_basis_content


def parse_legal_basis(legal_basis: str) -> dict[str, Optional[str]]:
    code_pattern = rf"({CODE_ABBREVIATION})$"

    article_number_capture = rf"{ARTICLE_PREFIX}\s+({ENTITY_ID})"
    point_number_capture = rf"pkt\s+({ENTITY_ID})"
    paragraph_number_capture = rf"§\s+({ENTITY_ID})"

    article_match = re.search(article_number_capture, legal_basis, re.IGNORECASE)
    article_number = article_match.group(1) if article_match else None

    paragraph_match = re.search(paragraph_number_capture, legal_basis, re.IGNORECASE)
    paragraph_number = paragraph_match.group(1) if paragraph_match else None

    point_match = re.search(point_number_capture, legal_basis, re.IGNORECASE)
    point_number = point_match.group(1) if point_match else None

    code_match = re.search(code_pattern, legal_basis, re.IGNORECASE)
    code_abbreviation = code_match.group(1) if code_match else None

    return {
        "code_abbreviation": code_abbreviation,
        "article_number": article_number,
        "paragraph_number": paragraph_number,
        "point_number": point_number,
    }


def format_abbreviation(abbreviation: str) -> str:
    return abbreviation.replace(".", "").replace(" ", "").lower()
