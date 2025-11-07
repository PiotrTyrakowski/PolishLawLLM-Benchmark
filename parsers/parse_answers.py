import os
import re
from datetime import datetime

import pdfplumber

# Primary pattern for table format: question_number | correct_answer | legal_basis
# Handles the structured table format shown in the image
# Legal basis format: art. NUMBER [§ NUMBER] ABBREVIATION
# Examples: art. 17 § 1 k.s.h. | art. 272 k.s.h. | art. 505 § 1 k.p.c.
ANSWERS_REGEXP = re.compile(
    r"(\d+)\.\s+([A-C])\s+(art\.\s+\d+(?:\s+§\s+\d+)?\s+(?:[a-z]\.)+)",
    re.IGNORECASE | re.MULTILINE,
)


def parse_answers(file_path: str, validate: bool = True) -> dict:
    """
    Parses a PDF file with answers in table format and returns a dictionary.
    Expects exactly 150 answers in a structured table format.

    Args:
        file_path: The path to the PDF file.
        validate: Whether to validate parsed answers.

    Returns:
        A dictionary with answers and metadata.
    """
    print(f"Parsing answers from: {file_path}")

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
            question_number = int(match.group(1))
        except ValueError:
            continue

        correct_answer = match.group(2).strip()
        legal_basis = re.sub(r"\s+", " ", match.group(3).strip())

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
