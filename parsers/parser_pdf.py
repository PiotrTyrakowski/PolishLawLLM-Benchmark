import pdfplumber
import json
import re
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import csv

def save_as_jsonl(data: List[Dict], output_path: str) -> None:
    """
    Save data in JSONL format (one JSON object per line).
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def load_jsonl(file_path: str) -> List[Dict]:
    """
    Load data from JSONL format.
    """
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data


def validate_question(question: Dict) -> Tuple[bool, List[str]]:
    """
    Validate a parsed question for completeness and correctness.
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if 'question_number' not in question:
        errors.append("Missing question number")
    
    if 'question' not in question or not question['question'].strip():
        errors.append("Missing or empty question text")
    
    for option in ['A', 'B', 'C']:
        if option not in question or not question[option].strip():
            errors.append(f"Missing or empty option {option}")
    
    if len(question.get('question', '')) < 10:
        errors.append("Question text suspiciously short")
    
    return len(errors) == 0, errors

def create_unified_jsonl(questions: List[Dict], answers: List[Dict], exam_type: str, year: str) -> List[Dict]:
    """
    Create unified JSONL format combining questions and answers with metadata.
    
    Args:
        questions: List of question dictionaries
        answers: List of answer dictionaries
        exam_type: Type of exam (e.g., 'adwokacki_radcowy')
        year: Year of the exam
    
    Returns:
        List of unified question-answer dictionaries
    """
    answer_dict = {a['question_number']: a for a in answers}
    unified_data = []
    
    for q in questions:
        q_num = q['question_number']
        answer_info = answer_dict.get(q_num, {})
        
        unified_item = {
            'id': q_num,
            'year': int(year),
            'exam_type': exam_type,
            'question': q['question'],
            'choices': [f"A) {q['A']}", f"B) {q['B']}", f"C) {q['C']}"],
            'answer': answer_info.get('correct_answer', ''),
            'legal_basis': answer_info.get('legal_basis', '')
        }
        
        unified_data.append(unified_item)
    
    return unified_data

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
            print(f"  Processing page {i}/{total_pages}...", end='\r')
            full_text += page.extract_text() + "\n"
        print()

    # Enhanced regex to find question blocks starting with question number
    # Matches: number. question_text A. option_a B. option_b C. option_c
    question_pattern = re.compile(
        r"(\d+)\.\s+(.*?)\s+A\.\s+(.*?)\s+B\.\s+(.*?)\s+C\.\s+(.*?)(?=\n\s*\d+\.\s+|\Z)",
        re.DOTALL | re.MULTILINE
    )

    questions = []
    matches = list(question_pattern.finditer(full_text))
    invalid_questions = []

    print(f"  Found {len(matches)} potential questions")

    for i, match in enumerate(matches):
        # Extract question number from the match
        try:
            question_num = int(match.group(1))
        except ValueError:
            question_num = i + 1

        # Clean up the extracted text by replacing newlines and multiple spaces
        question_text = re.sub(r'\s+', ' ', match.group(2).strip())
        option_a = re.sub(r'\s+', ' ', match.group(3).strip())
        option_b = re.sub(r'\s+', ' ', match.group(4).strip())
        option_c = re.sub(r'\s+', ' ', match.group(5).strip())

        question = {
            "question_number": question_num,
            "question": question_text,
            "A": option_a,
            "B": option_b,
            "C": option_c
        }

        if validate:
            is_valid, errors = validate_question(question)
            if not is_valid:
                invalid_questions.append({"question": question, "errors": errors})
            else:
                questions.append(question)
        else:
            questions.append(question)

    # Ensure we have exactly 150 questions
    if len(questions) != 150:
        print(f"  Warning: Expected 150 questions, found {len(questions)}")

    metadata = {
        "source_file": os.path.basename(file_path),
        "parsed_at": datetime.now().isoformat(),
        "total_questions": len(questions),
        "invalid_questions": len(invalid_questions),
        "expected_questions": 150
    }

    result = {
        "questions": questions,
        "metadata": metadata
    }

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
            print(f"  Processing page {i}/{total_pages}...", end='\r')
            full_text += page.extract_text() + "\n"
        print()

    answers = []

    # Primary pattern for table format: question_number | correct_answer | legal_basis
    # Handles the structured table format shown in the image
    table_pattern = re.compile(
        r"(\d+)\.\s+([A-C])\s+(.*?)(?=\n\s*\d+\.\s+[A-C]\s+|\Z)",
        re.DOTALL | re.MULTILINE
    )

    matches = list(table_pattern.finditer(full_text))
    print(f"  Found {len(matches)} answers using table pattern")

    for match in matches:
        try:
            question_number = int(match.group(1))
        except ValueError:
            continue

        correct_answer = match.group(2).strip()
        legal_basis = re.sub(r'\s+', ' ', match.group(3).strip())

        answer = {
            "question_number": question_number,
            "correct_answer": correct_answer,
            "legal_basis": legal_basis
        }

        if validate and correct_answer not in ['A', 'B', 'C']:
            print(f"  Warning: Invalid answer '{correct_answer}' for question {question_number}")
            continue

        answers.append(answer)

    # Alternative pattern for simpler table format (fallback)
    if len(answers) < 100:  # If we didn't find enough answers, try alternative patterns
        print("  Using alternative pattern for table format...")

        # Pattern for rows like "1. A art. 65 ust. 3 Konstytucji..."
        alt_pattern = re.compile(r"(\d+)\.\s+([A-C])\s+(.*?)(?=\n|\Z)", re.MULTILINE)
        alt_matches = list(alt_pattern.finditer(full_text))

        print(f"  Found {len(alt_matches)} additional answers using alternative pattern")

        for match in alt_matches:
            try:
                question_number = int(match.group(1))
                # Skip if we already have this question
                if any(a['question_number'] == question_number for a in answers):
                    continue

                correct_answer = match.group(2).strip()
                legal_basis = re.sub(r'\s+', ' ', match.group(3).strip())

                answer = {
                    "question_number": question_number,
                    "correct_answer": correct_answer,
                    "legal_basis": legal_basis
                }

                if validate and correct_answer not in ['A', 'B', 'C']:
                    continue

                answers.append(answer)
            except ValueError:
                continue

    # Final fallback - extract from potential table structure using basic pattern
    if len(answers) < 100:
        print("  Using basic fallback pattern...")
        basic_pattern = re.compile(r"(\d+)\s+([A-C])\s+(.+?)(?=\n\d+\s+[A-C]|\Z)", re.DOTALL)
        basic_matches = list(basic_pattern.finditer(full_text))

        for match in basic_matches:
            try:
                question_number = int(match.group(1))
                if any(a['question_number'] == question_number for a in answers):
                    continue

                correct_answer = match.group(2).strip()
                legal_basis = re.sub(r'\s+', ' ', match.group(3).strip())

                answers.append({
                    "question_number": question_number,
                    "correct_answer": correct_answer,
                    "legal_basis": legal_basis
                })
            except ValueError:
                continue

    # Sort answers by question number
    answers.sort(key=lambda x: x['question_number'])

    # Ensure we have exactly 150 answers
    if len(answers) != 150:
        print(f"  Warning: Expected 150 answers, found {len(answers)}")

    metadata = {
        "source_file": os.path.basename(file_path),
        "parsed_at": datetime.now().isoformat(),
        "total_answers": len(answers),
        "expected_answers": 150
    }

    return {"answers": answers, "metadata": metadata}

def generate_statistics(exam_data: Dict) -> Dict:
    """
    Generate statistics about parsed exam data.
    """
    questions = exam_data.get('questions', [])
    stats = {
        'total_questions': len(questions),
        'avg_question_length': sum(len(q['question']) for q in questions) / len(questions) if questions else 0,
        'avg_option_length': sum(
            len(q.get('A', '')) + len(q.get('B', '')) + len(q.get('C', ''))
            for q in questions) / (3 * len(questions)) if questions else 0,
        'questions_with_short_text': sum(1 for q in questions if len(q['question']) < 50),
        'questions_with_long_text': sum(1 for q in questions if len(q['question']) > 500)
    }
    return stats

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Parse Polish law exam PDFs')
    parser.add_argument('--stats', action='store_true', help='Generate statistics')
    parser.add_argument('--validate', action='store_true', default=True, help='Validate parsed data')
    args = parser.parse_args()
    
    # Get all pdf files in the pdfs directory
    pdf_dir = 'pdfs'
    if not os.path.exists(pdf_dir):
        if not os.path.exists(f"../{pdf_dir}"):
            print(f"Error: '{pdf_dir}' directory not found")
            exit(1)
        pdf_dir = f"../{pdf_dir}"
    
    all_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]

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

            # Create the output directory with new structure in root directory
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            output_dir = os.path.join(root_dir, 'data', 'exams', exam_type)
            os.makedirs(output_dir, exist_ok=True)

            # Parse questions and answers
            parsed_questions = None
            parsed_answers = None
            
            # Parse questions if file exists
            if 'questions_pdf' in files:
                questions_pdf_path = os.path.join(pdf_dir, files['questions_pdf'])
                parsed_questions = parse_questions(questions_pdf_path, validate=args.validate)
                print(f"  - Successfully parsed {len(parsed_questions['questions'])} questions.")
                
                if 'invalid_questions' in parsed_questions:
                    print(f"    Warning: {len(parsed_questions['invalid_questions'])} invalid questions found")
            else:
                print(f"  - Warning: Questions file not found for this exam.")
                continue

            # Parse answers if file exists
            if 'answers_pdf' in files:
                answers_pdf_path = os.path.join(pdf_dir, files['answers_pdf'])
                parsed_answers = parse_answers(answers_pdf_path, validate=args.validate)
                print(f"  - Successfully parsed {len(parsed_answers['answers'])} answers.")
            else:
                print(f"  - Warning: Answers file not found for this exam.")
                # Continue without answers - we can still create questions-only dataset
                parsed_answers = {'answers': []}
            
            # Create unified JSONL format
            unified_data = create_unified_jsonl(
                parsed_questions['questions'], 
                parsed_answers['answers'], 
                exam_type, 
                year
            )
            
            # Save unified JSONL file
            unified_path = os.path.join(output_dir, f'{year}.jsonl')
            save_as_jsonl(unified_data, unified_path)
            print(f"  - Saved unified format: {unified_path}")
            
            
            # Generate statistics if requested
            if args.stats:
                stats = generate_statistics(parsed_questions)
                stats['year'] = year
                stats['exam_type'] = exam_type
                stats_path = os.path.join(output_dir, f'stats_{year}.json')
                with open(stats_path, 'w', encoding='utf-8') as f:
                    json.dump(stats, f, ensure_ascii=False, indent=2)
                print(f"    Statistics saved to {stats_path}")