import os
import re
from datetime import datetime

import pdfplumber

ARTICLE_PREFIX = r"art\."
ENTITY_ID = r"\d+[a-z]*"
POINT_PATTERN = rf"pkt\s+{ENTITY_ID}"
PARAGRAPH_PATTERN = rf"§\s+{ENTITY_ID}"
CODE_ABBREVIATION = r"(?:[a-z\.]+|k\.r\.\s+i\s+o\.|k\.\s+r\.\s+i\s+o\.)"

# Full legal basis pattern (only one capture group for the entire legal basis)
LEGAL_BASIS = rf"({ARTICLE_PREFIX}\s+{ENTITY_ID}(?:\s+{POINT_PATTERN})?(?:\s+{PARAGRAPH_PATTERN})?(?:\s+{POINT_PATTERN})?\s+{CODE_ABBREVIATION})"

# Separator between legal basis and question number
SEPARATOR = r"\s*\n\s*"

# Question number
QUESTION_NUMBER = r"(\d+)\."

# Answer letter
ANSWER_LETTER = r"([A-C])"

# Complete pattern
ANSWERS_REGEXP = re.compile(
    rf"{LEGAL_BASIS}{SEPARATOR}{QUESTION_NUMBER}\s+{ANSWER_LETTER}",
    re.IGNORECASE | re.MULTILINE,
)


def parse_answers(file_path: str, validate: bool = True) -> dict:
    """
    Parses a PDF file with answers in table format and returns a dictionary.
    Returns dictionary with answers and metadata.
    """
    # TODO: Add processing of upper index numbers
    with pdfplumber.open(file_path) as pdf:
        full_text = ""
        total_pages = len(pdf.pages)
        for i, page in enumerate(pdf.pages, 1):
            print(f"  Processing page {i}/{total_pages}...", end="\r")
            full_text += page.extract_text() + "\n"
        print()

    answers = []

    matches = list(ANSWERS_REGEXP.finditer(full_text))
    print(f"  Found {len(matches)} answers using table pattern")

    for match in matches:
        try:
            question_number = int(match.group(2))
        except ValueError:
            continue

        legal_basis = re.sub(r"\s+", " ", match.group(1).strip())
        correct_answer = match.group(3).strip()

        answer = {
            "question_number": question_number,
            "correct_answer": correct_answer,
            "legal_basis": legal_basis,
        }

        if validate and correct_answer not in ["A", "B", "C"]:
            print(
                f"  Warning: Invalid answer '{correct_answer}' for question {question_number}"
            )
            continue

        answers.append(answer)

    answers.sort(key=lambda x: x["question_number"])

    if len(answers) != 150:
        print(f"  Warning: Expected 150 answers, found {len(answers)}")

    metadata = {
        "source_file": os.path.basename(file_path),
        "parsed_at": datetime.now().isoformat(),
        "total_answers": len(answers),
        "expected_answers": 150,
    }

    return {"answers": answers, "metadata": metadata}
