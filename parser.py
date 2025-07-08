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
    # Get all pdf files in the current directory
    all_files = [f for f in os.listdir('.') if f.endswith('.pdf')]

    # Group files by year and exam type
    exams = {}

    for pdf_file in all_files:
        # Extract year from filename (any 4-digit number)
        year_match = re.search(r'\d{4}', pdf_file)
        if not year_match:
            print(f"Warning: Could not find a year in '{pdf_file}', skipping.")
            continue
        year = year_match.group(0)

        # Determine exam type from filename
        exam_type = None
        if 'adwokack' in pdf_file or 'radcow' in pdf_file:
            exam_type = 'adwokacki_radcowy'
        elif 'komornic' in pdf_file:
            exam_type = 'komorniczy'
        elif 'notarialn' in pdf_file:
            exam_type = 'notarialny'

        if not exam_type:
            print(f"Warning: Could not determine exam type for '{pdf_file}', skipping.")
            continue

        # Initialize dictionaries if they don't exist
        if year not in exams:
            exams[year] = {}
        if exam_type not in exams[year]:
            exams[year][exam_type] = {}

        # Categorize as questions or answers pdf
        if pdf_file.startswith('Zestaw_pytań'):
            exams[year][exam_type]['questions_pdf'] = pdf_file
        elif pdf_file.startswith('Wykaz_prawidłowych_odpowiedzi'):
            exams[year][exam_type]['answers_pdf'] = pdf_file

    # Process each exam
    for year, types in exams.items():
        for exam_type, files in types.items():
            print(f"Processing exam: Year - {year}, Type - {exam_type}")

            # Create the output directory
            output_dir = os.path.join('exams', year, exam_type)
            os.makedirs(output_dir, exist_ok=True)

            # Parse questions if file exists
            if 'questions_pdf' in files:
                questions_pdf_path = files['questions_pdf']
                parsed_questions = parse_questions(questions_pdf_path)
                output_path = os.path.join(output_dir, 'questions.json')
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(parsed_questions, f, ensure_ascii=False, indent=4)
                print(f"  - Successfully parsed {len(parsed_questions['questions'])} questions.")
                print(f"    Saved to {output_path}")
            else:
                print(f"  - Warning: Questions file not found for this exam.")

            # Parse answers if file exists
            if 'answers_pdf' in files:
                answers_pdf_path = files['answers_pdf']
                parsed_answers = parse_answers(answers_pdf_path)
                output_path = os.path.join(output_dir, 'answers.json')
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(parsed_answers, f, ensure_ascii=False, indent=4)
                print(f"  - Successfully parsed {len(parsed_answers['answers'])} answers.")
                print(f"    Saved to {output_path}")
            else:
                print(f"  - Warning: Answers file not found for this exam.") 