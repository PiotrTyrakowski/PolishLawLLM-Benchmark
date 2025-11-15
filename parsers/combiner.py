from typing import Dict, List
from parsers.LegalBaseExtractor.LegalBaseExtractor import LegalBaseExtractor
from parsers.LegalBaseExtractor.initialize_extractors import extract_legal_basis


def create_unified_jsonl(
    questions: List[Dict],
    answers: List[Dict],
    exam_type: str,
    year: str,
    extractors: dict[str, LegalBaseExtractor],
) -> List[Dict]:
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
    answer_dict = {a["question_number"]: a for a in answers}
    unified_data = []

    for q in questions:
        q_num = q["question_number"]
        answer_info = answer_dict.get(q_num, {})

        correct_answer = answer_info.get("correct_answer", "")
        legal_basis = answer_info.get("legal_basis", "")

        if not correct_answer or not legal_basis:
            continue

        try:
            legal_basis_content = extract_legal_basis(legal_basis, extractors)
        except Exception as e:
            print(f"    Warning: {e} for question {q_num}")
            continue

        unified_item = {
            "id": q_num,
            "year": int(year),
            "exam_type": exam_type,
            "question": q["question"],
            "choices": [f"A) {q['A']}", f"B) {q['B']}", f"C) {q['C']}"],
            "answer": correct_answer,
            "legal_basis": legal_basis,
            "legal_basis_content": legal_basis_content,
        }

        unified_data.append(unified_item)

    return unified_data
