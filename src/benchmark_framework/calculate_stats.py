import argparse
from pathlib import Path
from typing import Dict, Any

from src.parsers.utils.file_utils import FileOperations


def calculate_stats(file_path: Path) -> Dict[str, Any]:
    """
    Loads a JSONL file and calculates accuracy and averages specific metrics.
    """
    dataset = FileOperations.load_jsonl(file_path)
    total_count = len(dataset)

    if total_count == 0:
        return {
            "accuracy_metrics": {"answer": 0.0},
            "text_metrics": {
                "exact_match": 0.0,
                "bleu": 0.0,
                "weighted_bleu": 0.0,
            },
        }

    correct_count = 0
    empty_legal_basis_count = 0

    # Accumulators for all items
    sum_exact_match = 0.0
    sum_bleu = 0.0
    sum_weighted_bleu = 0.0

    for data in dataset:
        accuracy_metrics = data.get("accuracy_metrics", {})
        is_correct = accuracy_metrics.get("answer", False)
        if is_correct:
            correct_count += 1

        legal_basis_content = data.get("model_legal_basis_content", "")
        if not legal_basis_content or legal_basis_content.strip() == "":
            empty_legal_basis_count += 1

        text_metrics = data.get("text_metrics", {})
        exact_match = text_metrics.get("exact_match", 0.0)
        sum_exact_match += exact_match

        current_bleu = 0.0
        current_weighted = 0.0

        for key, value in text_metrics.items():
            if key.startswith("bleu"):
                current_bleu = value
            elif key.startswith("weighted_bleu"):
                current_weighted = value

        sum_bleu += current_bleu
        sum_weighted_bleu += current_weighted

    accuracy = correct_count / total_count
    avg_exact_match = sum_exact_match / total_count
    avg_bleu = sum_bleu / total_count
    avg_weighted_bleu = sum_weighted_bleu / total_count

    return {
        "accuracy_metrics": {"answer": accuracy},
        "text_metrics": {
            "exact_match": avg_exact_match,
            "bleu": avg_bleu,
            "weighted_bleu": avg_weighted_bleu,
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate statistics from a JSONL file with benchmark results."
    )
    parser.add_argument(
        "file_path",
        type=Path,
        help="Path to the JSONL file containing benchmark results.",
    )
    args = parser.parse_args()

    file_path: Path = args.file_path

    if not file_path.exists():
        print(f"Error: File '{file_path}' not found.")
        exit(1)

    results = calculate_stats(file_path)

    print()
    print("=== Results ===")
    print("Accuracy Metrics:")
    print(f"  Answer accuracy: {results['accuracy_metrics']['answer']:.4f}")
    print()
    print("Text Metrics:")
    print(f"  Exact match: {results['text_metrics']['exact_match']:.4f}")
    print(f"  BLEU: {results['text_metrics']['bleu']:.4f}")
    print(f"  Weighted BLEU: {results['text_metrics']['weighted_bleu']:.4f}")
