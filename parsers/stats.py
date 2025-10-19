from typing import Dict


def generate_statistics(exam_data: Dict) -> Dict:
    """
    Generate statistics about parsed exam data.
    """
    questions = exam_data.get("questions", [])
    stats = {
        "total_questions": len(questions),
        "avg_question_length": sum(len(q["question"]) for q in questions) / len(questions)
        if questions
        else 0,
        "avg_option_length": sum(
            len(q.get("A", "")) + len(q.get("B", "")) + len(q.get("C", ""))
            for q in questions
        )
        / (3 * len(questions))
        if questions
        else 0,
        "questions_with_short_text": sum(1 for q in questions if len(q["question"]) < 50),
        "questions_with_long_text": sum(1 for q in questions if len(q["question"]) > 500),
    }
    return stats
