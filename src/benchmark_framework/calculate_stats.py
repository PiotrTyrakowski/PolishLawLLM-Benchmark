import argparse
from pathlib import Path
from typing import Dict, Any
from collections import defaultdict

from src.parsers.utils.file_utils import FileOperations


def calculate_stats(file_path: Path) -> Dict[str, Any]:
    """
    Loads a JSONL file and calculates accuracy and averages for all text metrics.
    """
    dataset = FileOperations.load_jsonl(file_path)
    total_count = len(dataset)

    if total_count == 0:
        return {
            "accuracy_metrics": {"answer": 0.0, "legal_basis": 0.0},
            "text_metrics": {},
            "malformed_response_rate": 0.0,
        }

    correct_count = 0
    correct_legal_basis = 0
    malformed_responses_count = 0

    # Accumulators for text metrics (dynamically collected)
    text_metrics_sum = defaultdict(float)

    for data in dataset:
        accuracy_metrics = data.get("accuracy_metrics", {})
        is_correct = accuracy_metrics.get("answer", False)
        if is_correct:
            correct_count += 1

        is_correct_legal_basis = accuracy_metrics.get("legal_basis", False)
        if is_correct_legal_basis:
            correct_legal_basis += 1

        required_keys = [
            "model_legal_basis_content",
            "model_legal_basis",
            "model_answer",
        ]
        if any(not (data.get(k) or "").strip() for k in required_keys):
            malformed_responses_count += 1

        # Accumulate all text metrics dynamically
        text_metrics = data.get("text_metrics", {})
        for metric_name, metric_value in text_metrics.items():
            assert isinstance(metric_value, (int, float))
            text_metrics_sum[metric_name] += metric_value

    accuracy = correct_count / total_count
    legal_basis = correct_legal_basis / total_count

    avg_text_metrics = {
        metric_name: total_sum / total_count
        for metric_name, total_sum in text_metrics_sum.items()
    }

    malformed_response_rate = malformed_responses_count / total_count

    return {
        "accuracy_metrics": {"answer": accuracy, "legal_basis": legal_basis},
        "text_metrics": avg_text_metrics,
        "malformed_response_rate": malformed_response_rate,
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
    print(f"  Legal basis accuracy: {results['accuracy_metrics']['legal_basis']:.4f}")
    print()
    print("Text Metrics:")
    for metric_name, metric_value in sorted(results["text_metrics"].items()):
        print(f"  {metric_name}: {metric_value:.4f}")
    print()
    print(f"Malformed Response Rate: {results['malformed_response_rate']:.4f}")
