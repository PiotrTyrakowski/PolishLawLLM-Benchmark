import pdfplumber
import json
import re
import os

def parse_questions(file_path: str) -> dict:
    """
    Parses a PDF file with questions and returns a dictionary.

    Args:
        file_path: The path to the PDF file.
        name: The name of the test.

    Returns:
        A dictionary with the test name and a list of questions.
    """
    with pdfplumber.open(file_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"

    # Regex to find question blocks. This regex is designed to be robust.
    # It looks for a number followed by a dot (the question number),
    # then captures the question text until it finds "A.", then captures answer A,
    # then "B.", captures answer B, then "C.", and captures answer C.
    # It handles multi-line questions and answers.
    question_pattern = re.compile(
        r"(\d+\.)\s*(.*?)\s*A\.\s*(.*?)\s*B\.\s*(.*?)\s*C\.\s*(.*?)(?=\d+\.|$)",
        re.DOTALL
    )

    questions = []
    matches = question_pattern.finditer(full_text)

    for match in matches:
        # We clean up the extracted text by replacing newlines and multiple spaces.
        question_text = ' '.join(match.group(2).strip().split())
        option_a = ' '.join(match.group(3).strip().split())
        option_b = ' '.join(match.group(4).strip().split())
        option_c = ' '.join(match.group(5).strip().split())

        questions.append({
            "question": question_text,
            "A": option_a,
            "B": option_b,
            "C": option_c
        })

    return {"questions": questions}


def parse_answers(file_path: str) -> dict:
    """
    Parses a PDF file with answers and returns a dictionary.

    Args:
        file_path: The path to the PDF file.
        name: The name of the test.

    Returns:
        A dictionary with the test name and a list of answers.
    """
    with pdfplumber.open(file_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"

    # Regex to find answers. It looks for a number followed by a dot,
    # a single letter (A, B, or C), and then captures the rest as legal basis.
    # It stops before the next question number.
    answer_pattern = re.compile(r"(\d+)\.\s+([A-C])\s+(.*?)(?=\n\d+\.|\Z)", re.DOTALL)

    answers = []
    matches = answer_pattern.finditer(full_text)

    for match in matches:
        question_number = int(match.group(1))
        correct_answer = match.group(2)
        legal_basis = ' '.join(match.group(3).strip().split())
        answers.append({
            "question_number": question_number,
            "correct_answer": correct_answer,
            "legal_basis": legal_basis
        })

    # Fallback for a simpler format if the above regex fails to find matches.
    if not answers:
        answer_pattern = re.compile(r"(\d+)\.\s+([A-C])")
        matches = answer_pattern.finditer(full_text)
        for match in matches:
            question_number = int(match.group(1))
            correct_answer = match.group(2)
            answers.append({
                "question_number": question_number,
                "correct_answer": correct_answer
            })


    return {"answers": answers}


if __name__ == "__main__":
    # The filenames are taken from the current directory.
    # Make sure the script is in the same directory as the PDF files.
    questions_pdf_path = "Zestaw_pytań_testowych_na_egzamin_wstępny_dla_kandydatów_na_aplikantów_adwokackich_i_radcowskich_28_września_2024.pdf"
    answers_pdf_path = "Wykaz_prawidłowych_odpowiedzi_do_zestawu_pytań_testowych_na_egzamin_wstępny_na_aplikację_adwokacką_i_radcowską_28_września_2024_.pdf"

    if os.path.exists(questions_pdf_path):
        # Parse questions and save to a JSON file
        parsed_questions = parse_questions(questions_pdf_path)
        with open("questions.json", "w", encoding="utf-8") as f:
            json.dump(parsed_questions, f, ensure_ascii=False, indent=4)
        print(f"Successfully parsed {len(parsed_questions['questions'])} questions from {questions_pdf_path}")
        print("Output saved to questions.json")
    else:
        print(f"Error: Questions file not found at {questions_pdf_path}")

    if os.path.exists(answers_pdf_path):
        # Parse answers and save to a JSON file
        parsed_answers = parse_answers(answers_pdf_path)
        with open("answers.json", "w", encoding="utf-8") as f:
            json.dump(parsed_answers, f, ensure_ascii=False, indent=4)
        print(f"Successfully parsed {len(parsed_answers['answers'])} answers from {answers_pdf_path}")
        print("Output saved to answers.json")
    else:
        print(f"Error: Answers file not found at {answers_pdf_path}") 