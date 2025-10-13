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

    # Primary pattern for table format: question_number | correct_answer | legal_basis
    # Handles the structured table format shown in the image
    table_pattern = re.compile(
        r"(\d+)\.\s+([A-C])\s+(.*?)(?=\n\s*\d+\.\s+[A-C]\s+|\Z)",
        re.DOTALL | re.MULTILINE,
    )

    matches = list(table_pattern.finditer(full_text))
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

      # If we didn't find enough answers, try alternative patterns
    if len(answers) < 100:
        print("  Using alternative pattern for table format...")

        # Pattern for rows like "1. A art. 65 ust. 3 Konstytucji..."
        alt_pattern = re.compile(r"(\d+)\.\s+([A-C])\s+(.*?)(?=\n|\Z)", re.MULTILINE)
        alt_matches = list(alt_pattern.finditer(full_text))

        print(f"  Found {len(alt_matches)} additional answers using alternative pattern")

        for match in alt_matches:
            try:
                question_number = int(match.group(1))
                if any(a["question_number"] == question_number for a in answers):
                    continue

                correct_answer = match.group(2).strip()
                legal_basis = re.sub(r"\s+", " ", match.group(3).strip())

                answer = {
                    "question_number": question_number,
                    "correct_answer": correct_answer,
                    "legal_basis": legal_basis,
                }

                if validate and correct_answer not in ["A", "B", "C"]:
                    continue

                answers.append(answer)
            except ValueError:
                continue

    # Final fallback - extract from potential table structure using basic pattern
    if len(answers) < 100:
        print("  Using basic fallback pattern...")
        basic_pattern = re.compile(
            r"(\d+)\s+([A-C])\s+(.+?)(?=\n\d+\s+[A-C]|\Z)", re.DOTALL
        )
        basic_matches = list(basic_pattern.finditer(full_text))

        for match in basic_matches:
            try:
                question_number = int(match.group(1))
                if any(a["question_number"] == question_number for a in answers):
                    continue

                correct_answer = match.group(2).strip()
                legal_basis = re.sub(r"\s+", " ", match.group(3).strip())

                answers.append(
                    {
                        "question_number": question_number,
                        "correct_answer": correct_answer,
                        "legal_basis": legal_basis,
                    }
                )
            except ValueError:
                continue

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
