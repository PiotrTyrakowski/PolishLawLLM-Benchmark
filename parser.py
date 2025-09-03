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
            'A': q['A'],
            'B': q['B'],
            'C': q['C'],
            'answer': answer_info.get('correct_answer', ''),
            'legal_basis': answer_info.get('legal_basis', '')
        }
        
        unified_data.append(unified_item)
    
    return unified_data

def parse_questions(file_path: str, validate: bool = True) -> dict:
    """
    Parses a PDF file with questions and returns a dictionary.

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
        for i, page in enumerate(pdf.pages, 1):
            print(f"  Processing page {i}/{total_pages}...", end='\r')
            full_text += page.extract_text() + "\n"
        print()

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
    matches = list(question_pattern.finditer(full_text))
    invalid_questions = []
    
    print(f"  Found {len(matches)} potential questions")

    for i, match in enumerate(matches):
        # Extract question number from the match
        question_num_str = match.group(1).strip('.')
        try:
            question_num = int(question_num_str)
        except ValueError:
            question_num = i + 1
        
        # Clean up the extracted text by replacing newlines and multiple spaces
        question_text = ' '.join(match.group(2).strip().split())
        option_a = ' '.join(match.group(3).strip().split())
        option_b = ' '.join(match.group(4).strip().split())
        option_c = ' '.join(match.group(5).strip().split())

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
    
    metadata = {
        "source_file": os.path.basename(file_path),
        "parsed_at": datetime.now().isoformat(),
        "total_questions": len(questions),
        "invalid_questions": len(invalid_questions)
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
    Parses a PDF file with answers and returns a dictionary.

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

    # Regex to find answers. It looks for a number followed by a dot,
    # a single letter (A, B, or C), and then captures the rest as legal basis.
    # It stops before the next question number.
    answer_pattern = re.compile(r"(\d+)\.\s+([A-C])\s+(.*?)(?=\n\d+\.|\Z)", re.DOTALL)

    answers = []
    matches = list(answer_pattern.finditer(full_text))
    
    print(f"  Found {len(matches)} answers")

    for match in matches:
        try:
            question_number = int(match.group(1))
        except ValueError:
            continue
        
        correct_answer = match.group(2)
        legal_basis = ' '.join(match.group(3).strip().split())
        
        answer = {
            "question_number": question_number,
            "correct_answer": correct_answer,
            "legal_basis": legal_basis
        }
        
        if validate and correct_answer not in ['A', 'B', 'C']:
            print(f"  Warning: Invalid answer '{correct_answer}' for question {question_number}")
            continue
        
        answers.append(answer)

    # Fallback for a simpler format if the above regex fails to find matches
    if not answers:
        print("  Using fallback pattern for answers...")
        answer_pattern = re.compile(r"(\d+)\.\s+([A-C])")
        matches = answer_pattern.finditer(full_text)
        for match in matches:
            try:
                question_number = int(match.group(1))
                correct_answer = match.group(2)
                answers.append({
                    "question_number": question_number,
                    "correct_answer": correct_answer
                })
            except ValueError:
                continue
    
    metadata = {
        "source_file": os.path.basename(file_path),
        "parsed_at": datetime.now().isoformat(),
        "total_answers": len(answers)
    }
    
    return {"answers": answers, "metadata": metadata}

def export_to_csv(questions: List[Dict], answers: List[Dict], output_path: str) -> None:
    """
    Export questions and answers to CSV format for easy analysis.
    """
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Question Number', 'Question', 'Option A', 'Option B', 'Option C', 
                        'Correct Answer', 'Legal Basis'])
        
        answer_dict = {a['question_number']: a for a in answers}
        
        for q in questions:
            answer_info = answer_dict.get(q['question_number'], {})
            writer.writerow([
                q['question_number'],
                q['question'],
                q['A'],
                q['B'],
                q['C'],
                answer_info.get('correct_answer', ''),
                answer_info.get('legal_basis', '')
            ])

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
    parser.add_argument('--csv', action='store_true', help='Also export to CSV format')
    parser.add_argument('--stats', action='store_true', help='Generate statistics')
    parser.add_argument('--validate', action='store_true', default=True, help='Validate parsed data')
    args = parser.parse_args()
    
    # Get all pdf files in the pdfs directory
    pdf_dir = 'pdfs'
    if not os.path.exists(pdf_dir):
        print(f"Error: '{pdf_dir}' directory not found")
        exit(1)
    
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

            # Create the output directory with new structure
            output_dir = os.path.join('data', 'exams', exam_type)
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
            
            
            # Export to CSV if requested
            if args.csv:
                csv_path = os.path.join(output_dir, f'exam_data_{year}.csv')
                export_to_csv(parsed_questions['questions'], parsed_answers['answers'], csv_path)
                print(f"    Exported to CSV: {csv_path}")
                
            # Generate statistics if requested
            if args.stats:
                stats = generate_statistics(parsed_questions)
                stats['year'] = year
                stats['exam_type'] = exam_type
                stats_path = os.path.join(output_dir, f'stats_{year}.json')
                with open(stats_path, 'w', encoding='utf-8') as f:
                    json.dump(stats, f, ensure_ascii=False, indent=2)
                print(f"    Statistics saved to {stats_path}")