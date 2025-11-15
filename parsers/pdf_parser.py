import os
import re
from datetime import datetime
from typing import Dict, List, Tuple

import pdfplumber


def validate_question(question: Dict) -> Tuple[bool, List[str]]:
    """
    Validate a parsed question for completeness and correctness.

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    if "question_number" not in question:
        errors.append("Missing question number")

    if "question" not in question or not question["question"].strip():
        errors.append("Missing or empty question text")

    for option in ["A", "B", "C"]:
        if option not in question or not question[option].strip():
            errors.append(f"Missing or empty option {option}")

    if len(question.get("question", "")) < 10:
        errors.append("Question text suspiciously short")

    return len(errors) == 0, errors


def parse_questions(file_path: str, validate: bool = True) -> dict:
    """
    Parses a PDF file with questions and returns a dictionary.
    Assumes questions start from page 2 and there are exactly 150 questions.

    Args:
        file_path: The path to the PDF file.
        validate: Whether to validate parsed questions.

    Returns:
        A dictionary with questions and metadata.
    """
    print(f"Parsing questions from: {file_path}")

    with pdfplumber.open(file_path) as pdf:
        full_text = ""
        total_pages = len(pdf.pages)
        # Start from page 2 (index 1) as page 1 contains exam information
        for i, page in enumerate(pdf.pages[1:], 2):
            print(f"  Processing page {i}/{total_pages}...", end="\r")
            full_text += page.extract_text() + "\n"
        print()

    # Enhanced regex to find question blocks starting with question number
    # Matches: number. question_text A. option_a B. option_b C. option_c
    question_pattern = re.compile(
        r"(\d+)\.\s+(.*?)\s+A\.\s+(.*?)\s+B\.\s+(.*?)\s+C\.\s+(.*?)(?=\n\s*\d+\.\s+|\Z)",
        re.DOTALL | re.MULTILINE,
    )

    questions = []
    matches = list(question_pattern.finditer(full_text))
    invalid_questions = []

    print(f"  Found {len(matches)} potential questions")

    for i, match in enumerate(matches):
        try:
            question_num = int(match.group(1))
        except ValueError:
            question_num = i + 1

        question_text = re.sub(r"\s+", " ", match.group(2).strip())
        option_a = re.sub(r"\s+", " ", match.group(3).strip())
        option_b = re.sub(r"\s+", " ", match.group(4).strip())
        option_c = re.sub(r"\s+", " ", match.group(5).strip())

        question = {
            "question_number": question_num,
            "question": question_text,
            "A": option_a,
            "B": option_b,
            "C": option_c,
        }

        if validate:
            is_valid, errors = validate_question(question)
            if not is_valid:
                invalid_questions.append({"question": question, "errors": errors})
            else:
                questions.append(question)
        else:
            questions.append(question)

    if len(questions) != 150:
        print(f"  Warning: Expected 150 questions, found {len(questions)}")

    metadata = {
        "source_file": os.path.basename(file_path),
        "parsed_at": datetime.now().isoformat(),
        "total_questions": len(questions),
        "invalid_questions": len(invalid_questions),
        "expected_questions": 150,
    }

    result = {"questions": questions, "metadata": metadata}

    if invalid_questions:
        result["invalid_questions"] = invalid_questions

    return result
