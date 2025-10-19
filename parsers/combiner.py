from typing import Dict, List


def create_unified_jsonl(
    questions: List[Dict], answers: List[Dict], exam_type: str, year: str
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

        unified_item = {
            "id": q_num,
            "year": int(year),
            "exam_type": exam_type,
            "question": q["question"],
            "choices": [f"A) {q['A']}", f"B) {q['B']}", f"C) {q['C']}"],
            "answer": answer_info.get("correct_answer", ""),
            "legal_basis": answer_info.get("legal_basis", ""),
        }

        unified_data.append(unified_item)

    return unified_data
