from pathlib import Path
from typing import Dict, Any, List
from collections import defaultdict

from src.common.file_operations import FileOperations


def calculate_stats(file_path: Path) -> Dict[str, Any]:
    dataset = FileOperations.load_jsonl(file_path)
    total_count = len(dataset)

    if total_count == 0:
        return {
            "accuracy_metrics": {"answer": 0.0, "legal_basis": 0.0},
            "text_metrics": {},
            "malformed_response_rate": 0.0,
            "questions_count": 0,
        }

    correct_count = 0
    correct_legal_basis = 0
    malformed_responses_count = 0
    text_metrics_sum = defaultdict(float)

    for data in dataset:
        accuracy_metrics = data.get("accuracy_metrics", {})
        if accuracy_metrics.get("answer", False):
            correct_count += 1
        if accuracy_metrics.get("legal_basis", False):
            correct_legal_basis += 1

        required_keys = [
            "model_legal_basis_content",
            "model_legal_basis",
            "model_answer",
        ]
        if any(not (data.get(k) or "").strip() for k in required_keys):
            malformed_responses_count += 1

        text_metrics = data.get("text_metrics", {})
        for metric_name, metric_value in text_metrics.items():
            assert isinstance(metric_value, (int, float))
            text_metrics_sum[metric_name] += metric_value

    accuracy = correct_count / total_count
    legal_basis = correct_legal_basis / total_count
    malformed_response_rate = malformed_responses_count / total_count

    avg_text_metrics = {
        metric_name: total_sum / total_count
        for metric_name, total_sum in text_metrics_sum.items()
    }

    return {
        "accuracy_metrics": {"answer": accuracy, "legal_basis": legal_basis},
        "text_metrics": avg_text_metrics,
        "malformed_response_rate": malformed_response_rate,
        "questions_count": total_count,
    }


def aggregate_results(results_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates average of metrics across multiple result dictionaries.
    """
    if not results_list:
        return {}

    correct_answers_sum = 0.0
    correct_legal_basis_sum = 0.0
    malformed_sum = 0.0
    total_questions_count = 0
    text_metrics_sums = defaultdict(float)

    for res in results_list:
        questions_count = res.get("questions_count", 0)
        if questions_count == 0:
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


def collect_yearly_stats(base_path: Path) -> Dict[str, Dict[str, Any]]:
    """
    Collects and aggregates statistics for each year directory.
    """
    if not base_path.is_dir():
        raise ValueError(f"Path '{base_path}' is not a directory.")

    year_dirs = sorted(
        [d for d in base_path.iterdir() if d.is_dir() and d.name.isdigit()],
        key=lambda x: int(x.name),
    )

    if not year_dirs:
        raise ValueError("No year directories found.")

    yearly_stats = {}

    for year_dir in year_dirs:
        year_name = year_dir.name
        jsonl_files = list(year_dir.glob("*.jsonl"))

        if not jsonl_files:
            continue

        year_results = []
        for file in jsonl_files:
            try:
                res = calculate_stats(file)
                year_results.append(res)
            except Exception as e:
                print(f"Warning: Failed to process {file}. Error: {e}")

        if year_results:
            yearly_stats[year_name] = aggregate_results(year_results)

    return yearly_stats


def calculate_stats_for_path(input_path: Path) -> Dict[str, Any]:
    target_files: List[Path] = []

    if input_path.is_dir():
        target_files = list(input_path.rglob("*.jsonl"))
        if not target_files:
            raise ValueError(f"No .jsonl files found in directory '{input_path}'.")
        print(f"Found {len(target_files)} files. Processing...")
    elif input_path.is_file():
        target_files = [input_path]
    else:
        raise ValueError(f"Invalid path '{input_path}'.")

    all_results = []
    for file in target_files:
        try:
            res = calculate_stats(file)
            all_results.append(res)
        except Exception as e:
            print(f"Warning: Failed to process {file}. Error: {e}")

    if not all_results:
        raise ValueError("No valid results computed.")

    return all_results[0] if len(all_results) == 1 else aggregate_results(all_results)
