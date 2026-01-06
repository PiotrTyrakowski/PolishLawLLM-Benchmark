import argparse
from pathlib import Path
from typing import Dict, Any, List
from collections import defaultdict

from src.common.file_operations import FileOperations


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
        "questions_count": total_count,
    }


def aggregate_results(results_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates the average of metrics across multiple result dictionaries.
    """
    if not results_list:
        return {}

    # Accumulators
    correct_answers_sum = 0.0
    correct_legal_basis_sum = 0.0
    malformed_sum = 0.0
    total_questions_count = 0
    text_metrics_sums = defaultdict(float)

    for res in results_list:
        questions_count = res.get("questions_count")
        if questions_count is None:
            continue

        total_questions_count += questions_count
        correct_answers_sum += (
            res["accuracy_metrics"].get("answer", 0.0) * questions_count
        )
        correct_legal_basis_sum += (
            res["accuracy_metrics"].get("legal_basis", 0.0) * questions_count
        )
        malformed_sum += res.get("malformed_response_rate", 0.0) * questions_count

        for k, v in res.get("text_metrics", {}).items():
            text_metrics_sums[k] += v * questions_count

    if total_questions_count == 0:
        raise ValueError("Total questions count is zero; cannot aggregate results.")

    # Average out
    avg_accuracy = {
        "answer": correct_answers_sum / total_questions_count,
        "legal_basis": correct_legal_basis_sum / total_questions_count,
    }
    avg_malformed = malformed_sum / total_questions_count
    avg_text_metrics = {}
    for k, total_val in text_metrics_sums.items():
        avg_text_metrics[k] = total_val / total_questions_count

    return {
        "accuracy_metrics": avg_accuracy,
        "text_metrics": avg_text_metrics,
        "malformed_response_rate": avg_malformed,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate statistics from a JSONL file with benchmark results."
    )
    parser.add_argument(
        "file_path",
        type=Path,
        help="Path to the JSONL file or directory containing benchmark results.",
    )
    args = parser.parse_args()

    input_path: Path = args.file_path
    target_files: List[Path] = []

    if not input_path.exists():
        print(f"Error: Path '{input_path}' not found.")
        exit(1)

    if input_path.is_dir():
        target_files = list(input_path.rglob("*.jsonl"))
        if not target_files:
            print(f"No .jsonl files found in directory '{input_path}'.")
            exit(0)
        print(f"Found {len(target_files)} files. Processing...")
    elif input_path.is_file():
        target_files = [input_path]
    else:
        print(f"Error: incorrect input path '{input_path}'.")
        exit(1)

    # Call calculate_stats for each file
    all_results = []
    for file in target_files:
        try:
            res = calculate_stats(file)
            all_results.append(res)
        except Exception as e:
            print(f"Warning: Failed to process {file}. Error: {e}")

    if not all_results:
        print("No valid results computed.")
        exit(1)

    if len(all_results) == 1:
        final_results = all_results[0]
    else:
        final_results = aggregate_results(all_results)

    print()
    print("=== Results ===")
    print("Accuracy Metrics:")
    print(f"  Answer accuracy: {final_results['accuracy_metrics']['answer']:.4f}")
    print(
        f"  Legal basis accuracy: {final_results['accuracy_metrics']['legal_basis']:.4f}"
    )
    print()
    print("Text Metrics:")
    for metric_name, metric_value in sorted(final_results["text_metrics"].items()):
        print(f"  {metric_name}: {metric_value:.4f}")
    print()
    print(f"Malformed Response Rate: {final_results['malformed_response_rate']:.4f}")
